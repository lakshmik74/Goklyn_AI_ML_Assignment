import streamlit as st
import yaml
import joblib

# Load playbooks
with open("playbooks.yml", "r") as f:
    playbooks = yaml.safe_load(f)

# Load classifier & vectorizer
clf = joblib.load("intent_classifier.joblib")
vectorizer = joblib.load("intent_vectorizer.joblib")

st.title("🛡️ Offline SIEM AI Agent")
st.write("Provide a log line and the AI agent will detect the intent and map it to the correct SOC playbook.")

log_input = st.text_area("Enter Security Log Message:")

if st.button("Analyze"):
    if log_input.strip():
        X = vectorizer.transform([log_input])
        intent = clf.predict(X)[0]

        st.subheader("🔍 Detected Intent")
        st.success(intent)

        st.subheader("📘 Recommended Playbook")

        if intent in playbooks:
            steps = playbooks[intent]
            for step in steps:
                st.write(f"- {step}")
        else:
            st.warning("No playbook found for this intent.")
    else:
        st.error("Please enter a log message first.")
