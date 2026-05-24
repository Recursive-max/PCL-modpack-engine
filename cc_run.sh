#!/bin/bash
KEY=$(cat /tmp/ds_key)
export ANTHROPIC_API_KEY="$KEY"
export ANTHROPIC_AUTH_TOKEN="$KEY"
export ANTHROPIC_BASE_URL="https://api.deepseek.com/anthropic"

timeout 120 claude --print "$1" 2>&1
