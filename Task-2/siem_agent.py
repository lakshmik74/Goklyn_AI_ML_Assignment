import re
import yaml
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression


# Load Playbooks (YAML)
def load_playbooks():
    with open("playbooks.yml", "r") as f:
        return yaml.safe_load(f)


# Train simple ML classifier for intent detection
def train_intent_classifier():
    training_sentences = [
        "Multiple failed login attempts detected",
        "User failed to login several times",
        "Several failed login alerts found",
        "Malware detected on host computer",
        "Virus identified on system",
        "Suspicious malware threat detected",
        "Connection from suspicious IP address",
        "Unknown IP is scanning network ports",
        "Unauthorized access detected",
        "User accessing restricted files",
        "Bruteforce login attempts observed",
        "Many failed logins in a short time"
    ]

    labels = [
        "failed login",
        "failed login",
        "failed login",
        "malware detected",
        "malware detected",
        "malware detected",
        "suspicious ip",
        "suspicious ip",
        "unauthorized access",
        "unauthorized access",
        "bruteforce attack",
        "failed login",
    ]

    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(training_sentences)

    model = LogisticRegression()
    model.fit(X, labels)

    return vectorizer, model


# Parse Logs
def analyze_logs():
    with open("sample_logs.txt", "r") as f:
        logs = f.read()

    ip_pattern = r"(?:\d{1,3}\.){3}\d{1,3}"
    ips = re.findall(ip_pattern, logs)

    failed_logins = len(re.findall(r"failed login", logs, re.I))

    result = {"ips": ips, "failed_logins": failed_logins}
    return result


# MAIN LOOP
def main():
    print("🔐 Local SIEM-AI Agent Ready")
    print("Type 'exit' to quit.\n")

    playbooks = load_playbooks()
    vectorizer, model = train_intent_classifier()

    while True:
        user_input = input("Analyst> ")

        if user_input.lower() == "exit":
            print("Agent stopped.")
            break

        # Check for log analysis request
        if "log" in user_input.lower():
            result = analyze_logs()
            print("\n📊 Log Summary:")
            print(" - Failed logins:", result["failed_logins"])
            print(" - IPs found:", result["ips"], "\n")
            continue

        # Predict intent
        X = vectorizer.transform([user_input])
        intent = model.predict(X)[0]

        print("\n📌 Detected Intent:", intent)
        print("📘 Recommended Playbook:\n")

        if intent in playbooks:
            for step in playbooks[intent]:
                print(" -", step)
        else:
            print("No playbook available.")

        print("\n")
if __name__ == "__main__":
    main()
