# skills_py/send_email.py

triggers = ["send report to me", "email me report"]

def run(user_input):
    # Extract subject & body or use defaults
    subject   = "Praetor Report"
    body      = "Here is your report."
    recipient = "nathanleffler@gmail.com"
    # Use single quotes so mail sees the whole string correctly
    cmd = f"echo '{body}' | mail -s '{subject}' {recipient}"
    return {"action": "system", "path_or_command": cmd}
