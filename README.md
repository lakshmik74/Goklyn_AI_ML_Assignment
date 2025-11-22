# 🧠 Goklyn AI/ML Internship – Assignment Submission  
### **Candidate: Lakshmi Reddy (`lakshmik74`)**

This repository contains my complete submission for the **Goklyn AI/ML Internship Assignment**, covering all three required tasks:  
**Machine Learning Pipeline**, **SIEM AI Agent**, and **AI-based SIEM Enhancement Proposal**.

---

## 📂 Repository Structure

```
Goklyn_Assignment/
│
├── Task-1/
│   ├── ml_pipeline.py
│   ├── breast_cancer_xgb_model.joblib
│   ├── scaler.joblib
│   ├── confusion_matrix.png
│   ├── roc_curve.png
│   ├── shap_summary.png
│   ├── Task1_Report.pdf
│   └── Task1_Detailed_Report.pdf
│
├── Task-2/
│   ├── app.py
│   ├── playbooks.yml
│   ├── sample_logs.txt
│   └── requirements.txt
│
├── Task-3/
│   └── Task3_Proposal.pdf
│
└── requirements.txt
```

---

# ✅ Task 1 — Machine Learning Classification Pipeline

### ✨ Features
- Breast Cancer classification using 4 ML models  
- Models: Logistic Regression, Random Forest, Gradient Boosting, XGBoost  
- Hyperparameter tuning using **RandomizedSearchCV**  
- Evaluation metrics: Accuracy, Precision, Recall, F1 Score, ROC-AUC  
- Explainability using **SHAP**  
- Saves trained model + scaler (joblib)  
- Generates Confusion Matrix, ROC Curve, SHAP Summary Plot  

### ▶️ Run Task 1
```bash
pip install -r requirements.txt
python Task-1/ml_pipeline.py
```

---

# 🤖 Task 2 — Offline SIEM AI Agent

### ✨ Features
- Works 100% offline (no API key required)
- Detects intent from security logs
- Maps detected intent → SOC playbook actions
- YAML-based playbooks for modular automation
- Sample logs included for evaluator testing
- Clean interactive UI using Streamlit

### ▶️ Run Task 2
```bash
pip install -r requirements.txt
python Task-2/siem_agent.py
```

---

# 📄 Task 3 — Proposal: AI Agents for SIEM Threat Detection

### ✨ Contents
- 1-page proposal on how AI Agents improve SIEM detection
- Automates SOC workflows & incident triage
- Uses **20 SIEM rules** (as required)
- Includes both Standard + Enhanced proposal PDFs

---

# 🛠 Tech Stack

- Python  
- Scikit-learn  
- XGBoost  
- Pandas / NumPy  
- Matplotlib / Seaborn  
- SHAP  
- YAML  

---
