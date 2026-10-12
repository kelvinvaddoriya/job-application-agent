"""Drive a XING /custom-apply/ wizard end to end.

Only for cards labelled "Easy apply". A card labelled "Apply without docs" is a
/quick-apply/ one-pager instead - see application/feedback.md, "XING — General".

KNOWN GAP: the German-level <select> on step 3 carries its visible label OUTSIDE its
parent chain, so the label-substring matcher below misses it. Identify that select by
its option set (Keine (Kenntnisse) / Muttersprache oder zweisprachig / Grundkenntnisse /
Verhandlungssicher / Gute Kenntnisse / Fliessend) and set it by hand: B1 = Grundkenntnisse.

Usage inside browser-harness:
    exec(open(r"<this file>").read())
    xing_apply("<slug-with-id>", cover_letter=r"C:\...\Anschreiben.pdf", answers={...})

`answers` maps a substring of the question label -> value.
  * date questions  -> "YYYY-MM-DD"
  * select          -> exact option text
  * radio group     -> "Yes" / "No" (matched on the option's own label)
  * text            -> plain string
Anything not covered is left untouched (optional questions).
"""


def _buttons():
    import json
    return json.loads(js(r"""(()=>{const out=[];document.querySelectorAll('button').forEach(b=>{const t=(b.innerText||'').trim();
     const rc=b.getBoundingClientRect(); if(t && rc.height>0) out.push({t:t.slice(0,40),x:Math.round(rc.x+rc.width/2),y:Math.round(rc.y+rc.height/2),d:b.disabled});});
     return JSON.stringify(out.slice(0,12));})()"""))


def _click(name, pause=5):
    for b in _buttons():
        if name in b["t"] and not b["d"]:
            click_at_xy(b["x"], b["y"])
            wait(pause)
            return True
    return False


def _unwedge():
    tid = current_tab()["targetId"]
    w = cdp("Browser.getWindowForTarget", targetId=tid)["windowId"]
    cdp("Browser.setWindowBounds", windowId=w, bounds={"windowState": "minimized"}); wait(1)
    cdp("Browser.setWindowBounds", windowId=w,
        bounds={"windowState": "normal", "left": 0, "top": 0, "width": 1500, "height": 1000}); wait(2)
    cdp("Page.bringToFront"); wait(1)
    cdp("Emulation.setDeviceMetricsOverride", width=1500, height=1300, deviceScaleFactor=1, mobile=False)


def _step_text():
    return js(r"""document.body.innerText.replace(/\s+/g,' ').slice(0,260)""")


def xing_apply(slug, phone, cover_letter=None, answers=None, extra_file=None):
    # `phone` is required on purpose: a default would be typed into a real application.
    import json
    answers = answers or {}
    new_tab("https://www.xing.com/jobs/custom-apply/" + slug)
    wait_for_load(); wait(6)
    _unwedge()
    if js("document.hidden"):
        return "WEDGED"
    print("S1:", _step_text()[:70])

    # ---- step 1: contact
    js(r"""(()=>{let n=0;document.querySelectorAll('input,select').forEach(e=>{e.setAttribute('data-x','x'+(n++));});return 1;})()""")
    ph = js(r"""(()=>{const e=[...document.querySelectorAll('[data-x]')].find(x=>x.name&&x.name.indexOf('phoneNumber')>-1);
             return e?e.getAttribute('data-x'):'';})()""")
    if ph and not js('document.querySelector(\'[data-x="%s"]\').value' % ph):
        fill_input('[data-x="%s"]' % ph, phone); wait(1)
    if not _click("Continue"):
        return "STUCK_S1"
    print("S2:", _step_text()[:70])

    # ---- step 2: country of residence
    js(r"""(()=>{const e=document.querySelector('select'); if(!e) return 0;
     const o=[...e.options].find(x=>x.text.trim()==='Germany'); if(!o) return 0;
     const s=Object.getOwnPropertyDescriptor(window.HTMLSelectElement.prototype,'value').set; s.call(e,o.value);
     e.dispatchEvent(new Event('input',{bubbles:true})); e.dispatchEvent(new Event('change',{bubbles:true})); return 1;})()""")
    wait(2)
    if not _click("Continue"):
        return "STUCK_S2"
    print("S3:", _step_text()[:90])

    # ---- step 3: employer questions
    fields = json.loads(js(r"""
     (()=>{const out=[];let n=0;
      document.querySelectorAll('input,select,textarea').forEach(el=>{const r=el.getBoundingClientRect();
       if(r.height===0) return;
       let lab='';let p=el.parentElement;
       for(let i=0;i<5&&p;i++){const t=(p.innerText||'').replace(/\s+/g,' ');if(t.length>8&&t.length<200){lab=t;break;}p=p.parentElement;}
       let own='';const L=el.closest('label'); if(L) own=(L.innerText||'').replace(/\s+/g,' ').trim();
       const k='z'+(n++); el.setAttribute('data-z',k);
       out.push({k:k,tag:el.tagName,type:el.type,lab:lab.slice(0,120),own:own.slice(0,20)});});
      return JSON.stringify(out);})()"""))
    for f in fields:
        val = None
        for key, v in answers.items():
            if key.lower() in f["lab"].lower():
                val = v; break
        if val is None:
            continue
        if f["type"] == "radio":
            if f["own"].strip().lower() == str(val).strip().lower():
                js('document.querySelector(\'[data-z="%s"]\').click()' % f["k"]); wait(0.5)
        elif f["tag"] == "SELECT":
            js(r"""(()=>{const e=document.querySelector('[data-z="%s"]');
             const o=[...e.options].find(x=>x.text.trim()===%s); if(!o) return 0;
             const s=Object.getOwnPropertyDescriptor(window.HTMLSelectElement.prototype,'value').set; s.call(e,o.value);
             e.dispatchEvent(new Event('input',{bubbles:true})); e.dispatchEvent(new Event('change',{bubbles:true})); return 1;})()"""
               % (f["k"], json.dumps(val)))
            wait(0.5)
        elif f["type"] == "date":
            js(r"""(()=>{const e=document.querySelector('[data-z="%s"]');
             const s=Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set; s.call(e,%s);
             e.dispatchEvent(new Event('input',{bubbles:true})); e.dispatchEvent(new Event('change',{bubbles:true}));
             e.dispatchEvent(new Event('blur',{bubbles:true})); return 1;})()""" % (f["k"], json.dumps(val)))
            wait(0.5)
        else:
            try:
                fill_input('[data-z="%s"]' % f["k"], str(val)); wait(0.5)
            except Exception as e:
                print("fill err", f["k"], e)
    print("S3 values:", js(r"""JSON.stringify([...document.querySelectorAll('[data-z]')].map(e=>e.getAttribute('data-z')+'='+(e.type==='radio'?e.checked:String(e.value).slice(0,22))))"""))
    if not _click("Continue"):
        return "STUCK_S3"
    print("S4:", _step_text()[:70])

    # ---- step 4: documents
    # The profile CV cannot be swapped here, so a tailored CV rides along as an extra document.
    for f in [p for p in (cover_letter, extra_file) if p]:
        cdp("Page.setInterceptFileChooserDialog", enabled=True)
        drain_events()
        if _click("Upload file", pause=3):
            bid = None
            for e in drain_events():
                if "fileChooserOpened" in e.get("method", ""):
                    bid = e["params"]["backendNodeId"]
            if bid:
                cdp("DOM.setFileInputFiles", files=[f], backendNodeId=bid)
                wait(8)
    docs = js(r"""document.body.innerText.replace(/\s+/g,' ').slice(0,900)""")
    print("DOCS:", docs[docs.find("Your CV"):][:220])
    if not _click("Continue"):
        return "STUCK_S4"

    # ---- review + send
    if js("document.hidden"):
        _unwedge()
    if not _click("Send application", pause=10):
        return "STUCK_REVIEW"
    txt = js(r"""document.body.innerText.replace(/\s+/g,' ').slice(0,200)""")
    print("RESULT:", txt[:120])
    return "SUBMITTED" if "Application submitted" in txt else ("UNCLEAR: " + txt[:120])
