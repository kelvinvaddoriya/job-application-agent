"""Check that strip_marks drops invisible marks without touching real text.

    PYTHONUTF8=1 python tests/test_strip_marks.py

Every mark here is built with chr() from a code point, never written as a
"\\u200b" escape. A cleaner pass over this repo decodes such an escape and
strips it, which silently turns this file into a test that asserts nothing and
still prints OK.

The nbsp and umlaut cases are the point: a cleaner that also ate those would
move text on the page and mangle German, which is worse than the marks.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from make_tailored_cv import ZERO_WIDTH, strip_marks  # noqa: E402

ZWSP, SHY, BOM, WJ = chr(0x200B), chr(0x00AD), chr(0xFEFF), chr(0x2060)
NBSP, NNBSP = chr(0x00A0), chr(0x202F)

assert len(ZERO_WIDTH) == 14, len(ZERO_WIDTH)

dirty = "Ich%shabe %smein%s Studium%s abgeschlossen." % (ZWSP, SHY, BOM, WJ)
assert dirty != "Ichhabe mein Studium abgeschlossen.", "fixture was stripped - test is vacuous"
assert strip_marks(dirty) == "Ichhabe mein Studium abgeschlossen.", repr(strip_marks(dirty))

# Real characters survive: nbsp, narrow nbsp, umlauts, eszett.
keep = "café%sstraße%süber München" % (NBSP, NNBSP)
assert strip_marks(keep) == keep, repr(strip_marks(keep))

# Word count is what coverletter.md gates on, so it must not move.
assert len(strip_marks(dirty).split()) == len(dirty.split())

# Idempotent, and a no-op on already-clean prose.
assert strip_marks(strip_marks(dirty)) == strip_marks(dirty)
assert strip_marks("plain ascii") == "plain ascii"

print("OK: %d marks stripped, nbsp/umlauts kept, word count stable" % len(ZERO_WIDTH))
