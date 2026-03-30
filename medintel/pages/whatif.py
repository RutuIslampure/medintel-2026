"""pages/whatif.py - What-If Treatment Simulation"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from utils.helpers import (
    load_data, load_model, VITAL_RANGES, RISK_COLORS,
    predict_risk, vital_status, generate_health_story
)

def show():
    patients, readings = load_data()
    model, scaler, le, features, fi = load_model()

    st.markdown('<h1 style="font-family:\'DM Serif Display\',serif; font-size:2.2rem;">What-If Simulator</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color:#8892a4;">Virtually test treatment changes and see predicted risk impact before applying them</p>', unsafe_allow_html=True)

    # Patient selector
    patient_options = {f"{r['name']} (ID: {r['patient_id']})": r['patient_id'] for _, r in patients.iterrows()}
    selected_name = st.selectbox("Select Patient", list(patient_options.keys()))
    pid = patient_options[selected_name]

    patient = patients[patients["patient_id"] == pid].iloc[0]
    pat_readings = readings[readings["patient_id"] == pid].sort_values("reading_num")
    latest = pat_readings.iloc[-1]
    vital_keys = list(VITAL_RANGES.keys())
    current_vitals = {k: latest[k] for k in vital_keys}

    current_risk, current_proba = predict_risk(current_vitals, patient["age"], patient["gender"], model, scaler, le, features)

    st.markdown("---")
    st.markdown(f"""
    <div style="display:flex;gap:16px;align-items:center;margin-bottom:16px;">
      <div>
        <div style="font-size:0.75rem;color:#8892a4;text-transform:uppercase;">Patient</div>
        <div style="font-weight:600;">{patient['name']} · {patient['condition']}</div>
      </div>
      <div>
        <div style="font-size:0.75rem;color:#8892a4;text-transform:uppercase;">Current Risk</div>
        <div style="font-weight:700;color:{'#e8394d' if current_risk=='High' else '#f5a623' if current_risk=='Moderate' else '#00d4aa'};">{current_risk} ({latest['risk_score']:.0f}/100)</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    col_sliders, col_result = st.columns([1.2, 1])

    with col_sliders:
        st.markdown('<div class="section-title">🎛️ Adjust Vitals (Simulated Treatment)</div>', unsafe_allow_html=True)
        
        # Scenario presets
        preset = st.selectbox("Quick Scenario", [
            "Custom", "Oxygen Therapy", "Antihypertensive", "Fluid Resuscitation",
            "Fever Reduction", "Insulin Therapy"
        ])

        simulated = dict(current_vitals)

        if preset == "Oxygen Therapy":
            simulated["oxygen_saturation"] = min(100, current_vitals["oxygen_saturation"] + 6)
            simulated["respiratory_rate"] = max(12, current_vitals["respiratory_rate"] - 4)
            st.info("📋 Simulating: Supplemental O₂ administration")
        elif preset == "Antihypertensive":
            simulated["systolic_bp"] = max(90, current_vitals["systolic_bp"] - 25)
            simulated["diastolic_bp"] = max(60, current_vitals["diastolic_bp"] - 12)
            simulated["heart_rate"] = max(55, current_vitals["heart_rate"] - 10)
            st.info("📋 Simulating: Antihypertensive medication")
        elif preset == "Fluid Resuscitation":
            simulated["heart_rate"] = max(60, current_vitals["heart_rate"] - 15)
            simulated["systolic_bp"] = min(140, current_vitals["systolic_bp"] + 15)
            st.info("📋 Simulating: IV fluid bolus administration")
        elif preset == "Fever Reduction":
            simulated["temperature"] = max(36.5, current_vitals["temperature"] - 1.5)
            simulated["heart_rate"] = max(60, current_vitals["heart_rate"] - 8)
            st.info("📋 Simulating: Antipyretic therapy (Paracetamol)")
        elif preset == "Insulin Therapy":
            simulated["glucose"] = max(80, current_vitals["glucose"] - 100)
            st.info("📋 Simulating: Insulin administration")

        # Manual slider adjustments
        st.markdown("**Fine-tune individual vitals:**")
        cols = st.columns(2)
        for i, (key, info) in enumerate(VITAL_RANGES.items()):
            with cols[i % 2]:
                base = simulated[key]
                lo = info["min"] * 0.5
                hi = info["max"] * 1.8
                val = st.slider(
                    f"{info['label']} ({info['unit']})",
                    min_value=float(lo), max_value=float(hi),
                    value=float(round(base, 1)), step=0.5,
                    key=f"sim_{key}"
                )
                simulated[key] = val

    with col_result:
        st.markdown('<div class="section-title">📊 Simulation Result</div>', unsafe_allow_html=True)
        
        sim_risk, sim_proba = predict_risk(simulated, patient["age"], patient["gender"], model, scaler, le, features)
        
        current_score = latest["risk_score"]
        # Estimate simulated score from proba
        sim_score = sim_proba.get("High", 0) * 0.85 + sim_proba.get("Moderate", 0) * 0.45 + sim_proba.get("Low", 0) * 0.1
        sim_score = round(sim_score, 1)
        delta = sim_score - current_score
        arrow = "▼" if delta < 0 else "▲"
        delta_color = "#00d4aa" if delta < 0 else "#e8394d"

        risk_css_map = {"High":"risk-high","Moderate":"risk-moderate","Low":"risk-low"}

        st.markdown(f"""
        <div class="medintel-card">
          <div style="text-align:center;">
            <div style="font-size:0.8rem;color:#8892a4;text-transform:uppercase;letter-spacing:0.1em;">Before Treatment</div>
            <div style="font-family:'JetBrains Mono';font-size:3rem;color:{'#e8394d' if current_risk=='High' else '#f5a623' if current_risk=='Moderate' else '#00d4aa'};font-weight:700;">{current_score:.0f}</div>
            <span class="risk-badge {risk_css_map[current_risk]}">{current_risk} Risk</span>
          </div>
          <div style="text-align:center;margin:12px 0;font-size:1.5rem;">{arrow}</div>
          <div style="text-align:center;">
            <div style="font-size:0.8rem;color:#8892a4;text-transform:uppercase;letter-spacing:0.1em;">After Simulated Treatment</div>
            <div style="font-family:'JetBrains Mono';font-size:3rem;color:{'#e8394d' if sim_risk=='High' else '#f5a623' if sim_risk=='Moderate' else '#00d4aa'};font-weight:700;">{sim_score:.0f}</div>
            <span class="risk-badge {risk_css_map[sim_risk]}">{sim_risk} Risk</span>
          </div>
          <div style="text-align:center;margin-top:12px;">
            <span style="font-size:1.2rem;color:{delta_color};font-weight:700;">{arrow} {abs(delta):.1f} points {'reduction' if delta < 0 else 'increase'}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Probability comparison
        st.markdown('<div class="section-title">Risk Probability Comparison</div>', unsafe_allow_html=True)
        categories = ["Low", "Moderate", "High"]
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name="Current", x=categories,
            y=[current_proba.get(c, 0) for c in categories],
            marker_color=["#00d4aa","#f5a623","#e8394d"],
            opacity=0.5,
        ))
        fig.add_trace(go.Bar(
            name="Simulated", x=categories,
            y=[sim_proba.get(c, 0) for c in categories],
            marker_color=["#00d4aa","#f5a623","#e8394d"],
            opacity=1.0,
        ))
        fig.update_layout(
            paper_bgcolor="#111827", plot_bgcolor="#111827",
            barmode="group", height=220,
            margin=dict(l=10, r=10, t=10, b=30),
            font=dict(family="DM Sans", color="#f0f4ff"),
            yaxis=dict(gridcolor="#1a2236", title="%"),
            xaxis=dict(gridcolor="#1a2236"),
            legend=dict(bgcolor="#1a2236"),
        )
        st.plotly_chart(fig, use_container_width=True)

        # What changed
        st.markdown('<div class="section-title">Vital Changes Summary</div>', unsafe_allow_html=True)
        changes = []
        for key, info in VITAL_RANGES.items():
            diff = simulated[key] - current_vitals[key]
            if abs(diff) > 0.1:
                direction = "↑" if diff > 0 else "↓"
                color = "#00d4aa" if (
                    (diff < 0 and key in ["systolic_bp","heart_rate","glucose","respiratory_rate","wbc","temperature","creatinine"]) or
                    (diff > 0 and key in ["oxygen_saturation","hemoglobin"])
                ) else "#e8394d"
                changes.append(f"<span style='color:{color};'>{direction} {info['label']}: {current_vitals[key]:.1f} → {simulated[key]:.1f} {info['unit']}</span>")
        if changes:
            st.markdown("<br>".join(changes), unsafe_allow_html=True)
        else:
            st.info("No vital changes from baseline.")
