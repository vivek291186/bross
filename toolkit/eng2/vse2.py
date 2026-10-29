# Run with: blender -b -P vse2.py   (assembles frames + overlays + audio -> mp4)
import bpy, json, os
B = os.path.expanduser("~/Downloads/.bbf/ep02/")
OV = B + "ep02ov/"
OUT = os.path.expanduser("~/Downloads/Bro Bros Fun - Ep 2 - The Lunchbox Swap Mystery.mp4")
M = json.load(open(OV + "ov.json")); total = M["total"]
scn = bpy.context.scene
scn.render.resolution_x, scn.render.resolution_y, scn.render.resolution_percentage = 1920, 1080, 100
scn.render.fps = 24; scn.frame_start = 1; scn.frame_end = total
scn.view_settings.view_transform = "Standard"; scn.sequencer_colorspace_settings.name = "sRGB"
se = scn.sequence_editor_create()
def imgseq(name, folder, files, ch, start):
    s = se.sequences.new_image(name, folder + files[0], ch, start)
    for f in files[1:]: s.elements.append(f)
    return s
frames = sorted(x for x in os.listdir(B + "frames") if x.endswith(".jpg"))
base = imgseq("frames", B + "frames/", frames, 1, 1)
se.sequences.new_sound("audio", B + "audio.wav", 2, 1)
logo = se.sequences.new_image("logo", OV + "logo.png", 3, 1); logo.frame_final_end = total + 1; logo.blend_type = "ALPHA_OVER"
for i, (fn, f0, f1) in enumerate(M["subs"]):
    s = se.sequences.new_image("sub%d" % i, OV + fn, 4 + (i % 2), f0); s.frame_final_end = max(f0 + 1, f1); s.blend_type = "ALPHA_OVER"
intro = imgseq("intro", OV, ["intro_%04d.png" % (i + 1) for i in range(M["intro"])], 6, 1); intro.blend_type = "ALPHA_OVER"
for j, (pre, f0, n) in enumerate(M["wipes"]):
    w = imgseq("wipe%d" % j, OV, ["%s%04d.png" % (pre, i) for i in range(n)], 7, f0); w.blend_type = "ALPHA_OVER"
e0 = M["end_start"]
end = imgseq("end", OV, ["end_%04d.png" % (i + 1) for i in range(M["end_n"])], 8, e0); end.blend_type = "ALPHA_OVER"
hold = se.sequences.new_image("endhold", OV + "end_%04d.png" % M["end_n"], 9, e0 + M["end_n"]); hold.frame_final_end = total + 1; hold.blend_type = "ALPHA_OVER"
r = scn.render
r.image_settings.file_format = "FFMPEG"
r.ffmpeg.format = "MPEG4"; r.ffmpeg.codec = "H264"; r.ffmpeg.constant_rate_factor = "HIGH"; r.ffmpeg.ffmpeg_preset = "GOOD"
r.ffmpeg.audio_codec = "AAC"; r.ffmpeg.audio_bitrate = 192; r.ffmpeg.audio_channels = "STEREO"; r.ffmpeg.audio_mixrate = 48000
r.use_sequencer = True; r.use_compositing = False
r.filepath = OUT
bpy.ops.render.render(animation=True)
open(B + "VSE_DONE", "w").write("ok")
