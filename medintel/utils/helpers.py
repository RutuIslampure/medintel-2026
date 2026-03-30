"""utils/helpers.py - Shared utilities for MedIntel"""
import pandas as pd
import numpy as np
import joblib
import streamlit as st

VITAL_RANGES = {
    "heart_rate":          {"min": 60,  "max": 100,  "unit": "bpm",   "label": "Heart Rate"},
    "systolic_bp":         {"min": 90,  "max": 140,  "unit": "mmHg",  "label": "Systolic BP"},
    "diastolic_bp":        {"min": 60,  "max": 90,   "unit": "mmHg",  "label": "Diastolic BP"},
    "temperature":         {"min": 36.1,"max": 37.2, "unit": "°C",    "label": "Temperature"},
    "oxygen_saturation":   {"min": 95,  "max": 100,  "unit": "%",     "label": "O₂ Saturation"},
    "respiratory_rate":    {"min": 12,  "max": 20,   "unit": "/min",  "label": "Respiratory Rate"},
    "glucose":             {"min": 70,  "max": 140,  "unit": "mg/dL", "label": "Blood Glucose"},
    "wbc":                 {"min": 4.0, "max": 11.0, "unit": "K/μL",  "label": "WBC Count"},
    "creatinine":          {"min": 0.6, "max": 1.2,  "unit": "mg/dL", "label": "Creatinine"},
    "hemoglobin":          {"min": 12.0,"max": 17.5, "unit": "g/dL",  "label": "Hemoglobin"},
}

RISK_COLORS = {
    "Low":      "#00d4aa",
    "Moderate": "#f5a623",
    "High":     "#e8394d",
}

RISK_ICONS = {
    "Low": "🟢",
    "Moderate": "🟡",
    "High": "🔴",
}

@st.cache_resource
def load_model():
    model    = joblib.load("models/risk_model.pkl")
    scaler   = joblib.load("models/scaler.pkl")
    le       = joblib.load("models/label_encoder.pkl")
    features = joblib.load("models/features.pkl")
    fi       = joblib.load("models/feature_importance.pkl")
    return model, scaler, le, features, fi

@st.cache_data
def load_data():
    patients = pd.read_csv("data/patients.csv")
    readings = pd.read_csv("data/readings.csv")
    return patients, readings

def predict_risk(vitals_dict, age, gender, model, scaler, le, features):
    """Predict risk for a single patient reading."""
    row = {**vitals_dict, "age": age, "gender_enc": int(gender == "Male")}
    X = np.array([[row[f] for f in features]])
    X_sc = scaler.transform(X)
    proba = model.predict_proba(X_sc)[0]
    pred_idx = np.argmax(proba)
    label = le.inverse_transform([pred_idx])[0]
    proba_dict = {le.inverse_transform([i])[0]: round(float(p)*100, 1) for i, p in enumerate(proba)}
    return label, proba_dict

def vital_status(key, value):
    """Returns 'normal', 'warning', or 'critical'"""
    r = VITAL_RANGES.get(key, {})
    lo, hi = r.get("min", 0), r.get("max", 9999)
    if value < lo * 0.85 or value > hi * 1.2:
        return "critical"
    elif value < lo or value > hi:
        return "warning"
    return "normal"

def generate_health_story(patient_row, latest_vitals, risk_label, proba_dict):
    """Generate a narrative health story for the patient."""
    name = patient_row["name"].split()[0]
    condition = patient_row["condition"]
    age = patient_row["age"]
    
    concerns = []
    positives = []
    
    for key, val in latest_vitals.items():
        if key not in VITAL_RANGES: continue
        status = vital_status(key, val)
        label = VITAL_RANGES[key]["label"]
        unit = VITAL_RANGES[key]["unit"]
        if status == "critical":
            concerns.append(f"**{label}** is critically abnormal at {val:.1f} {unit}")
        elif status == "warning":
            concerns.append(f"**{label}** is slightly outside normal range ({val:.1f} {unit})")
        else:
            positives.append(label)

    story = f"### 📖 Health Story: {name}\n\n"
    story += f"*{age}-year-old patient with {condition}*\n\n"
    
    if risk_label == "High":
        story += f"⚠️ **Immediate attention required.** {name}'s vitals indicate a **high-risk** state "
        story += f"with {proba_dict.get('High', 0):.0f}% probability of complications.\n\n"
    elif risk_label == "Moderate":
        story += f"🔶 **Monitoring advised.** {name}'s condition is **moderately concerning** "
        story += f"and warrants close observation.\n\n"
    else:
        story += f"✅ **Stable condition.** {name} appears to be in a **low-risk** state. "
        story += f"Continue routine monitoring.\n\n"
    
    if concerns:
        story += "**Areas of Concern:**\n"
        for c in concerns:
            story += f"- {c}\n"
        story += "\n"
    
    if positives:
        story += f"**Stable Vitals:** {', '.join(positives[:4])}\n\n"
    
    story += f"*Risk confidence: Low {proba_dict.get('Low',0):.0f}% | Moderate {proba_dict.get('Moderate',0):.0f}% | High {proba_dict.get('High',0):.0f}%*"
    return story
