# Gerrit Code Review Plugin

Automated code review for Gerrit changes using Claude Code with multi-agent analysis and confidence scoring.

## 🚀 Quick Start

```bash
# 1. Install the plugin
/plugin marketplace add madroidmaq/gerrit-agent
/plugin install gerrit@gerrit-agent

# 2. Configure Gerrit (one-time setup)
export GERRIT_URL=https://gerrit.example.com
export GERRIT_USERNAME=your-username
export GERRIT_TOKEN=your-token

# 3. Review a change
/review 12345
```

## ✨ Features

- **Multi-agent review**: 3 specialized agents analyze CLAUDE.md compliance, git history patterns, and documentation
- **Confidence scoring**: Filters issues to show only high-confidence findings (≥80)
- **User confirmation**: Never auto-posts - always asks before submitting comments
- **Inline comments**: Automatically posts structured feedback to Gerrit changes

## 📋 Prerequisites

- [Claude Code](https://claude.ai/code) installed
- Git repository (commands run from your project directory)
- Gerrit server credentials (see configuration below)

## 📦 Installation

**Option 1: From Marketplace (Recommended)**

```bash
/plugin marketplace add madroidmaq/gerrit-agent
/plugin install gerrit@gerrit-agent
```

Or use the UI: `Browse and install plugins` → `gerrit-agent` → `gerrit` → `Install now`

**Option 2: Local Development**

```bash
git clone https://github.com/madroidmaq/gerrit-agent.git
cd gerrit-agent
claude plugins link .
```

## ⚙️ Configuration

Set up your Gerrit credentials (required for API access):

```bash
# Create .env file from template
cp .env.example .env

# Edit .env with your credentials:
export GERRIT_URL=https://gerrit.example.com
export GERRIT_USERNAME=your-username
export GERRIT_TOKEN=your-http-token  # Recommended
# OR
export GERRIT_PASSWORD=your-password  # Alternative
```

> 💡 Generate HTTP token at: `Gerrit Settings → HTTP Credentials`

## 💻 Usage

This plugin provides both a **command** (for direct invocation) and a **skill** (for natural language):

| Method | Example | Use Case |
|--------|---------|----------|
| **Command** | `/review 12345` | Quick, direct review (recommended) |
| **With namespace** | `/gerrit:review 12345` | Explicit plugin reference |
| **Natural language** | `"Review Gerrit change 12345"` | Conversational interface |

The command (`/review`) provides direct access, while natural language triggers the `gerrit-reviewer` skill for more flexible interaction.

## 🔄 Review Workflow

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
