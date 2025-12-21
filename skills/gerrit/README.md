# Gerrit Code Review Skill

Automated code review for Gerrit changes using Claude AI with multi-agent analysis and confidence scoring.

## Features

- **Multi-agent review**: 3 specialized agents analyze CLAUDE.md compliance, git history patterns, and documentation
- **Confidence scoring**: Filters issues to show only high-confidence findings (≥80)
- **User confirmation**: Never auto-posts - always asks before submitting comments
- **Inline comments**: Automatically posts structured feedback to Gerrit changes

## Prerequisites

- [Gerrit CLI](https://github.com/your-repo/gerrit-cli) installed and configured
- Git repository (current directory)
- Environment variables:
  ```bash
  GERRIT_URL=https://gerrit.example.com
  GERRIT_USERNAME=your-username
  GERRIT_TOKEN=your-token  # or GERRIT_PASSWORD
  ```

## Installation

### Local Development

```bash
# Navigate to your gerrit-cli directory
cd /path/to/gerrit-cli

# Start Claude Code with the skill
claude --skill-dir ./skills/gerrit
```

### Install from Marketplace (when published)

```bash
claude /skill install gerrit
```

## Usage

### Method 1: Explicit Command

```bash
/gerrit:review 12345
```

### Method 2: Natural Language

Simply ask Claude:
```
"Review Gerrit change 12345"
"Check change 12345 for security issues"
```

Claude will recognize your intent and execute the review workflow.

## What Happens During Review

1. Validates environment and change accessibility
2. Checks out the change locally (with automatic stashing)
3. Generates change summary
4. Launches 3 parallel review agents
5. Scores each issue for confidence (0-100)
6. Shows only high-confidence issues (≥80)
7. Asks for your confirmation
8. Posts inline comments to Gerrit

## License

MIT
