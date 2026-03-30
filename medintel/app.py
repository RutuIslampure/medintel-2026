"""
app.py - MedIntel: AI Clinical Decision Intelligence System
Run with: streamlit run app.py
"""
import streamlit as st

st.set_page_config(
    page_title="MedIntel AI",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&family=JetBrains+Mono:wght@400;600&display=swap');

:root {
    --bg-primary: #0a0e1a;
    --bg-card: #111827;
    --bg-card2: #1a2236;
    --accent-blue: #3b82f6;
    --accent-teal: #00d4aa;
    --accent-amber: #f5a623;
    --accent-red: #e8394d;
    --text-primary: #f0f4ff;
    --text-muted: #8892a4;
    --border: rgba(59,130,246,0.2);
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1321 0%, #111827 100%) !important;
    border-right: 1px solid var(--border);
}

/* Cards */
.medintel-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 16px;
    transition: border-color 0.2s;
}
.medintel-card:hover { border-color: var(--accent-blue); }

/* Metric boxes */
.metric-box {
    background: var(--bg-card2);
    border-radius: 12px;
    padding: 16px;
    text-align: center;
    border: 1px solid var(--border);
    margin: 4px;
}
.metric-box .metric-val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.8rem;
    font-weight: 600;
    line-height: 1;
}
.metric-box .metric-label {
    font-size: 0.72rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 4px;
}
.metric-normal  { color: var(--accent-teal); }
.metric-warning { color: var(--accent-amber); }
.metric-critical{ color: var(--accent-red); }

/* Risk badge */
.risk-badge {
    display: inline-block;
    padding: 6px 18px;
    border-radius: 999px;
    font-weight: 600;
    font-size: 0.9rem;
    letter-spacing: 0.05em;
}
.risk-high     { background: rgba(232,57,77,0.15);  color: #e8394d; border: 1px solid #e8394d; }
.risk-moderate { background: rgba(245,166,35,0.15); color: #f5a623; border: 1px solid #f5a623; }
.risk-low      { background: rgba(0,212,170,0.15);  color: #00d4aa; border: 1px solid #00d4aa; }

/* Logo header */
.logo-header {
    font-family: 'DM Serif Display', serif;
    font-size: 2rem;
    background: linear-gradient(135deg, #3b82f6, #00d4aa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0;
}
.logo-sub {
    font-size: 0.75rem;
    color: var(--text-muted);
    letter-spacing: 0.12em;
    text-transform: uppercase;
}

/* Pulse animation for high risk */
@keyframes pulse-red {
    0%, 100% { box-shadow: 0 0 0 0 rgba(232,57,77,0.4); }
    50%       { box-shadow: 0 0 0 8px rgba(232,57,77,0); }
}
.pulse { animation: pulse-red 1.8s infinite; }

/* Section headers */
.section-title {
    font-family: 'DM Serif Display', serif;
    font-size: 1.3rem;
    color: var(--text-primary);
    border-left: 3px solid var(--accent-blue);
    padding-left: 12px;
    margin: 16px 0 12px;
}

/* Streamlit overrides */
.stSelectbox > div > div { background: var(--bg-card2) !important; border-color: var(--border) !important; }
.stSlider > div { color: var(--text-primary); }
div[data-testid="metric-container"] { background: var(--bg-card2); border-radius: 10px; padding: 10px; }
.stButton > button {
    background: linear-gradient(135deg, #3b82f6, #1d4ed8) !important;
    color: white !important; border: none !important; border-radius: 10px !important;
    font-weight: 600 !important; padding: 0.5rem 1.5rem !important;
    transition: transform 0.15s !important;
}
.stButton > button:hover { transform: translateY(-1px) !important; }
.stTabs [data-baseweb="tab"] { background: transparent !important; color: var(--text-muted) !important; }
.stTabs [aria-selected="true"] { color: var(--accent-blue) !important; border-bottom: 2px solid var(--accent-blue) !important; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar navigation ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="logo-header">Med<span style="color:#3b82f6">Intel</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="logo-sub">AI Clinical Intelligence</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    page = st.radio(
        "Navigation",
        ["🏠 Dashboard", "👤 Patient Monitor", "🔮 What-If Simulator", "📊 Analytics", "ℹ️ About"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown(f"""
    <div style="font-size:0.72rem; color: var(--text-muted); line-height:1.8;">
    🏥 <b>PES University</b><br>
    Centre for Healthcare<br>Engineering & Learning<br><br>
    <span style="color:#00d4aa;">● System Online</span>
    </div>
    """, unsafe_allow_html=True)

# ── Route pages ────────────────────────────────────────────────────────────────
if page == "🏠 Dashboard":
    from pages.dashboard import show
    show()
elif page == "👤 Patient Monitor":
    from pages.patient_monitor import show
    show()
elif page == "🔮 What-If Simulator":
    from pages.whatif import show
    show()
elif page == "📊 Analytics":
    from pages.analytics import show
    show()
else:
    from pages.about import show
    show()
