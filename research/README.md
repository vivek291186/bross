# Bro Bros research agent

Continuous market research on what kids watch and what music attracts them.

- `knowledge.json` - the knowledge tree (branches -> leaves). Each leaf: t (finding), src, conf (high/medium/low), date.
- `playbook` inside knowledge.json - the rules used when making next week's songs.
- `log` inside knowledge.json - one line per research run.
- `build_tree.py` - builds `tree.html` from knowledge.json.
- Live page (artifact): slug ea37e855-8a3d-4681-abdb-0d7a2a88fb0a  https://claude.ai/artifact/VvVZud9NVxQwTcRszcbyxM
- Metricool brand blogId 7552626 (Asia/Kolkata) for our own channel results.

Before making a new week of songs: read knowledge.json playbook + branches first.
