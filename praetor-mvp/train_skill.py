import subprocess
import datetime
import os
import sys
import traceback

def auto_push_to_git(skill_file_path):
    try:
        os.chdir(os.path.expanduser("~/praetor"))

        # Pull latest changes with rebase
        subprocess.run(["git", "pull", "--rebase", "origin", "main"], check=True)

        # Check if there are any staged or unstaged changes
        status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if status.stdout.strip():
            # Add the specific skill file
            subprocess.run(["git", "add", skill_file_path], check=True)

            # Commit with timestamp
            commit_msg = f"Skill update ({os.path.basename(skill_file_path)}): {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            subprocess.run(["git", "commit", "-m", commit_msg], check=True)

            # Push to main
            subprocess.run(["git", "push", "origin", "main"], check=True)

            print(f"✅ Git updated: {commit_msg}")
        else:
            print("🟢 No changes detected. Git not updated.")

    except subprocess.CalledProcessError as e:
        print(f"❌ Git operation failed during skill update. Rolling back...")
        traceback.print_exc()

        # Rollback to clean state
        subprocess.run(["git", "reset", "--hard"], check=True)
        subprocess.run(["git", "clean", "-fd"], check=True)

        print("🔁 Git rollback completed.")
        raise RuntimeError("Git auto-push failed and was rolled back.")

# Example wrapper — modify your actual training function accordingly
def train_skill(skill_name):
    try:
        print(f"🧠 Training skill: {skill_name}")

        # -------------------------------
        # Your training logic goes here
        # -------------------------------
        skill_file_path = f"skills/{skill_name}.py"
        with open(skill_file_path, "w") as f:
            f.write(f"# Skill logic for {skill_name}\n")  # placeholder

        print(f"✅ Finished training skill: {skill_name}")

        # Auto-push the skill to Git
        auto_push_to_git(skill_file_path)

    except Exception as e:
        print(f"🔥 Error during skill training: {e}")
        traceback.print_exc()
        sys.exit(1)
