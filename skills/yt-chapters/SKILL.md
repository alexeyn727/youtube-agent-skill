---
name: yt-chapters
description: >-
  Write YouTube chapters from a transcript, validated against YouTube's own
  rules so they actually render. Use for "add chapters", "timestamps",
  "break this video into sections".
  По-русски: «таймкоды», «главы для видео», «разбей ролик на части».
---

# yt-chapters

```bash
python3 chapters.py transcript.srt --target 8
```

## The rules, which are not optional

A chapter list that breaks any of these silently does not become chapters at all - the block just
sits in the description doing nothing:

- The first entry must be **00:00**.
- There must be **at least three**.
- Each must be **at least 10 seconds** long.

The tool checks all three and tells you when a list is invalid rather than letting you paste it.

## Retitle every line

`chapters.py` finds the BOUNDARIES well - it scores the pauses you actually took by how much the
vocabulary shifts across them. The titles it emits are the topic words, and they are a draft. A
chapter called "Thumbnails Titles Packaging" is a placeholder. Rewrite each one as the promise of
that section, in the user's voice, three to five words.

Chapters are also a retention diagnostic: if a section cannot be named in five words, it is two
sections or it is filler.

## Русский язык

- Если пользователь пишет по-русски или его `voice.md` на русском — всё, что отдаёшь, пиши по-русски:
  живой разговорный язык, который можно произнести вслух, без канцелярита и кальки с английского.
- Формулы хуков бери из `hooks.json` в русской версии: `name_ru`, `shape_ru`, `example_ru`,
  `fails_when_ru`. Английские поля — для англоязычных роликов.
- `chapters.py` понимает русские расшифровки: отбрасывает русские служебные слова и сравнивает слова по основе, поэтому «канал» и «канала» — одна тема.
- Оценки в русских списках — перевод английской эвристики, отдельной калибровки на русских роликах
  не было. Низкий балл — повод перечитать, высокий — не обещание.
- Финальный вопрос по-русски: **публикуем или правим?**
- На Windows, если `python3` не находится, запускай `python`.

## The gate

Nothing here publishes. This skill writes and you publish. Every output ends in a block the user
copies, and the last line of every run is the question: **ship it, or change it?**
