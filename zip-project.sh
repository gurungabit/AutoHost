#!/bin/bash

# AutoHost Project Zipper
# Creates a clean zip archive excluding dependencies and build artifacts

PROJECT_NAME="AutoHost"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ZIP_NAME="${PROJECT_NAME}_${TIMESTAMP}.zip"

echo "Creating archive: $ZIP_NAME"
echo "Excluding dependencies and build artifacts..."

zip -r "$ZIP_NAME" . \
  -x "*.git*" \
  -x "*node_modules/*" \
  -x "*__pycache__/*" \
  -x "*.pyc" \
  -x "*.pyo" \
  -x "*.pyd" \
  -x "*/.venv/*" \
  -x "*/venv/*" \
  -x "*/ENV/*" \
  -x "*/.uv/*" \
  -x "*/uv.lock" \
  -x "*.env" \
  -x "*/dist/*" \
  -x "*/build/*" \
  -x "*.egg-info/*" \
  -x "*.log" \
  -x "*/.DS_Store" \
  -x "*/Thumbs.db" \
  -x "*/.vscode/*" \
  -x "*/.idea/*" \
  -x "*.swp" \
  -x "*.swo" \
  -x "*~" \
  -x "*/scripts/*.json" \
  -x "*/logs/*" \
  -x "*/.claude/*"

echo ""
echo "Archive created successfully!"
echo "File: $ZIP_NAME"
echo "Size: $(du -h "$ZIP_NAME" | cut -f1)"
echo ""
echo "To extract: unzip $ZIP_NAME"
