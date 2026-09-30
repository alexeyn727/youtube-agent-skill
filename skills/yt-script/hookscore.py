#!/usr/bin/env python3
"""hookscore.py - score a YouTube hook before you waste a take on it.

Five properties, 0-100 each, and a verdict that is 60% the mean and 40% the weakest one. The
weakest-link weighting is deliberate: a hook with four strong properties and one dead one is a hook
that leaks at the dead one, and averaging hides that.

    python3 hookscore.py hooks.txt            # one hook per line, ranked
    python3 hookscore.py --hook "one line"    # score a single hook
    python3 hookscore.py --json hooks.txt     # machine-readable

English and Russian. A hook with Cyrillic in it is scored against the Russian word lists and the
match_ru patterns in hooks.json, and the report is printed in Russian. JSON keys stay English.

WHAT THIS CAN AND CANNOT TELL YOU. Measured against 74 real short-form hooks (first 15 seconds of
auto-captions, top-8 and bottom-8 by views across five channels): it separates deliberately bad
hooks from real ones well, and it separates a creator's own hits from their own misses barely at
all. Treat a low score as a reason to look again, never a high score as a promise. The Russian
lists are a translation of the English heuristic, not a separate calibration.
"""
import json, os, re, sys

if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
FORMULAS = json.load(open(os.path.join(HERE, "hooks.json"), encoding="utf-8"))["hooks"]

def is_ru(t): return bool(re.search(r"[а-яё]", t, re.I))

EN = {
 "filler": {"basically","actually","literally","just","really","very","so","kind","sort","like",
            "guys","hey","welcome","today","video","subscribe","channel"},
 "vague": {"amazing","incredible","insane","crazy","huge","massive","game","changer","secret",
           "powerful","ultimate","best","revolutionary","mind","blowing","unbelievable"},
 "concrete": re.compile(r"\b(\d[\d,.]*\s?(%|k|m|x|s|m|h)?|\$\d|\d+\s?(second|minute|hour|day|week|month|year)s?)\b", re.I),
 "you": re.compile(r"\b(you|your|you're|youre|yourself)\b", re.I),
 "stake": re.compile(r"\b(lose|lost|wasting|waste|quit|fail|broke|cost|risk|before|stop|never|die|dying|dead)\b", re.I),
 "curiosity": re.compile(r"\b(why|how|what|which|until|before|but|nobody|almost|except|reason|actually)\b", re.I),
 "closed": re.compile(r"\b(because|so that|which means)\b", re.I),
 "band": (9, 24),
}
# Russian inflects, so the vague list is stems matched by prefix, and the regexes end in \w*.
RU = {
 "filler": {"короче","типа","ну","вот","просто","реально","очень","вообще","буквально","собственно",
            "значит","ребята","ребят","привет","всем","друзья","сегодня","видео","ролик","ролике",
            "подписывайтесь","подпишись","подписаться","канал","канале"},
 "vague": ("потрясающ","невероятн","безумн","крут","огромн","мощн","секрет","лучш","революцион",
           "умопомрачит","шок","топов","гениальн","идеальн","нереальн","офигенн","бомбическ"),
 "concrete": re.compile(r"(\d[\d\s,.]*\s?(%|тыс|млн|млрд|₽|руб|\$|x|х\b)|\$\d|\d+\s?(секунд|минут|час|дн|день|недел|месяц|год|лет)\w*)", re.I),
 "you": re.compile(r"\b(ты|тебя|тебе|тобой|твой|твоя|твоё|твое|твои|твоих|твоим|вы|вас|вам|вами|ваш|ваша|ваше|ваши|ваших|вашим)\b", re.I),
 "stake": re.compile(r"\b(теря\w*|потер\w*|трат\w*|потрат\w*|слива\w*|слил\w*|брос\w*|провал\w*|разор\w*|стоит|стоил\w*|"
                     r"риск\w*|прежде|перестань\w*|хватит|никогда|умира\w*|умер\w*|мёртв\w*|мертв\w*|ошиб\w*|впуст\w*|зря)\b", re.I),
 "curiosity": re.compile(r"\b(почему|зачем|как|что|какой|какая|какие|пока|но|однако|никто|почти|кроме|причина|оказалось|"
                         r"на самом деле)\b", re.I),
 "closed": re.compile(r"\b(потому что|так что|а значит|то есть)\b", re.I),
 # Russian words are longer and spoken a little slower, so the same ten seconds holds fewer of them.
 "band": (7, 20),
}

def lang(t): return RU if is_ru(t) else EN

def words(t): return re.findall(r"[a-zа-яё0-9'%$.₽]+", t.lower())

def vague_hits(w, L):
    if L is EN: return sum(1 for x in w if x in EN["vague"])
    return sum(1 for x in w if x.startswith(RU["vague"]))

def specificity(t):
    L = lang(t); w = words(t)
    if not w: return 0
    nums = len(L["concrete"].findall(t))
    vague = vague_hits(w, L)
    filler = sum(1 for x in w if x in L["filler"])
    s = 34 + nums * 22 - vague * 16 - filler * 5
    # proper nouns that are not sentence-initial read as named things
    s += min(18, 6 * sum(1 for x in t.split()[1:] if x[:1].isupper()))
    return max(0, min(100, s))

def address(t):
    L = lang(t)
    n = len(L["you"].findall(t))
    first = 30 if L["you"].search(" ".join(t.split()[:6])) else 0
    return max(0, min(100, 26 + n * 20 + first))

def stakes(t):
    L = lang(t)
    n = len(L["stake"].findall(t))
    return max(0, min(100, 22 + n * 26 + (14 if L["concrete"].search(t) else 0)))

def curiosity(t):
    L = lang(t)
    n = len(L["curiosity"].findall(t))
    q = 18 if t.strip().endswith("?") else 0
    # a hook that resolves itself has no gap left
    closed = -18 if L["closed"].search(t) else 0
    return max(0, min(100, 24 + n * 17 + q + closed))

def brevity(t):
    lo, hi = lang(t)["band"]
    n = len(words(t))
    if n == 0: return 0
    # the band a spoken hook lands in inside 10 seconds (~150wpm English, ~130wpm Russian)
    if lo <= n <= hi: return 100
    if n < lo: return max(30, 100 - (lo - n) * 11)
    return max(10, 100 - (n - hi) * 7)

PROPS = [("SPECIFICITY", specificity), ("ADDRESS", address), ("STAKES", stakes),
         ("CURIOSITY", curiosity), ("BREVITY", brevity)]

def classify(t):
    ru = is_ru(t)
    best, hits = None, 0
    for f in FORMULAS:
        n = sum(1 for p in f.get("match_ru" if ru else "match", []) if re.search(p, t, re.I))
        if n > hits: best, hits = f, n
    if not best: return ("Без формулы" if ru else "Unclassified"), 0
    return (best.get("name_ru", best["name"]) if ru else best["name"]), hits

def score(t):
    parts = {n: fn(t) for n, fn in PROPS}
    vals = list(parts.values())
    verdict = round(0.6 * (sum(vals) / len(vals)) + 0.4 * min(vals))
    name, hits = classify(t)
    return parts, verdict, name, hits

def band(v): return "STRONG" if v >= 72 else "WORKABLE" if v >= 55 else "WEAK"

FIX = {
 "SPECIFICITY": "swap one adjective for a number, a name or a date",
 "ADDRESS": "say 'you' in the first six words",
 "STAKES": "name what it costs them to keep doing it the current way",
 "CURIOSITY": "cut the half of the sentence that answers itself",
 "BREVITY": "9 to 24 words. Read it out loud and stop where you run out of breath",
}
LABEL_RU = {"SPECIFICITY": "КОНКРЕТИКА", "ADDRESS": "ОБРАЩЕНИЕ", "STAKES": "СТАВКИ",
            "CURIOSITY": "ИНТРИГА", "BREVITY": "КРАТКОСТЬ"}
BAND_RU = {"STRONG": "СИЛЬНЫЙ", "WORKABLE": "РАБОЧИЙ", "WEAK": "СЛАБЫЙ"}
FIX_RU = {
 "SPECIFICITY": "замените одно прилагательное цифрой, именем или датой",
 "ADDRESS": "скажите «ты» или «вы» в первых шести словах",
 "STAKES": "назовите, чего зрителю стоит продолжать делать по-старому",
 "CURIOSITY": "уберите ту половину фразы, которая сама на себя отвечает",
 "BREVITY": "7–20 слов. Прочитайте вслух и остановитесь там, где кончился воздух",
}

def report(t, parts, verdict, name, hits):
    ru = is_ru(t)
    print(f"\n  {t.strip()}")
    print(f"  {'-' * min(72, max(20, len(t.strip())))}")
    for k, v in parts.items():
        print(f"    {(LABEL_RU[k] if ru else k):<12} {v:3d}  {'#' * (v // 5)}")
    b = band(verdict)
    print(f"    {('ИТОГ' if ru else 'VERDICT'):<12} {verdict:3d}  {BAND_RU[b] if ru else b}")
    low = min(parts, key=parts.get)
    if ru:
        print(f"    формула      {name}" + (f"  (совпало шаблонов: {hits})" if hits else "  (ни одна формула не подошла - обычно это пересказ, а не хук)"))
        print(f"    слабее всего {LABEL_RU[low]} - {FIX_RU[low]}")
    else:
        print(f"    formula      {name}" + (f"  ({hits} pattern{'s' if hits != 1 else ''} matched)" if hits else "  (no formula matched - that is usually a summary, not a hook)"))
        print(f"    weakest      {low} - {FIX[low]}")

def main():
    a = sys.argv[1:]
    as_json = "--json" in a
    a = [x for x in a if x != "--json"]
    if "--hook" in a:
        lines = [a[a.index("--hook") + 1]]
    elif a and os.path.exists(a[0]):
        lines = [l for l in open(a[0], encoding="utf-8-sig").read().splitlines() if l.strip()]
    else:
        print(__doc__); sys.exit(1 if not a else 0)
    out = []
    for t in lines:
        parts, verdict, name, hits = score(t)
        out.append({"hook": t.strip(), "properties": parts, "verdict": verdict,
                    "band": band(verdict), "formula": name, "matched": hits})
    out.sort(key=lambda r: -r["verdict"])
    if as_json:
        print(json.dumps([{k: v for k, v in r.items() if k != "matched"} for r in out], indent=1, ensure_ascii=False)); return
    for r in out:
        report(r["hook"], r["properties"], r["verdict"], r["formula"], r["matched"])
    if len(out) > 1:
        w = out[0]
        if is_ru(w["hook"]): print(f"\n  победитель: {w['hook']}  ({w['verdict']}, {BAND_RU[w['band']]})\n")
        else: print(f"\n  winner: {w['hook']}  ({w['verdict']}, {w['band']})\n")

if __name__ == "__main__":
    main()
