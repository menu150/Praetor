#!/usr/bin/env bash

cd ~/praetor || exit 1

echo "📡 Git Watch Daemon started at $(date)"

inotifywait -m -r -e modify,create,delete --exclude '(\.git|venv|__pycache__|\.log)' . |
while read -r path action file; do
    echo "🔄 Change detected: $file ($action)"

    git pull --rebase origin main

    # Only commit if something changed
    if [[ -n $(git status --porcelain) ]]; then
        git add .
        git commit -m "Real-time update: $(date +'%Y-%m-%d %H:%M:%S')"
        git push origin main
        echo "✅ Git push complete."
    else
        echo "🟢 No actual changes to push."
    fi
done
