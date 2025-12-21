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

**Gerrit Agent** is an AI-powered code review platform that integrates cutting-edge Code Agents (Claude Code, Gemini CLI, etc.) with Gerrit Code Review. It provides automated code analysis, intelligent inline comments, and multi-agent review workflows - all directly from your terminal.

### Why Gerrit Agent?

- 🧠 **Multiple AI Agents**: Use Claude, Gemini, or any Claude Agent Skill Protocol-compatible agent
- 🎯 **Smart Reviews**: Multi-agent analysis with confidence scoring (only shows high-confidence findings ≥80%)
- 💬 **Inline Comments**: Automatically posts structured feedback directly to Gerrit changes
- ⚡ **Fast CLI**: Modern, GitHub CLI-like interface for Gerrit operations
- 🔌 **Extensible**: Built on open protocols, works with any compatible Code Agent

---

## ✨ Features

**🤖 AI Agent Integrations:**
- Claude Code Skill (multi-agent review, confidence scoring)
- Gemini CLI Extension (natural language reviews)
- Compatible with Claude Agent Skill Protocol

**💻 CLI Operations:**
List, view, checkout, review changes • Inline comments • JSON/Table output

**🛡️ Developer-Friendly:**
HTTP token auth • Rich terminal UI • `.env` config • Comprehensive tests

---


## 🚀 Quick Start

**Install:**
```bash
pip install gerrit-agent-skill
```

**Configure:**
```bash
export GERRIT_URL=https://gerrit.example.com
export GERRIT_USERNAME=your_username
export GERRIT_TOKEN=your_http_token
```

**Verify:**
```bash
gerrit --help
```

---

## 🎯 Usage Modes

### 🤖 Claude Code Skill

Multi-agent code review with confidence scoring.

```bash
# Install skill
claude --skill-dir /path/to/gerrit-agent-skill/skills/gerrit

# Use it
/gerrit:review 12345
```

Features: 3 specialized analyzers, confidence scoring (≥80%), user confirmation before posting.

📚 [Full documentation →](skills/gerrit/README.md)

---

### 🧠 Gemini CLI Extension

Natural language code reviews with "Principal Software Engineer" persona.

```bash
# Install
gemini extensions link https://github.com/madroidmaq/gerrit-agent-skill/gemini-cli-extensions

# Use it
gemini "Review change 12345"
gemini /gerrit:review 12345
```

📚 [Full documentation →](gemini-cli-extensions/README.md)

---

### 💻 Standalone CLI

GitHub CLI-like experience for Gerrit operations.

```bash
# List changes
gerrit list --owner me --status open

# View change
gerrit show 12345 --diff

# Checkout and review
gerrit checkout 12345
gerrit review 12345 --code-review +2 -m "LGTM!"
```

📚 [Full CLI reference →](docs/CLI_REFERENCE.md)

---

## 📚 Documentation

- [CLI Reference](docs/CLI_REFERENCE.md)
- [Claude Skill Setup](skills/gerrit/README.md)
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
