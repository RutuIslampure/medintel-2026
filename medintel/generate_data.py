"""
generate_data.py - Generates synthetic patient dataset for MedIntel
Run once: python generate_data.py
"""
import pandas as pd
import numpy as np
from faker import Faker
import random

fake = Faker()
np.random.seed(42)
random.seed(42)

N_PATIENTS = 200
N_READINGS_PER_PATIENT = 10  # time series readings

conditions = ["Hypertension", "Diabetes", "Heart Failure", "COPD", "Sepsis", "Cancer", "Healthy"]
condition_weights = [0.23, 0.23, 0.15, 0.10, 0.10, 0.06, 0.13]

def generate_vitals(condition, severity=0.5):
    """Generate vitals based on condition and severity (0=mild, 1=critical)"""
    base = {
        "heart_rate": 75,
        "systolic_bp": 120,
        "diastolic_bp": 80,
        "temperature": 36.8,
        "oxygen_saturation": 98,
        "respiratory_rate": 16,
        "glucose": 95,
        "wbc": 7.5,
        "creatinine": 1.0,
        "hemoglobin": 14.0,
    }

    noise = lambda s: np.random.normal(0, s)

    if condition == "Hypertension":
        base["systolic_bp"] += 20 + severity * 40
        base["diastolic_bp"] += 10 + severity * 20
        base["heart_rate"] += severity * 15
    elif condition == "Diabetes":
        base["glucose"] += 50 + severity * 150
        base["creatinine"] += severity * 1.5
    elif condition == "Heart Failure":
        base["heart_rate"] += 10 + severity * 30
        base["oxygen_saturation"] -= severity * 12
        base["respiratory_rate"] += severity * 8
    elif condition == "COPD":
        base["oxygen_saturation"] -= 5 + severity * 15
        base["respiratory_rate"] += 4 + severity * 10
    elif condition == "Sepsis":
        base["temperature"] += 1.5 + severity * 2.5
        base["heart_rate"] += 20 + severity * 40
        base["wbc"] += 5 + severity * 15
        base["oxygen_saturation"] -= severity * 10
        base["respiratory_rate"] += 8 + severity * 12
    elif condition == "Cancer":
        base["hemoglobin"] -= 2 + severity * 5
        base["wbc"] -= 1.5 + severity * 3
        base["heart_rate"] += 10 + severity * 25
        base["temperature"] += severity * 2.0
        base["oxygen_saturation"] -= severity * 10
        base["creatinine"] += severity * 1.8
        base["systolic_bp"] -= severity * 15    
    
    # Add realistic noise
    vitals = {k: max(0, v + noise(v * 0.03)) for k, v in base.items()}
    vitals["oxygen_saturation"] = min(100, vitals["oxygen_saturation"])
    return vitals

def compute_risk(vitals, condition):
    """Compute risk score 0-100"""
    score = 0
    if vitals["heart_rate"] > 100: score += 15
    if vitals["heart_rate"] < 50: score += 20
    if vitals["systolic_bp"] > 160: score += 15
    if vitals["systolic_bp"] < 90: score += 25
    if vitals["oxygen_saturation"] < 95: score += 20
    if vitals["oxygen_saturation"] < 90: score += 20
    if vitals["temperature"] > 38.5: score += 10
    if vitals["respiratory_rate"] > 25: score += 15
    if vitals["glucose"] > 250: score += 10
    if vitals["wbc"] > 12 or vitals["wbc"] < 4: score += 10
    if vitals["creatinine"] > 2.0: score += 10
    if condition == "Sepsis": score += 15
    if condition == "Cancer": score += 8
    if condition == "Healthy": score = max(0, score - 20)
    return min(100, score + np.random.normal(0, 3))

records = []
patients = []

for pid in range(1, N_PATIENTS + 1):
    age = random.randint(25, 85)
    gender = random.choice(["Male", "Female"])
    condition = random.choices(conditions, weights=condition_weights)[0]
    name = fake.name()
    
    patients.append({
        "patient_id": pid,
        "name": name,
        "age": age,
        "gender": gender,
        "condition": condition,
        "admission_date": fake.date_between(start_date="-30d", end_date="today").isoformat()
    })
    
    base_severity = random.uniform(0.1, 0.9)
    for t in range(N_READINGS_PER_PATIENT):
        # Severity evolves over time (can improve or worsen)
        severity = np.clip(base_severity + np.random.normal(0, 0.05) * t, 0, 1)
        vitals = generate_vitals(condition, severity)
        risk = compute_risk(vitals, condition)
        
        records.append({
            "patient_id": pid,
            "reading_num": t + 1,
            "timestamp": f"2026-03-{random.randint(1,10):02d} {random.randint(0,23):02d}:{random.randint(0,59):02d}",
            "risk_score": round(risk, 1),
            "risk_label": "High" if risk > 60 else ("Moderate" if risk > 35 else "Low"),
            **{k: round(v, 2) for k, v in vitals.items()}
        })

df_patients = pd.DataFrame(patients)
df_readings = pd.DataFrame(records)

df_patients.to_csv("data/patients.csv", index=False)
df_readings.to_csv("data/readings.csv", index=False)

# Merge for ML training
df_ml = df_readings.merge(df_patients[["patient_id","age","gender","condition"]], on="patient_id")
df_ml["gender_enc"] = (df_ml["gender"] == "Male").astype(int)
df_ml.to_csv("data/ml_dataset.csv", index=False)

print(f"✅ Generated {len(df_patients)} patients and {len(df_readings)} readings.")
print(f"   Risk distribution:\n{df_readings['risk_label'].value_counts()}")
