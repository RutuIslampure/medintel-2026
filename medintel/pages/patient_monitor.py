"""pages/patient_monitor.py - Individual patient deep-dive with Health Story Timeline"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from utils.helpers import (
    load_data, load_model, VITAL_RANGES, RISK_COLORS,
    predict_risk, vital_status, generate_health_story
)

def show():
    patients, readings = load_data()
    model, scaler, le, features, fi = load_model()

    st.markdown('<h1 style="font-family:\'DM Serif Display\',serif; font-size:2.2rem;">Patient Monitor</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color:#8892a4;">Deep-dive into individual patient vitals, trends & AI health narrative</p>', unsafe_allow_html=True)

    # Patient selector
    col_sel, col_info = st.columns([1, 2])
    with col_sel:
        patient_options = {f"{r['name']} (ID: {r['patient_id']})": r['patient_id'] for _, r in patients.iterrows()}
        selected_name = st.selectbox("Select Patient", list(patient_options.keys()))
        pid = patient_options[selected_name]

    patient = patients[patients["patient_id"] == pid].iloc[0]
    pat_readings = readings[readings["patient_id"] == pid].sort_values("reading_num")
    latest = pat_readings.iloc[-1]

    vital_keys = [k for k in VITAL_RANGES.keys()]
    latest_vitals = {k: latest[k] for k in vital_keys}
    risk_label, proba_dict = predict_risk(latest_vitals, patient["age"], patient["gender"], model, scaler, le, features)

    with col_info:
        risk_css = {"High":"risk-high","Moderate":"risk-moderate","Low":"risk-low"}[risk_label]
        st.markdown(f"""
        <div class="medintel-card" style="margin-top:0;">
          <div style="display:flex;justify-content:space-between;align-items:start;">
            <div>
              <div style="font-family:'DM Serif Display',serif;font-size:1.4rem;">{patient['name']}</div>
              <div style="color:#8892a4;font-size:0.85rem;">
                {patient['age']} yrs · {patient['gender']} · {patient['condition']} · 
                Admitted: {patient['admission_date']}
              </div>
            </div>
            <span class="risk-badge {risk_css}">{risk_label} Risk</span>
          </div>
          <div style="margin-top:12px;display:flex;gap:16px;">
            <div style="text-align:center;">
              <div style="font-family:'JetBrains Mono';font-size:2rem;color:{'#e8394d' if risk_label=='High' else '#f5a623' if risk_label=='Moderate' else '#00d4aa'};">{latest['risk_score']:.0f}</div>
              <div style="font-size:0.72rem;color:#8892a4;">RISK SCORE</div>
            </div>
            {''.join([f'<div style="text-align:center;"><div style="font-size:1.1rem;font-weight:600;color:{RISK_COLORS[lbl]};">{p:.0f}%</div><div style="font-size:0.68rem;color:#8892a4;">{lbl.upper()}</div></div>' for lbl, p in proba_dict.items()])}
          </div>
        </div>
        """, unsafe_allow_html=True)

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Vitals Dashboard", "📖 Health Story", "📈 Trend Timeline", "🧠 AI Explainability"])

    # ── Tab 1: Vitals ─────────────────────────────────────────────────────────
    with tab1:
        st.markdown('<div class="section-title">Current Vitals</div>', unsafe_allow_html=True)
        cols = st.columns(5)
        for i, (key, info) in enumerate(VITAL_RANGES.items()):
            val = latest_vitals[key]
            status = vital_status(key, val)
            color = {"normal":"#00d4aa","warning":"#f5a623","critical":"#e8394d"}[status]
            icon  = {"normal":"✓","warning":"⚠","critical":"✕"}[status]
            with cols[i % 5]:
                st.markdown(f"""
                <div class="metric-box" style="border-color:{color}40;">
                  <div style="font-size:0.6rem;color:#8892a4;text-transform:uppercase;letter-spacing:0.1em;">{info['label']}</div>
                  <div class="metric-val" style="color:{color};font-size:1.5rem;">{val:.1f}</div>
                  <div style="font-size:0.65rem;color:#8892a4;">{info['unit']} {icon}</div>
                </div>""", unsafe_allow_html=True)

        # Normal ranges reference
        st.markdown('<div class="section-title">Vital Sign Status</div>', unsafe_allow_html=True)
        status_data = []
        for key, info in VITAL_RANGES.items():
            val = latest_vitals[key]
            status = vital_status(key, val)
            status_data.append({
                "Vital": info["label"], "Value": f"{val:.1f} {info['unit']}",
                "Normal Range": f"{info['min']} – {info['max']}",
                "Status": status.capitalize()
            })
        status_df = pd.DataFrame(status_data)
        def color_status(val):
            c = {"Normal":"#00d4aa","Warning":"#f5a623","Critical":"#e8394d"}.get(val, "white")
            return f"color:{c};font-weight:600"
        st.dataframe(
            status_df.style.applymap(color_status, subset=["Status"]),
            use_container_width=True, hide_index=True
        )

    # ── Tab 2: Health Story ───────────────────────────────────────────────────
    with tab2:
        story = generate_health_story(patient, latest_vitals, risk_label, proba_dict)
        st.markdown(f'<div class="medintel-card">{story}</div>', unsafe_allow_html=True)

        # Recommended actions
        st.markdown('<div class="section-title">📋 Recommended Actions</div>', unsafe_allow_html=True)
        actions = []
        if risk_label == "High":
            actions = [
                "🚨 **Immediate physician review** recommended",
                "📡 Increase vital sign monitoring frequency to every 15 minutes",
                "💊 Review current medication regimen for contraindications",
                "🏥 Consider ICU transfer assessment",
                "🩸 Order stat labs: CBC, BMP, Lactate",
            ]
        elif risk_label == "Moderate":
            actions = [
                "👁️ Increase monitoring to hourly vital checks",
                "💬 Physician notification within 2 hours",
                "📝 Document changes in patient condition",
                "🔬 Consider additional diagnostic workup",
            ]
        else:
            actions = [
                "✅ Continue standard monitoring protocol",
                "📅 Routine physician review at next scheduled visit",
                "📊 Maintain current treatment plan",
            ]
        for a in actions:
            st.markdown(f"- {a}")

    # ── Tab 3: Trend Timeline ─────────────────────────────────────────────────
    with tab3:
        st.markdown('<div class="section-title">Risk Score Over Time</div>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=pat_readings["reading_num"], y=pat_readings["risk_score"],
            mode="lines+markers", line=dict(color="#3b82f6", width=3),
            marker=dict(
                size=8,
                color=[RISK_COLORS.get(l, "#3b82f6") for l in pat_readings["risk_label"]],
                line=dict(width=2, color="#0a0e1a")
            ),
            fill="tozeroy", fillcolor="rgba(59,130,246,0.08)",
            name="Risk Score"
        ))
        fig.add_hline(y=60, line_dash="dot", line_color="#e8394d", annotation_text="High Risk Threshold")
        fig.add_hline(y=35, line_dash="dot", line_color="#f5a623", annotation_text="Moderate Threshold")
        fig.update_layout(
            paper_bgcolor="#111827", plot_bgcolor="#111827",
            height=300, margin=dict(l=10, r=10, t=10, b=30),
            xaxis_title="Reading #", yaxis_title="Risk Score",
            font=dict(family="DM Sans", color="#f0f4ff"),
            yaxis=dict(range=[0,105], gridcolor="#1a2236"),
            xaxis=dict(gridcolor="#1a2236"),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Multi-vital trends
        st.markdown('<div class="section-title">Vital Trend Comparison</div>', unsafe_allow_html=True)
        selected_vitals = st.multiselect(
            "Select vitals to plot",
            options=list(VITAL_RANGES.keys()),
            default=["heart_rate", "oxygen_saturation", "systolic_bp"],
            format_func=lambda k: VITAL_RANGES[k]["label"]
        )
        if selected_vitals:
            fig2 = go.Figure()
            palette = ["#3b82f6","#00d4aa","#f5a623","#a78bfa","#f472b6","#34d399"]
            for i, key in enumerate(selected_vitals):
                fig2.add_trace(go.Scatter(
                    x=pat_readings["reading_num"],
                    y=pat_readings[key],
                    name=VITAL_RANGES[key]["label"],
                    mode="lines+markers",
                    line=dict(color=palette[i % len(palette)], width=2),
                    marker=dict(size=5),
                ))
            fig2.update_layout(
                paper_bgcolor="#111827", plot_bgcolor="#111827",
                height=280, margin=dict(l=10, r=10, t=10, b=30),
                font=dict(family="DM Sans", color="#f0f4ff"),
                yaxis=dict(gridcolor="#1a2236"),
                xaxis=dict(gridcolor="#1a2236", title="Reading #"),
                legend=dict(bgcolor="#1a2236", bordercolor="#1f2d45"),
            )
            st.plotly_chart(fig2, use_container_width=True)

    # ── Tab 4: Explainability ─────────────────────────────────────────────────
    with tab4:
        st.markdown('<div class="section-title">🧠 Why is this patient at risk?</div>', unsafe_allow_html=True)
        st.markdown("*Feature importance shows which vitals are driving the AI's risk prediction.*")

        # Use model feature importances + current vital deviation from normal
        importance_df = fi.copy()
        
        # Compute deviation score for each vital
        deviation = {}
        for key in vital_keys:
            val = latest_vitals[key]
            r = VITAL_RANGES[key]
            mid = (r["min"] + r["max"]) / 2
            span = r["max"] - r["min"]
            dev = abs(val - mid) / (span / 2)
            deviation[key] = min(dev, 3.0)

        # Blend model importance with deviation
        importance_df["patient_impact"] = importance_df.apply(
            lambda row: row["importance"] * deviation.get(row["feature"], 0), axis=1
        )
        importance_df = importance_df[importance_df["feature"].isin(vital_keys)].sort_values("patient_impact", ascending=True)

        colors = []
        for _, row in importance_df.iterrows():
            key = row["feature"]
            status = vital_status(key, latest_vitals.get(key, 0))
            colors.append({"normal":"#00d4aa","warning":"#f5a623","critical":"#e8394d"}[status])

        fig3 = go.Figure(go.Bar(
            x=importance_df["patient_impact"],
            y=[VITAL_RANGES.get(f, {}).get("label", f) for f in importance_df["feature"]],
            orientation="h",
            marker_color=colors,
            text=[f"{v:.2f}" for v in importance_df["patient_impact"]],
            textposition="outside",
        ))
        fig3.update_layout(
            paper_bgcolor="#111827", plot_bgcolor="#111827",
            height=350, margin=dict(l=20, r=40, t=10, b=30),
            font=dict(family="DM Sans", color="#f0f4ff"),
            xaxis=dict(gridcolor="#1a2236", title="Impact Score"),
            yaxis=dict(gridcolor="#1a2236"),
        )
        st.plotly_chart(fig3, use_container_width=True)
        st.caption("🟢 Normal  🟡 Warning  🔴 Critical — bar length = model importance × deviation from normal")
