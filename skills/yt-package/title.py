#!/usr/bin/env python3
"""title.py - lint a YouTube title and thumbnail pairing before you publish it.

    python3 title.py --title "..." --thumb "AI RAN IT"
    python3 title.py titles.txt            # one per line, ranked
    python3 title.py --title "..." --json

The pairing is the unit, not the title. A title that repeats the thumbnail text wastes half the
click surface, and that is the single most common mistake this checks for.

Length: YouTube truncates around 60 characters on desktop search and around 40 on a mobile home
feed. Both limits are reported because they are different failures - a desktop truncation loses the
tail, a mobile one can lose the subject.

English and Russian. A Cyrillic title is checked against Russian word lists, and title/thumbnail
duplication is compared on word stems, so "канал" on the thumbnail and "канала" in the title count
as the same word. Messages print in Russian; JSON keys and issue codes stay English.
"""
import json, re, sys, os

if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")

DESKTOP, MOBILE, HARD = 60, 40, 100
VAGUE = {"amazing","incredible","insane","crazy","huge","massive","ultimate","best","powerful",
         "secret","revolutionary","mindblowing","epic","perfect","complete","everything"}
STOP = {"the","a","an","of","for","to","in","on","and","or","is","are","with","your","you","my","i",
        "this","that","it","how","what","why"}
# Russian: vague words are stems matched by prefix; stop words are whole words.
VAGUE_RU = ("потрясающ","невероятн","безумн","крут","огромн","мощн","секрет","лучш","революцион",
            "умопомрачит","шок","эпичн","идеальн","полн","нереальн","топов","гениальн")
STOP_RU = {"и","в","во","на","с","со","к","ко","по","о","об","от","до","за","из","у","для","без","про",
           "а","но","или","это","этот","эта","эти","как","что","почему","зачем","мой","моя","мои","мое","моё",
           "твой","твоя","твои","ваш","ваша","ваши","ты","вы","я","он","она","мы","они","не","же","ли","бы"}

def is_ru(t): return bool(re.search(r"[а-яё]", t, re.I))
def words(t): return re.findall(r"[a-zа-яё0-9']+", t.lower().replace("ё", "е"))
# Crude stem: Russian endings change with case and number, so compare the first five letters.
def stem(w): return w[:5] if re.match(r"[а-я]", w) and len(w) > 5 else w

MSG = {
 "en": {
  "hard": "{n} characters - YouTube's hard limit is {h}",
  "desktop": "{n} characters - desktop search cuts near {d}",
  "fits": "{n} characters, inside the {d}-character desktop cut",
  "mobile": 'a mobile feed shows about "{head}..." - check the subject survives',
  "shouting": "{c} all-caps words - two is the ceiling before it reads as spam",
  "caps_ok": "{c} all-caps word for emphasis",
  "vague": "{v} - swap for a number, a name or a date",
  "number": "carries a concrete figure ({nums})",
  "no-number": "no number, date or name - the most reliable single fix",
  "question": "open question in the title",
  "front-load": "the first three words are all filler - move the subject forward",
  "duplicate": "thumbnail repeats the title on {s} - the thumbnail should say what the title does not",
  "distinct": "thumbnail and title carry different words",
  "thumb-length": "{c} words on the thumbnail - three is the ceiling at feed size",
  "head": "{c} chars   score {s}/100",
 },
 "ru": {
  "hard": "{n} симв. - жёсткий предел YouTube {h}",
  "desktop": "{n} симв. - поиск на компьютере обрезает около {d}",
  "fits": "{n} симв., влезает в {d} симв. поиска на компьютере",
  "mobile": 'в мобильной ленте видно примерно "{head}..." - проверьте, что суть не отрезана',
  "shouting": "{c} слов капсом - больше двух выглядит как спам",
  "caps_ok": "{c} слово капсом для акцента",
  "vague": "{v} - замените цифрой, именем или датой",
  "number": "есть конкретная цифра ({nums})",
  "no-number": "нет цифры, даты или имени - это самое надёжное исправление",
  "question": "открытый вопрос в заголовке",
  "front-load": "первые три слова - служебные, вынесите суть вперёд",
  "duplicate": "обложка повторяет заголовок: {s} - на обложке должно быть то, чего нет в заголовке",
  "distinct": "на обложке и в заголовке разные слова",
  "thumb-length": "{c} слов на обложке - в ленте читается максимум три",
  "head": "{c} симв.   оценка {s}/100",
 },
}

def check(title, thumb=None):
    t = title.strip()
    ru = is_ru(t) or bool(thumb and is_ru(thumb))
    M = MSG["ru" if ru else "en"]
    n = len(t)
    issues, good = [], []
    if n > HARD: issues.append(("length", M["hard"].format(n=n, h=HARD)))
    elif n > DESKTOP: issues.append(("length", M["desktop"].format(n=n, d=DESKTOP)))
    else: good.append(M["fits"].format(n=n, d=DESKTOP))
    if n > MOBILE:
        head = t[:MOBILE].rsplit(" ", 1)[0]
        issues.append(("mobile", M["mobile"].format(head=head)))
    caps = [w for w in t.split() if len(w) > 2 and w.isupper()]
    if len(caps) > 2: issues.append(("shouting", M["shouting"].format(c=len(caps))))
    elif caps: good.append(M["caps_ok"].format(c=len(caps)))
    if ru: v = [w for w in words(t) if w.startswith(VAGUE_RU)]
    else:  v = [w for w in words(t) if w in VAGUE]
    if v: issues.append(("vague", M["vague"].format(v=", ".join(sorted(set(v))))))
    nums = re.findall(r"\d[\d,.]*%?", t)
    if nums: good.append(M["number"].format(nums=", ".join(nums[:3])))
    else: issues.append(("no-number", M["no-number"]))
    if t.endswith("?"): good.append(M["question"])
    stop = STOP | STOP_RU
    front = [w for w in words(t)[:3] if w not in stop]
    if not front: issues.append(("front-load", M["front-load"]))
    if thumb:
        hw = {stem(w) for w in words(thumb) if w not in stop}
        shared = {w for w in words(t) if w not in stop and stem(w) in hw}
        if shared:
            issues.append(("duplicate", M["duplicate"].format(s=", ".join(sorted(shared)))))
        else:
            good.append(M["distinct"])
        if len(words(thumb)) > 4:
            issues.append(("thumb-length", M["thumb-length"].format(c=len(words(thumb)))))
    score = max(0, min(100, 100 - 14 * len(issues) + 4 * len(good)))
    return {"title": t, "chars": n, "score": score, "issues": issues, "good": good, "lang": "ru" if ru else "en"}

def show(r):
    M = MSG[r["lang"]]
    print(f'\n  "{r["title"]}"')
    print("  " + M["head"].format(c=r["chars"], s=r["score"]))
    for k, m in r["issues"]: print(f"    x  {k:<12} {m}")
    for m in r["good"]:      print(f"    ok              {m}")

def main():
    a = sys.argv[1:]
    as_json = "--json" in a; a = [x for x in a if x != "--json"]
    thumb = a[a.index("--thumb") + 1] if "--thumb" in a else None
    if "--title" in a:
        rows = [check(a[a.index("--title") + 1], thumb)]
    elif a and os.path.exists(a[0]):
        rows = [check(l, thumb) for l in open(a[0], encoding="utf-8-sig").read().splitlines() if l.strip()]
    else:
        print(__doc__); sys.exit(1)
    rows.sort(key=lambda r: -r["score"])
    if as_json: print(json.dumps([{k: v for k, v in r.items() if k != "lang"} for r in rows], indent=1, ensure_ascii=False)); return
    for r in rows: show(r)
    print()

if __name__ == "__main__":
    main()
