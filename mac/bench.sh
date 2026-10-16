#!/bin/bash
cd "$(dirname "$0")/.."
for device in mps cpu; do
    echo "=== $device ==="
    bash mac/voice.sh --device "$device" --limit 6 2>&1 | grep -E "device|^\[|FAILED|Error|finished"
done
