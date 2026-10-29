# Bro Bros Fun production toolkit (backup)

Restore into a fresh workspace:
- `toolkit/eng2/*` -> `/home/claude/eng2/` (Blender episode builder `build9.py`, sets, props, lip-sync)
- `toolkit/bbf/*` -> `/home/claude/bbf/` (episode scripts + `engine.py`: Kokoro voices, music, SFX)
- `toolkit/song/*` -> `/home/claude/song/` (`build_song2.py` + song specs)
- `toolkit/tools/*` -> `/home/claude/tools/` (ov9 / ov_song2 overlays, compose_ep / compose_song, make_short2, Mac render scripts)
- `toolkit/lib/make_lib.py` rebuilds `/home/claude/lib/bbf_lib.blend` (characters + all animations) from the episode .blend files.

Dependencies: `pip install bpy==4.2.0 soundfile kokoro-onnx opencv-python-headless pillow scipy` (python3.11),
Kokoro model files from github.com/thewh1teagle/kokoro-onnx releases (model-files-v1.0) into /home/claude/tts/.
Song lyric timing comes from Suno's aligned-lyrics API (no Whisper needed).
