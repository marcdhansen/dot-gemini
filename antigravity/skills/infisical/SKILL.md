---
name: Infisical
description: Skill for managing team secrets and projects using the Infisical CLI. Provides tools for secure secret injection, project initialization, and credential management.
---

# Infisical Skill

This skill provides a standardized way for agents to interact with **Infisical Cloud** for secret management. It abstracts the CLI location and provides common workflows for secret injection and project handling.

## 🛠️ Installation & Setup

If the Infisical CLI is not found in the path, it can be installed locally:

```bash
# Install to ~/.infisical/bin/infisical
mkdir -p ~/.infisical/bin && \
curl -L -o ~/.infisical/infisical.tar.gz https://github.com/Infisical/cli/releases/download/v0.43.62/cli_0.43.62_darwin_arm64.tar.gz && \
tar -xzf ~/.infisical/infisical.tar.gz -C ~/.infisical/bin/ && \
rm ~/.infisical/infisical.tar.gz
```

## 🔐 Core Commands

### 1. Execute with Secrets (Preferred)

Always use `infisical run` to inject secrets into a process. This avoids writing secrets to disk.

```bash
# Standard usage
~/.infisical/bin/infisical run -- <your-command>

# Example: Run a python script with secrets
~/.infisical/bin/infisical run -- python3 scripts/my_script.py
```

### 2. View Secrets

```bash
~/.infisical/bin/infisical secrets
```

### 3. Initialize a New Project

To connect a repository to a new or existing Infisical project:

```bash
~/.infisical/bin/infisical init
```
*Note: This usually requires a browser login. If prompted, provide the login link to the user and wait for the token.*

## 🚀 Workflows

### Adding a New Project
1.  **Dashboard**: Create the project in the [Infisical Dashboard](https://app.infisical.com).
2.  **Init**: Run `infisical init` in the repository root.
3.  **Populate**: Use `infisical secrets set KEY=VALUE` to add initial secrets.

### Importing from `.env`
To bulk-import existing secrets from a `.env` file into the current project:
```bash
# WARNING: This will overwrite existing secrets with the same names
~/.infisical/bin/infisical secrets set --env=.env
```

## ⚠️ Security Best Practices
- **NEVER** commit `.env` files with real secrets. Use `.env.example` instead.
- **NEVER** log API keys or secrets to the console.
- **ALWAYS** use `infisical run` for runtime injection.
- **PRUNE** local `.env` files once secrets are migrated to Infisical.

## 🤖 Agent Integration
When an agent needs to perform an action requiring secrets (e.g., calling an LLM API, accessing a database):
1.  Check for Infisical initialization (`.infisical.json`).
2.  Wrap the command in `infisical run`.
3.  If unauthorized, guide the user through `infisical login`.
