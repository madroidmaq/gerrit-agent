<div align="center">

# 🤖 Gerrit Agent

**AI-Powered Code Review Assistant for Gerrit**

[![PyPI version](https://badge.fury.io/py/gerrit-agent-skill.svg)](https://badge.fury.io/py/gerrit-agent-skill)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

Transform your Gerrit code reviews with AI-powered analysis using **Claude Code**, **Gemini CLI**, and other advanced Code Agents.

[Features](#-features) • [Quick Start](#-quick-start) • [Usage](#-usage-modes) • [Documentation](#-documentation) • [Contributing](#-contributing)

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


## 🚀 Quick Start

Get started with the **Claude Code Plugin** (recommended):

```bash
# 1. Register the plugin marketplace
/plugin marketplace add madroidmaq/gerrit-agent-skill

# 2. Install the plugin
/plugin install gerrit@gerrit-agent-skills

# 3. Configure Gerrit credentials (copy .env.example and edit)
export GERRIT_URL=https://gerrit.example.com
export GERRIT_USERNAME=your_username
export GERRIT_TOKEN=your_http_token

# 4. Review a change
/review 12345
```

> 💡 See [.env.example](.env.example) for configuration options or [CLI Quick Start](#-standalone-cli) for standalone usage

---

## 🎯 Usage Modes

### 🤖 Claude Code Plugin

AI-powered code reviews with multi-agent analysis and confidence scoring.

**Installation:**

See [Quick Start](#-quick-start) above, or use the UI:

1. Run `/plugin marketplace add madroidmaq/gerrit-agent-skill`
2. Select `Browse and install plugins` → `gerrit-agent-skills` → `gerrit` → `Install now`

**Usage:**

| Method | Command | Description |
|--------|---------|-------------|
| **Command** | `/review 12345` | Direct review command (recommended) |
| **With namespace** | `/gerrit:review 12345` | Full command path |
| **Natural language** | `"Review Gerrit change 12345"` | Triggers gerrit-reviewer skill |

📚 [Full plugin documentation →](plugins/gerrit/README.md)

---

### 💻 Standalone CLI

GitHub CLI-like interface for Gerrit operations (list, view, checkout, review).

**Quick Start:**
```bash
pip install gerrit-agent-skill
export GERRIT_URL=https://gerrit.example.com GERRIT_USERNAME=user GERRIT_TOKEN=token
gerrit list --owner me --status open
```

**Common Commands:**
```bash
gerrit show 12345 --diff           # View change with diff
gerrit checkout 12345               # Checkout change locally
gerrit review 12345 --code-review +2 -m "LGTM!"  # Post review
```

📚 [Full CLI reference →](docs/CLI_REFERENCE.md)

---

### 🧠 Gemini CLI Extension

Natural language code reviews with "Principal Software Engineer" persona.

```bash
# Install
gemini extensions link https://github.com/madroidmaq/gerrit-agent-skill/gemini-cli-extensions

# Use natural language
gemini "Review change 12345"
```

📚 [Full documentation →](gemini-cli-extensions/README.md)

---

## 📚 Documentation

- [CLI Reference](docs/CLI_REFERENCE.md)
- [Claude Code Plugin](plugins/gerrit/README.md)
- [Gemini Extension](gemini-cli-extensions/README.md)

---

## 🤝 Contributing

Contributions welcome! See [Issues](https://github.com/madroidmaq/gerrit-agent-skill/issues) for planned features.

```bash
git clone https://github.com/madroidmaq/gerrit-agent-skill.git && cd gerrit-agent-skill
uv sync --extra dev && uv run pytest
```

---


## 📄 License

MIT License - see [LICENSE](LICENSE) file.

---

<div align="center">

Built with [Click](https://click.palletsprojects.com/), [Rich](https://rich.readthedocs.io/), [httpx](https://www.python-httpx.org/), [Pydantic](https://pydantic-docs.helpmanual.io/)

**If you find this helpful, please ⭐ star the repo!**

[Report Bug](https://github.com/madroidmaq/gerrit-agent-skill/issues) • [Request Feature](https://github.com/madroidmaq/gerrit-agent-skill/issues)

</div>
