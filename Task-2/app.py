import streamlit as st
import yaml
import re
import os

STREAMLIT_PATH = os.path.dirname(__file__)
PLAYBOOK_PATH = os.path.join(STREAMLIT_PATH, "playbooks.yml")

# ------------------------- Load Playbooks -------------------------
def load_playbooks():
    try:
        with open(PLAYBOOK_PATH, "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        st.error(f"Failed to load playbooks.yml: {e}")
        return {}

# ------------------------- Intent Detection -------------------------
def detect_intent(log):
    log_lower = log.lower()

    patterns = {
        "failed login": r"failed login|authentication failed|invalid password",
        "brute force": r"multiple failed|too many attempts|bruteforce",
        "malware detected": r"malware|virus|trojan|worm detected",
        "sql injection": r"sql injection|select .* from|drop table",
        "port scan": r"nmap scan|port scan detected|reconnaissance",
        "ddos attack": r"ddos|flooding|traffic spike",
        "lateral movement": r"unauthorized lateral|moving inside network",
        "privilege escalation": r"escalated privileges|sudo abuse",
        "data exfiltration": r"exfiltration|large outbound traffic",
        "ransomware": r"ransomware|file encryption detected"
    }

    for intent, pattern in patterns.items():
        if re.search(pattern, log_lower):
            return intent

    return "unknown"

# ------------------------- UI -------------------------
def main():
    st.title("🔐 SIEM Offline AI Agent")
    st.write("Analyze security logs and generate automated SOC responses.")

    playbooks = load_playbooks()

    log_input = st.text_area("Enter security log message:", height=140)

    if st.button("Analyze Log"):
        if not log_input.strip():
            st.warning("Please enter a log message.")
            return

        intent = detect_intent(log_input)
        st.subheader("📌 Detected Intent:")
        st.success(intent)

        if intent in playbooks:
            st.subheader("📘 Recommended Playbook:")
            steps = playbooks[intent]["steps"]
            for i, step in enumerate(steps, 1):
                st.write(f"**{i}. {step}**")
        else:
            st.error("No playbook available for this intent.")

    st.divider()
    st.subheader("📂 Sample Logs Preview")
    st.code("""
[WARNING] Failed login attempt from 192.168.1.10  
[ALERT] Possible SQL Injection on /login  
[CRITICAL] Malware detected on endpoint-22  
""")

if __name__ == "__main__":
    main()
