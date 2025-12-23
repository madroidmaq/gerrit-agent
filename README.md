<div align="center">

# 🤖 Gerrit Agent

**AI-Powered Code Review Assistant for Gerrit**

[![PyPI version](https://badge.fury.io/py/gerrit-agent.svg)](https://badge.fury.io/py/gerrit-agent)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

Transform your Gerrit code reviews with AI-powered analysis using **Claude Code**, **Gemini CLI**, and other advanced Code Agents.

[Features](#-features) • [Usage Modes](#-usage-modes) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

---

## 📖 Overview

**Gerrit Agent** transforms Gerrit code reviews with AI-powered analysis. Get automated, intelligent code reviews through Claude Code Plugin, standalone CLI, or Gemini integration - with multi-agent analysis, confidence scoring, and inline comment posting.

**Key Features:**

- 🤖 **Multi-Agent Reviews** - 3 specialized analyzers (CLAUDE.md compliance, git patterns, documentation)
- 🎯 **Smart Filtering** - Confidence scoring shows only high-quality findings (≥80%)
- 💬 **Direct Integration** - Posts inline comments to Gerrit with your approval
- ⚡ **Modern CLI** - GitHub CLI-like interface for all Gerrit operations
- 🔌 **Multiple Modes** - Claude Code Plugin, standalone CLI, or Gemini extension

---

## 🎯 Usage Modes

### 💻 Standalone CLI

GitHub CLI-like interface for Gerrit operations (list, view, checkout, review). **This is the foundation of the project** - all other modes are built on top of this CLI.

**Installation:**

```bash
# Install from PyPI
pip install gerrit-agent

# Or install from source
git clone https://github.com/madroidmaq/gerrit-agent.git
cd gerrit-agent
pip install -e .
```

**Configuration:**

Set up your Gerrit credentials (required for all usage modes):

```bash
# Method 1: Environment variables (recommended)
export GERRIT_URL=https://gerrit.example.com
export GERRIT_USERNAME=your_username
export GERRIT_TOKEN=your_http_token  # Recommended: HTTP password from Gerrit settings

# Method 2: Or use password instead of token
export GERRIT_PASSWORD=your_password  # Less secure, use token when possible
```

> 💡 **Getting your token:** Go to Gerrit → Settings → HTTP Credentials → Generate Password
>
> 📝 **For persistent config:** Copy [.env.example](.env.example) to `.env` and edit with your credentials

**Common Commands:**

```bash
# List changes
gerrit list --owner me --status open
gerrit list --reviewer me --limit 20

# View change details
gerrit show 12345                   # View change info
gerrit show 12345 --diff            # View with full diff

# Checkout change locally
gerrit checkout 12345               # Creates local branch for review

# Post reviews
gerrit review 12345 --code-review +2 -m "LGTM!"
gerrit review 12345 --code-review -1 -m "Needs fixes"
```

📚 [Full CLI reference →](docs/CLI_REFERENCE.md)

---

### 🤖 Claude Code Plugin

AI-powered code reviews with multi-agent analysis and confidence scoring, built on top of the Standalone CLI. **Recommended for the best experience.**

**Prerequisites:**

- Install the `gerrit-agent` CLI tool (see [Standalone CLI](#-standalone-cli) above)
- Configure Gerrit credentials using environment variables (see CLI configuration above)

**Installation:**

```bash
# Option 1: Using commands (recommended)
/plugin marketplace add madroidmaq/gerrit-agent
/plugin install gerrit@gerrit-agent

# Option 2: Using UI
# Run: /plugin marketplace add madroidmaq/gerrit-agent
# Then select: Browse and install plugins → gerrit-agent → gerrit → Install now
```

**Usage:**

| Method | Command | Description |
|--------|---------|-------------|
| **Command** | `/gerrit:review 12345` | Direct review command (recommended) |
| **Natural language** | `"Review Gerrit change 12345"` | Triggers gerrit-reviewer skill |

**What happens during review:**
- 🤖 Three specialized agents analyze your code (compliance, git patterns, documentation)
- 🎯 Smart filtering shows only high-confidence findings (≥80%)
- 💬 Posts inline comments to Gerrit (with your approval)

📚 [Full plugin documentation →](plugins/gerrit/README.md)

---

### 🧠 Gemini CLI Extension

Natural language code reviews with "Principal Software Engineer" persona, powered by Google's Gemini.

**Prerequisites:**

Ensure you've configured Gerrit credentials as described in [Standalone CLI Configuration](#-standalone-cli) above.

**Installation:**

```bash
# Link the extension to Gemini CLI
gemini extensions link https://github.com/madroidmaq/gerrit-agent/gemini-cli-extensions
```

**Usage:**

```bash
# Use natural language to review changes
gemini "Review change 12345"
gemini "Check the latest changes in project XYZ"
```

📚 [Full documentation →](gemini-cli-extensions/README.md)

---

## 📚 Documentation

- [CLI Reference](docs/CLI_REFERENCE.md)
- [Claude Code Plugin](plugins/gerrit/README.md)
- [Gemini Extension](gemini-cli-extensions/README.md)

---

## 🤝 Contributing

Contributions welcome! See [Issues](https://github.com/madroidmaq/gerrit-agent/issues) for planned features.

```bash
git clone https://github.com/madroidmaq/gerrit-agent.git && cd gerrit-agent
uv sync --extra dev && uv run pytest
```

---


## 📄 License

MIT License - see [LICENSE](LICENSE) file.

---

<div align="center">

Built with [Click](https://click.palletsprojects.com/), [Rich](https://rich.readthedocs.io/), [httpx](https://www.python-httpx.org/), [Pydantic](https://pydantic-docs.helpmanual.io/)

**If you find this helpful, please ⭐ star the repo!**

[Report Bug](https://github.com/madroidmaq/gerrit-agent/issues) • [Request Feature](https://github.com/madroidmaq/gerrit-agent/issues)

</div>
