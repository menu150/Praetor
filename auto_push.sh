cat <<'EOF' > ~/praetor/auto_push.sh
#!/usr/bin/env bash

# Move into your repo
cd ~/praetor

# Make sure we’re on the right branch
git checkout main

# If there are any changes, commit & push
if ! git diff-index --quiet HEAD --; then
  git add -A
  git commit -m "Auto-backup: $(date +'%Y-%m-%d\ %H:%M:%S')"
  git push origin main
fi
EOF

# Make it executable
chmod +x ~/praetor/auto_push.sh
