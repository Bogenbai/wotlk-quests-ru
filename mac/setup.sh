#!/bin/bash
set -e
cd "$(dirname "$0")/.."
PYTHON="${PYTHON:-python3.12}"
if ! command -v "$PYTHON" >/dev/null; then
    echo "Python 3.12 not found. Install it from https://www.python.org/downloads/macos/"
    exit 1
fi
"$PYTHON" -m venv venv
venv/bin/python -m pip install --upgrade pip
venv/bin/python -m pip install -r requirements-mac.txt
venv/bin/python -m pip install transformers==4.55.4
echo "Setup done"
