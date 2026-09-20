"""Browser helpers for form filling inside `browser-harness`. Load at the top of a heredoc:

    browser-harness <<'PY'
    exec(open(r"<REPO>/scripts/bh_helpers.py", encoding="utf-8").read())
    print(li_apply_routes(["4464796918", "4467054846"]))
    PY

Every helper is JS-first and returns data instead of screenshots; `snap()` is the one budgeted screenshot.

  li_apply_routes(ids)               logged-in LinkedIn: {id: "EASY_APPLY" | employer URL | "ALREADY_APPLIED" | "CLOSED" | None}
  dismiss_dialog(accept=True)        clear a pending beforeunload/alert that makes goto_url/js time out
  snap(path, scale=0.55, clip=None)  JPEG screenshot to a file (Read it afterwards)
  set_text(css, value)               focus + select-all + Input.insertText, returns the read-back value
  upload(js_expr, path)              DOM.setFileInputFiles on the element a JS expression returns (works where
                                     upload_file()'s CSS lookup fails: shadow DOM, re-rendered or duplicate inputs)
  pick_option(css, text, typed=None) open a combobox/select by coordinate click, optionally type to filter, click the
                                     [role=option] whose text equals `text` (Workday, Eightfold, SuccessFactors)
  click_text(text, tags="button")    coordinate-click the first visible element whose trimmed text equals `text`
  deep_text()                        page text including shadow roots (SmartRecruiters oneclick splits labels)
  deep_inputs()                      [(index, id, type, value)] of inputs across shadow roots
  deep_set(index, value)             set the index-th deep input (from deep_inputs) via insertText
  deep_choose(index, contains, typed=None)  SmartRecruiters typeahead: open, optional filter, click option by substring
  keep_rendering()                   focus emulation: a background tab reports visible/focused, rAF runs
  form_snapshot(limit=300)           ONE call: controls across shadow roots (label/value/required/options) + errors
  hit_test(ref) / safe_click(ref)    ref = snapshot n or CSS; refuses covered/stale/disabled targets, names the blocker
  safe_fill(ref, text)               hit-tested click + selectAll + insertText, read-back verified
  safe_select(ref, option_text)      native <select> by exact option text
  Self-test: browser-harness < tests/bh_selftest.py   (fixture: tests/fixtures/form.html)
Umlauts: never write German literals into js() strings; match an ASCII substring (e.g. 'nnlich').
"""
import base64 as _b64, json as _json, time as _time, urllib.parse as _up

_DEEP_INPUTS = ("(()=>{const acc=[];const walk=r=>{r.querySelectorAll('*').forEach(e=>{if(e.tagName==='INPUT'&&e.type!=='file'"
                "&&e.type!=='checkbox'&&e.type!=='hidden')acc.push(e);if(e.shadowRoot)walk(e.shadowRoot)})};walk(document);return acc})()")
_DEEP_OPTS = ("(()=>{const acc=[];const walk=r=>{r.querySelectorAll('[role=option],spl-dropdown-item,li').forEach(e=>{if(e.getClientRects().length)"
              "{const t=(e.innerText||e.textContent||'').trim();const b=e.getBoundingClientRect();if(t&&t.length<200)acc.push([t,b.x+b.width/2,b.y+b.height/2])}});"
              "r.querySelectorAll('*').forEach(e=>{if(e.shadowRoot)walk(e.shadowRoot)})};walk(document);return acc})()")


def _center(js_expr):
    js(f"(()=>{{const e={js_expr};e.scrollIntoView({{block:'center'}})}})()")
    _time.sleep(0.6)
    return js(f"(()=>{{const b=({js_expr}).getBoundingClientRect();return [b.x+b.width/2,b.y+b.height/2]}})()")


def li_apply_routes(ids, wait=5):
    out = {}
    for i in ids:
        goto_url(f"https://www.linkedin.com/jobs/view/{i}/")
        wait_for_load(); _time.sleep(wait)
        r = js("(()=>{const b=[...document.querySelectorAll('button,a')].find(e=>/^(Apply|Easy Apply|Bewerben|Einfach bewerben)/i"
               ".test((e.innerText||'').trim()));if(!b)return null;return [(b.innerText||'').trim(),b.href||'']})()")
        if not r:
            t = js("document.body.innerText")
            out[i] = "ALREADY_APPLIED" if "Applied " in t or "Application submitted" in t else \
                     "CLOSED" if "No longer accepting" in t else None
        elif "easy" in r[0].lower() or "einfach" in r[0].lower():
            out[i] = "EASY_APPLY"
        else:
            q = _up.parse_qs(_up.urlparse(r[1]).query).get("url", [r[1]])[0]
            out[i] = q
    return out


def dismiss_dialog(accept=True):
    try:
        cdp("Page.handleJavaScriptDialog", accept=accept)
        return True
    except Exception:
        return False


def snap(path, scale=0.55, clip=None):
    c = dict(clip or {"x": 0, "y": 0, "width": 1366, "height": 551}); c["scale"] = scale
    d = cdp("Page.captureScreenshot", format="jpeg", quality=55, clip=c)
    open(path, "wb").write(_b64.b64decode(d["data"]))
    return path


def set_text(css, value):
    sel = _json.dumps(css)
    js(f"(()=>{{const e=document.querySelector({sel});e.scrollIntoView({{block:'center'}});e.focus();"
       f"try{{e.setSelectionRange(0,e.value.length)}}catch(_){{e.select&&e.select()}}}})()")
    _time.sleep(0.3)
    cdp("Input.insertText", text=value)
    _time.sleep(0.3)
    return js(f"document.querySelector({sel}).value")


def upload(js_expr, path, wait=6):
    o = cdp("Runtime.evaluate", expression=js_expr)
    oid = o.get("result", {}).get("objectId")
    if not oid:
        raise RuntimeError(f"upload: no element for {js_expr}")
    cdp("DOM.setFileInputFiles", files=[path], objectId=oid)
    _time.sleep(wait)


def pick_option(css, text, typed=None):
    x, y = _center(f"document.querySelector({_json.dumps(css)})")
    click_at_xy(x, y); _time.sleep(1.2)
    if typed:
        cdp("Input.insertText", text=typed); _time.sleep(1.5)
    opts = js(_DEEP_OPTS)
    hit = [o for o in opts if o[0] == text]
    if not hit:
        press_key("Escape")
        return {"missing": text, "options": [o[0] for o in opts][:25]}
    js("(()=>{const e=[...document.querySelectorAll('[role=option]')].find(e=>e.innerText.trim()===%s);e&&e.scrollIntoView({block:'nearest'})})()" % _json.dumps(text))
    _time.sleep(0.4)
    hit = [o for o in js(_DEEP_OPTS) if o[0] == text]
    click_at_xy(hit[0][1], hit[0][2]); _time.sleep(0.8)
    return text


def click_text(text, tags="button"):
    x, y = _center("[...document.querySelectorAll(%s)].filter(e=>e.getClientRects().length).find(e=>(e.innerText||e.value||'').trim()===%s)"
                   % (_json.dumps(tags), _json.dumps(text)))
    click_at_xy(x, y)


def deep_text():
    return js("(()=>{let s=[];const walk=r=>{r.childNodes.forEach(n=>{if(n.nodeType===3){const x=n.textContent.trim();if(x)s.push(x)}"
              "else if(n.nodeType===1){if(!/^(SCRIPT|STYLE)$/.test(n.tagName))walk(n);if(n.shadowRoot)walk(n.shadowRoot)}"
              "else if(n.nodeType===11)walk(n)})};walk(document.body);return s.join(' | ')})()")


def deep_inputs():
    return js(f"{_DEEP_INPUTS}.map((e,i)=>[i,e.id||e.name,e.type,e.value])")


def deep_set(index, value):
    js(f"(()=>{{const e={_DEEP_INPUTS}[{index}];e.scrollIntoView({{block:'center'}});e.focus();try{{e.setSelectionRange(0,e.value.length)}}catch(_){{e.select&&e.select()}}}})()")
    _time.sleep(0.3)
    cdp("Input.insertText", text=value); _time.sleep(0.3)
    return js(f"{_DEEP_INPUTS}[{index}].value")


def deep_choose(index, contains, typed=None):
    x, y = _center(f"{_DEEP_INPUTS}[{index}]")
    click_at_xy(x, y); _time.sleep(1.3)
    if typed:
        cdp("Input.insertText", text=typed); _time.sleep(1.8)
    hit = [o for o in js(_DEEP_OPTS) if contains.lower() in o[0].lower()]
    if not hit:
        press_key("Escape")
        return {"missing": contains}
    click_at_xy(hit[0][1], hit[0][2]); _time.sleep(1)
    return hit[0][0]


# --- keep_rendering / form_snapshot / safe_* (ported from browser-use/jev-ultrafast, adapted for ATS forms) ---
# Node refs are stable per document: window.__bh keeps a WeakMap element->id and a Map id->element, so a ref taken
# from form_snapshot() stays valid until that element leaves the DOM (then every safe_* call reports "stale").
# The JS deliberately contains no backslashes: the harness pre-processes escapes in js() strings.
_BH_JS = r"""
window.__bh = window.__bh || {ids:new WeakMap(), nodes:new Map(), next:1};
(() => {
  const B = window.__bh;
  B.id = e => { if (!B.ids.has(e)) B.ids.set(e, B.next++); const i = B.ids.get(e); B.nodes.set(i, e); return i; };
  B.all = sel => { const out = []; const walk = r => { r.querySelectorAll(sel).forEach(e => out.push(e));
    r.querySelectorAll('*').forEach(e => { if (e.shadowRoot) walk(e.shadowRoot); }); }; walk(document); return out; };
  B.get = ref => typeof ref === 'number' ? B.nodes.get(ref) : B.all(ref)[0];
  B.vis = e => !!e && e.isConnected && !e.closest('[aria-hidden="true"],[inert]') &&
    e.checkVisibility({checkOpacity:true, checkVisibilityCSS:true}) && e.getBoundingClientRect().width > 0;
  B.name = (e, seen) => {
    seen = seen || new Set(); if (!e || seen.has(e)) return ''; seen.add(e);
    const root = e.getRootNode();
    const byId = i => (root.getElementById ? root.getElementById(i) : null) || document.getElementById(i);
    const by = ((e.getAttribute && e.getAttribute('aria-labelledby')) || '').split(' ').filter(Boolean)
      .map(i => { const l = byId(i); return l ? l.innerText : ''; }).join(' ');
    const lab = [...(e.labels || [])].map(l => l.innerText).join(' ');
    const role = e.getAttribute && e.getAttribute('role');
    const own = (['BUTTON','A','SUMMARY'].includes(e.tagName) ||
      ['button','option','tab','link','checkbox','radio','switch','menuitem'].includes(role))
      ? ((e.innerText || '').trim() || (role && e.parentElement ? (e.parentElement.innerText || '') : '')) : '';
    const t = by || (e.getAttribute && e.getAttribute('aria-label')) || lab || own ||
      (['button','submit','reset'].includes(e.type) ? e.value : '') ||
      (e.getAttribute && (e.getAttribute('placeholder') || e.getAttribute('title') || e.getAttribute('name'))) || e.id || '';
    return t.split(String.fromCharCode(10)).join(' ').trim().slice(0, 120);
  };
  B.deepHit = (x, y) => { let t = document.elementFromPoint(x, y);
    while (t && t.shadowRoot) { const i = t.shadowRoot.elementFromPoint(x, y); if (!i || i === t) break; t = i; } return t; };
  B.chain = t => { const out = []; while (t) { out.push(t); t = t.parentNode || t.host || null; } return out; };
  B.target = e => (!B.vis(e) && e.labels && e.labels.length) ? ([...e.labels].find(B.vis) || e) : e;
  B.hit = (ref, scroll) => {
    const e = B.get(ref);
    if (!e || !e.isConnected) return {ok:false, reason:'stale'};
    if (e.matches(':disabled') || e.closest('[aria-disabled="true"]')) return {ok:false, reason:'disabled'};
    const t = B.target(e);
    if (!B.vis(t)) return {ok:false, reason:'invisible'};
    if (scroll) t.scrollIntoView({block:'center', inline:'center'});
    const r = t.getBoundingClientRect(), x = r.x + r.width / 2, y = r.y + r.height / 2;
    if (x < 0 || y < 0 || x >= innerWidth || y >= innerHeight) return {ok:false, reason:'offscreen'};
    const h = B.deepHit(x, y), chain = B.chain(h);
    const lab = h && h.closest && h.closest('label');
    if (chain.includes(t) || chain.includes(e) || (lab && [...(e.labels || [])].includes(lab))) return {ok:true, x, y};
    return {ok:false, reason:'covered', x, y, blocker:h ? {tag:h.tagName, id:h.id, cls:String(h.className).slice(0, 60),
      text:(h.innerText || '').trim().slice(0, 60)} : null};
  };
  B.snapshot = limit => {
    const sel = 'input,textarea,select,button,[contenteditable="true"],[role=button],[role=combobox],[role=checkbox],' +
      '[role=radio],[role=switch],[role=textbox],[role=option],[role=tab]';
    const out = [];
    for (const e of B.all(sel)) {
      if (e.type === 'hidden') continue;
      const visible = B.vis(e);
      const labelled = !visible && ['checkbox','radio'].includes(e.type) && [...(e.labels || [])].some(B.vis);
      if (!visible && !labelled && e.type !== 'file') continue;
      const c = {n:B.id(e), tag:e.tagName.toLowerCase(), type:e.type || e.getAttribute('role') || '', label:B.name(e)};
      if (e.id) c.id = e.id; if (e.name && e.name !== e.id) c.name = e.name;
      if (e.type !== 'password' && e.type !== 'file' && 'value' in e && e.tagName !== 'BUTTON') c.value = String(e.value).slice(0, 80);
      if (e.type === 'file') c.value = [...(e.files || [])].map(f => f.name).join(', ');
      if (e.isContentEditable) c.value = e.innerText.slice(0, 80);
      if (['checkbox','radio'].includes(e.type)) c.checked = e.checked;
      if (e.getAttribute('aria-checked') !== null) c.checked = e.getAttribute('aria-checked') === 'true';
      if (e.tagName === 'SELECT') { c.value = [...e.selectedOptions].map(o => o.text.trim()).join(', ');
        c.options = [...e.options].map(o => o.text.trim()).slice(0, 40); }
      const star = (c.label + ' ' + [...(e.labels || [])].map(l => l.innerText).join(' ')).includes('*');
      if (e.required || e.getAttribute('aria-required') === 'true' || star) c.required = true;
      if (e.matches(':disabled') || e.getAttribute('aria-disabled') === 'true') c.disabled = true;
      if (e.getAttribute('aria-invalid') === 'true') c.invalid = true;
      if (!visible) c.hidden = true;
      if (e.getRootNode() !== document) c.shadow = true;
      out.push(c);
      if (out.length >= limit) break;
    }
    const errors = B.all('[role=alert],[aria-live=assertive],.error,.errorMessage,.invalid-feedback')
      .filter(B.vis).map(e => e.innerText.trim()).filter(Boolean).map(t => t.slice(0, 160)).slice(0, 10);
    return {url:location.href, hidden:document.hidden, controls:out, errors};
  };
})();
"""


def _bh(expr):
    """Evaluate `expr` with the window.__bh toolkit installed (idempotent: re-installing keeps existing node refs)."""
    return js("(()=>{" + _BH_JS + "return " + expr + "})()")


def keep_rendering():
    """Make the active tab behave as focused and visible (CDP focus emulation, as jev-ultrafast does for owned tabs):
    document.hidden -> false, hasFocus() -> true, requestAnimationFrame keeps running. This is what fixes submit
    buttons that stay disabled and widgets that never open while the tab is in the background. It is per CDP session
    and survives later browser-harness calls while the daemon lives; call it after switch_tab/new_tab (cheap and
    idempotent). Returns True when the page now reports visible."""
    cdp("Emulation.setFocusEmulationEnabled", enabled=True)
    return js("!document.hidden")


def form_snapshot(limit=300):
    """ONE js() call: every visible control (plus file inputs and label-wrapped hidden checkboxes/radios), across open
    shadow roots, as {n, tag, type, label, value, checked, options, required, disabled, invalid, hidden, shadow}, plus
    visible error/alert texts. `n` is a stable ref for hit_test/safe_click/safe_fill/safe_select. Password values are
    never returned. Iframes are NOT walked - drive an embed through its own target."""
    return _bh("window.__bh.snapshot(%d)" % limit)


def hit_test(ref, scroll=True):
    """Where a click on `ref` (snapshot n, or a CSS selector searched through shadow roots) would land. {'ok': True,
    x, y} only when the element itself, its own label or a shadow child is on top at its centre; otherwise `reason`
    is stale / disabled / invisible / offscreen / covered, and 'covered' names the blocker (tag, id, cls, text).
    Pages that ignore scrollIntoView (Greenhouse hosted boards) are brought into view with the CDP mouse wheel."""
    h = _bh("window.__bh.hit(%s, %s)" % (_json.dumps(ref), "true" if scroll else "false"))
    for _ in range(8 if scroll else 0):
        if h.get("reason") != "offscreen":
            break
        dy = _bh("(e => { const t = window.__bh.target(e); const r = t.getBoundingClientRect(); "
                 "return Math.round(r.y + r.height / 2 - innerHeight / 2); })(window.__bh.get(%s))" % _json.dumps(ref))
        cdp("Input.dispatchMouseEvent", type="mouseWheel", x=200, y=200, deltaX=0, deltaY=dy)
        _time.sleep(0.3)
        h = _bh("window.__bh.hit(%s, false)" % _json.dumps(ref))
    return h


def safe_click(ref):
    """hit_test, then a trusted CDP mouse click at the centre. Never clicks through an overlay: when not ok it returns
    the hit_test dict unchanged, so the caller can remove the named blocker and retry."""
    h = hit_test(ref)
    if not h.get("ok"):
        return h
    x, y = h["x"], h["y"]
    cdp("Input.dispatchMouseEvent", type="mouseMoved", x=x, y=y)
    for ev in ("mousePressed", "mouseReleased"):
        cdp("Input.dispatchMouseEvent", type=ev, x=x, y=y, button="left", clickCount=1)
    return h


def safe_fill(ref, text):
    """Replace a text-like control's value with `text` via trusted input: hit-tested click, the selectAll editing
    command (works on email/number/contenteditable, unlike setSelectionRange), Input.insertText. Reads the value back,
    so a concatenation ('<postcode2>' + '<postcode>') or a widget that rejected the text shows up at once.
    Returns {'ok': value == text, 'value': read-back}, or the failing hit_test dict."""
    h = safe_click(ref)
    if not h.get("ok"):
        return h
    cdp("Input.dispatchKeyEvent", type="rawKeyDown", key="a", code="KeyA", windowsVirtualKeyCode=65, modifiers=2,
        commands=["selectAll"])
    cdp("Input.dispatchKeyEvent", type="keyUp", key="a", code="KeyA", windowsVirtualKeyCode=65, modifiers=2)
    cdp("Input.insertText", text=text)
    _time.sleep(0.15)
    v = _bh("(e => e ? (e.isContentEditable ? e.innerText : e.value) : null)(window.__bh.get(%s))" % _json.dumps(ref))
    return {"ok": v == text, "value": v}


def safe_select(ref, option_text):
    """Native <select>: hit-test the control, pick the option whose trimmed text EQUALS `option_text` (never a
    substring - 'Other' must not match 'Brothers'), fire input+change. Returns {'ok', 'value'}, a 'no option' dict
    listing the options, or the failing hit_test dict."""
    h = hit_test(ref)
    if not h.get("ok"):
        return h
    return _bh("""(e => { if (!e || e.tagName !== 'SELECT') return {ok:false, reason:'not a select'};
      const o = [...e.options].find(o => o.text.trim() === %s && !o.disabled);
      if (!o) return {ok:false, reason:'no option', options:[...e.options].map(o => o.text.trim()).slice(0, 40)};
      e.value = o.value; e.dispatchEvent(new Event('input', {bubbles:true})); e.dispatchEvent(new Event('change', {bubbles:true}));
      return {ok:true, value:e.options[e.selectedIndex].text.trim()}; })(window.__bh.get(%s))"""
               % (_json.dumps(option_text), _json.dumps(ref)))
