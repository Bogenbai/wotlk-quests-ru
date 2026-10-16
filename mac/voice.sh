#!/bin/bash
cd "$(dirname "$0")/.."
mkdir -p work out/progress
export TTS_HOME="$PWD/models"
export PYTORCH_ENABLE_MPS_FALLBACK=1
exec venv/bin/python -I tools/voice_quests.py \
    work/quests_horde.json \
    wrath/sounds/quests \
    out/AI_VoiceOverData_Russian \
    out/progress \
    "$@"
