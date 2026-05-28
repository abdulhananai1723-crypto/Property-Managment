st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

* {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
    radial-gradient(circle at top left, rgba(99,102,241,0.18), transparent 30%),
    radial-gradient(circle at top right, rgba(236,72,153,0.15), transparent 30%),
    linear-gradient(135deg,#f8fafc 0%,#eef2ff 45%,#fdf2f8 100%);
}

/* MOBILE FIX */
.block-container {
    padding-left: 1rem !important;
    padding-right: 1rem !important;
    max-width: 100% !important;
}

section[data-testid="stSidebar"] {
    background: rgba(15,23,42,0.95);
    backdrop-filter: blur(20px);
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

.hero-card {
    background: linear-gradient(135deg,#2563eb,#7c3aed,#db2777);
    padding: 32px;
    border-radius: 28px;
    color: white;
    margin-bottom: 24px;
    box-shadow: 0 25px 60px rgba(79,70,229,0.35);
}

.hero-card h1 {
    color: white !important;
    font-size: 40px;
    font-weight: 800;
}

.hero-card p {
    color: #eef2ff !important;
    font-size: 17px;
}

.card {
    background: rgba(255,255,255,0.80);
    backdrop-filter: blur(22px);
    border-radius: 24px;
    padding: 22px;
    margin-bottom: 22px;
    box-shadow: 0 18px 45px rgba(15,23,42,0.08);
}

.stTextInput input,
.stNumberInput input,
textarea {
    border-radius: 16px !important;
    padding: 13px !important;
    border: 1px solid #cbd5e1 !important;
}

.stButton>button,
.stFormSubmitButton>button {
    background: linear-gradient(135deg,#2563eb,#7c3aed,#db2777);
    color: white !important;
    border: none;
    border-radius: 16px;
    padding: 13px 22px;
    font-weight: 800;
    width: 100%;
}

.stDownloadButton>button {
    background: linear-gradient(135deg,#0f172a,#334155);
    color: white !important;
    border: none;
    border-radius: 16px;
    padding: 13px 22px;
    font-weight: 800;
    width: 100%;
}

[data-testid="metric-container"] {
    background: rgba(255,255,255,0.85);
    border-radius: 22px;
    padding: 20px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.08);
}

.stDataFrame {
    overflow-x: auto !important;
}

#MainMenu,
footer,
header {
    visibility: hidden;
}

/* RESPONSIVE MOBILE */
@media (max-width: 768px) {

    .hero-card {
        padding: 22px !important;
        border-radius: 22px !important;
    }

    .hero-card h1 {
        font-size: 26px !important;
    }

    .hero-card p {
        font-size: 14px !important;
    }

    .card {
        padding: 16px !important;
        border-radius: 18px !important;
    }

    [data-testid="stHorizontalBlock"] {
        flex-direction: column !important;
        gap: 1rem !important;
    }

    [data-testid="column"] {
        width: 100% !important;
        flex: 1 1 100% !important;
    }

    .stTextInput input,
    .stNumberInput input,
    textarea {
        font-size: 16px !important;
    }

    .stButton>button,
    .stFormSubmitButton>button,
    .stDownloadButton>button {
        width: 100% !important;
    }

    img {
        width: 100% !important;
        height: auto !important;
        border-radius: 14px;
    }

    section[data-testid="stSidebar"] {
        width: 100% !important;
    }
}
</style>
""", unsafe_allow_html=True)
