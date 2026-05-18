import streamlit as st 
import preprocessing
import resumeparser
from pipeline import run_pipeline
import tempfile 
import os 

st.set_page_config(
    page_title="ATS Scorer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');
 
/* ── Reset & base ── */
*, *::before, *::after { box-sizing: border-box; }
 
html, body, [data-testid="stAppViewContainer"] {
    background-color: #0a0a0a !important;
    color: #e8e4dc !important;
    font-family: 'DM Mono', monospace !important;
}
 
[data-testid="stAppViewContainer"] {
    background-image:
        radial-gradient(ellipse 80% 50% at 20% 10%, rgba(255,210,100,0.06) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 80%, rgba(255,150,80,0.05) 0%, transparent 60%);
}
 
/* Hide streamlit chrome */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"] { display: none !important; }
 
/* ── Main container ── */
.main-wrap {
    max-width: 1100px;
    margin: 0 auto;
    padding: 20px 24px 80px;
}
 
/* ── Header ── */
.hero {
    text-align: center;
    margin-bottom: 60px;
}
 
.hero-eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #c8a84b;
    margin-bottom: 16px;
}
 
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(42px, 6vw, 72px);
    font-weight: 800;
    line-height: 1;
    letter-spacing: -0.03em;
    color: #f0ebe0;
    margin: 0 0 20px;
}
 
.hero-title span {
    color: #c8a84b;
}
 
.hero-sub {
    font-family: 'DM Mono', monospace;
    font-size: 13px;
    color: #6b6560;
    letter-spacing: 0.05em;
}
 
/* ── Two-column panel ── */
.panels {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2px;
    background: #1e1b17;
    border: 1px solid #2a2520;
    margin-bottom: 40px;
}
 
.panel {
    background: #0f0d0b;
    padding: 36px 32px;
}
 
.panel-label {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: #c8a84b;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    gap: 10px;
}
 
.panel-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: #2a2520;
}
 
/* ── Upload zone ── */
.upload-zone {
    border: 1px dashed #2e2a25;
    background: #0a0906;
    border-radius: 2px;
    padding: 48px 24px;
    text-align: center;
    transition: border-color 0.2s;
    cursor: pointer;
    min-height: 260px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 12px;
}
 
.upload-zone:hover { border-color: #c8a84b; }
 
.upload-icon {
    font-size: 32px;
    opacity: 0.4;
}
 
.upload-text {
    font-size: 12px;
    color: #4a4540;
    letter-spacing: 0.08em;
}
 
.upload-hint {
    font-size: 10px;
    color: #2e2a25;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
 
/* ── Streamlit file uploader overrides ── */
[data-testid="stFileUploader"] {
    background: transparent !important;
}
 
[data-testid="stFileUploader"] > div {
    background: #0a0906 !important;
    border: 1px dashed #2e2a25 !important;
    border-radius: 2px !important;
    padding: 40px 24px !important;
    min-height: 260px !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    transition: border-color 0.2s !important;
}
 
[data-testid="stFileUploader"] > div:hover {
    border-color: #c8a84b !important;
}
 
[data-testid="stFileUploaderDropzoneInstructions"] {
    color: #4a4540 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 12px !important;
}
 
[data-testid="stFileUploaderDropzoneInstructions"] span {
    color: #4a4540 !important;
}
 
[data-testid="stFileUploaderDropzone"] svg {
    fill: #2e2a25 !important;
}
 
/* Upload button */
[data-testid="stFileUploader"] button {
    background: transparent !important;
    border: 1px solid #2e2a25 !important;
    color: #6b6560 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 0.12em !important;
    border-radius: 1px !important;
    padding: 8px 20px !important;
    transition: all 0.2s !important;
}
 
[data-testid="stFileUploader"] button:hover {
    border-color: #c8a84b !important;
    color: #c8a84b !important;
}
 
/* ── Textarea overrides ── */
[data-testid="stTextArea"] textarea {
    background: #0a0906 !important;
    border: 1px solid #2e2a25 !important;
    border-radius: 2px !important;
    color: #c8c4bc !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 12px !important;
    line-height: 1.7 !important;
    padding: 20px !important;
    resize: none !important;
    transition: border-color 0.2s !important;
    min-height: 260px !important;
}
 
[data-testid="stTextArea"] textarea:focus {
    border-color: #c8a84b !important;
    box-shadow: none !important;
    outline: none !important;
}
 
[data-testid="stTextArea"] textarea::placeholder {
    color: #2e2a25 !important;
}
 
[data-testid="stTextArea"] label {
    display: none !important;
}
 
/* ── CTA button ── */
.cta-wrap {
    display: flex;
    justify-content: center;
    margin-top: 8px;
}
 
[data-testid="stButton"] > button {
    background: #c8a84b !important;
    color: #0a0a0a !important;
    border: none !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    letter-spacing: 0.18em !important;
    text-transform: uppercase !important;
    padding: 18px 56px !important;
    border-radius: 1px !important;
    cursor: pointer !important;
    transition: all 0.2s !important;
    width: auto !important;
}
 
[data-testid="stButton"] > button:hover {
    background: #e0bf60 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 32px rgba(200,168,75,0.25) !important;
}
 
[data-testid="stButton"] {
    display: flex !important;
    justify-content: center !important;
}
[data-testid="stButton"] > button:active {
    transform: translateY(0) !important;
}
 
/* ── Status pill ── */
.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-size: 11px;
    letter-spacing: 0.1em;
    padding: 6px 14px;
    border-radius: 1px;
    margin-top: 16px;
}
 
.status-pill.ready {
    background: rgba(100,200,120,0.08);
    border: 1px solid rgba(100,200,120,0.2);
    color: #64c878;
}
 
.status-pill.missing {
    background: rgba(200,100,80,0.08);
    border: 1px solid rgba(200,100,80,0.15);
    color: #c86450;
}
 
/* ── Footer note ── */
.footer-note {
    text-align: center;
    font-size: 10px;
    color: #2e2a25;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-top: 48px;
}
 
/* ── Column gap fix ── */
[data-testid="stColumns"] {
    gap: 16px !important;
    align-items: stretch !important;
}

[data-testid="stColumn"] {
    background: #0f0d0b !important;
    border: 1px solid #2a2520 !important;
    padding: 36px 32px !important;
    border-radius: 2px !important;
}
</style>
""", unsafe_allow_html=True)

if "page" not in st.session_state:
    st.session_state.page = "input"
if "resume_file" not in st.session_state:
    st.session_state.resume_file = None
if "jd_text" not in st.session_state:
    st.session_state.jd_text = ""

def input_page():
    st.markdown("""
    <div class="main-wrap">
    <div class="hero">
                <div class="hero-eyebrow">Resume Intelligence</div>
                <h1 class="hero-title">ATS Scorer</h1>
                <p class="hero-sub"> // paste a job description . upload your resume . close the gap</p>
    </div>
    </div>
    """, unsafe_allow_html=True)
    col_left, col_right = st.columns(2)
    with col_left:
        st.markdown("01 &nbsp;&nbsp; RESUME")
        uploaded_file = st.file_uploader(
            "Upload resume",
            type=["pdf", "docx"],
            label_visibility="collapsed",
        )
        if uploaded_file:
            st.markdown(f'<div class="status-pill ready">✓ &nbsp; {uploaded_file.name}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-pill missing">○ &nbsp; No file selected</div>', unsafe_allow_html=True)

    
    with col_right:
        st.markdown("02 &nbsp;&nbsp; JOB DESCRIPTION")
        jd_text = st.text_area(
            "Job description",
            height=340,
            placeholder="Paste the job description here...",
            label_visibility="collapsed",
        )
    
    st.markdown("<div style='height: 40px'></div>", unsafe_allow_html=True)
    # col1, col2, col3 = st.columns([1,1,1])
    # with col2:
    #     match_clicked = st.button("⟶  Match My Resume", use_container_width=True)
    # ADD this instead
    st.markdown("<div style='display:flex; justify-content:center; margin-top:32px;'>", unsafe_allow_html=True)
    match_clicked = st.button("⟶  Match My Resume")
    st.markdown("</div>", unsafe_allow_html=True)
    if match_clicked:
        if not uploaded_file:
            st.error("Please upload your resume to continue.")
        elif not jd_text.strip():
            st.error("Please paste a job description to continue.")
        else:
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[-1]) as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name 
            try:
                results = run_pipeline(tmp_path, jd_text)
                if results["success"]:
                    st.session_state.results = results["result"]
                    st.session_state.page = "results"
                    st.rerun()
                else:
                    st.error(results["message"])
            except Exception as e: 
                st.error("Failed to parse resume")
            finally:
                os.unlink(tmp_path)
    
    st.markdown("""
    <div class="footer-note">
        Supported formats: PDF · DOCX &nbsp;|&nbsp; Your data never leaves this session
    </div>
    """, unsafe_allow_html=True)

def results_page():
    results = st.session_state.get("results", {})
    if not results:
        st.session_state.page = "input"
        st.rerun()
        return

    final_score = results["final_score"]
    semantic_score = results["semantic_score"]
    keyword_score = results["keyword_score"]
    matched = results["matched_keywords"]
    unmatched = results["unmatched_keywords"]

    st.markdown("""
    <div class="main-wrap">
        <div class="hero">
            <div class="hero-eyebrow">Analysis Complete</div>
            <h1 class="hero-title">Your <span>Score</span></h1>
        </div>
    </div>
    """, unsafe_allow_html=True)

    score_color = "#64c878" if final_score >= 70 else "#c8a84b" if final_score >= 45 else "#c86450"
    st.markdown(f"""
    <div style="text-align:center; margin-bottom:48px;">
        <div style="font-family:'Syne',sans-serif; font-size:96px; font-weight:800; color:{score_color}; line-height:1;">
            {final_score}
        </div>
        <div style="font-size:11px; letter-spacing:0.2em; color:#6b6560; margin-top:8px;">ATS MATCH SCORE</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div style="text-align:center; padding:24px; border:1px solid #2a2520; background:#0f0d0b;">
            <div style="font-family:'Syne',sans-serif; font-size:36px; font-weight:700; color:#e8e4dc;">{semantic_score}</div>
            <div style="font-size:10px; letter-spacing:0.2em; color:#6b6560; margin-top:4px;">SEMANTIC SCORE</div>
            <div style="font-size:10px; color:#4a4540; margin-top:8px;">contextual relevance · 60% weight</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="text-align:center; padding:24px; border:1px solid #2a2520; background:#0f0d0b;">
            <div style="font-family:'Syne',sans-serif; font-size:36px; font-weight:700; color:#e8e4dc;">{keyword_score}</div>
            <div style="font-size:10px; letter-spacing:0.2em; color:#6b6560; margin-top:4px;">KEYWORD SCORE</div>
            <div style="font-size:10px; color:#4a4540; margin-top:8px;">keyword coverage · 40% weight</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:48px'></div>", unsafe_allow_html=True)

    # Gap analysis - group unmatched by priority
    critical = [kw for kw in unmatched if kw["priority"] == "critical"]
    moderate = [kw for kw in unmatched if kw["priority"] == "moderate"]
    nice_to_have = [kw for kw in unmatched if kw["priority"] == "nice_to_have"]

    st.markdown("""
    <div style="font-family:'DM Mono',monospace; font-size:10px; font-weight:500; letter-spacing:0.25em; color:#c8a84b; margin-bottom:20px;">
        GAP ANALYSIS — MISSING KEYWORDS
    </div>
    """, unsafe_allow_html=True)

    if critical:
        st.markdown(f"""
        <div style="margin-bottom:20px; padding:16px 20px; border-left:3px solid #c86450; background:rgba(200,100,80,0.05);">
            <div style="font-size:10px; letter-spacing:0.15em; color:#c86450; margin-bottom:10px;">CRITICAL — HIGH FREQUENCY IN JD</div>
            <div style="font-size:12px; color:#e8e4dc; line-height:2;">{' &nbsp;·&nbsp; '.join(kw['skill'] for kw in critical)}</div>
        </div>
        """, unsafe_allow_html=True)

    if moderate:
        st.markdown(f"""
        <div style="margin-bottom:20px; padding:16px 20px; border-left:3px solid #c8a84b; background:rgba(200,168,75,0.05);">
            <div style="font-size:10px; letter-spacing:0.15em; color:#c8a84b; margin-bottom:10px;">MODERATE — MENTIONED IN JD</div>
            <div style="font-size:12px; color:#e8e4dc; line-height:2;">{' &nbsp;·&nbsp; '.join(kw['skill'] for kw in moderate)}</div>
        </div>
        """, unsafe_allow_html=True)

    if nice_to_have:
        st.markdown(f"""
        <div style="margin-bottom:20px; padding:16px 20px; border-left:3px solid #4a4540; background:rgba(74,69,64,0.05);">
            <div style="font-size:10px; letter-spacing:0.15em; color:#4a4540; margin-bottom:10px;">NICE TO HAVE — LOW PRIORITY</div>
            <div style="font-size:12px; color:#6b6560; line-height:2;">{' &nbsp;·&nbsp; '.join(kw['skill'] for kw in nice_to_have)}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div style="font-family:'DM Mono',monospace; font-size:10px; font-weight:500; letter-spacing:0.25em; color:#c8a84b; margin-bottom:20px;">
        MATCHED KEYWORDS — {results['matched_count']} FOUND
    </div>
    <div style="padding:16px 20px; border-left:3px solid #64c878; background:rgba(100,200,120,0.05);">
        <div style="font-size:12px; color:#e8e4dc; line-height:2;">{' &nbsp;·&nbsp; '.join(kw['skill'] for kw in matched)}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:48px'></div>", unsafe_allow_html=True)
    if st.button("← Analyze Another Resume"):
        st.session_state.page = "input"
        st.session_state.results = None
        st.rerun()


if st.session_state.page == "input":
    input_page()
elif st.session_state.get("results"):
    results_page()