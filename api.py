import os
import io
import sys
import pkgutil
import importlib
from flask import Flask, request, jsonify, redirect
from flask_httpauth import HTTPTokenAuth
from dotenv import load_dotenv
from flasgger import Swagger

# Load environment variables
load_dotenv()
API_KEY = os.getenv("PRAETOR_API_KEY")
if not API_KEY:
    raise RuntimeError("PRAETOR_API_KEY missing in .env")

# Initialize Flask, Swagger, and Auth
app = Flask(__name__)
swagger = Swagger(app, template_file='swagger.yaml')
auth = HTTPTokenAuth(scheme="ApiKey")

@auth.verify_token
def verify_token(token):
    return token == API_KEY

@app.route("/", methods=["GET"])
def home():
    return redirect("/apidocs/")

# Import brain and train_skill modules
import brain
import train_skill

# Ad-hoc command endpoint
@app.route('/command', methods=['POST'])
@auth.login_required
def command():
    data = request.get_json(force=True, silent=True)
    if not data or 'command' not in data:
        return jsonify(error="Provide JSON with a 'command' field"), 400

    buf, old_stdout = io.StringIO(), sys.stdout
    sys.stdout = buf
    try:
        brain.handle_command(data['command'])
    except Exception as e:
        sys.stdout = old_stdout
        return jsonify(error=str(e)), 500
    finally:
        sys.stdout = old_stdout

    return jsonify(response=buf.getvalue().splitlines())

# Teaching endpoint
@app.route('/teach', methods=['POST'])
@auth.login_required
def teach():
    data = request.get_json(force=True, silent=True)
    if not data or 'trigger' not in data or 'command' not in data:
        return jsonify(error="Provide JSON with 'trigger' and 'command' fields"), 400

    teach_input = f"teach '{data['trigger']}' runs '{data['command']}'"
    try:
        result = train_skill.run(teach_input)
    except Exception as e:
        return jsonify(error=f"Training failed: {e}"), 500

    return jsonify(result=result)

# List available skills triggers
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

# --- Dynamic skill loader --------------------------------------------------
skills = {}
from skills import __path__ as skills_path
for finder, name, ispkg in pkgutil.iter_modules(skills_path):
    if ispkg:
        try:
            module = importlib.import_module(f"skills.{name}.orchestrator")
        except ImportError:
            continue
    else:
        module = importlib.import_module(f"skills.{name}")
    if hasattr(module, "run"):
        skills[name] = module.run

# --- Intent endpoint -------------------------------------------------------
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
