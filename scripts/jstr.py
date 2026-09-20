# -*- coding: utf-8 -*-
"""Build a JS string expression that survives the harness's encoding path.

Both JS string literals and fill_input() mangle non-ASCII (UTF-8 bytes get
re-read as cp1252). String.fromCharCode(n) is the only reliable channel.
"""


def jstr(s):
    parts = []
    buf = []
    for ch in s:
        if 32 <= ord(ch) < 127 and ch not in "'\\":
            buf.append(ch)
        else:
            if buf:
                parts.append("'" + "".join(buf) + "'")
                buf = []
            parts.append("String.fromCharCode(%d)" % ord(ch))
    if buf:
        parts.append("'" + "".join(buf) + "'")
    return "+".join(parts) if parts else "''"


def set_value(js, selector, text):
    """Native-setter fill that preserves umlauts, then fire React events."""
    expr = """
    var e=document.querySelector(%s);
    var proto = e.tagName==='TEXTAREA' ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
    var s=Object.getOwnPropertyDescriptor(proto,'value').set;
    s.call(e, %s);
    ['input','change','blur'].forEach(function(t){e.dispatchEvent(new Event(t,{bubbles:true}));});
    e.value
    """ % (jstr(selector), jstr(text))
    return js(expr)
