#!/bin/bash
# Wrapper to call claude with proper env
export ANTHROPIC_API_KEY="ANTHROPIC_API_KEY_REMOVED"
export ANTHROPIC_BASE_URL="https://api.deepseek.com/anthropic"
export CLAUDE_CODE_SUBAGENT_MODEL="deepseek-v4-flash"
cd ~/pcl2
claude --print "$1" 2>&1