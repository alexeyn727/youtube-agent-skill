---
name: yt-edit
description: >-
  Turn a raw recording's transcript into an edit decision list - dead air,
  filler cues and retakes, with timecodes. Use for "edit this", "cut the
  dead space", "tighten this video", "I rambled", or any request to shorten
  footage from a transcript.
  По-русски: «убери паузы», «сократи ролик», «что вырезать», «я много мямлил».
---

# yt-edit

An edit decision list from a timestamped transcript. It prints the cuts. You apply them.

```bash
python3 deadair.py transcript.srt              # srt, vtt or whisper json
python3 deadair.py transcript.srt --floor 0.35 --json
```

No transcript yet? Ask for one, or produce one first - `whisper`, `faster-whisper`, or the caption
track YouTube generates on an unlisted upload all work. Do not guess at timings.

## What it finds

- **DEAD** - gaps longer than the floor, trimmed from the MIDDLE so both sides keep a breath.
  Cutting flush against speech is what makes a tightened take sound gasping.
- **FILLER** - cues that are nothing but "um", "so yeah", "basically".
- **REPEAT** - a sentence restarted. Compared against the last cue that was actually speech, not
  the literal previous cue, because most retakes have an "um" between the two attempts.

## What it will not do

It does not touch media. It has no opinion about your B-roll. A 40% cut on the report is a 40% cut
of SPEECH, and if the video has a long silent demo in it that number is wrong - check the report
against the footage before you trust the runtime at the bottom.

## Русский язык

- Если пользователь пишет по-русски или его `voice.md` на русском — всё, что отдаёшь, пиши по-русски:
  живой разговорный язык, который можно произнести вслух, без канцелярита и кальки с английского.
- Формулы хуков бери из `hooks.json` в русской версии: `name_ru`, `shape_ru`, `example_ru`,
  `fails_when_ru`. Английские поля — для англоязычных роликов.
- `deadair.py` знает русские слова-паразиты: «эм», «ну вот», «короче», «типа», «в общем», «как бы», «это самое».
- Оценки в русских списках — перевод английской эвристики, отдельной калибровки на русских роликах
  не было. Низкий балл — повод перечитать, высокий — не обещание.
- Финальный вопрос по-русски: **публикуем или правим?**
- На Windows, если `python3` не находится, запускай `python`.

## The gate

Nothing here publishes. This skill writes and you publish. Every output ends in a block the user
copies, and the last line of every run is the question: **ship it, or change it?**
