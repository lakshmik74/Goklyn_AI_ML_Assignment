import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import shap
import joblib
import os
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, roc_curve
)
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from xgboost import XGBClassifier

# Load Dataset
data = load_breast_cancer()
X = pd.DataFrame(data.data, columns=data.feature_names)
y = pd.Series(data.target, name="target")

print("\nDataset Loaded:")
print(X.head())

# Train/Test Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print("\nTrain/Test Sizes:", X_train.shape, X_test.shape)

# Scaling
scaler = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X_test_sc = scaler.transform(X_test)

# Baseline Models
models = {
    "Logistic Regression": LogisticRegression(max_iter=5000),
    "Random Forest": RandomForestClassifier(n_estimators=300, random_state=42),
    "Gradient Boosting": GradientBoostingClassifier(random_state=42),
    "XGBoost": XGBClassifier(use_label_encoder=False, eval_metric="logloss", random_state=42)
}

results = {}

print("\nTraining baseline models...")

for name, model in models.items():
    model.fit(X_train_sc, y_train)
    preds = model.predict(X_test_sc)
    probs = model.predict_proba(X_test_sc)[:,1]

    results[name] = {
        "Accuracy": accuracy_score(y_test, preds),
        "Precision": precision_score(y_test, preds),
        "Recall": recall_score(y_test, preds),
        "F1": f1_score(y_test, preds),
        "ROC-AUC": roc_auc_score(y_test, probs)
    }

results_df = pd.DataFrame(results).T
print("\nBaseline Model Performance:\n")
print(results_df)

# Hyperparameter Tuning (XGBoost)
param_grid = {
    "n_estimators": [100, 300, 500],
    "learning_rate": [0.01, 0.05, 0.1],
    "max_depth": [3, 4, 5],
    "subsample": [0.6, 0.8, 1.0],
    "colsample_bytree": [0.6, 0.8, 1.0]
}

tuner = RandomizedSearchCV(
    models["XGBoost"],
    param_distributions=param_grid,
    n_iter=10,
    cv=3,
    scoring="roc_auc",
    n_jobs=-1,
    random_state=42
)

tuner.fit(X_train_sc, y_train)
best_model = tuner.best_estimator_

print("\nBest XGBoost Params:", tuner.best_params_)

# Final Evaluation
final_preds = best_model.predict(X_test_sc)
final_probs = best_model.predict_proba(X_test_sc)[:,1]

print("\nFinal Model Metrics:")
print("Accuracy: ", accuracy_score(y_test, final_preds))
print("Precision:", precision_score(y_test, final_preds))
print("Recall:   ", recall_score(y_test, final_preds))
print("F1 Score: ", f1_score(y_test, final_preds))
print("ROC-AUC: ", roc_auc_score(y_test, final_probs))

# Confusion Matrix
cm = confusion_matrix(y_test, final_preds)

plt.figure(figsize=(6,5))
sns.heatmap(cm, annot=True, cmap='Blues', fmt='d')
plt.title("Confusion Matrix")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.tight_layout()
plt.savefig("confusion_matrix.png")
plt.close()

# ROC Curve
fpr, tpr, _ = roc_curve(y_test, final_probs)

plt.figure(figsize=(7,6))
plt.plot(fpr, tpr, label=f"AUC = {roc_auc_score(y_test, final_probs):.3f}")
plt.plot([0,1], [0,1], 'k--')
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("ROC Curve")
plt.legend()
plt.tight_layout()
plt.savefig("roc_curve.png")
plt.close()

# SHAP Explainability
explainer = shap.TreeExplainer(best_model)
shap_values = explainer.shap_values(X_test_sc)

shap.summary_plot(shap_values, X_test, show=False)
plt.tight_layout()
plt.savefig("shap_summary.png")
plt.close()

# Save Model
joblib.dump(best_model, "breast_cancer_xgb_model.joblib")
joblib.dump(scaler, "scaler.joblib")

print("\nModel + Visuals saved successfully!")
