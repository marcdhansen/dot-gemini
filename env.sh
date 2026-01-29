#!/usr/bin/env bash

# 🌐 Global Standard Mission Protocol (SMP) Environment
# Source this file to align any agent with the global system standards.

# 🐚 Task Management (Beads)
export BD_ACTOR="${BD_ACTOR:-$USER}"
export BD_DB_PATH="${HOME}/.gemini/beads/beads.db" # Default global DB if not project-local

# 🧠 Skills & Configuration
export GEMINI_HOME="${HOME}/.gemini"
export ANTIGRAVITY_HOME="${HOME}/.antigravity"
export SKILLS_PATH="${GEMINI_HOME}/antigravity/skills"

# 📊 Observability (Langfuse)
# These should be set in your private .env file, but we define the vars here.
# export LANGFUSE_PUBLIC_KEY="..."
# export LANGFUSE_SECRET_KEY="..."
# export LANGFUSE_HOST="http://localhost:3000"

# 🐍 Python Paths
export PYTHONPATH="${SKILLS_PATH}:${PYTHONPATH}"

# 🏗️ Alias for convenience
alias agready="python ${SKILLS_PATH}/FlightDirector/scripts/check_flight_readiness.py --pfc"
alias agdone="python ${SKILLS_PATH}/FlightDirector/scripts/check_flight_readiness.py --rtb"

echo "✅ SMP Environment Loaded: ${BD_ACTOR} ready for mission."
