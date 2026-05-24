#!/bin/bash
# cc wrapper: auto-loads DeepSeek env
export ANTHROPIC_BASE_URL="https://api.deepseek.com/anthropic"
export ANTHROPIC_AUTH_TOKEN="ANTHROPIC_API_KEY_REMOVED"
export ANTHROPIC_API_KEY="ANTHROPIC_API_KEY_REMOVED"
export ANTHROPIC_MODEL="deepseek-v4-pro"
export ANTHROPIC_DEFAULT_OPUS_MODEL="deepseek-v4-pro"
export ANTHROPIC_DEFAULT_SONNET_MODEL="deepseek-v4-pro"
export ANTHROPIC_DEFAULT_HAIKU_MODEL="deepseek-v4-flash"
export CLAUDE_CODE_SUBAGENT_MODEL="deepseek-v4-flash"
export CLAUDE_CODE_EFFORT_LEVEL="max"
export CLAUDE_CODE_MAX_OUTPUT_TOKENS=8192
exec claude "$@"
