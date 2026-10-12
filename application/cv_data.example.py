# -*- coding: utf-8 -*-
"""CV content for the generators - EXAMPLE. Copy to application/cv_data.py and fill it in.

    cp application/cv_data.example.py application/cv_data.py     # cv_data.py is gitignored

Read by scripts/make_tailored_cv.py (LaTeX CV), scripts/make_cover_letter_tex.py
(LaTeX letter) and scripts/make_combined_cv.py (.docx CV). Every fact here is a
rendering of something in application/resume.md, which stays the source of truth:
when resume.md changes, change it here too, and never add a claim here first.

Everything above JOBS is your standing content, written once. Per job, the agent
adds one JOBS entry (and one LETTERS entry under the same slug if the letter is
LaTeX too) that selects and orders that content - it does not write new facts.

Strings are LaTeX unless noted: \\& for &, -- for a dash, \\texttt{..} for code,
\\enquote{..} for quotes. A value is either one string shared by both languages
or an {"en": .., "de": ..} pair. DOCX_CV at the bottom is plain text, not LaTeX.

Try the example end to end before filling in your own:

    PYTHONUTF8=1 python scripts/make_tailored_cv.py --data application/cv_data.example.py --job example_ml_thesis --compile
"""

NAME = "Jane Doe"
FILE_STEM = "Jane_Doe"      # -> CV_Jane_Doe.pdf / Lebenslauf_Jane_Doe.pdf; match your designed CV's filename
DOB_DE = "01.01.2000"       # shown on German CVs only, where it is customary; set to None to omit
CONTACT = ["jane.doe@example.com", "(+49) 000 0000000"]
ADDRESS = {"en": "Musterstr. 1, 12345 Musterstadt, Germany",
           "de": "Musterstr. 1, 12345 Musterstadt, Deutschland"}
LINKS = [  # (label shown, URL) - only URLs that actually resolve
    ("linkedin.com/in/jane-doe", "https://linkedin.com/in/jane-doe"),
    ("github.com/janedoe", "https://github.com/janedoe"),
]

EDUCATION = [
    dict(
        degree={"en": "M.Sc. Computer Science", "de": "M. Sc. Informatik"},
        org={"en": "Example University, Germany", "de": "Beispieluniversität, Deutschland"},
        dates={"en": "10/2024 -- present (expected 09/2026)", "de": "10.2024 -- heute (Abschluss vsl. 09.2026)"},
        note={"en": "Machine Learning | Distributed Systems | Information Retrieval",
              "de": "Maschinelles Lernen | Verteilte Systeme | Information Retrieval"},
    ),
    dict(
        degree={"en": "B.Sc. Computer Science", "de": "B. Sc. Informatik"},
        org={"en": "Sample Institute of Technology", "de": "Sample Institute of Technology"},
        dates={"en": "10/2020 -- 09/2024", "de": "10.2020 -- 09.2024"},
        note={"en": "Data Structures \\& Algorithms | Databases | Linear Algebra",
              "de": "Datenstrukturen \\& Algorithmen | Datenbanken | Lineare Algebra"},
    ),
]

EXPERIENCE = {
    "assistant": dict(
        role={"en": "Student Assistant", "de": "Studentische Hilfskraft"},
        org={"en": "Example University -- Musterstadt, Germany",
             "de": "Beispieluniversität -- Musterstadt, Deutschland"},
        dates={"en": "04/2025 -- 09/2025", "de": "04.2025 -- 09.2025"},
        bullets={
            "en": ["Built an image classifier by transfer learning on a pretrained CNN and "
                   "reported accuracy on a held-out test split.",
                   "Wrote a small GUI for uploading an image and inspecting the prediction."],
            "de": ["Entwicklung eines Bildklassifikators mittels Transfer Learning auf einem "
                   "vortrainierten CNN, Genauigkeit auf einem getrennten Testdatensatz ausgewiesen.",
                   "Entwicklung einer kleinen GUI zum Hochladen eines Bildes und zur Anzeige der Vorhersage."],
        },
    ),
}

PROJECTS = {
    "docsearch": dict(
        title={"en": "DocSearch -- grounded question answering over manuals",
               "de": "DocSearch -- belegbasierte Fragebeantwortung über Handbücher"},
        dates={"en": "01/2026 -- present", "de": "01.2026 -- heute"},
        stack="Python, FastAPI, hybrid vector + BM25 retrieval, Postgres",
        bullets={
            "en": ["Retrieval pipeline that answers a question and cites the passage it came from.",
                   "Evaluated chunking strategies against a hand-labelled question set."],
            "de": ["Retrieval-Pipeline, die eine Frage beantwortet und die zugrunde liegende Textstelle zitiert.",
                   "Bewertung von Chunking-Strategien anhand eines handannotierten Fragensatzes."],
        },
    ),
    "sensorboard": dict(
        title={"en": "SensorBoard -- low-power measurement node", "de": "SensorBoard -- stromsparender Messknoten"},
        dates={"en": "03/2025 -- 08/2025", "de": "03.2025 -- 08.2025"},
        stack="C++, ESP32, SPI, BLE, KiCad",
        bullets={
            "en": ["Designed the PCB and wrote the firmware that reads a sensor over SPI.",
                   "Streams measurements as JSON over BLE to a \\texttt{read\\_node} client."],
            "de": ["Entwurf der Leiterplatte und der Firmware, die einen Sensor über SPI ausliest.",
                   "Überträgt Messwerte als JSON über BLE an einen \\texttt{read\\_node}-Client."],
        },
    ),
}

SKILL_GROUPS = {  # key: (label, content) - content is shared by both languages
    "programming": ({"en": "Programming", "de": "Programmierung"}, "Python · C++ · SQL"),
    "ml": ({"en": "AI / ML", "de": "KI / Machine Learning"}, "PyTorch · scikit-learn · RAG · embeddings"),
    "embedded": ({"en": "Embedded \\& Hardware", "de": "Embedded \\& Hardware"}, "ESP32 · SPI · BLE · KiCad"),
    "tools": ({"en": "Tools", "de": "Werkzeuge"}, "Git · Linux · Docker · CI/CD"),
}

CERTS = {
    "cloud": {"en": "Example Cloud Practitioner -- Example Cloud, Sep 2025",
              "de": "Example Cloud Practitioner -- Example Cloud, 09.2025"},
    "english": {"en": "IELTS: CEFR C1 (English) -- May 2024", "de": "IELTS: CEFR C1 (Englisch) -- 05.2024"},
}

LANGUAGES = {
    "en": "English (C1) $\\cdot$ German (B1)",
    "de": "Englisch (C1) $\\cdot$ Deutsch (B1)",
}

AVAILABILITY = {
    "en": "Enrolled full time until September 2026. Available from 1 March 2026. Willing to relocate.",
    "de": "Bis September 2026 als Vollzeitstudentin eingeschrieben. Verfügbar ab dem 1. März 2026. Umzugsbereit.",
}

# --------------------------------------------------------------------------
# Per-job tailoring. Each entry selects and orders the facts above.
# A German posting gets lang="de". The headline and profile never name the employer.
# --------------------------------------------------------------------------
JOBS = {
    "example_ml_thesis": dict(
        folder="ExampleCorp_Master_Thesis_Retrieval",   # the package folder mkpkg.py created
        lang="en",
        headline="Machine Learning Engineer -- Retrieval, Evaluation and Python Backends",
        profile=(
            "Master's student in Computer Science who builds retrieval systems that show their "
            "sources. My question-answering pipeline combines vector and BM25 search behind a "
            "FastAPI service and was evaluated against a hand-labelled question set rather than "
            "by eye."
        ),
        projects=["docsearch", "sensorboard"],
        experience=["assistant"],
        skills=["programming", "ml", "tools"],
        certs=["cloud", "english"],
    ),
    "example_embedded_werkstudent": dict(
        folder="Musterfirma_Werkstudent_Embedded",
        lang="de",
        headline="Embedded-Entwicklerin -- Firmware in C++, Sensorik und Leiterplattenentwurf",
        profile=(
            "Masterstudentin der Informatik mit praktischer Erfahrung vom Leiterplattenentwurf bis "
            "zur Firmware: Mein Messknoten liest einen Sensor über SPI aus und überträgt die "
            "Werte als JSON über BLE."
        ),
        projects=["sensorboard", "docsearch"],
        experience=["assistant"],
        skills=["programming", "embedded", "tools"],
        certs=["english"],
    ),
}

# --------------------------------------------------------------------------
# LaTeX cover letters (scripts/make_cover_letter_tex.py), keyed like JOBS.
# Five paragraphs; 250-260 words in English, 210-235 in German. `filename` is
# optional (default Cover_Letter_<FILE_STEM> / Anschreiben_<FILE_STEM>).
# --------------------------------------------------------------------------
LETTERS = {
    "example_ml_thesis": dict(
        lang="en",
        recipient=["ExampleCorp GmbH", "Ms Erika Mustermann", "Beispielweg 2", "54321 Beispielstadt"],
        date="Musterstadt, 1 February 2026",
        subject="Application for the Master Thesis \\enquote{Evaluating Retrieval for Technical Documentation}",
        greeting="Dear Ms Mustermann,",
        paragraphs=[
            "A retrieval system that is wrong is a nuisance; one that is wrong and confident is a "
            "hazard. That distinction draws me to this thesis, because your posting asks the "
            "question most projects skip: how do you know the retrieved passage was the right "
            "one? I have spent the last year building a system around exactly that question.",

            "In my project DocSearch I built a question-answering pipeline over technical manuals. "
            "It combines vector search with BM25 behind a FastAPI service, and every answer cites "
            "the passage it came from. The hard part was not generation but what sits underneath "
            "it: how a manual is cut into chunks decided answer quality far more than the choice "
            "of model did, so I compared chunking strategies against a hand-labelled question set "
            "instead of judging by eye.",

            "Before that I designed a low-power measurement node, from the circuit board to the "
            "firmware that reads a sensor over SPI and streams its values over BLE. That work "
            "taught me to distrust a number until I know how it was produced, a habit that "
            "carries over into evaluating retrieval, where a metric can look excellent for the "
            "wrong reason.",

            "I read the literature first and write code that someone else can rerun. My projects "
            "are version-controlled with automated checks, because a result I cannot reproduce "
            "next month is not a result. I am comfortable saying a score looks too good and "
            "rechecking the split.",

            "I am enrolled until September 2026 and available from 1 March 2026. I would welcome "
            "a conversation about the topic.",
        ],
        closing="Yours sincerely",
    ),
}

# --------------------------------------------------------------------------
# .docx CV (scripts/make_combined_cv.py) - PLAIN TEXT, not LaTeX.
# Each entry is (kind, *args): head/bullet/text take one string, entry and skill two.
# --------------------------------------------------------------------------
DOCX_CV = {
    "en": {
        "role": "Machine Learning & Embedded Software Developer",
        "sections": [
            ("head", "Education"),
            ("entry", "M.Sc. Computer Science, Example University", "10/2024 – present  ·  Musterstadt, Germany"),
            ("bullet", "Machine Learning | Distributed Systems | Information Retrieval"),
            ("head", "Projects"),
            ("entry", "DocSearch – grounded question answering over manuals", "01/2026 – present"),
            ("bullet", "Retrieval pipeline that answers a question and cites the passage it came from."),
            ("head", "Skills"),
            ("skill", "Programming", "Python · C++ · SQL"),
            ("head", "Languages"),
            ("text", "English (C1) · German (B1)"),
        ],
    },
    "de": {
        "role": "Entwicklerin für Machine Learning & Embedded Software",
        "sections": [
            ("head", "Ausbildung"),
            ("entry", "M. Sc. Informatik, Beispieluniversität", "10.2024 – heute  ·  Musterstadt, Deutschland"),
            ("bullet", "Maschinelles Lernen | Verteilte Systeme | Information Retrieval"),
            ("head", "Projekte"),
            ("entry", "DocSearch – belegbasierte Fragebeantwortung über Handbücher", "01.2026 – heute"),
            ("bullet", "Retrieval-Pipeline, die eine Frage beantwortet und die zugrunde liegende Textstelle zitiert."),
            ("head", "Kenntnisse"),
            ("skill", "Programmierung", "Python · C++ · SQL"),
            ("head", "Sprachen"),
            ("text", "Englisch (C1) · Deutsch (B1)"),
        ],
    },
}
