"""LinkedIn guest-API discovery: sweep, dedupe against the tracker, and screen full postings.
No browser, no login. Everything is cached under tmp/li/ so a batch never pages postings through context.

    python scripts/li_jobs.py search [--days 3] [--kw "Masterarbeit KI" --kw ...]   # -> tmp/li/cards.json
    python scripts/li_jobs.py filter                                                 # new student/tech cards
    python scripts/li_jobs.py screen 4464760543,4467054846 [--req]                  # language gate + flags

`filter` drops cards whose ref is already in the tracker and cards whose company already has a row with the
same position prefix; the last column is the company's prior-row count (still run `tracker.py check`).
`screen` prints, per posting, every Deutsch/German mention with BAD/ok (proximity screen) plus flags
(Pflichtpraktikum, Bachelor, PhD, ...). `--req` also prints the requirements block. The apply route is NOT in
the guest HTML: read it from the logged-in page with `li_apply_routes()` in scripts/bh_helpers.py.
"""
import argparse, html, json, os, re, sys, time, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "tmp", "li")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128 Safari/537.36"}
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DEFAULT_KW = [
    "Masterarbeit Informatik", "Masterarbeit KI", "Abschlussarbeit Machine Learning", "Master Thesis AI", "Thesis LLM",
    "Abschlussarbeit Informatik", "Masterarbeit Data Science", "Werkstudent Softwareentwicklung", "Werkstudent Python",
    "Werkstudent KI", "Werkstudent Data", "Werkstudent Informatik", "Werkstudent Backend", "Werkstudent Testautomatisierung",
    "Working Student AI", "Working Student Software", "Working Student Machine Learning", "Working Student Backend",
    "Praktikum Softwareentwicklung", "Praktikum KI", "Praktikum Data Science", "Internship Machine Learning",
    "Internship Software Engineer", "Intern AI",
]
STUD = re.compile(r"werkstudent|working student|studentische|praktik|intern\b|internship|thesis|masterarbeit|abschlussarbeit|student", re.I)
BAD_TITLE = re.compile(r"senior|lead\b|manager|director|head of|principal|bachelorarbeit|bachelor thesis|pflichtprakti|mandatory intern|dual|ausbildung|"
                       r"marketing|sales|vertrieb|\bhr\b|recruit|finance|controlling|accounting|legal|einkauf|procurement|logistik|mechanical|"
                       r"maschinenbau|elektrotechnik|chemie|biolog|pharma|design|content|social media|kommunikation|communication|event|steuer|"
                       r"\btax|audit|business development|customer|office|buchhaltung|personal|phd|schüler", re.I)
TECH = re.compile(r"software|informatik|data|\bki\b|\bai\b|machine|\bml\b|llm|python|backend|cloud|devops|entwickl|develop|engineer|comput|"
                  r"vision|nlp|agent|generative|genai|automat|digital|\bit\b|test|robot|analytics|full.?stack|app|web|platform|mlops", re.I)
LANG = re.compile(r"deutsch(?!land)|german(?!y)", re.I)
BAD_LANG = re.compile(r"\bc1\b|\bc2\b|\bb2\b|flie(ß|ss)end|fluent|verhandlungssicher|sehr gut|\bsicher|exzellent|muttersprach|native|excellent|proficien", re.I)
FLAGS = ("Pflichtpraktikum", "mandatory internship", "Bachelorarbeit", "Bachelor thesis", "PhD", "unpaid", "enrolled in Hamburg",
         "Pflicht", "verpflichtend")


def fetch(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20).read().decode("utf-8", "replace")


def text_of(fragment):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


def cmd_search(a):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, "cards.json")
    cards = json.load(open(path, encoding="utf-8")) if os.path.exists(path) and not a.fresh else {}
    for q in a.kw or DEFAULT_KW:
        for start in range(0, a.pages * 10, 10):
            url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?" + urllib.parse.urlencode(
                {"keywords": q, "location": a.location, "f_TPR": f"r{a.days * 86400}", "start": start})
            try:
                h = fetch(url)
            except Exception as e:
                print("ERR", q, start, e); time.sleep(3); continue
            lis = re.findall(r"<li>(.*?)</li>", h, re.S)
            if not lis:
                break
            for li in lis:
                m = re.search(r"jobPosting:(\d+)", li)
                if not m:
                    continue
                g = lambda p: text_of(re.search(p, li, re.S).group(1)) if re.search(p, li, re.S) else ""
                d = re.search(r'datetime="([^"]+)"', li)
                cards[m.group(1)] = dict(id=m.group(1), title=g(r"base-search-card__title[^>]*>(.*?)</h3>"),
                                         company=g(r"base-search-card__subtitle[^>]*>(.*?)</h4>"),
                                         loc=g(r"job-search-card__location[^>]*>(.*?)</span>"), date=d.group(1) if d else "", q=q)
            time.sleep(1.2)
    json.dump(cards, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print(f"{len(cards)} cards -> {path}")


def cmd_filter(a):
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    import tracker  # rows: 0 Date, 1 Company, 2 Position, 3 Location, 4 Reference Code, 5 Status, ...
    _, rows = tracker.load(tracker.DEFAULT_FILE)
    cards = json.load(open(os.path.join(OUT, "cards.json"), encoding="utf-8"))
    refs = " ".join(str(r[4]) for r in rows)
    out = []
    for c in cards.values():
        t = c["title"]
        if not STUD.search(t) or BAD_TITLE.search(t) or not TECH.search(t) or c["id"] in refs:
            continue
        nc = tracker.norm(c["company"])
        prior = [r for r in rows if nc and (nc == tracker.norm(r[1]) or (len(nc) > 4 and nc in tracker.norm(r[1])))]
        if any(tracker.norm(r[2])[:25] == tracker.norm(t)[:25] for r in prior):
            continue
        out.append((c["company"], t, c["loc"], c["date"], c["id"], len(prior)))
    for o in sorted(out):
        print(" | ".join(map(str, o)))
    print(len(out), "new cards")


def cmd_screen(a):
    cache = os.path.join(OUT, "posts")
    os.makedirs(cache, exist_ok=True)
    for i in a.ids.split(","):
        p = os.path.join(cache, i + ".txt")
        if not os.path.exists(p):
            try:
                h = fetch(f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{i}")
            except Exception as e:
                print(i, "ERR", e); continue
            title = re.search(r"top-card-layout__title[^>]*>(.*?)</h2>", h, re.S)
            org = re.search(r"topcard__org-name-link[^>]*>(.*?)</a>", h, re.S)
            body = re.search(r"show-more-less-html__markup[^>]*>(.*?)</div>", h, re.S)
            open(p, "w", encoding="utf-8").write(
                f"{text_of(title.group(1)) if title else ''}\n{text_of(org.group(1)) if org else ''}\n"
                f"https://www.linkedin.com/jobs/view/{i}/\n\n{text_of(body.group(1)) if body else ''}")
            time.sleep(1)
        lines = open(p, encoding="utf-8").read().split("\n", 4)
        text = lines[4] if len(lines) > 4 else ""
        flags = [f for f in FLAGS if f.lower() in text.lower()]
        print(f"== {i} {lines[1][:30]} | {lines[0][:70]} | {len(text)}ch | flags {flags}")
        for m in list(LANG.finditer(text))[:3]:
            win = text[max(0, m.start() - 80): m.end() + 80]
            print("   ", "BAD" if BAD_LANG.search(win) else "ok ", win)
        if a.req:
            m = re.search(r"(Your Profile|Dein Profil|Ihr Profil|Das bringst|What you bring|Requirements|Qualifications|"
                          r"What We.re Looking For|Your Skills|Anforderungen|Du bringst)", text)
            print("   REQ:", text[m.start(): m.start() + 700] if m else text[:700])
        print(f"   file: {p}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search"); s.add_argument("--kw", action="append"); s.add_argument("--days", type=int, default=3)
    s.add_argument("--pages", type=int, default=3); s.add_argument("--location", default="Germany")
    s.add_argument("--fresh", action="store_true", help="discard the existing cards.json")
    sub.add_parser("filter")
    s = sub.add_parser("screen"); s.add_argument("ids"); s.add_argument("--req", action="store_true")
    a = ap.parse_args()
    {"search": cmd_search, "filter": cmd_filter, "screen": cmd_screen}[a.cmd](a)


if __name__ == "__main__":
    main()
