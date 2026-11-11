
import io
import json
import os
import hmac
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

from questions import (
    PROFILE_QUESTIONS,
    LIKERT_OPTIONS,
    LIKERT_LABELS,
    DIMENSIONS,
    OVERALL_READINESS_QUESTION,
)
from scoring import calculate_readiness
from database import (
    initialize_database,
    save_submission,
    get_all_assessments,
)
from i18n import get_language_pack


# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="Egypt AI Readiness",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==========================================================
# COMPLETE DESIGN SYSTEM
# ==========================================================

CSS = """
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Cairo:wght@400;500;600;700;800&display=swap');

:root {
    --navy: #0f2438;
    --navy-2: #173449;
    --teal: #0d8a93;
    --teal-dark: #0a6b72;
    --teal-tint: #e4f3f3;
    --ink: #16242f;
    --muted: #5b7083;
    --line: #dbe4ea;
    --surface: #ffffff;
    --bg: #f4f7fa;
    --danger: #b3261e;
    --danger-tint: #fdeceb;
    --success: #1a7f5a;
    --success-tint: #e8f6f0;
    --warn: #9a6b00;
    --warn-tint: #fdf3e0;
    --radius-s: 8px;
    --radius-m: 12px;
    --radius-l: 18px;
    --shadow-card: 0 1px 2px rgba(15,36,56,.05), 0 6px 20px rgba(15,36,56,.06);
}

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after { transition: none !important; animation: none !important; }
}

/* ======================================================
   GLOBAL
====================================================== */

html, body { font-family: 'DM Sans', sans-serif !important; }

.stApp, [data-testid="stAppViewContainer"] { background: var(--bg) !important; }
[data-testid="stAppViewContainer"] .main { background: var(--bg) !important; color: var(--ink); }

.block-container { max-width: 1180px; padding-top: 1.6rem; padding-bottom: 3.5rem; }

[data-testid="stAppViewContainer"] .main h1,
[data-testid="stAppViewContainer"] .main h2,
[data-testid="stAppViewContainer"] .main h3,
[data-testid="stAppViewContainer"] .main h4,
[data-testid="stAppViewContainer"] .main p,
[data-testid="stAppViewContainer"] .main li,
[data-testid="stAppViewContainer"] .main strong,
[data-testid="stAppViewContainer"] .main span,
[data-testid="stAppViewContainer"] .main label {
    color: var(--ink);
}

[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p,
.small-note, .stat-label { color: var(--muted) !important; }

*:focus-visible {
    outline: 2px solid var(--teal) !important;
    outline-offset: 2px !important;
}

/* ======================================================
   SIDEBAR
====================================================== */

[data-testid="stSidebar"] { background: var(--navy) !important; }

[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] .stCaption {
    color: #eaf4f5 !important;
}

[data-testid="stSidebar"] button {
    background: var(--navy-2) !important;
    border: 1px solid #2e4e63 !important;
    color: #ffffff !important;
    transition: background .15s ease, transform .1s ease;
}
[data-testid="stSidebar"] button:hover { background: var(--teal-dark) !important; border-color: var(--teal-dark) !important; }
[data-testid="stSidebar"] button:active { transform: scale(.98); }
[data-testid="stSidebar"] button p, [data-testid="stSidebar"] button span { color: #ffffff !important; }

[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: var(--navy-2) !important;
    border-color: #35566b !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] *, [data-testid="stSidebar"] input {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

/* ======================================================
   HERO
====================================================== */

.hero {
    background: linear-gradient(120deg, #0f2438 0%, #15415a 55%, #0d8a93 100%) !important;
    padding: 2.1rem 2.4rem;
    border-radius: var(--radius-l);
    margin: 0 0 1.3rem;
    box-shadow: 0 10px 26px rgba(15,36,56,.14);
}

.hero, .hero * { color: #ffffff !important; }
.hero h1 { font-size: 2rem; line-height: 1.2; margin: .5rem 0; font-weight: 800; }
.hero p { font-size: .98rem; margin: 0; max-width: 820px; color: #dcf0f1 !important; }
.hero .eyebrow { font-size: .72rem; letter-spacing: .1em; font-weight: 700; color: #9fdfe0 !important; }

/* ======================================================
   PANELS
====================================================== */

.panel {
    background: #ffffff !important;
    border: 1px solid var(--line);
    border-radius: var(--radius-m);
    padding: 1.2rem 1.4rem;
    margin: .7rem 0 1rem;
    box-shadow: var(--shadow-card);
}

.panel h1, .panel h2, .panel h3, .panel h4, .panel p, .panel span, .panel strong { color: var(--ink) !important; }
.panel .kicker { color: var(--teal-dark) !important; }
.panel .muted { color: var(--muted) !important; }

.kicker { font-size: .72rem; letter-spacing: .09em; font-weight: 700; color: var(--teal-dark); }
.muted { color: var(--muted) !important; }

/* ======================================================
   FORMS
====================================================== */

[data-testid="stForm"] {
    background: #ffffff !important;
    border: 1px solid var(--line);
    padding: 1.3rem 1.5rem;
    border-radius: var(--radius-m);
    box-shadow: var(--shadow-card);
}

[data-testid="stForm"] p, [data-testid="stForm"] label,
[data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] label {
    color: var(--ink) !important;
    font-weight: 500;
}

/* ======================================================
   RADIO — styled as selectable option cards
====================================================== */

[data-testid="stRadio"] [role="radiogroup"] {
    gap: .5rem;
    flex-wrap: wrap;
}

[data-testid="stRadio"] label[data-baseweb="radio"] {
    background: var(--bg);
    border: 1.5px solid var(--line);
    border-radius: var(--radius-s);
    padding: .55rem .95rem;
    margin: 0 !important;
    cursor: pointer;
    transition: border-color .15s ease, background .15s ease, transform .08s ease;
}

[data-testid="stRadio"] label[data-baseweb="radio"]:hover {
    border-color: var(--teal);
    background: var(--teal-tint);
}

[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked),
[data-testid="stRadio"] label[data-baseweb="radio"][aria-checked="true"] {
    background: var(--teal) !important;
    border-color: var(--teal) !important;
}

[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) *,
[data-testid="stRadio"] label[data-baseweb="radio"][aria-checked="true"] * {
    color: #ffffff !important;
}

[data-testid="stRadio"] label[data-baseweb="radio"]:active { transform: scale(.98); }

/* ======================================================
   INPUTS AND SELECTS
====================================================== */

[data-baseweb="input"] { background: #ffffff !important; }

[data-baseweb="input"] input, [data-baseweb="textarea"] textarea {
    background: #ffffff !important;
    color: var(--ink) !important;
    -webkit-text-fill-color: var(--ink) !important;
    border-color: var(--line) !important;
}

[data-baseweb="select"] > div {
    background: #ffffff !important;
    border-color: var(--line) !important;
    transition: border-color .15s ease;
}
[data-baseweb="select"] > div:hover { border-color: var(--teal) !important; }

[data-baseweb="select"] input, [data-baseweb="select"] span {
    color: var(--ink) !important;
    -webkit-text-fill-color: var(--ink) !important;
}

[data-baseweb="popover"] { background: #ffffff !important; box-shadow: var(--shadow-card) !important; }
[data-baseweb="popover"] *, [role="option"] { color: var(--ink) !important; }
[role="option"]:hover { background: var(--teal-tint) !important; }

/* ======================================================
   METRIC CARDS
====================================================== */

[data-testid="stMetric"] {
    background: #ffffff !important;
    border: 1px solid var(--line) !important;
    padding: 1rem 1.1rem;
    border-radius: var(--radius-m);
    box-shadow: var(--shadow-card);
    transition: box-shadow .15s ease, transform .1s ease;
}
[data-testid="stMetric"]:hover { box-shadow: 0 4px 16px rgba(15,36,56,.1); transform: translateY(-1px); }

[data-testid="stMetricLabel"], [data-testid="stMetricLabel"] p { color: var(--muted) !important; }
[data-testid="stMetricValue"], [data-testid="stMetricValue"] div { color: var(--navy) !important; font-weight: 800 !important; }
[data-testid="stMetricDelta"] { color: var(--teal-dark) !important; }

/* ======================================================
   BUTTONS
====================================================== */

.stButton > button, .stFormSubmitButton > button, .stDownloadButton > button {
    border-radius: var(--radius-s);
    min-height: 2.7rem;
    font-weight: 700;
    background: #ffffff !important;
    color: var(--navy) !important;
    border: 1.5px solid #cbd8e2 !important;
    transition: border-color .15s ease, background .15s ease, transform .08s ease, box-shadow .15s ease;
}
.stButton > button:hover, .stFormSubmitButton > button:hover, .stDownloadButton > button:hover {
    border-color: var(--teal) !important;
    background: var(--teal-tint) !important;
}
.stButton > button:active, .stFormSubmitButton > button:active, .stDownloadButton > button:active { transform: scale(.98); }

.stButton > button p, .stFormSubmitButton > button p, .stDownloadButton > button p { color: var(--navy) !important; }

.stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"], .stDownloadButton > button[kind="primary"] {
    background: var(--teal) !important;
    border-color: var(--teal) !important;
    color: #ffffff !important;
    box-shadow: 0 3px 10px rgba(13,138,147,.25);
}
.stButton > button[kind="primary"]:hover, .stFormSubmitButton > button[kind="primary"]:hover, .stDownloadButton > button[kind="primary"]:hover {
    background: var(--teal-dark) !important;
    border-color: var(--teal-dark) !important;
}
.stButton > button[kind="primary"] *, .stFormSubmitButton > button[kind="primary"] *, .stDownloadButton > button[kind="primary"] * {
    color: #ffffff !important;
}

/* ======================================================
   TABLES
====================================================== */

[data-testid="stDataFrame"], [data-testid="stTable"] {
    background: #ffffff !important;
    border: 1px solid var(--line);
    border-radius: var(--radius-m);
    overflow: hidden;
}

/* ======================================================
   EXPANDERS
====================================================== */

[data-testid="stExpander"] {
    background: #ffffff !important;
    border: 1px solid var(--line) !important;
    border-radius: var(--radius-m) !important;
    overflow: hidden;
}
[data-testid="stExpander"] summary, [data-testid="stExpander"] summary p { color: var(--ink) !important; }
[data-testid="stExpander"] summary:hover { background: var(--teal-tint); }

/* ======================================================
   ALERTS — left-accent style, clear in light theme
====================================================== */

div[data-testid="stAlert"] {
    border-radius: var(--radius-s);
    border: 1px solid var(--line);
    border-left: 4px solid var(--teal);
    background: #ffffff !important;
}
div[data-testid="stAlert"] p, div[data-testid="stAlert"] span { color: var(--ink) !important; }

div[data-testid="stAlert"][data-baseweb] { background: #ffffff !important; }

/* Streamlit uses distinct classnames per alert kind via icon; color the left border to match */
div[data-testid="stAlert"]:has(svg[title="Warning"]) { border-left-color: var(--warn); }
div[data-testid="stAlert"]:has(svg[title="Error"]) { border-left-color: var(--danger); }
div[data-testid="stAlert"]:has(svg[title="Success"]) { border-left-color: var(--success); }

/* ======================================================
   PROGRESS BAR
====================================================== */

.stProgress > div { background: var(--line) !important; border-radius: 99px; overflow: hidden; }
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, var(--teal), var(--teal-dark)) !important;
    transition: width .35s ease;
}

/* ======================================================
   PLOTLY
====================================================== */

[data-testid="stPlotlyChart"] { background: transparent !important; }

/* ======================================================
   CLEAN INTERFACE
====================================================== */

footer, #MainMenu { visibility: hidden; display: none; }

/* ======================================================
   ARABIC
====================================================== */

html[dir="rtl"] body, html[dir="rtl"] [class*="css"] { font-family: 'Cairo', sans-serif !important; }
html[dir="rtl"] .hero, html[dir="rtl"] .panel { text-align: right; }
html[dir="rtl"] [data-testid="stSidebar"] { text-align: right; }
"""


st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)


def scroll_to_top():
    """Force the viewport back to the top of the page on navigation.
    Streamlit reruns the script in place and does not reset scroll
    position on its own, so without this a 'Next' click leaves the
    user wherever they were scrolled to on the previous section."""
    components.html(
        """
        <script>
        (function () {
            var doc = window.parent.document;
            var container = doc.querySelector('[data-testid="stAppViewContainer"]');
            if (container) { container.scrollTo(0, 0); }
            if (doc.documentElement) { doc.documentElement.scrollTop = 0; }
            if (doc.body) { doc.body.scrollTop = 0; }
            window.parent.scrollTo(0, 0);
        })();
        </script>
        """,
        height=0,
    )


# ==========================================================
# DATABASE AND SESSION STATE
# ==========================================================

initialize_database()

DEFAULTS = {
    "page": "welcome",
    "profile": {},
    "answers": {},
    "overall_answer": None,
    "results": None,
    "assessment_id": None,
    "eligible": None,
    "admin_ok": False,
    "consent": False,
}

for key, val in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = val


# ==========================================================
# LANGUAGE SELECTION
# ==========================================================

with st.sidebar:

    st.markdown("## ◆ Egypt AI Readiness")

    language = st.selectbox(
        "Language / اللغة",
        ["English", "العربية"],
        index=0,
        key="language_choice",
    )

    lang = "العربية" if language == "العربية" else "English"

    T = get_language_pack(lang)

    if lang == "العربية":
        st.markdown(
            "<style>html{direction:rtl}</style>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<style>html{direction:ltr}</style>",
            unsafe_allow_html=True,
        )

    st.caption(T["tagline"])
    st.divider()

    if st.button(
        T["welcome"],
        use_container_width=True,
        disabled=(st.session_state.eligible is False),
    ):
        st.session_state.page = "welcome"
        st.rerun()

    if st.button(T["admin"], use_container_width=True):
        st.session_state.page = "admin"
        st.rerun()

    st.divider()

    st.caption("Local research application • Streamlit + SQLite")


# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def t_profile_options(i):
    return T["profile_options"][i]


def hero(title, subtitle, tag=None):

    tag = tag or T["tagline"]

    st.markdown(
        f"""
        <div class="hero">
            <div class="eyebrow">{tag}</div>
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def progress(step):

    st.progress(min(step / 7, 1.0))

    st.caption(
        f'{T["step"]} {step} {T["of"]} 7'
    )


def reset_assessment():

    for k, v in {
        "page": "welcome",
        "profile": {},
        "answers": {},
        "overall_answer": None,
        "results": None,
        "assessment_id": None,
        "eligible": None,
        "consent": False,
    }.items():

        st.session_state[k] = v

    st.rerun()


def is_admin_configured():

    try:
        return bool(st.secrets.get("ADMIN_PASSWORD", ""))

    except Exception:
        return bool(os.environ.get("ADMIN_PASSWORD"))


def admin_password():

    try:

        val = st.secrets.get("ADMIN_PASSWORD", "")

        if val:
            return str(val)

    except Exception:
        pass

    return os.environ.get("ADMIN_PASSWORD", "")


def dimension_keys():

    return list(DIMENSIONS.keys())


def answer_value_for_label(label, labels):

    try:
        return labels.index(label) + 1

    except ValueError:
        return None


# ==========================================================
# WELCOME PAGE
# ==========================================================

def welcome_page():

    scroll_to_top()

    hero(T["welcome"], T["welcome_sub"])

    st.markdown(
        f"""
        <div class="panel">
            <div class="kicker">{T["about"]}</div>
            <h3>{T["app_title"]}</h3>
            <p class="muted">{T["about_text"]}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    a, b, c = st.columns(3)

    a.metric(T["questions"], "37")
    b.metric(T["time"], T["minutes"])
    c.metric(T["dimensions"], "5")

    with st.expander(T["privacy"], expanded=True):
        st.write(T["privacy_text"])

    st.info(T["no_right"])

    consent = st.checkbox(
        T["consent_label"] + ": " + T["consent"],
        value=st.session_state.consent,
        key="consent_widget",
    )

    st.session_state.consent = consent

    if st.button(
        T["start"] + " →",
        type="primary",
        use_container_width=True,
    ):

        if not consent:
            st.error(T["consent_required"])

        else:
            st.session_state.page = "profile"
            st.rerun()


# ==========================================================
# PROFILE PAGE
# ==========================================================

def profile_page():

    scroll_to_top()

    hero(T["profile"], T["profile_sub"])

    progress(1)

    st.markdown(
        f"""
        <div class="panel">
            <div class="kicker">SECTION 01</div>
            <h3>{T["profile"]}</h3>
            <p class="muted">{T["no_identity"]}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    values = {}
    keys = list(PROFILE_QUESTIONS)

    with st.form("profile_form", clear_on_submit=False):

        cols = st.columns(2)

        for i, key in enumerate(keys):

            with cols[i % 2]:

                old = st.session_state.profile.get(key)

                opts = t_profile_options(i)

                old_index = opts.index(old) if old in opts else None

                values[key] = st.selectbox(
                    T["profile_labels"][i],
                    opts,
                    index=old_index,
                    placeholder=(
                        "اختر إجابة"
                        if lang == "العربية"
                        else "Choose an answer"
                    ),
                    key=f"profile_{key}_{lang}",
                )

        submitted = st.form_submit_button(
            T["continue"] + " →",
            type="primary",
            use_container_width=True,
        )

    if submitted:

        if any(v is None for v in values.values()):

            st.error(T["answer_profile"])

        elif values["employment"] in ("No", "لا"):

            st.session_state.eligible = False
            st.session_state.profile = {}
            st.session_state.answers = {}
            st.session_state.page = "ineligible"

            st.rerun()

        else:

            st.session_state.eligible = True
            st.session_state.profile = values
            st.session_state.page = "dimension_0"

            st.rerun()

    if st.button("← " + T["welcome"]):

        st.session_state.page = "welcome"
        st.rerun()


# ==========================================================
# INELIGIBLE PAGE
# ==========================================================

def ineligible_page():

    scroll_to_top()

    st.session_state.profile = {}
    st.session_state.answers = {}
    st.session_state.results = None
    st.session_state.assessment_id = None

    hero(
        T["not_eligible"],
        T["not_eligible_text"],
        "ELIGIBILITY CHECK",
    )

    st.error(T["not_eligible_text"])

    st.caption(
        "Close this browser tab to end the session."
        if lang != "العربية"
        else "يُرجى إغلاق علامة تبويب المتصفح لإنهاء الجلسة."
    )


# ==========================================================
# DIMENSION PAGES
# ==========================================================

def dimension_page(i):

    scroll_to_top()

    if st.session_state.eligible is not True:

        st.session_state.page = "ineligible"
        st.rerun()

    keys = dimension_keys()

    key = keys[i]

    questions = DIMENSIONS[key]

    translated = T["dimension_questions"][i]

    display_name = T["dimension_labels"][i]

    hero(display_name, T["dimension_sub"])

    progress(i + 2)

    st.markdown(
        f"""
        <div class="panel">
            <div class="kicker">
                SECTION 02 • {T["dimension"].upper()} {i + 1} OF 5
            </div>
            <h3>{display_name}</h3>
            <p class="muted">{T["required_six"]}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    selected = {}

    with st.form(f"dimension_form_{i}_{lang}"):

        for j, q in enumerate(questions):

            old = st.session_state.answers.get(q)

            labels = T["likert"]

            oldlabel = (
                labels[old - 1]
                if isinstance(old, int) and 1 <= old <= 5
                else None
            )

            idx = labels.index(oldlabel) if oldlabel in labels else None

            selected[q] = st.radio(
                f"{j + 1:02d}. {translated[j]}",
                labels,
                index=idx,
                horizontal=(lang != "العربية"),
                key=f"item_{i}_{j}_{lang}",
            )

            if j < 5:
                st.divider()

        submitted = st.form_submit_button(
            T["next"] + " →",
            type="primary",
            use_container_width=True,
        )

    if submitted:

        if any(v is None for v in selected.values()):

            st.error(T["answer_six"])

        else:

            st.session_state.answers.update(
                {
                    q: T["likert"].index(v) + 1
                    for q, v in selected.items()
                }
            )

            st.session_state.page = (
                "overall"
                if i == 4
                else f"dimension_{i + 1}"
            )

            st.rerun()

    left, right = st.columns([1, 2])

    with left:

        if st.button("← " + T["previous"], use_container_width=True):

            st.session_state.page = (
                "profile"
                if i == 0
                else f"dimension_{i - 1}"
            )

            st.rerun()

    with right:

        st.caption(T["saved"])


# ==========================================================
# OVERALL READINESS PAGE
# ==========================================================

def overall_page():

    scroll_to_top()

    if st.session_state.eligible is not True:

        st.session_state.page = "ineligible"
        st.rerun()

    hero(T["overall"], T["overall_sub"])

    progress(7)

    labels = T["overall_options"]

    old = st.session_state.overall_answer

    with st.form("overall_form"):

        st.markdown(
            f"""
            <div class="panel">
                <div class="kicker">SECTION 03</div>
                <h3>{T["overall"]}</h3>
            </div>
            """,
            unsafe_allow_html=True,
        )

        idx = labels.index(old) if old in labels else None

        answer = st.radio(
            T["overall_q"],
            labels,
            index=idx,
            key=f"overall_{lang}",
        )

        submitted = st.form_submit_button(
            T["submit"],
            type="primary",
            use_container_width=True,
        )

    if submitted:

        if answer is None:

            st.error(T["answer_overall"])

        else:

            result = calculate_readiness(
                st.session_state.answers
            )

            if result.get("overall_score") is None:

                st.error(T["missing"])

            else:

                st.session_state.overall_answer = answer

                result["overall_response"] = answer

                st.session_state.results = result

                st.session_state.assessment_id = save_submission(
                    st.session_state.profile,
                    st.session_state.answers,
                    result,
                )

                st.session_state.page = "results"

                st.rerun()

    if st.button("← " + T["previous"]):

        st.session_state.page = "dimension_4"
        st.rerun()


# ==========================================================
# PDF REPORT
# ==========================================================

def make_pdf(result, aid, lang):

    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
    )
    from reportlab.lib.styles import (
        getSampleStyleSheet,
        ParagraphStyle,
    )
    from reportlab.lib.units import mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    buff = io.BytesIO()

    doc = SimpleDocTemplate(
        buff,
        pagesize=A4,
        rightMargin=17 * mm,
        leftMargin=17 * mm,
        topMargin=17 * mm,
        bottomMargin=17 * mm,
    )

    styles = getSampleStyleSheet()

    is_ar = lang == "العربية"

    font_path = Path(__file__).parent / "assets" / "DejaVuSans.ttf"

    if is_ar:

        try:

            import arabic_reshaper
            from bidi.algorithm import get_display

            pdfmetrics.registerFont(
                TTFont("DejaVuArabic", str(font_path))
            )

            def shape(s):
                return get_display(
                    arabic_reshaper.reshape(str(s))
                )

            font = "DejaVuArabic"

        except Exception:

            def shape(s):
                return str(s)

            font = "Helvetica"

    else:

        def shape(s):
            return str(s)

        font = "Helvetica"

    title_style = ParagraphStyle(
        "TitleCustom",
        parent=styles["Title"],
        fontName=font,
        textColor=colors.HexColor("#10283f"),
        alignment=2 if is_ar else 0,
    )

    body = ParagraphStyle(
        "BodyCustom",
        parent=styles["BodyText"],
        fontName=font,
        leading=15,
        alignment=2 if is_ar else 0,
    )

    heading = ParagraphStyle(
        "HeadingCustom",
        parent=styles["Heading2"],
        fontName=font,
        textColor=colors.HexColor("#087f8c"),
        alignment=2 if is_ar else 0,
    )

    Tpdf = get_language_pack(lang)

    title = (
        "تقرير تقييم جاهزية الذكاء الاصطناعي"
        if is_ar
        else "AI Readiness Assessment Report"
    )

    story = [
        Paragraph(shape(title), title_style),
        Spacer(1, 5 * mm),
        Paragraph(
            shape(f'{Tpdf["reference"]}: {aid}'),
            body,
        ),
        Spacer(1, 4 * mm),
        Paragraph(
            shape(
                f'{Tpdf["overall_score"]}: '
                f'{result["overall_score"]:.1f}/100'
            ),
            heading,
        ),
        Spacer(1, 4 * mm),
    ]

    data = [
        [
            shape(Tpdf["dimension_results"]),
            shape(Tpdf["mean"]),
            shape(Tpdf["score"]),
        ]
    ]

    for i, (name, val) in enumerate(result["dimensions"].items()):

        data.append(
            [
                shape(Tpdf["dimension_labels"][i]),
                f'{val["mean"]:.2f}',
                f'{val["score"]:.1f}',
            ]
        )

    table = Table(
        data,
        colWidths=[105 * mm, 32 * mm, 32 * mm],
        repeatRows=1,
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#10283f"),
                ),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    .45,
                    colors.HexColor("#dce5ec"),
                ),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [
                        colors.white,
                        colors.HexColor("#f3f6f9"),
                    ],
                ),
                ("FONTNAME", (0, 0), (-1, -1), font),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                (
                    "ALIGN",
                    (0, 0),
                    (-1, -1),
                    "RIGHT" if is_ar else "LEFT",
                ),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("PADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )

    story += [
        table,
        Spacer(1, 6 * mm),
        Paragraph(shape(Tpdf["scoring_note"]), body),
    ]

    doc.build(story)

    buff.seek(0)

    return buff.getvalue()


# ==========================================================
# INDIVIDUAL RESULTS DASHBOARD
# ==========================================================

def results_page():

    scroll_to_top()

    if (
        st.session_state.eligible is not True
        or not st.session_state.results
    ):

        st.session_state.page = (
            "ineligible"
            if st.session_state.eligible is not True
            else "welcome"
        )

        st.rerun()

    result = st.session_state.results

    hero(T["results"], T["results_sub"])

    c1, c2, c3 = st.columns(3)

    c1.metric(
        T["overall_score"],
        f'{result["overall_score"]:.1f} / 100',
    )

    c2.metric(
        T["overall_response"],
        st.session_state.overall_answer,
    )

    c3.metric(
        T["completed"],
        "5 / 5",
    )

    rows = []

    for i, (name, v) in enumerate(result["dimensions"].items()):

        rows.append(
            {
                T["dimension_results"]: T["dimension_labels"][i],
                T["mean"]: v["mean"],
                T["score"]: v["score"],
            }
        )

    df = pd.DataFrame(rows)

    st.subheader(T["dimension_results"])

    st.dataframe(
        df.style.format(
            {
                T["mean"]: "{:.2f}",
                T["score"]: "{:.1f}",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

    left, right = st.columns(2)

    with left:

        fig = px.bar(
            df.sort_values(T["score"]),
            x=T["score"],
            y=T["dimension_results"],
            orientation="h",
            range_x=[0, 100],
            text=T["score"],
            color_discrete_sequence=["#087f8c"],
        )

        fig.update_traces(
            texttemplate="%{text:.1f}",
            textposition="outside",
            cliponaxis=False,
        )

        fig.update_layout(
            template="plotly_white",
            height=410,
            margin=dict(l=8, r=35, t=25, b=15),
            xaxis_title=T["score"],
            yaxis_title="",
            font=dict(color="#172b3a"),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(
                range=[0, 110],
                gridcolor="#e7edf2",
            ),
            yaxis=dict(automargin=True),
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={"displayModeBar": False},
        )

    with right:

        radar = go.Figure()

        radar.add_trace(
            go.Scatterpolar(
                r=[
                    r[T["score"]]
                    for r in rows
                ] + [
                    rows[0][T["score"]]
                ],
                theta=[
                    r[T["dimension_results"]]
                    for r in rows
                ] + [
                    rows[0][T["dimension_results"]]
                ],
                fill="toself",
                line=dict(
                    color="#087f8c",
                    width=3,
                ),
                fillcolor="rgba(8,127,140,.16)",
                name=T["score"],
            )
        )

        radar.update_layout(
            template="plotly_white",
            height=410,
            showlegend=False,
            margin=dict(l=35, r=35, t=30, b=30),
            font=dict(color="#172b3a"),
            paper_bgcolor="rgba(0,0,0,0)",
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    gridcolor="#dce5ec",
                    tickfont=dict(color="#52687a"),
                ),
                angularaxis=dict(
                    gridcolor="#dce5ec",
                    tickfont=dict(color="#172b3a"),
                ),
            ),
        )

        st.plotly_chart(
            radar,
            use_container_width=True,
            config={"displayModeBar": False},
        )

    st.info(T["scoring_note"])

    st.subheader(T["areas"])

    st.caption(T["areas_note"])

    avg = result["overall_score"]

    recs = []

    for i, (name, v) in enumerate(result["dimensions"].items()):

        if v["score"] < avg:

            recs.append(
                (
                    i,
                    T["recommendations"][name],
                )
            )

    if not recs:

        st.write(T["no_areas"])

    for i, items in recs:

        with st.expander(
            T["dimension_labels"][i],
            expanded=True,
        ):

            for item in items:

                st.markdown("- " + item)

    try:

        pdf = make_pdf(
            result,
            st.session_state.assessment_id,
            lang,
        )

        st.download_button(
            T["pdf"],
            pdf,
            file_name=(
                "AI_Readiness_Report_AR.pdf"
                if lang == "العربية"
                else "AI_Readiness_Report_EN.pdf"
            ),
            mime="application/pdf",
            type="primary",
        )

    except Exception as e:

        st.warning(f"PDF generation issue: {e}")

    st.caption(
        f'{T["reference"]}: '
        f'{st.session_state.assessment_id}'
    )

    if st.button(T["new"]):

        reset_assessment()


# ==========================================================
# HISTORICAL GOOGLE FORMS DATA DASHBOARD
# ==========================================================

def historical_data_dashboard():
    """Descriptive dashboard for the original 27 Google Forms responses.

    This historical dataset is intentionally kept separate from new app
    submissions stored in SQLite.
    """
    data_dir = Path(__file__).resolve().parent / "data"
    xlsx_path = data_dir / "original_google_forms_responses.xlsx"
    reliability_path = data_dir / "reliability_summary.csv"

    st.markdown("### Original Google Forms dataset")
    st.caption("Historical dataset · 27 completed responses · kept separate from new web-app submissions")
    if not xlsx_path.exists():
        st.error("The original Google Forms Excel file is missing from the data folder.")
        return

    raw = pd.read_excel(xlsx_path)
    if raw.shape[1] < 38:
        st.error(f"Expected 38 columns (timestamp, 6 profile fields, 30 items, overall response); found {raw.shape[1]}.")
        return

    # The original export stores the six profile questions in columns 1–6,
    # the 30 Likert items in columns 7–36, and the overall item in column 37.
    profile_cols = list(raw.columns[1:7])
    item_cols = list(raw.columns[7:37])
    overall_col = raw.columns[37]
    numeric = raw[item_cols].apply(lambda col: col.map(LIKERT_OPTIONS).fillna(pd.to_numeric(col, errors="coerce")))

    dimension_names = list(DIMENSIONS.keys())
    dimension_scores = pd.DataFrame(index=raw.index)
    for idx, name in enumerate(dimension_names):
        block = numeric.iloc[:, idx * 6:(idx + 1) * 6]
        means = block.mean(axis=1)
        # Require all six items for a dimension score, matching the app scoring rule.
        complete = block.notna().sum(axis=1).eq(6)
        dimension_scores[name] = (((means - 1) / 4) * 100).where(complete)
    dimension_scores["Overall calculated score"] = dimension_scores[dimension_names].mean(axis=1).where(dimension_scores[dimension_names].notna().all(axis=1))

    analysis = pd.concat([raw[profile_cols].copy(), dimension_scores], axis=1)
    analysis["Direct overall response"] = raw[overall_col]
    n = len(raw)
    overall_mean = dimension_scores["Overall calculated score"].mean()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Completed responses", f"{n}")
    m2.metric("Overall calculated score", f"{overall_mean:.1f}/100" if pd.notna(overall_mean) else "—")
    m3.metric("Survey statements", "30")
    m4.metric("Readiness dimensions", "5")
    st.info("Scores represent respondents’ perceptions of their organizations. They are descriptive results from this sample, not objective institutional audits or nationally representative estimates.")

    left, right = st.columns([1.35, 1])
    with left:
        st.markdown("#### Average score by dimension")
        avg = dimension_scores[dimension_names].mean().rename_axis("Dimension").reset_index(name="Average score")
        avg["Dimension"] = [T["dimension_labels"][i] for i in range(5)]
        fig = px.bar(avg, x="Dimension", y="Average score", text="Average score", range_y=[0,100], color_discrete_sequence=["#0d8a93"])
        fig.update_traces(texttemplate="%{text:.1f}", textposition="outside", cliponaxis=False)
        fig.update_layout(template="plotly_white", height=390, margin=dict(l=8,r=8,t=24,b=90), xaxis_title="", yaxis_title="Score (0–100)", showlegend=False)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
    with right:
        st.markdown("#### Direct overall-readiness responses")
        counts = raw[overall_col].value_counts(dropna=False).rename_axis("Response").reset_index(name="Count")
        fig2 = px.bar(counts, x="Count", y="Response", orientation="h", text="Count", color_discrete_sequence=["#173449"])
        fig2.update_layout(template="plotly_white", height=390, margin=dict(l=8,r=8,t=24,b=8), xaxis_title="Number of respondents", yaxis_title="")
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar":False})

    st.markdown("#### Respondent profile")
    profile_titles = ["Organization type", "Main work area", "AI familiarity", "Governorate", "Organizational level"]
    profile_cols_display = profile_cols[1:]
    profile_layout = st.columns(2)
    for j, (col, title) in enumerate(zip(profile_cols_display, profile_titles)):
        with profile_layout[j % 2]:
            counts = raw[col].fillna("Not reported").value_counts().rename_axis("Category").reset_index(name="Respondents")
            pf = px.bar(counts, x="Respondents", y="Category", orientation="h", text="Respondents", title=title, color_discrete_sequence=["#0d8a93"])
            pf.update_layout(template="plotly_white", height=300, margin=dict(l=8,r=8,t=42,b=8), xaxis_title="Respondents", yaxis_title="")
            st.plotly_chart(pf, use_container_width=True, config={"displayModeBar":False})

    st.markdown("#### Item-level response patterns")
    dim_choice = st.selectbox("Select a readiness dimension", dimension_names, key="historical_dimension")
    dim_idx = dimension_names.index(dim_choice)
    start = dim_idx * 6
    item_summary = []
    labels = list(LIKERT_OPTIONS.keys())
    for j, col in enumerate(item_cols[start:start+6]):
        vals = numeric[col]
        row = {"Question": f"Q{start+j+1}", "Statement": col.split("\n")[0].strip()}
        for label, value in LIKERT_OPTIONS.items():
            row[label] = int((vals == value).sum())
        row["Mean (1–5)"] = round(vals.mean(), 2)
        item_summary.append(row)
    st.dataframe(pd.DataFrame(item_summary), use_container_width=True, hide_index=True)

    st.markdown("#### Internal consistency (Cronbach’s alpha)")
    if reliability_path.exists():
        reliability = pd.read_csv(reliability_path)
        rel_view = reliability[["Dimension", "Items", "N", "Cronbach_alpha", "Lowest_corrected_item_total_correlation"]].copy()
        rel_view.columns = ["Dimension", "Items", "N", "Cronbach’s alpha", "Lowest corrected item–total correlation"]
        rel_view["Cronbach’s alpha"] = rel_view["Cronbach’s alpha"].map(lambda x: f"{x:.3f}")
        rel_view["Lowest corrected item–total correlation"] = rel_view["Lowest corrected item–total correlation"].map(lambda x: f"{x:.3f}")
        st.dataframe(rel_view, use_container_width=True, hide_index=True)
        st.caption("These alpha estimates provide preliminary internal-consistency evidence only. They do not establish content, construct, or criterion validity; interpretation is limited by the small sample (n=27).")
    else:
        st.warning("Reliability summary CSV not found in the data folder.")

    st.markdown("#### Preliminary interpretation and limitations")
    if pd.notna(overall_mean):
        st.write(f"The sample’s mean calculated overall score is **{overall_mean:.1f}/100**. The dimension profile should be read comparatively and descriptively.")
    governorate = raw[profile_cols[4]].value_counts()
    if len(governorate):
        top_gov, top_n = governorate.index[0], int(governorate.iloc[0])
        st.write(f"**Geographic concentration:** {top_n} of {n} respondents ({top_n/n:.1%}) reported {top_gov}. The sample therefore has limited geographic coverage.")
    st.write("The sample is purposive/non-probability and should not be presented as statistically representative of all Egyptian public-sector organizations. The direct overall-readiness item is reported separately from the calculated 0–100 composite score.")

    export = analysis.copy()
    export.insert(0, "Original response number", range(1, n+1))
    st.download_button("Download original dataset with calculated scores (CSV)", export.to_csv(index=False).encode("utf-8-sig"), file_name="original_google_forms_with_scores.csv", mime="text/csv", key="historical_export")


# ==========================================================
# RESEARCHER / ADMIN DASHBOARD
# ==========================================================

def admin_page():

    scroll_to_top()

    hero(
        T["admin"],
        T["admin_sub"],
        "RESEARCHER AREA",
    )

    if not is_admin_configured():

        st.error(T["admin_locked"])
        return

    if not st.session_state.admin_ok:

        st.markdown(
            f"""
            <div class="panel">
                <div class="kicker">RESTRICTED ACCESS</div>
                <h3>{T["admin_login"]}</h3>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("admin_login"):

            password = st.text_input(
                T["password"],
                type="password",
            )

            submitted = st.form_submit_button(
                T["login"],
                type="primary",
                use_container_width=True,
            )

        if submitted:

            if hmac.compare_digest(
                password,
                admin_password(),
            ):

                st.session_state.admin_ok = True
                st.rerun()

            else:

                st.error(T["bad_password"])

        return

    tab_original, tab_new = st.tabs(["Original Google Forms (27)", "New web-app submissions"])
    with tab_original:
        historical_data_dashboard()
    with tab_new:
        app_submissions_dashboard()


def app_submissions_dashboard():
        st.warning(T["admin_warning"])

        records = get_all_assessments()

        if not records:

            st.info(T["no_records"])
            return

        parsed = []

        for rec in records:

            p = json.loads(rec["profile"])
            r = json.loads(rec["results"])

            row = {
                "Reference": rec["id"],
                "Submitted (UTC)": rec["submitted_at"],
                "Organization type": p.get("organization_type"),
                "Work area": p.get("work_area"),
                "Governorate": p.get("governorate"),
                "Level": p.get("organizational_level"),
                "Overall score": r.get("overall_score"),
                "Overall response": r.get("overall_response"),
            }

            for d, v in r.get("dimensions", {}).items():

                row[d] = v.get("score") if v else None

            parsed.append(row)

        df = pd.DataFrame(parsed)

        fh_left, fh_right = st.columns([5, 1])

        with fh_left:
            st.subheader(T["filters"])

        with fh_right:
            if st.button(T["clear_filters"], use_container_width=True):
                for col in ("Organization type", "Work area", "Governorate", "Level"):
                    st.session_state.pop("filter_" + col, None)
                st.rerun()

        f1, f2, f3, f4 = st.columns(4)

        filtered = df.copy()

        for col, box, label in [
            ("Organization type", f1, T["org"]),
            ("Work area", f2, T["work"]),
            ("Governorate", f3, T["gov"]),
            ("Level", f4, T["level"]),
        ]:

            vals = sorted(
                [
                    x
                    for x in filtered[col].dropna().unique()
                ]
            )

            choice = box.selectbox(
                label,
                [T["all"]] + vals,
                key="filter_" + col,
            )

            if choice != T["all"]:

                filtered = filtered[
                    filtered[col] == choice
                ]

        a, b, c = st.columns(3)

        a.metric(
            T["submissions"],
            len(filtered),
        )

        b.metric(
            T["mean_overall"],
            (
                f'{filtered["Overall score"].mean():.1f}'
                if len(filtered)
                else "—"
            ),
        )

        c.metric(
            T["governorates"],
            filtered["Governorate"].nunique(),
        )

        if not len(filtered):

            st.info(T["no_matches"])

        if len(filtered):

            dimcols = list(DIMENSIONS.keys())

            mean_df = pd.DataFrame(
                {
                    "Dimension": [
                        T["dimension_labels"][i]
                        for i in range(5)
                    ],
                    "Mean score": [
                        filtered[d].mean()
                        for d in dimcols
                    ],
                }
            )

            fig = px.bar(
                mean_df,
                x="Dimension",
                y="Mean score",
                range_y=[0, 100],
                text="Mean score",
                color_discrete_sequence=["#087f8c"],
            )

            fig.update_traces(
                texttemplate="%{text:.1f}",
                textposition="outside",
                cliponaxis=False,
            )

            fig.update_layout(
                template="plotly_white",
                height=370,
                margin=dict(
                    l=10,
                    r=10,
                    t=25,
                    b=90,
                ),
                xaxis_title="",
                yaxis_title="Score (0–100)",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#172b3a"),
                yaxis=dict(
                    gridcolor="#e7edf2",
                ),
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={"displayModeBar": False},
            )

        if len(filtered):

            trend_df = filtered.copy()
            trend_df["Date"] = pd.to_datetime(
                trend_df["Submitted (UTC)"]
            ).dt.date
            trend_counts = (
                trend_df.groupby("Date")
                .size()
                .reset_index(name="Submissions")
                .sort_values("Date")
            )

            if len(trend_counts) > 1:

                st.subheader(T["trend"])

                trend_fig = px.line(
                    trend_counts,
                    x="Date",
                    y="Submissions",
                    markers=True,
                )

                trend_fig.update_traces(
                    line=dict(color="#0d8a93", width=3),
                    marker=dict(color="#0d8a93", size=7),
                )

                trend_fig.update_layout(
                    template="plotly_white",
                    height=280,
                    margin=dict(l=10, r=10, t=20, b=10),
                    xaxis_title="",
                    yaxis_title=T["submissions"],
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#16242f"),
                    yaxis=dict(gridcolor="#e7edf2", rangemode="tozero"),
                )

                st.plotly_chart(
                    trend_fig,
                    use_container_width=True,
                    config={"displayModeBar": False},
                )

        st.subheader(T["table"])

        st.dataframe(
            filtered,
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            T["export"],
            filtered.to_csv(index=False).encode("utf-8-sig"),
            file_name="ai_readiness_submissions.csv",
            mime="text/csv",
            type="primary",
        )

        if st.button(T["logout"]):

            st.session_state.admin_ok = False
            st.rerun()


# ==========================================================
# ROUTING AND ELIGIBILITY PROTECTION
# ==========================================================

page = st.session_state.page

if (
    st.session_state.eligible is False
    and page not in ("ineligible", "admin")
):

    st.session_state.page = "ineligible"
    page = "ineligible"

if (
    page.startswith("dimension_")
    and st.session_state.eligible is not True
):

    page = "ineligible"
    st.session_state.page = page

if (
    page == "welcome"
    and st.session_state.eligible is False
):

    st.session_state.page = "ineligible"
    st.rerun()

elif page == "welcome":

    welcome_page()

elif page == "profile":

    profile_page()

elif page == "ineligible":

    ineligible_page()

elif page.startswith("dimension_"):

    dimension_page(
        int(page.split("_")[1])
    )

elif page == "overall":

    overall_page()

elif page == "results":

    results_page()

elif page == "admin":

    admin_page()

else:

    st.session_state.page = "welcome"
    st.rerun()
