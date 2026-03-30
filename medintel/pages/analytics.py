"""pages/analytics.py - Hospital-wide analytics and insights"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from utils.helpers import load_data, load_model, RISK_COLORS, VITAL_RANGES

def show():
    patients, readings = load_data()
    model, scaler, le, features, fi = load_model()

    st.markdown('<h1 style="font-family:\'DM Serif Display\',serif; font-size:2.2rem;">Analytics</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color:#8892a4;">Population-level insights, risk heatmaps & model performance</p>', unsafe_allow_html=True)

    merged = readings.merge(patients, on="patient_id")

    tab1, tab2, tab3 = st.tabs(["🌡️ Population Risk", "🗺️ Risk Heatmap", "🔬 Model Insights"])

    with tab1:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="section-title">Risk Trend — All Patients</div>', unsafe_allow_html=True)
            trend = merged.groupby("reading_num")["risk_score"].agg(["mean","min","max"]).reset_index()
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=trend["reading_num"], y=trend["max"],
                fill=None, mode="lines", line_color="rgba(232,57,77,0.2)", name="Max",
            ))
            fig.add_trace(go.Scatter(
                x=trend["reading_num"], y=trend["min"],
                fill="tonexty", fillcolor="rgba(59,130,246,0.08)",
                mode="lines", line_color="rgba(59,130,246,0.2)", name="Min",
            ))
            fig.add_trace(go.Scatter(
                x=trend["reading_num"], y=trend["mean"],
                mode="lines+markers", line=dict(color="#3b82f6", width=3),
                marker=dict(size=6), name="Mean Risk",
            ))
            fig.update_layout(
                paper_bgcolor="#111827", plot_bgcolor="#111827",
                height=280, margin=dict(l=10,r=10,t=10,b=30),
                font=dict(family="DM Sans",color="#f0f4ff"),
                yaxis=dict(gridcolor="#1a2236"),
                xaxis=dict(gridcolor="#1a2236"),
                legend=dict(bgcolor="#1a2236"),
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown('<div class="section-title">Risk by Age Group</div>', unsafe_allow_html=True)
            latest = readings.sort_values("reading_num").groupby("patient_id").last().reset_index()
            merged_latest = latest.merge(patients, on="patient_id")
            merged_latest["age_group"] = pd.cut(merged_latest["age"], bins=[20,40,55,65,100], labels=["20-40","40-55","55-65","65+"])
            age_risk = merged_latest.groupby(["age_group","risk_label"]).size().reset_index(name="count")
            fig2 = px.bar(age_risk, x="age_group", y="count", color="risk_label",
                color_discrete_map=RISK_COLORS, template="plotly_dark",
                labels={"count":"Patients","age_group":"Age Group"},
            )
            fig2.update_layout(
                paper_bgcolor="#111827",plot_bgcolor="#111827",
                height=280, margin=dict(l=10,r=10,t=10,b=30),
                font=dict(family="DM Sans",color="#f0f4ff"),
                xaxis=dict(gridcolor="#1a2236"), yaxis=dict(gridcolor="#1a2236"),
                legend_title="",
            )
            st.plotly_chart(fig2, use_container_width=True)

        # Condition breakdown
        st.markdown('<div class="section-title">Average Risk Score by Condition</div>', unsafe_allow_html=True)
        cond_avg = merged_latest.groupby("condition")["risk_score"].mean().reset_index().sort_values("risk_score", ascending=False)
        colors = ["#e8394d" if v > 60 else "#f5a623" if v > 35 else "#00d4aa" for v in cond_avg["risk_score"]]
        fig3 = go.Figure(go.Bar(
            x=cond_avg["condition"], y=cond_avg["risk_score"],
            marker_color=colors,
            text=[f"{v:.1f}" for v in cond_avg["risk_score"]],
            textposition="outside",
        ))
        fig3.update_layout(
            paper_bgcolor="#111827", plot_bgcolor="#111827",
            height=280, margin=dict(l=10,r=10,t=10,b=30),
            font=dict(family="DM Sans",color="#f0f4ff"),
            yaxis=dict(gridcolor="#1a2236",range=[0,100]),
            xaxis=dict(gridcolor="#1a2236"),
        )
        st.plotly_chart(fig3, use_container_width=True)

    with tab2:
        st.markdown('<div class="section-title">🗺️ Hospital Risk Heatmap</div>', unsafe_allow_html=True)
        st.markdown("*Simulated ward layout — color intensity = average risk score*")

        latest = readings.sort_values("reading_num").groupby("patient_id").last().reset_index()
        merged_latest = latest.merge(patients, on="patient_id")

        # Simulate ward assignments
        np.random.seed(10)
        merged_latest["ward"] = np.random.choice(["ICU","Cardiology","Nephrology","General A","General B","Emergency"], len(merged_latest))
        merged_latest["bed"] = np.random.randint(1, 11, len(merged_latest))

        ward_stats = merged_latest.groupby("ward").agg(
            avg_risk=("risk_score","mean"),
            high_risk=("risk_label", lambda x: (x=="High").sum()),
            total=("patient_id","count")
        ).reset_index().sort_values("avg_risk", ascending=False)

        fig_heat = go.Figure(go.Bar(
            x=ward_stats["ward"],
            y=ward_stats["avg_risk"],
            marker=dict(
                color=ward_stats["avg_risk"],
                colorscale=[[0,"#00d4aa"],[0.5,"#f5a623"],[1,"#e8394d"]],
                showscale=True,
                colorbar=dict(title="Risk Score")
            ),
            text=[f"⚠ {r} high-risk" for r in ward_stats["high_risk"]],
            textposition="outside",
        ))
        fig_heat.update_layout(
            paper_bgcolor="#111827", plot_bgcolor="#111827",
            height=320, margin=dict(l=10,r=10,t=10,b=30),
            font=dict(family="DM Sans",color="#f0f4ff"),
            yaxis=dict(gridcolor="#1a2236", range=[0,100], title="Avg Risk Score"),
            xaxis=dict(gridcolor="#1a2236"),
        )
        st.plotly_chart(fig_heat, use_container_width=True)

        # Ward table
        st.dataframe(
            ward_stats.rename(columns={"ward":"Ward","avg_risk":"Avg Risk","high_risk":"High-Risk Patients","total":"Total Patients"}).round(1),
            use_container_width=True, hide_index=True
        )

    with tab3:
        st.markdown('<div class="section-title">Model Feature Importance</div>', unsafe_allow_html=True)
        fig_fi = go.Figure(go.Bar(
            x=fi["importance"],
            y=[VITAL_RANGES.get(f,{}).get("label",f) for f in fi["feature"]],
            orientation="h",
            marker_color=px.colors.sequential.Blues_r[:len(fi)],
            text=[f"{v:.3f}" for v in fi["importance"]],
            textposition="outside",
        ))
        fig_fi.update_layout(
            paper_bgcolor="#111827", plot_bgcolor="#111827",
            height=380, margin=dict(l=20,r=60,t=10,b=30),
            font=dict(family="DM Sans",color="#f0f4ff"),
            xaxis=dict(gridcolor="#1a2236",title="Importance"),
            yaxis=dict(gridcolor="#1a2236"),
        )
        st.plotly_chart(fig_fi, use_container_width=True)

        st.markdown('<div class="section-title">Risk Score Distribution (Violin)</div>', unsafe_allow_html=True)
        latest2 = readings.sort_values("reading_num").groupby("patient_id").last().reset_index()
        m2 = latest2.merge(patients, on="patient_id")
        fig_v = px.violin(m2, x="condition", y="risk_score", color="risk_label",
            color_discrete_map=RISK_COLORS, template="plotly_dark", box=True,
            labels={"risk_score":"Risk Score","condition":"Condition"},
        )
        fig_v.update_layout(
            paper_bgcolor="#111827", plot_bgcolor="#111827",
            height=300, margin=dict(l=10,r=10,t=10,b=30),
            font=dict(family="DM Sans",color="#f0f4ff"),
            xaxis=dict(gridcolor="#1a2236",tickangle=-20), yaxis=dict(gridcolor="#1a2236"),
            legend_title="",
        )
        st.plotly_chart(fig_v, use_container_width=True)
