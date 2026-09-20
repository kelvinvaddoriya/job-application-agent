"""Find and read a job on public ATS APIs without a browser.

    python scripts/ats_probe.py boards accure,snke "thesis|werkstudent"     # which ATS hosts these company slugs
    python scripts/ats_probe.py personio accure 2795156 [--save PKG_DIR]     # posting text + apply-form required fields
    python scripts/ats_probe.py workday trumpf.wd3.myworkdayjobs.com trumpf TRUMPF_Students "Datenfusion" [--save PKG_DIR]
    python scripts/ats_probe.py smartrecruiters Bertelsmann-Jobs 744000148727889 [--save PKG_DIR]

`boards` tries Personio, JOIN, Ashby, Greenhouse, Lever, Recruitee and SmartRecruiters for each slug and prints
matching titles. `workday` searches the CXS API (a LinkedIn req that is not on the tenant's board returns 0 hits -
look for its live twin) and saves the first hit's description with `--save`. `--save` writes job_posting.txt.
"""
import argparse, html, json, os, re, sys, urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/128 Safari/537.36", "Accept": "application/json"}
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def get(url, data=None):
    h = dict(UA)
    if data is not None:
        h["Content-Type"] = "application/json"
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, data=data, headers=h), timeout=20)
        return r.status, r.read().decode("utf-8", "replace")
    except Exception as e:
        return getattr(e, "code", "ERR"), ""


def clean(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", html.unescape(s or "")))).strip()


def save(pkg, header, text):
    if pkg:
        os.makedirs(pkg, exist_ok=True)
        open(os.path.join(pkg, "job_posting.txt"), "w", encoding="utf-8").write(header + "\n\n" + text)
        print("saved", os.path.join(pkg, "job_posting.txt"))


def cmd_boards(a):
    kw = [k for k in (a.kw or "").lower().split("|") if k]
    for slug in a.slugs.split(","):
        for name, url in [("personio", f"https://{slug}.jobs.personio.de/xml"),
                          ("join", f"https://join.com/api/public/companies/{slug}/jobs"),
                          ("ashby", f"https://api.ashbyhq.com/posting-api/job-board/{slug}"),
                          ("greenhouse", f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"),
                          ("lever", f"https://api.lever.co/v0/postings/{slug}?mode=json"),
                          ("recruitee", f"https://{slug}.recruitee.com/api/offers/"),
                          ("smartrecruiters", f"https://api.smartrecruiters.com/v1/companies/{slug}/postings?limit=100")]:
            s, b = get(url)
            if s != 200 or len(b) < 60:
                continue
            titles = re.findall(r"<name>(.*?)</name>", b) if name == "personio" else \
                re.findall(r'"(?:title|name|text)"\s*:\s*"([^"]{8,140})"', b)
            hits = [clean(t) for t in titles if not kw or any(k in t.lower() for k in kw)]
            if name == "smartrecruiters" and '"totalFound":0' in b:
                continue
            print(slug, name, "|", hits[:10])


def cmd_personio(a):
    s, x = get(f"https://{a.slug}.jobs.personio.de/xml?language=en")
    for pos in re.findall(r"<position>(.*?)</position>", x, re.S):
        if re.search(r"<id>(\d+)</id>", pos).group(1) != a.id:
            continue
        name = clean(re.search(r"<name>(.*?)</name>", pos).group(1))
        office = clean((re.search(r"<office>(.*?)</office>", pos) or [0, ""])[1] if re.search(r"<office>", pos) else "")
        desc = clean(" ".join(re.findall(r"<value>(.*?)</value>", pos, re.S)))
        url = f"https://{a.slug}.jobs.personio.de/job/{a.id}"
        print(name, "|", office); print(desc[:1500])
        save(a.save, f"{name}\n{url}\n{office}", desc)
    s, h = get(f"https://{a.slug}.jobs.personio.de/job/{a.id}/apply?language=en")
    h2 = html.unescape(h).replace('\\"', '"')
    seen = set()
    print("apply form fields (required | name):")
    for m in re.finditer(r'"(?:label|name)":"([^"]{2,90})"[^{}]{0,200}?"(?:required|isRequired|is_required)":(true|false)', h2):
        if m.group(1) not in seen:
            seen.add(m.group(1)); print("  ", m.group(2), "|", m.group(1))


def cmd_workday(a):
    base = f"https://{a.host}/wday/cxs/{a.tenant}/{a.site}"
    s, b = get(base + "/jobs", json.dumps({"appliedFacets": {}, "limit": 20, "offset": 0, "searchText": a.text}).encode())
    j = json.loads(b or "{}")
    posts = j.get("jobPostings", [])
    print("total", j.get("total"))
    for p in posts:
        print("  ", p.get("title"), "|", p.get("postedOn"), "|", f"https://{a.host}/{a.site}{p['externalPath']}")
    if a.save and posts:
        s, d = get(base + posts[0]["externalPath"])
        info = json.loads(d)["jobPostingInfo"]
        save(a.save, f"{info['title']}\n{info.get('externalUrl', '')}\nposted {info.get('postedOn')}", clean(info["jobDescription"]))


def cmd_smartrecruiters(a):
    s, b = get(f"https://api.smartrecruiters.com/v1/companies/{a.company}/postings/{a.id}")
    j = json.loads(b or "{}")
    sec = j.get("jobAd", {}).get("sections", {})
    text = "\n\n".join(clean(v["text"]) for v in sec.values() if v.get("text"))
    print(j.get("name"), "|", j.get("location", {}).get("city"), "|", j.get("applyUrl")); print(text[:1500])
    save(a.save, f"{j.get('name')}\n{j.get('applyUrl')}", text)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("boards"); s.add_argument("slugs"); s.add_argument("kw", nargs="?")
    s = sub.add_parser("personio"); s.add_argument("slug"); s.add_argument("id"); s.add_argument("--save")
    s = sub.add_parser("workday"); s.add_argument("host"); s.add_argument("tenant"); s.add_argument("site"); s.add_argument("text")
    s.add_argument("--save")
    s = sub.add_parser("smartrecruiters"); s.add_argument("company"); s.add_argument("id"); s.add_argument("--save")
    a = ap.parse_args()
    {"boards": cmd_boards, "personio": cmd_personio, "workday": cmd_workday, "smartrecruiters": cmd_smartrecruiters}[a.cmd](a)


if __name__ == "__main__":
    main()
