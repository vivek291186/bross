# Lip-sync for MPFB2 characters: phonemes from the TTS tokenizer (IPA) aligned to the audio energy envelope,
# mapped onto the MakeHuman "visemes01" shape keys (Microsoft viseme set) + a little jawOpen from loudness.
import numpy as np, re

# IPA -> viseme target name (shape key "visemes:<name>")
VIS = [
    ("aɪ", "ay_11"), ("aʊ", "aw_09"), ("ɔɪ", "oy_10"), ("eɪ", "ey_eh_uh_04"), ("oʊ", "ow_08"), ("əʊ", "ow_08"),
    ("tʃ", "sh_ch_jh_zh_16"), ("dʒ", "sh_ch_jh_zh_16"), ("ɑː", "aa_02"), ("ɜː", "er_05"), ("iː", "y_iy_ih_ix_06"), ("uː", "w_uw_07"), ("ɔː", "ao_03"),
    ("ɑ", "aa_02"), ("a", "aa_ah_ax_01"), ("æ", "aa_02"), ("ʌ", "aa_ah_ax_01"), ("ə", "aa_ah_ax_01"), ("ɐ", "aa_ah_ax_01"), ("ɛ", "ey_eh_uh_04"), ("e", "ey_eh_uh_04"),
    ("ɪ", "y_iy_ih_ix_06"), ("i", "y_iy_ih_ix_06"), ("ʊ", "ey_eh_uh_04"), ("u", "w_uw_07"), ("ɔ", "ao_03"), ("o", "ow_08"), ("ɚ", "er_05"), ("ɜ", "er_05"),
    ("w", "w_uw_07"), ("j", "y_iy_ih_ix_06"), ("ɹ", "r_13"), ("r", "r_13"), ("l", "l_14"), ("h", "h_12"), ("ɾ", "d_t_n_19"),
    ("s", "s_z_15"), ("z", "s_z_15"), ("ʃ", "sh_ch_jh_zh_16"), ("ʒ", "sh_ch_jh_zh_16"), ("θ", "th_dh_17"), ("ð", "th_dh_17"), ("f", "f_v_18"), ("v", "f_v_18"),
    ("d", "d_t_n_19"), ("t", "d_t_n_19"), ("n", "d_t_n_19"), ("k", "k_g_ng_20"), ("g", "k_g_ng_20"), ("ŋ", "k_g_ng_20"), ("p", "p_b_m_21"), ("b", "p_b_m_21"), ("m", "p_b_m_21"),
]
VOWELS = {"ay_11", "aw_09", "oy_10", "ey_eh_uh_04", "ow_08", "aa_02", "er_05", "y_iy_ih_ix_06", "w_uw_07", "ao_03", "aa_ah_ax_01"}
JAW = {"aa_02": 0.55, "aa_ah_ax_01": 0.4, "ao_03": 0.4, "aw_09": 0.45, "ay_11": 0.45, "ey_eh_uh_04": 0.3, "ow_08": 0.3, "er_05": 0.25, "y_iy_ih_ix_06": 0.15, "w_uw_07": 0.15, "oy_10": 0.35, "h_12": 0.25, "l_14": 0.2, "r_13": 0.15}

def phonemes(ipa):
    """IPA string -> list of (viseme or None for pause/space, weight)"""
    out = []; i = 0; s = ipa
    while i < len(s):
        c = s[i]
        if c in " ,.!?;:—-":
            out.append((None, 0.6 if c != " " else 0.35)); i += 1; continue
        if c in "ˈˌː̩":   # stress / length marks
            if c == "ː" and out and out[-1][0]: out[-1] = (out[-1][0], out[-1][1] * 1.3)
            i += 1; continue
        hit = None
        for pat, vis in VIS:
            if s.startswith(pat, i): hit = (pat, vis); break
        if hit: out.append((hit[1], 1.3 if hit[1] in VOWELS else 0.8)); i += len(hit[0])
        else: i += 1
    return out

def envelope(audio, sr, hop=0.01):
    n = int(hop * sr); m = len(audio) // n
    e = np.sqrt((audio[:m * n].reshape(m, n) ** 2).mean(1))
    return e / (e.max() + 1e-9)

def align(text, audio, sr, tokenizer, lang="en-us"):
    """returns list of (t_seconds, viseme, jaw_amount) phoneme centres, and (t0,t1) speech span"""
    ipa = tokenizer.phonemize(text, lang=lang)
    ph = phonemes(ipa)
    env = envelope(audio, sr); hop = 0.01
    voiced = np.where(env > 0.08)[0]
    if len(voiced) == 0: return [], (0, 0)
    t0, t1 = voiced[0] * hop, voiced[-1] * hop
    # proportional durations, shortened for leading/trailing pauses
    w = np.array([p[1] for p in ph], float)
    if len(w) and ph[0][0] is None: w[0] = 0.1
    if len(w) and ph[-1][0] is None: w[-1] = 0.1
    cum = np.concatenate([[0], np.cumsum(w)]) / max(1e-6, w.sum())
    out = []
    for k, (vis, _) in enumerate(ph):
        a, b = t0 + cum[k] * (t1 - t0), t0 + cum[k + 1] * (t1 - t0)
        tc = (a + b) / 2
        ei = min(len(env) - 1, int(tc / hop)); loud = float(env[max(0, ei - 2): ei + 3].max())
        out.append((tc, vis, loud))
    return out, (t0, t1)

def key_shapes(kb, phones, t_offset, fps, name_prefix="visemes:", jaw_key="faceunits:jawOpen", gain=1.0):
    """keyframe shape keys on key_blocks kb. phones: output of align(); t_offset: seconds where the audio starts in the timeline"""
    F = lambda t: int(round((t + t_offset) * fps)) + 1
    names = sorted({v for _, v, _ in phones if v})
    # zero all at the start and end
    for v in names + [jaw_key.split(":")[-1]]:
        k = kb.get(name_prefix + v) if v in names else kb.get(jaw_key)
        if k is None: continue
        k.value = 0.0; k.keyframe_insert("value", frame=F(phones[0][0]) - 4); k.keyframe_insert("value", frame=F(phones[-1][0]) + 5)
    for i, (t, vis, loud) in enumerate(phones):
        f = F(t)
        if vis is None:   # pause: everything closed
            for v in names:
                k = kb.get(name_prefix + v)
                if k: k.value = 0.0; k.keyframe_insert("value", frame=f)
            if kb.get(jaw_key): kb[jaw_key].value = 0.0; kb[jaw_key].keyframe_insert("value", frame=f)
            continue
        k = kb.get(name_prefix + vis)
        amp = min(1.0, (0.55 + 0.6 * loud) * gain)
        if k:
            # ramp: 0 at previous/next phoneme centres, peak here
            for j in (i - 1, i + 1):
                if 0 <= j < len(phones) and phones[j][1] != vis:
                    k.value = 0.0; k.keyframe_insert("value", frame=F(phones[j][0]))
            k.value = amp; k.keyframe_insert("value", frame=f)
        jk = kb.get(jaw_key)
        if jk:
            jk.value = JAW.get(vis, 0.08) * (0.6 + 0.6 * loud) * gain; jk.keyframe_insert("value", frame=f)
    return names
