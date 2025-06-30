import os
import io
import sys
import pkgutil
import importlib
from flask import Flask, request, jsonify
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

# Import brain and train_skill modules
import brain
import train_skill

# Command endpoint
@app.route('/command', methods=['POST'])
@auth.login_required
def command():
    """
    Handle an ad-hoc command via brain.handle_command
    ---
    post:
      summary: Execute a plain-text command
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                command:
                  type: string
              required:
                - command
      responses:
        200:
          description: Command output
          content:
            application/json:
              schema:
                type: object
                properties:
                  response:
                    type: array
                    items:
                      type: string
        400:
          description: Missing 'command' field
        401:
          description: Unauthorized
        500:
          description: Internal server error
    """
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

# Teach endpoint
@app.route('/teach', methods=['POST'])
@auth.login_required
def teach():
    """
    Teach a new trigger-command mapping via train_skill.run
    ---
    post:
      summary: Teach a new skill
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                trigger:
                  type: string
                command:
                  type: string
              required:
                - trigger
                - command
      responses:
        200:
          description: Training result
          content:
            application/json:
              schema:
                type: object
                properties:
                  result:
                    type: string
        400:
          description: Missing fields
        401:
          description: Unauthorized
        500:
          description: Training failed
    """
    data = request.get_json(force=True, silent=True)
    if not data or 'trigger' not in data or 'command' not in data:
        return jsonify(error="Provide JSON with 'trigger' and 'command' fields"), 400

    teach_input = f"teach '{data['trigger']}' runs '{data['command']}'"
    try:
        result = train_skill.run(teach_input)
    except Exception as e:
        return jsonify(error=f"Training failed: {e}"), 500

    return jsonify(result=result)

# List skills endpoint
@app.route('/skills', methods=['GET'])
@auth.login_required
def list_skills():
    """
    List all available skill triggers
    ---
    get:
      summary: List loaded commands
      responses:
        200:
          description: List of triggers
          content:
            application/json:
              schema:
                type: object
                properties:
                  skills:
                    type: array
                    items:
                      type: string
        401:
          description: Unauthorized
    """
    # Combine JSON/DB triggers and dynamic module-based skills
    json_trigs = sorted(brain.COMMANDS.keys()) if hasattr(brain, 'COMMANDS') else []
    module_trigs = []
    # dynamic import from skills/ if needed
    try:
        from skills import __path__ as skills_path
        for finder, name, ispkg in pkgutil.iter_modules(skills_path):
            module_trigs.append(name)
    except ImportError:
        pass

    all_skills = sorted(set(json_trigs + module_trigs))
    return jsonify(skills=all_skills)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
