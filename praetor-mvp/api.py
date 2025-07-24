import os
import io
import sys
import pkgutil
import importlib
from flask import Flask, request, jsonify, redirect
from flask_httpauth import HTTPTokenAuth
from flask_cors import CORS
from dotenv import load_dotenv
from flasgger import Swagger


# Load environment variables
load_dotenv()
API_KEY = os.getenv("PRAETOR_API_KEY")
if not API_KEY:
    raise RuntimeError("PRAETOR_API_KEY missing in .env")

# Initialize Flask, Swagger, Auth, and CORS
app = Flask(__name__)
swagger = Swagger(app, template_file='swagger.yaml')
auth = HTTPTokenAuth(scheme="ApiKey")
CORS(app)

@auth.verify_token
def verify_token(token):
    return token == API_KEY

@app.route("/", methods=["GET"])
def home():
    return redirect("/apidocs/")

# Import core logic
import brain
import train_skill

# Route: Universal chat endpoint for web interface
@app.route("/api/praetor/chat", methods=["POST"])
@auth.login_required
def praetor_chat():
    data = request.get_json(force=True, silent=True)
    user_input = data.get("message", "")

    if not user_input:
        return jsonify(error="No message provided"), 400

    try:
        buffer, old_stdout = io.StringIO(), sys.stdout
        sys.stdout = buffer
        brain.handle_command(user_input)
        sys.stdout = old_stdout
        return jsonify(response=buffer.getvalue().strip())
    except Exception as e:
        sys.stdout = old_stdout
        return jsonify(error=str(e)), 500

# Route: Ad-hoc command
@app.route('/command', methods=['POST'])
@auth.login_required
def command():
    data = request.get_json(force=True, silent=True)
    if not data or 'command' not in data:
        return jsonify(error="Provide JSON with a 'command' field"), 400

    try:
        buffer, old_stdout = io.StringIO(), sys.stdout
        sys.stdout = buffer
        brain.handle_command(data['command'])
        sys.stdout = old_stdout
        return jsonify(response=buffer.getvalue().splitlines())
    except Exception as e:
        sys.stdout = old_stdout
        return jsonify(error=str(e)), 500

# Route: Teaching new skills
@app.route('/teach', methods=['POST'])
@auth.login_required
def teach():
    data = request.get_json(force=True, silent=True)
    if not data or 'trigger' not in data or 'command' not in data:
        return jsonify(error="Provide JSON with 'trigger' and 'command' fields"), 400

    try:
        teach_input = f"teach '{data['trigger']}' runs '{data['command']}'"
        result = train_skill.run(teach_input)
        return jsonify(result=result)
    except Exception as e:
        return jsonify(error=f"Training failed: {e}"), 500

# Route: List available skills
@app.route('/skills', methods=['GET'])
@auth.login_required
def list_skills():
    json_trigs = sorted(brain.COMMANDS.keys()) if hasattr(brain, 'COMMANDS') else []
    module_trigs = []
    try:
        from skills import __path__ as skills_path
        for finder, name, ispkg in pkgutil.iter_modules(skills_path):
            module_trigs.append(name)
    except ImportError:
        pass
    all_skills = sorted(set(json_trigs + module_trigs))
    return jsonify(skills=all_skills)

# Load dynamic skills
skills = {}
from skills import __path__ as skills_path
for finder, name, ispkg in pkgutil.iter_modules(skills_path):
    try:
        module_path = f"skills.{name}.orchestrator" if ispkg else f"skills.{name}"
        module = importlib.import_module(module_path)
        if hasattr(module, "run"):
            skills[name] = module.run
    except ImportError:
        continue

# Route: Intent-based API
@app.route("/api/intent", methods=["POST"])
@auth.login_required
def intent_endpoint():
    data = request.get_json(force=True, silent=True)
    if not data or "intent" not in data:
        return jsonify(error="Provide JSON with an 'intent' field"), 400

    intent = data["intent"]
    params = data.get("params", {})
    handler = skills.get(intent)

    if not handler:
        return jsonify(error=f"Unknown intent '{intent}'"), 404

    try:
        result = handler(**params)
        return jsonify(status="ok", intent=intent, response=result)
    except Exception as e:
        return jsonify(status="error", error=str(e)), 500
import socket

def find_open_port(start_port=5000, max_tries=10):
    port = start_port
    for _ in range(max_tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("", port))
                s.listen(1)
                return port
            except OSError:
                port += 1
    raise RuntimeError("No open ports found in range.")

if __name__ == "__main__":
    port = find_open_port(5000)
    with open(".flask_port", "w") as f:
        f.write(str(port))
    print(f"[🚀] Flask starting on port {port}")
    app.run(host="0.0.0.0", port=port)
