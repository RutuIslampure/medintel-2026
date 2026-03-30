"""pages/about.py"""
import streamlit as st

def show():
    st.markdown("""
    <div style="max-width:760px;margin:0 auto;">
    
    <h1 style="font-family:'DM Serif Display',serif;font-size:2.8rem;background:linear-gradient(135deg,#3b82f6,#00d4aa);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;">MedIntel AI</h1>
    <p style="color:#8892a4;font-size:1.1rem;">AI Clinical Decision Intelligence System for Early Risk Detection</p>
    <p style="color:#8892a4;font-size:0.85rem;">PES University · HEAL-A-THON 2026 · Team MedIntel</p>
    
    <hr style="border-color:#1a2236;margin:24px 0;">
    
    <h3 style="font-family:'DM Serif Display',serif;color:#f0f4ff;">The Problem</h3>
    <p style="color:#c4cdd8;line-height:1.8;">
    Clinicians are inundated with raw numbers from EHRs and wearables. 
    This data overload causes critical early warning signs to be missed — leading to preventable ICU admissions, 
    higher costs, and worse patient outcomes.
    </p>
    
    <h3 style="font-family:'DM Serif Display',serif;color:#f0f4ff;margin-top:24px;">Our Solution</h3>
    <p style="color:#c4cdd8;line-height:1.8;">
    MedIntel transforms raw patient vitals into <b>actionable clinical intelligence</b> — 
    replacing manual data-hunting with instant, predictive, explainable alerts.
    </p>
    
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:24px 0;">
    """, unsafe_allow_html=True)

    features = [
        ("🤖 AI Risk Prediction", "Gradient Boosting ML model forecasts complications before they occur, trained on 2,000+ patient readings."),
        ("📖 Health Narratives", "Converts raw vitals into plain-English 'Patient Health Stories' for faster clinical decisions."),
        ("🔮 What-If Simulation", "Virtually test treatment changes — oxygen therapy, medications, fluids — and see predicted risk instantly."),
        ("🧠 Explainable AI", "SHAP-based explanations show exactly which vitals are driving the risk score."),
        ("🗺️ Risk Heatmaps", "Hospital-wide ward-level risk heatmaps for resource prioritization."),
        ("📊 Real-time Analytics", "Population-level trends, age-group breakdown, and condition risk profiling."),
    ]

    for title, desc in features:
        st.markdown(f"""
        <div class="medintel-card" style="margin-bottom:12px;">
          <div style="font-weight:600;font-size:1rem;margin-bottom:6px;">{title}</div>
          <div style="color:#8892a4;font-size:0.88rem;line-height:1.6;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <h3 style="font-family:'DM Serif Display',serif;color:#f0f4ff;margin-top:24px;">Tech Stack</h3>
    <div style="display:flex;flex-wrap:wrap;gap:10px;margin:12px 0;">
    """, unsafe_allow_html=True)
    
    for tech, color in [("Python","#3b82f6"),("Scikit-Learn","#f5a623"),("Streamlit","#e8394d"),
                        ("Plotly","#00d4aa"),("Pandas","#a78bfa"),("NumPy","#34d399"),("PostgreSQL","#60a5fa")]:
        st.markdown(f'<span style="background:{color}20;color:{color};border:1px solid {color}40;padding:4px 12px;border-radius:6px;font-size:0.82rem;font-weight:600;">{tech}</span>', unsafe_allow_html=True)

    st.markdown("""
    <h3 style="font-family:'DM Serif Display',serif;color:#f0f4ff;margin-top:24px;">Team MedIntel</h3>
    """, unsafe_allow_html=True)
    
    members = [
        ("Rutu Shivanand Islampure", "CSE-AIML, 5th Sem"),
        ("Asmita Satyappa Akkiwad", "CSE, 5th Sem"),
        ("Aptha K S", "CSE-DS, 5th Sem"),
        ("Navya D A", "CSE-AIML, 5th Sem"),
    ]
    for name, dept in members:
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid #1a2236;">
          <div style="width:36px;height:36px;background:linear-gradient(135deg,#3b82f6,#00d4aa);border-radius:50%;
          display:flex;align-items:center;justify-content:center;font-weight:700;font-size:0.9rem;">
            {name[0]}
          </div>
          <div>
            <div style="font-weight:600;">{name}</div>
            <div style="font-size:0.8rem;color:#8892a4;">{dept}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
