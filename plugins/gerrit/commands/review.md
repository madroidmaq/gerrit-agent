---
allowed-tools: Bash(gerrit:*), Bash(git:*)
description: Code review a Gerrit change using gerrit-agent-skill
disable-model-invocation: false
---

Perform automated code review on a Gerrit change using multi-agent analysis.

## Prerequisites Check

Before starting, verify gerrit CLI is installed:

```bash
gerrit --version
```

If not installed, show this message:
```
Error: gerrit CLI not found. Please install it first:
https://github.com/madroid/gerrit-agent-skill

Required environment variables:
  GERRIT_URL          - Your Gerrit server URL
  GERRIT_USERNAME     - Your Gerrit username
  GERRIT_TOKEN        - Your Gerrit API token (or GERRIT_PASSWORD)
```

## Execution

**Follow the complete workflow defined in `../skills/gerrit-reviewer/SKILL.md`.**

The skill handles all review logic including validation, checkout, analysis, scoring, and posting.
