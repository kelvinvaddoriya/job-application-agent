# Self-test for keep_rendering / form_snapshot / hit_test / safe_click / safe_fill / safe_select in scripts/bh_helpers.py.
# Runs INSIDE browser-harness against tests/fixtures/form.html, opened in a background tab of the real Chrome:
#     browser-harness < tests/bh_selftest.py
# ASCII-only on purpose (stdin may be read as cp1252); umlauts are written as \u escapes.
import json, os, time

# Repo root: this file's grandparent, so the test runs from any checkout. Override
# with JOBAGENT_ROOT if your harness execs scripts with a different __file__.
ROOT = os.environ.get("JOBAGENT_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = ROOT.replace("\\", "/")
exec(open(ROOT + "/scripts/bh_helpers.py", encoding="utf-8").read())

results = []
def check(name, cond, detail=""):
    results.append((bool(cond), name, "" if cond else str(detail)[:300]))

tid = cdp("Target.createTarget", url="file:///" + ROOT + "/tests/fixtures/form.html", background=True)["targetId"]
try:
    time.sleep(1.5)
    switch_tab(tid)
    for _ in range(50):
        if js("document.readyState") == "complete":
            break
        time.sleep(0.1)

    # 1. keep_rendering: a background tab is hidden and frozen until focus emulation is on.
    before_hidden = js("document.hidden")
    r0 = js("window.raf"); time.sleep(0.3); r1 = js("window.raf")
    check("background tab starts hidden", before_hidden is True, before_hidden)
    check("background tab starts with rAF throttled", r1 - r0 <= 2, r1 - r0)
    check("keep_rendering returns True", keep_rendering() is True)
    r0 = js("window.raf"); time.sleep(0.3); r1 = js("window.raf")
    check("after keep_rendering: document.hidden false", js("document.hidden") is False)
    check("after keep_rendering: hasFocus true", js("document.hasFocus()") is True)
    check("after keep_rendering: rAF runs", r1 - r0 >= 5, r1 - r0)
    check("keep_rendering is idempotent", keep_rendering() is True)

    # 2. form_snapshot: one js() call, correct labels/values/flags, shadow-piercing, no secrets.
    real_js, calls = js, [0]
    def counting_js(*a, **k):
        calls[0] += 1
        return real_js(*a, **k)
    globals()["js"] = counting_js
    t0 = time.time(); s = form_snapshot(); dt = time.time() - t0
    globals()["js"] = real_js
    check("form_snapshot is exactly one js() call", calls[0] == 1, calls[0])
    check("form_snapshot under 1 s", dt < 1.0, dt)
    by = {c["label"]: c for c in s["controls"]}
    labels = list(by)
    def ctl(label):
        return by.get(label, {})
    check("label from <label for>", ctl("First name *").get("required") is True, labels)
    check("label from aria-labelledby", "Last name" in by, labels)
    check("id and name reported", ctl("First name *").get("id") == "first" and ctl("First name *").get("name") == "first_name",
          ctl("First name *"))
    check("label from placeholder", "City" in by, labels)
    check("value reported", ctl("Postal code").get("value") == "12345", ctl("Postal code"))
    check("textarea value", ctl("Motivation").get("value") == "old text", ctl("Motivation"))
    sel = ctl("Country")
    check("select value + options", sel.get("value") == "Select..." and "Other" in sel.get("options", []), sel)
    agree = ctl("I agree to the privacy notice *")
    check("label-wrapped opacity:0 checkbox kept, flagged hidden+required",
          agree.get("hidden") is True and agree.get("required") is True and agree.get("checked") is False, agree)
    check("disabled flagged", ctl("Locked").get("disabled") is True, ctl("Locked"))
    check("display:none control excluded", "Gone" not in by, labels)
    check("type=hidden excluded", not any(c.get("value") == "t0k3n" for c in s["controls"]))
    check("password listed without its value", "Password" in by and "value" not in ctl("Password"), ctl("Password"))
    check("secret never in snapshot", "secret123" not in json.dumps(s))
    check("hidden file input kept", ctl("CV").get("type") == "file" and ctl("CV").get("hidden") is True, ctl("CV"))
    check("role=button included", "Role button" in by, labels)
    check("contenteditable value", ctl("Rich text").get("value") == "old rich", ctl("Rich text"))
    check("role=checkbox div labelled from surrounding text (JOIN answer cards)", "B Intermediate" in by, labels)
    check("aria-invalid flagged", ctl("React field").get("invalid") is True, ctl("React field"))
    check("shadow input found + flagged", ctl("Shadow input *").get("shadow") is True and ctl("Shadow input *").get("required"), labels)
    check("shadow button found", ctl("Shadow button").get("shadow") is True, labels)
    check("iframe content not walked", "InsideFrame" not in by, labels)
    check("errors collected", any("correct the errors" in e for e in s["errors"]), s["errors"])
    ns = [c["n"] for c in s["controls"]]
    check("node refs unique", len(ns) == len(set(ns)))
    s2 = form_snapshot()
    check("node refs stable across snapshots", {c["label"]: c["n"] for c in s2["controls"]} == {c["label"]: c["n"] for c in s["controls"]})

    # 3. hit-tested clicks: never click through an overlay; name the blocker.
    n_cov = ctl("Covered button")["n"]
    h = safe_click(n_cov)
    check("covered click refused", h.get("ok") is False and h.get("reason") == "covered", h)
    check("blocker named", "overlayShim" in (h.get("blocker") or {}).get("cls", ""), h)
    check("covered click did not fire", js("window.log.includes('covered')") is False)
    js("document.getElementById('shim').remove()")
    check("click after removing blocker", safe_click(n_cov).get("ok") is True and js("window.log.includes('covered')"))
    check("off-screen target scrolled into view and clicked",
          safe_click(ctl("Far submit")["n"]).get("ok") is True and js("window.log.includes('far')"))
    check("CSS ref works", safe_click("#far").get("ok") is True)
    # Greenhouse hosted boards ignore scrollIntoView; hit_test must fall back to the CDP mouse wheel.
    js("window.scrollTo(0, 0); window.__siv = Element.prototype.scrollIntoView; Element.prototype.scrollIntoView = function () {}")
    n_far = ctl("Far submit")["n"]
    js("window.log = window.log.filter(x => x !== 'far')")
    h = safe_click(n_far)
    check("scrollIntoView-proof page: wheel fallback reaches the target",
          h.get("ok") is True and js("window.log.includes('far')") and js("window.scrollY") > 1000, (h, js("window.scrollY")))
    js("Element.prototype.scrollIntoView = window.__siv")
    check("role=button click", safe_click(ctl("Role button")["n"]).get("ok") and js("window.log.includes('rb')"))
    h = safe_click(agree["n"])
    time.sleep(0.2)
    check("hidden checkbox clicked through its label", h.get("ok") is True and js("document.getElementById('agree').checked"), h)
    check("checkbox change event fired", js("window.log.includes('agree:true')"))
    check("disabled refused", hit_test(ctl("Locked")["n"]).get("reason") == "disabled")
    check("invisible refused", hit_test("#gone").get("reason") == "invisible")
    check("missing selector reported stale", hit_test("#does-not-exist").get("reason") == "stale")
    check("shadow button click", safe_click(ctl("Shadow button")["n"]).get("ok") and js("window.log.includes('sbtn')"))

    # 4. safe_fill: replaces (never concatenates), all input kinds, events fire, unicode survives.
    r = safe_fill(ctl("Postal code")["n"], "54321")
    check("prefilled value replaced, not concatenated", r == {"ok": True, "value": "54321"}, r)
    r = safe_fill(ctl("E-Mail *")["n"], "you@example.com")
    check("email input replaced", r.get("ok"), r)
    r = safe_fill(ctl("Salary")["n"], "1300")
    check("number input replaced", r.get("ok"), r)
    r = safe_fill(ctl("Motivation")["n"], "line one\nline two")
    check("textarea multi-line", r.get("ok"), r)
    city = "M\u00fcnchen Stra\u00dfe"
    r = safe_fill(ctl("City")["n"], city)
    check("umlaut / sharp s survive", r.get("value") == city, r)
    r = safe_fill(ctl("Rich text")["n"], "new rich")
    check("contenteditable replaced", r.get("ok"), r)
    before = js("window.inputEvents")
    r = safe_fill(ctl("React field")["n"], "typed")
    check("input events fire (React-style listener)", r.get("ok") and js("window.inputEvents") > before, r)
    r = safe_fill(ctl("Shadow input *")["n"], "in shadow")
    check("shadow input filled", r.get("ok"), r)
    r = safe_fill("#sin", "via css")
    check("shadow input via CSS ref", r.get("ok"), r)
    check("fill on disabled refused", safe_fill(ctl("Locked")["n"], "nope").get("reason") == "disabled")

    # 5. safe_select: exact option text only.
    n_sel = sel["n"]
    r = safe_select(n_sel, "Other")
    check("exact option chosen (Other, not Brothers)", r == {"ok": True, "value": "Other"}, r)
    check("select change event fired", js("window.log.includes('country:other')"))
    r = safe_select(n_sel, "Oth")
    check("substring does not match", r.get("reason") == "no option", r)
    r = safe_select(n_sel, "India (disabled)")
    check("disabled option not chosen", r.get("reason") == "no option", r)
    r = safe_select(ctl("City")["n"], "x")
    check("non-select refused", r.get("reason") == "not a select", r)

    # 6. stale refs: a removed node is reported, never silently re-targeted.
    n_rb = ctl("Role button")["n"]
    js("document.getElementById('rb').remove()")
    check("removed node reported stale", safe_click(n_rb).get("reason") == "stale")
    check("still rendering at the end", js("document.hidden") is False)
finally:
    try:
        cdp("Target.closeTarget", targetId=tid)
    except Exception:
        pass

failed = [r for r in results if not r[0]]
for ok, name, detail in results:
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else "  -> " + detail))
print("%d/%d passed" % (len(results) - len(failed), len(results)))
if failed:
    raise SystemExit(1)
