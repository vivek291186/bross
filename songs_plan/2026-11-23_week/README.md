# Next week: one song a day at 08:00 IST (23 to 29 Nov 2026)

Built from the research tree (playbook, next week ideas, trend bank, our own Metricool results). Full details for every song (Suno lyrics, Style and Exclude fields, Meshy motion prompts, set, thumbnail brief, Short and Reel hooks, YouTube title, tags, hashtags) are in `songs.json`.

| Day | # | Song | Why this day | BPM |
|---|---|---|---|---|
| Mon 23 | 45 | Here Comes the Garbage Truck! (stomp, lift, dump) | vehicle songs chart, strong Monday opener | 118 |
| Tue 24 | 46 | Who Took the Cookie? One for You, One for Me! | our most proven hook plus sharing | 112 |
| Wed 25 | 47 | Red Light, Green Light, Cross With Me! | our most shared Reel topic, safety | 110 |
| Thu 26 | 48 | Brave at the Doctor! One, Two, Three, Sticker! | healthy habit and helper song of the week | 108 |
| Fri 27 | 49 | Freeze, Then Jingle! Christmas Freeze Dance | strongest song for Friday, plus the weekly compilation | 116 |
| Sat 28 | 50 | Dear Santa, I'm THIS Tall! | rising Reels trend, kindness wish | 112 |
| Sun 29 | 51 | Snowflake, Snowflake, Float Down Slow | weekly slow bedtime song | 66 |

## Publishing (each day)

* 08:00 IST (02:30 UTC): long video on YouTube, Reel on Instagram.
* 08:05 IST: the YouTube Short, related video set to the full song.
* Made for kids ON, AI content disclosure ON, thumbnail set by hand if Metricool warns.
* Description ending: "Original song created for Bro Bros Fun. New songs every day at 8 AM!" (the older videos say 10 AM and 4 PM).

Note: our own data says 10:00 IST is our best slot (about 611 vs 346 views at 16:00). Treat 08:00 as a one week test and compare the first 48 hours with the 10:00 weeks.

## Making each song

1. Suno (paid plan): paste the lyrics, Style and Exclude fields; pick the take whose chorus lands by about 0:15; master to about -14 LUFS.
2. Meshy: the four motion prompts per song (standing, in place, no floor moves).
3. Blender: `toolkit/song/build_song2.py` with a spec like `spec_song08.py`, set and cast from `songs.json`, save to `songs/<date>/songNN_*.mp4`, plus `_short`, `_reel` and `_thumb`.
4. Schedule in Metricool for 08:00 and 08:05 IST.
