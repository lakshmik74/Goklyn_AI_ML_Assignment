import streamlit as st
import yaml
<<<<<<< HEAD
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
=======
from siem_agent import detect_intent, load_playbooks


# -------------------------------------------------------
# PAGE CONFIGURATION
# -------------------------------------------------------
st.set_page_config(
    page_title="SIEM AI Agent",
    page_icon="🛡️",
    layout="wide"
)

# Custom styling
st.markdown("""
    <style>
        .title {font-size: 40px; font-weight: bold; color: #1f77b4;}
        .sub {font-size: 22px; color: #4f4f4f;}
        .intent-box {padding: 10px; border-radius: 8px; background: #e8f5e9; font-size: 20px;}
        .playbook-box {padding: 12px; border: 1px solid #cfcfcf; border-radius: 8px; background: #fafafa;}
    </style>
""", unsafe_allow_html=True)


# -------------------------------------------------------
# LOAD PLAYBOOKS
# -------------------------------------------------------
playbooks = load_playbooks()


# -------------------------------------------------------
# TITLE
# -------------------------------------------------------
st.markdown("<div class='title'>🛡️ SIEM AI Agent (Offline)</div>", unsafe_allow_html=True)
st.markdown("<div class='sub'>Analyze logs → Detect Intent → Recommend SOC Playbook</div>", unsafe_allow_html=True)
st.write("---")


# -------------------------------------------------------
# SIDEBAR MENU
# -------------------------------------------------------
st.sidebar.header("Options")
menu = st.sidebar.radio("Choose Mode:", ["Enter Log Manually", "Upload Log File", "Use Sample Logs"])


# -------------------------------------------------------
# MANUAL LOG INPUT
# -------------------------------------------------------
user_log = ""

if menu == "Enter Log Manually":
    user_log = st.text_area("📝 Enter a log message:", height=150)

elif menu == "Upload Log File":
    uploaded = st.file_uploader("📁 Upload a .txt log file")
    if uploaded:
        user_log = uploaded.read().decode("utf-8")
        st.code(user_log)

elif menu == "Use Sample Logs":
    try:
        with open("sample_logs.txt", "r") as f:
            samples = f.read().splitlines()
        sample_choice = st.selectbox("📌 Select a sample log:", samples)
        user_log = sample_choice
        st.code(sample_choice)
    except:
        st.error("sample_logs.txt not found.")


st.write("---")


# -------------------------------------------------------
# PROCESSING
# -------------------------------------------------------
if st.button("🔍 Analyze Log"):
    if not user_log.strip():
        st.warning("Please enter or upload a log.")
    else:
        # Detect intent using your offline agent
        intent = detect_intent(user_log)

        st.markdown("### 🔎 Detected Intent")
        st.markdown(
            f"<div class='intent-box'>Intent: <b>{intent}</b></div>",
            unsafe_allow_html=True
        )

        # Playbook mapping
        st.markdown("### 📘 Recommended Playbook")
        if intent in playbooks:
            pb = playbooks[intent]
            st.markdown("<div class='playbook-box'>", unsafe_allow_html=True)
            st.write(pb.get("steps", "No steps available"))
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.error("❌ No playbook found for this intent.")

        # Extra Info
        st.markdown("### 🧠 How the Agent Detected This Intent")
        st.info("""
        ⚙ This SIEM Agent uses:
        - Keyword-based offline classification  
        - Pattern matching  
        - Log context analysis  
        - Mapping rules from playbooks.yml  
        """)

st.write("---")
st.success("✅ SIEM Agent Ready. This app runs 100% offline — no API key required.")
>>>>>>> 979eef7 (Fixed paths for Streamlit deployment)
