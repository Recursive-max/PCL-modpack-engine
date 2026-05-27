#!/bin/bash
# cc wrapper: auto-loads DeepSeek env
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENV_FILE="$HOME/.openclaw/.env.local"

# 从 .env.local 读取 API key
DEEPSEEK_KEY=""
if [ -f "$ENV_FILE" ]; then
    DEEPSEEK_KEY=$(grep DEEPSEEK_API_KEY "$ENV_FILE" | head -1 | cut -d= -f2-)
fi

export ANTHROPIC_BASE_URL="https://api.deepseek.com/anthropic"
export ANTHROPIC_AUTH_TOKEN="$DEEPSEEK_KEY"
export ANTHROPIC_API_KEY="$DEEPSEEK_KEY"
export ANTHROPIC_MODEL="deepseek-v4-pro"
export ANTHROPIC_DEFAULT_OPUS_MODEL="deepseek-v4-pro"
export ANTHROPIC_DEFAULT_SONNET_MODEL="deepseek-v4-pro"
export ANTHROPIC_DEFAULT_HAIKU_MODEL="deepseek-v4-flash"
export CLAUDE_CODE_SUBAGENT_MODEL="deepseek-v4-flash"
export CLAUDE_CODE_EFFORT_LEVEL="max"
export CLAUDE_CODE_MAX_OUTPUT_TOKENS=8192
exec claude "$@"
