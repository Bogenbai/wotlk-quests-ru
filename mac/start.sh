#!/bin/bash
cd "$(dirname "$0")/.."
mkdir -p work
if [ -f work/voice.pid ] && ps -p "$(cat work/voice.pid)" -o command= | grep -q voice_quests.py; then
    echo "Already running (PID $(cat work/voice.pid))"
    exit
fi
nohup bash mac/voice.sh --device "${1:-auto}" > work/voice.log 2> work/voice.err.log &
echo $! > work/voice.pid
nohup caffeinate -i -s -w "$!" >/dev/null 2>&1 &
echo "Started (PID $(cat work/voice.pid)). Progress: tail -n 5 work/voice.log"
