---
name: yt-retention
description: >-
  Read a YouTube Studio audience-retention export and find where viewers
  actually leave, then say what to change. Use for "why do people stop
  watching", "my retention is bad", a pasted retention chart or CSV, or "fix
  my pacing".
  По-русски: «почему не досматривают», «плохое удержание», «где уходят зрители», «график удержания».
---

# yt-retention

The retention graph is the only honest feedback YouTube gives you. Almost nobody exports it.

```bash
python3 retention.py retention.csv --duration 600
python3 retention.py retention.csv --transcript transcript.srt
```

Getting the file: Studio -> a video -> Analytics -> Engagement -> the audience-retention chart ->
the download icon -> "Audience retention".

## Three different problems

- **HOOK LEAK** - what is lost in the first 30 seconds. Under 25% is healthy. This is always the
  first thing to fix and it is always the first fifteen seconds of script, never the edit.
- **CLIFFS** - single steep drops. A cliff is a moment: a topic change with no signposting, a
  sponsor read, a long setup. With `--transcript` the tool prints what was being said there, which
  is what makes the report actionable instead of interesting.
- **SLIDE** - the steady bleed across the middle. A flat slide is pacing. The fix is cutting, not
  rewriting.

## What to hand back

Name the single biggest leak and one change for it. Not a list of five. Then, only if asked, the
rest. And if the hook leak is healthy and the slide is flat, say the video is fine and the problem
is packaging - send them to `/yt-package`.

## Русский язык

- Если пользователь пишет по-русски или его `voice.md` на русском — всё, что отдаёшь, пиши по-русски:
  живой разговорный язык, который можно произнести вслух, без канцелярита и кальки с английского.
- Формулы хуков бери из `hooks.json` в русской версии: `name_ru`, `shape_ru`, `example_ru`,
  `fails_when_ru`. Английские поля — для англоязычных роликов.
- `retention.py` читает выгрузку из русской локали: файл через точку с запятой и числа вида «45,3» (иначе 45,3% превратилось бы в 453%).
- Оценки в русских списках — перевод английской эвристики, отдельной калибровки на русских роликах
  не было. Низкий балл — повод перечитать, высокий — не обещание.
- Финальный вопрос по-русски: **публикуем или правим?**
- На Windows, если `python3` не находится, запускай `python`.

## The gate

Nothing here publishes. This skill writes and you publish. Every output ends in a block the user
copies, and the last line of every run is the question: **ship it, or change it?**
