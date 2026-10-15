#!/bin/bash
# Синхронизация текстовой БЗ проекта в KB платформы (для viking_ingest_local)
set -e
mkdir -p /Users/user0/golden-land-new/dsh/kb
rsync -a --delete \
  --exclude '*.png' --exclude '*.jpg' --exclude '*.jpeg' --exclude '*.gif' \
  --exclude '*.mp4' --exclude '*.webm' \
  --exclude '.DS_Store' --exclude '__pycache__' --exclude '*.pyc' \
  /Users/user0/godot-hybrid-casual/ /Users/user0/golden-land-new/dsh/kb/godot-hybrid-casual/
echo "KB synced: $(find /Users/user0/golden-land-new/dsh/kb/godot-hybrid-casual -type f | wc -l | tr -d ' ') files, $(du -sh /Users/user0/golden-land-new/runtime/kb/godot-hybrid-casual | cut -f1)"
