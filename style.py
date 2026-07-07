import streamlit as st


def inject_custom_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=IBM+Plex+Sans:wght@600;700&display=swap');
    
        :root {
            --navy-950: #0b1f33;
            --navy-900: #0f2942;
            --navy-800: #1c3a5e;
            --blue-600: #2563eb;
            --blue-500: #3b82f6;
            --slate-900: #1e293b;
            --slate-600: #475569;
            --slate-400: #94a3b8;
            --slate-200: #e2e8f0;
            --bg: #f4f6f9;
            --surface: #ffffff;
            --border: #dde3ea;
            --success: #15803d;   --success-bg: #ecfdf5;  --success-border: #10b981;
            --warning: #b45309;   --warning-bg: #fffbeb;  --warning-border: #f59e0b;
            --danger:  #b91c1c;   --danger-bg:  #fef2f2;  --danger-border:  #ef4444;
            --info:    #1d4ed8;   --info-bg:    #eff6ff;  --info-border:    #3b82f6;
            --radius: 10px;
        }
    
        /* ── Base ─────────────────────────────────────────────────────── */
        [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {
            font-family: 'Inter', -apple-system, sans-serif;
        }
        [data-testid="stAppViewContainer"] { background-color: var(--bg); }
        [data-testid="stHeader"] { background-color: transparent; }
        .block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1200px; }
        footer { visibility: hidden; }
    
        h1, h2, h3 { font-family: 'IBM Plex Sans', sans-serif; color: var(--navy-900) !important; letter-spacing: -0.01em; }
        h1 { font-weight: 700; border-bottom: 3px solid var(--blue-600); padding-bottom: .5rem; margin-bottom: 1.25rem; }
        h2, h3 { font-weight: 600; color: var(--navy-800) !important; }
        hr { border-color: var(--border) !important; margin: 1.5rem 0 !important; }
    
        [data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"] li,
        [data-testid="stAppViewContainer"] label {
            color: var(--slate-900) !important;
        }
    
        /* ── Sidebar ──────────────────────────────────────────────────── */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, var(--navy-900), var(--navy-950));
        }
        [data-testid="stSidebar"] * { color: #e6edf5; }
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] label *,
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] li {
            color: #e6edf5 !important;
        }
        [data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.12) !important; }
        [data-testid="stSidebar"] input[type="radio"] { accent-color: var(--blue-500); }
    
        .sidebar-brand { display: flex; align-items: center; gap: .75rem; padding: .25rem 0 .75rem 0; }
        .sidebar-brand-icon {
            width: 44px; height: 44px; border-radius: 10px;
            background: rgba(59,130,246,0.18); border: 1px solid rgba(59,130,246,0.35);
            display: flex; align-items: center; justify-content: center; font-size: 1.4rem; flex-shrink: 0;
        }
        .sidebar-brand-title { font-family: 'IBM Plex Sans', sans-serif; font-weight: 700; font-size: 1.02rem; color: #fff; line-height: 1.2; }
        .sidebar-brand-sub { font-size: .75rem; color: #9fb3c8; letter-spacing: .03em; }
    
        [data-testid="stSidebar"] label:has(input[type="radio"]) {
            border-radius: 8px; padding: .55rem .7rem; transition: background-color .15s ease;
        }
        [data-testid="stSidebar"] label:has(input[type="radio"]):hover { background-color: rgba(255,255,255,0.06); }
        [data-testid="stSidebar"] label:has(input:checked) {
            background-color: rgba(59,130,246,0.16);
            border-left: 3px solid var(--blue-500);
            font-weight: 600;
        }
    
        /* ── Métricas (KPIs) ──────────────────────────────────────────── */
        [data-testid="stMetric"] {
            background: var(--surface);
            border: 1px solid var(--border);
            border-left: 4px solid var(--blue-600);
            border-radius: var(--radius);
            padding: 1rem 1.25rem;
            box-shadow: 0 1px 2px rgba(15,23,42,0.05);
        }
        [data-testid="stMetricValue"] { color: var(--navy-900); font-family: 'IBM Plex Sans', sans-serif; font-weight: 700; }
        [data-testid="stMetricLabel"] { color: var(--slate-600); text-transform: uppercase; letter-spacing: .04em; font-size: .78rem; font-weight: 600; }
    
        /* ── Botões ───────────────────────────────────────────────────── */
        .stButton > button, [data-testid="stFormSubmitButton"] button {
            border-radius: 8px; font-weight: 600; border: 1px solid var(--border);
            margin-top: 0.35rem;
            transition: filter .15s ease, background-color .15s ease;
        }
        .stButton > button[kind="primary"], [data-testid="stFormSubmitButton"] button[kind="primary"] {
            background-color: var(--blue-600); border-color: var(--blue-600);
        }
        .stButton > button[kind="primary"]:hover, [data-testid="stFormSubmitButton"] button[kind="primary"]:hover {
            filter: brightness(0.92);
        }
        .stButton > button[kind="secondary"]:hover { background-color: var(--slate-200); }
    
        /* ── Formulários, expanders, tabelas ──────────────────────────── */
        [data-testid="stForm"] {
            background: var(--surface); border: 1px solid var(--border);
            border-radius: var(--radius); padding: 1.5rem 1.5rem .5rem;
            box-shadow: 0 1px 3px rgba(15,23,42,0.04);
        }
        [data-testid="stExpander"] { border: 1px solid var(--border); border-radius: var(--radius); background: var(--surface); }
        [data-testid="stDataFrame"] { border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; }
    
        .stTextInput input, .stNumberInput input, .stDateInput input, .stTextArea textarea,
        .stSelectbox div[data-baseweb="select"] > div {
            border-radius: 8px !important; border-color: var(--border) !important;
        }
        .stTextInput input:focus, .stNumberInput input:focus, .stDateInput input:focus, .stTextArea textarea:focus {
            border-color: var(--blue-500) !important; box-shadow: 0 0 0 1px var(--blue-500) !important;
        }
    
        /* ── Alertas (success/info/warning/error) ────────────────────── */
        [data-testid="stAlert"], .stAlert { border-radius: var(--radius) !important; border: 1px solid var(--border); }
    </style>
    """, unsafe_allow_html=True)
