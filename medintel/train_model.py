"""
train_model.py - Trains the risk prediction ML model
Run once: python train_model.py
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import os

os.makedirs("models", exist_ok=True)

print("📊 Loading dataset...")
df = pd.read_csv("data/ml_dataset.csv")

FEATURES = [
    "age", "gender_enc", "heart_rate", "systolic_bp", "diastolic_bp",
    "temperature", "oxygen_saturation", "respiratory_rate",
    "glucose", "wbc", "creatinine", "hemoglobin"
]

X = df[FEATURES]
y = df["risk_label"]  # Low / Moderate / High

le = LabelEncoder()
y_enc = le.fit_transform(y)

X_train, X_test, y_train, y_test = train_test_split(X, y_enc, test_size=0.2, random_state=42, stratify=y_enc)

scaler = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X_test_sc = scaler.transform(X_test)

print("🤖 Training Gradient Boosting model...")
model = GradientBoostingClassifier(
    n_estimators=200, max_depth=5, learning_rate=0.1,
    min_samples_leaf=5, random_state=42
)
model.fit(X_train_sc, y_train)

scores = cross_val_score(model, X_train_sc, y_train, cv=5)
print(f"✅ CV Accuracy: {scores.mean():.3f} ± {scores.std():.3f}")

y_pred = model.predict(X_test_sc)
print("\n📋 Classification Report:")
print(classification_report(y_test, y_pred, target_names=le.classes_))

# Feature importance
importances = pd.DataFrame({
    "feature": FEATURES,
    "importance": model.feature_importances_
}).sort_values("importance", ascending=False)
print("\n🔍 Feature Importances:")
print(importances.to_string(index=False))

joblib.dump(model, "models/risk_model.pkl")
joblib.dump(scaler, "models/scaler.pkl")
joblib.dump(le, "models/label_encoder.pkl")
joblib.dump(FEATURES, "models/features.pkl")
joblib.dump(importances, "models/feature_importance.pkl")

print("\n✅ Model saved to models/")
