import yaml
import re
import os
from datetime import datetime
import streamlit as st

# -------- Locate paths for Streamlit Cloud --------
BASE_DIR = os.path.dirname(__file__)
PLAYBOOK_PATH = os.path.join(BASE_DIR, "playbooks.yml")
SAMPLE_LOGS_PATH = os.path.join(BASE_DIR, "sample_logs.txt")

# -------- Load playbooks --------
def load_playbooks():
    try:
        with open(PLAYBOOK_PATH, "r") as f:
            data = yaml.safe_load(f)
            # Ensure we always return a dict (yaml.safe_load may return None)
            if not isinstance(data, dict):
                return {}
            return data
    except Exception as e:
        st.error(f"Error loading playbooks.yml: {e}")
        return {}

# -------- Detect Intent --------
def detect_intent(log):
    log = log.lower()

    patterns = {
        "failed login": r"failed login|authentication failed|invalid password",
        "malware detected": r"malware|virus|trojan|infection",
        "suspicious ip": r"suspicious ip|unknown ip|connection from",
        "unauthorized access": r"unauthorized access|privilege misuse",
        "bruteforce attack": r"bruteforce|too many attempts|multiple failed",
    }

    for intent, pattern in patterns.items():
        if re.search(pattern, log):
            return intent

    return "unknown"

# -------- UI: Streamlit --------
def main():
    st.title("🔐 SIEM Offline AI Agent")
    st.write("Analyze security logs and generate automated SOC playbook actions.")

    playbooks = load_playbooks()

    # Use session state for the input so buttons can populate it during a live demo
    if 'log_input' not in st.session_state:
        st.session_state['log_input'] = ''
    log_input = st.text_area("Enter security log message:", height=150, key='log_input')

    # Analyze either when the button is clicked or when a demo button populated the input
    do_analyze = False
    if st.button("Analyze Log"):
        do_analyze = True
    if st.session_state.get('auto_analyze'):
        do_analyze = True
        # consume the flag so it doesn't loop
        st.session_state['auto_analyze'] = False

    if do_analyze:
        if not log_input.strip():
            st.warning("Please enter a log message.")
            return

        intent = detect_intent(log_input)

        st.subheader("📌 Detected Intent")
        st.success(intent)

        st.subheader("📘 Recommended Playbook")

        if intent in playbooks:
            steps = playbooks[intent]["steps"]
            for i, step in enumerate(steps, 1):
                st.write(f"**{i}. {step}**")
            # If this was an unauthorized-access inference and we have stored details, show them
            if intent == 'unauthorized access':
                details = st.session_state.get('inference_details') or {}
                if details:
                    st.subheader("🔎 Inference Details")
                    dtype = details.get('type', 'evidence')
                    st.write(f"**Method:** {dtype}")
                    for ev in details.get('evidence', []):
                        if ev.get('ip'):
                            st.write(f"- **IP:** `{ev.get('ip')}`")
                        if ev.get('failed'):
                            st.write(f"  - Failed line: `{ev.get('failed')}`")
                        if ev.get('successful'):
                            st.write(f"  - Successful line: `{ev.get('successful')}`")
        else:
            st.error("No playbook available for this intent.")

        # AI assistant removed — no external AI calls will be made.

    st.divider()
    st.subheader("📂 Sample Logs Preview")

    # Debug: show file paths so we know exactly which files the app is reading
    st.caption(f"Playbooks file: `{PLAYBOOK_PATH}`")
    st.caption(f"Sample logs file: `{SAMPLE_LOGS_PATH}`")

    # A manual reload button helps when editing the sample file externally
    if st.button("Reload sample logs"):
        # pressing the button triggers a rerun; we keep going to re-read below
        pass

    # Toggle to enable/disable the weak unauthorized-access heuristic
    enable_weak = st.checkbox("Enable weak unauthorized heuristic (match success+fail anywhere)", value=True, key='enable_weak_unauth')

    # Show options (intents) present in the sample logs file instead of raw content
    if os.path.exists(SAMPLE_LOGS_PATH):
        try:
            with open(SAMPLE_LOGS_PATH, "r", encoding="utf-8") as f:
                lines = [ln.strip() for ln in f.readlines() if ln.strip()]

            if not lines:
                st.info(f"`sample_logs.txt` is empty: {SAMPLE_LOGS_PATH}")
            else:
                # Map each line to a detected intent and show unique options only
                detected = [detect_intent(ln) for ln in lines]
                # Count detected intents
                from collections import Counter, defaultdict
                counts = Counter([d for d in detected if d != "unknown"])

                # preserve order of first appearance
                options = []
                for d in detected:
                    if d != "unknown" and d not in options:
                        options.append(d)

                # If there are many failed login entries, add 'bruteforce attack'
                if counts.get('failed login', 0) >= 3 and 'bruteforce attack' not in options:
                    options.append('bruteforce attack')

                # Infer unauthorized access: failed login(s) followed by successful login from same IP
                ip_re = re.compile(r"(\d{1,3}(?:\.\d{1,3}){3})")
                events_by_ip = defaultdict(list)
                for ln in lines:
                    ip_match = ip_re.search(ln)
                    if ip_match:
                        ip = ip_match.group(1)
                        intent_for_line = detect_intent(ln)
                        events_by_ip[ip].append(intent_for_line)

                unauthorized_detected = False
                for ip, events in events_by_ip.items():
                    # if a failed login appears before a successful login for same IP
                    if 'failed login' in events and 'successful login' not in events:
                        # can't infer successful login, continue
                        continue
                    if 'failed login' in events and 'successful login' in events:
                        # check order: failed login occurred before a successful login
                        first_failed = next((i for i,v in enumerate(events) if v=='failed login'), None)
                        first_success = next((i for i,v in enumerate(events) if v=='successful login'), None)
                        if first_failed is not None and first_success is not None and first_failed < first_success:
                            unauthorized_detected = True
                            break

                if unauthorized_detected and 'unauthorized access' not in options:
                    options.append('unauthorized access')

                # Note: no noisy heuristic here — 'unauthorized access' is inferred only
                # by a per-IP failed->successful sequence (strict detection) to avoid false positives.
                
                # Weak heuristic: if any line contains a successful-login phrase anywhere
                # and there are failed login(s) present, also include 'unauthorized access'.
                success_pattern = re.compile(r"successful login|login success|accepted password|logged in|successful authentication", re.I)
                success_present = any(success_pattern.search(ln) for ln in lines)
                if success_present and counts.get('failed login', 0) > 0 and 'unauthorized access' not in options:
                    options.append('unauthorized access')

                if options:
                    st.write("**Options available in sample logs:**")
                    # For demo: show each option as a button that inserts a matching sample
                    def _set_sample(val, details=None):
                        st.session_state['log_input'] = val or ''
                        st.session_state['auto_analyze'] = True
                        st.session_state['inference_details'] = details or {}

                    for i, opt in enumerate(options):
                        # find a sample line matching this intent
                        sample_line = next((ln for ln in lines if detect_intent(ln) == opt), None)
                        sample_details = None
                        # If this is a derived 'bruteforce attack' option and no direct sample
                        # exists, build a short multi-line failed-login example using the
                        # most common failed-login IP from the sample logs (or a fallback).
                        if sample_line is None and opt == 'bruteforce attack':
                            # determine most common failed-login IP
                            failed_ips = {ip: evts.count('failed login') for ip, evts in events_by_ip.items()}
                            if failed_ips:
                                ip = max(failed_ips, key=failed_ips.get)
                                attempts = failed_ips.get(ip, 3)
                            else:
                                ip = '192.168.1.100'
                                attempts = 3
                            # single-line timestamped summary for demo
                            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            sample_line = f"{now} Multiple failed login attempts detected from {ip} ({attempts} attempts)"

                        # Prepare details for 'unauthorized access' option when possible
                        if opt == 'unauthorized access':
                            # strict per-IP evidence
                            unauth_details = {'type': 'strict', 'evidence': []}
                            if unauthorized_detected:
                                for ip_addr, events in events_by_ip.items():
                                    if 'failed login' in events and 'successful login' in events:
                                        failed_line = next((ln for ln in lines if ip_addr in ln and detect_intent(ln) == 'failed login'), None)
                                        success_line = next((ln for ln in lines if ip_addr in ln and re.search(r"successful login|login success|accepted password|logged in|successful authentication", ln, re.I)), None)
                                        unauth_details['evidence'].append({'ip': ip_addr, 'failed': failed_line, 'successful': success_line})
                                if unauth_details['evidence']:
                                    sample_details = unauth_details

                            # weak heuristic evidence if enabled
                            if not sample_details and enable_weak:
                                failed_ln = next((ln for ln in lines if detect_intent(ln) == 'failed login'), None)
                                success_ln = next((ln for ln in lines if re.search(r"successful login|login success|accepted password|logged in|successful authentication", ln, re.I)), None)
                                if failed_ln or success_ln:
                                    sample_details = {'type': 'weak', 'evidence': [{'failed': failed_ln, 'successful': success_ln}]}

                            # synthesize a short sample line for demo if none available
                            if sample_line is None:
                                if sample_details and sample_details.get('evidence'):
                                    ev = sample_details['evidence'][0]
                                    if ev.get('ip'):
                                        sample_line = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Unauthorized access suspected for {ev.get('ip')}"
                                    else:
                                        f_failed = ev.get('failed') or 'failed login(s) found'
                                        f_succ = ev.get('successful') or 'successful login(s) found'
                                        sample_line = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Unauthorized access suspected: {f_failed} || {f_succ}"
                                else:
                                    sample_line = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Unauthorized access suspected"

                        btn_key = f"opt_{i}_{opt}"
                        st.button(opt, key=btn_key, on_click=_set_sample, args=(sample_line, sample_details))
                else:
                    st.info("No recognized intents in sample logs.\nYou can enable 'Show raw sample logs' below to inspect content.")

                # Allow user to reveal raw logs if needed
                if st.checkbox("Show raw sample logs"):
                    st.code("\n".join(lines))
        except Exception as e:
            st.error(f"Could not read sample_logs.txt: {e}")
    else:
        st.error(f"sample_logs.txt not found at: {SAMPLE_LOGS_PATH}")


if __name__ == "__main__":
    main()
