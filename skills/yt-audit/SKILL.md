---
name: yt-audit
description: >-
  Audit a YouTube channel end to end - packaging, consistency, the first
  fifteen seconds, and what to fix first. Use for "audit my channel", "why
  isn't my channel growing", "review my videos", or a pasted channel URL.
  По-русски: «проверь мой канал», «аудит канала», «почему канал не растёт», «разбери мои ролики».
---

# yt-audit

An audit that lists twenty problems is a way of avoiding the one that matters. This ends in ONE fix.

## Before you write

1. Read `~/.claude/youtube/voice.md` if it exists. That is the user's voice profile: how they talk
   on camera, the words they never use, who they are talking to, what they will not claim. If it
   does not exist, ask for **three of their own videos**, read or transcribe them, infer the voice,
   and write the file. A script in the wrong voice is worse than no script, because they have to
   read it out loud.
2. Never invent a number, a result or a source. If a figure would strengthen it and you do not have
   one, ask for it or write the line without it.

## What to look at, in this order

1. **The last ten titles, as a set.** Read them as a list, the way the channel page shows them. Do
   they promise different things? Run them through `../yt-package/title.py`. A channel where every
   title is the same shape has a format problem, not a title problem.
2. **The thumbnails, at feed size.** Shrink them. What survives? If three of them are unreadable at
   that size, that is the fix and nothing else matters yet.
3. **The first fifteen seconds of the three most recent.** Transcribe them and score with
   `../yt-script/hookscore.py`. This is where most channels lose.
4. **Upload rhythm.** Not frequency - CONSISTENCY. Six videos in one week and then nothing for a
   month is worse than one a fortnight forever.
5. **The retention shape**, if they can export it. `/yt-retention`.

## What to hand back

- The single biggest fix, named, with what to do this week.
- Three things that are already working, so they do not break them. Be specific; "your energy is
  good" is not an observation.
- What NOT to do yet, and why.

Never open an audit with praise you do not mean, and never end one with a list of twenty things.

## Русский язык

- Если пользователь пишет по-русски или его `voice.md` на русском — всё, что отдаёшь, пиши по-русски:
  живой разговорный язык, который можно произнести вслух, без канцелярита и кальки с английского.
- Формулы хуков бери из `hooks.json` в русской версии: `name_ru`, `shape_ru`, `example_ru`,
  `fails_when_ru`. Английские поля — для англоязычных роликов.
- `title.py` и `hookscore.py` сами распознают кириллицу и отвечают по-русски.
- Оценки в русских списках — перевод английской эвристики, отдельной калибровки на русских роликах
  не было. Низкий балл — повод перечитать, высокий — не обещание.
- Финальный вопрос по-русски: **публикуем или правим?**
- На Windows, если `python3` не находится, запускай `python`.

## The gate

Nothing here publishes. This skill writes and you publish. Every output ends in a block the user
copies, and the last line of every run is the question: **ship it, or change it?**
