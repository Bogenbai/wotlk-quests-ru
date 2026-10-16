#!/bin/bash
cd "$(dirname "$0")/.."
if [ -f work/voice.pid ] && ps -p "$(cat work/voice.pid)" -o command= | grep -q voice_quests.py; then
    kill "$(cat work/voice.pid)"
    echo "Stopped"
else
    echo "Not running"
fi
