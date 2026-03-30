"""pages/dashboard.py - Main overview dashboard"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.helpers import load_data, load_model, RISK_COLORS, RISK_ICONS, predict_risk, VITAL_RANGES

def show():
    st.markdown('<h1 style="font-family:\'DM Serif Display\',serif; font-size:2.2rem; margin-bottom:4px;">Command Center</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color:#8892a4; margin-top:0;">Real-time patient risk overview across all wards</p>', unsafe_allow_html=True)

    patients, readings = load_data()

    # Get latest reading per patient
    latest = readings.sort_values("reading_num").groupby("patient_id").last().reset_index()
    merged = latest.merge(patients, on="patient_id")

    # ── KPI Row ───────────────────────────────────────────────────────────────
    total = len(merged)
    high_risk = (merged["risk_label"] == "High").sum()
    mod_risk  = (merged["risk_label"] == "Moderate").sum()
    low_risk  = (merged["risk_label"] == "Low").sum()
    avg_risk  = merged["risk_score"].mean()

    c1, c2, c3, c4, c5 = st.columns(5)
    kpis = [
        (c1, "Total Patients",    str(total),         "#3b82f6", ""),
        (c2, "High Risk 🔴",      str(high_risk),      "#e8394d", "pulse" if high_risk > 5 else ""),
        (c3, "Moderate Risk 🟡",  str(mod_risk),       "#f5a623", ""),
        (c4, "Low Risk 🟢",       str(low_risk),       "#00d4aa", ""),
        (c5, "Avg Risk Score",    f"{avg_risk:.1f}",   "#a78bfa", ""),
    ]
    for col, label, val, color, cls in kpis:
        with col:
            st.markdown(f"""
            <div class="metric-box {cls}" style="border-color:{color}40;">
              <div class="metric-val" style="color:{color};">{val}</div>
              <div class="metric-label">{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts Row ────────────────────────────────────────────────────────────
    col_l, col_r = st.columns([1.2, 1])

    with col_l:
        st.markdown('<div class="section-title">Risk Score Distribution</div>', unsafe_allow_html=True)
        fig = px.histogram(
            merged, x="risk_score", nbins=25, color="risk_label",
            color_discrete_map=RISK_COLORS,
            template="plotly_dark",
            labels={"risk_score": "Risk Score", "count": "Patients"},
        )
        fig.update_layout(
            paper_bgcolor="#111827", plot_bgcolor="#111827",
            legend_title="Risk Level", height=280,
            margin=dict(l=10, r=10, t=10, b=30),
            font=dict(family="DM Sans"),
        )
        fig.update_xaxes(gridcolor="#1a2236")
        fig.update_yaxes(gridcolor="#1a2236")
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-title">By Condition</div>', unsafe_allow_html=True)
        cond_risk = merged.groupby(["condition", "risk_label"]).size().reset_index(name="count")
        fig2 = px.bar(
            cond_risk, x="condition", y="count", color="risk_label",
            color_discrete_map=RISK_COLORS, template="plotly_dark",
            labels={"count": "Patients", "condition": ""},
        )
        fig2.update_layout(
            paper_bgcolor="#111827", plot_bgcolor="#111827",
            height=280, margin=dict(l=10, r=10, t=10, b=30),
            font=dict(family="DM Sans"), legend_title="",
        )
        fig2.update_xaxes(gridcolor="#1a2236", tickangle=-20)
        fig2.update_yaxes(gridcolor="#1a2236")
        st.plotly_chart(fig2, use_container_width=True)

    # ── High-Risk Alerts ─────────────────────────────────────────────────────
    st.markdown('<div class="section-title">🚨 High-Risk Alerts</div>', unsafe_allow_html=True)
    high_df = merged[merged["risk_label"] == "High"].sort_values("risk_score", ascending=False).head(8)
    
    if high_df.empty:
        st.success("✅ No high-risk patients at this time.")
    else:
        for _, row in high_df.iterrows():
            col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1.5])
            with col1:
                st.markdown(f"**{row['name']}**  \n<span style='color:#8892a4;font-size:0.8rem;'>ID:{row['patient_id']} · {row['condition']}</span>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<span style='color:#8892a4;font-size:0.8rem;'>Age</span><br><b>{row['age']}</b>", unsafe_allow_html=True)
            with col3:
                st.markdown(f"<span style='color:#8892a4;font-size:0.8rem;'>O₂ Sat</span><br><b style='color:{'#e8394d' if row['oxygen_saturation']<95 else '#00d4aa'};'>{row['oxygen_saturation']:.1f}%</b>", unsafe_allow_html=True)
            with col4:
                st.markdown(f"<span style='color:#8892a4;font-size:0.8rem;'>HR</span><br><b style='color:{'#e8394d' if row['heart_rate']>100 else '#00d4aa'};'>{row['heart_rate']:.0f}</b>", unsafe_allow_html=True)
            with col5:
                score = row['risk_score']
                bar_color = "#e8394d" if score > 60 else "#f5a623"
                st.markdown(f"""
                <div style="background:#1a2236;border-radius:8px;padding:8px;text-align:center;">
                  <span style="font-family:'JetBrains Mono';font-size:1.2rem;color:{bar_color};font-weight:700;">{score:.0f}</span>
                  <span style="color:#8892a4;font-size:0.7rem;"> /100</span>
                </div>""", unsafe_allow_html=True)
            st.markdown('<div style="border-bottom:1px solid #1a2236;margin:4px 0;"></div>', unsafe_allow_html=True)

    # ── Patient Table ─────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">All Patients</div>', unsafe_allow_html=True)
    display = merged[["patient_id","name","age","gender","condition","risk_score","risk_label"]].copy()
    display.columns = ["ID","Name","Age","Gender","Condition","Risk Score","Risk Level"]
    
    def color_risk(val):
        c = {"High":"#e8394d","Moderate":"#f5a623","Low":"#00d4aa"}.get(val,"white")
        return f"color: {c}; font-weight: 600"
    
    st.dataframe(
        display.sort_values("Risk Score", ascending=False).style.applymap(color_risk, subset=["Risk Level"]),
        use_container_width=True, height=300,
    )
