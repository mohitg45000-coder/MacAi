#!/bin/bash
set -e

echo "🤖 Building Jarvis..."
rm -rf build dist

python3 -m PyInstaller --noconfirm --clean --onedir --windowed \
  --name Jarvis \
  --collect-all ai_edge_litert \
  --collect-all openwakeword \
  --hidden-import=ai_edge_litert.interpreter \
  --runtime-hook runtime_hook.py \
  main.py

echo "✅ Jarvis build complete!"
