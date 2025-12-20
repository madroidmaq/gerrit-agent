# Gerrit Agent: AI-Powered Gerrit Assistant

**gerrit-agent** (formerly `gerrit-cli`) is a next-generation command-line interface and AI Agent for Gerrit Code Review. It goes beyond simple API wrappers by integrating with LLMs to act as your intelligent copilot for code reviews.

> **Note:** This project has been renamed from `gerrit-cli` to `gerrit-agent` to better reflect its AI capabilities.

## 🚀 Key Features

*   **🤖 AI-Powered Review Agent**: Integrates with Gemini CLI to automatically analyze changes and post inline comments.
*   **💻 Modern CLI**: A human-friendly terminal interface for Gerrit (List, Show, Checkout, Review).
*   **🔌 Extensible**: Designed to work as a Gemini CLI Extension and (soon) a Claude Code / MCP server.
*   **🛠️ Developer Friendly**: Built with `click`, `rich`, and `httpx`.

---

## 🛠️ Installation & Configuration

All modes (CLI, Gemini Agent, MCP) require the base python package and configuration.

### 1. Install

```bash
pip install gerrit-agent
```

### 2. Configure Environment

Create a `.env` file in your working directory or export these variables:

```bash
# Gerrit Server Configuration
export GERRIT_URL=https://gerrit.example.com
export GERRIT_USERNAME=your_username
export GERRIT_PASSWORD=your_password 
# Or use HTTP Token (Recommended)
# export GERRIT_TOKEN=your_http_token
```

---

## 🤖 Mode 1: Gemini CLI Extension (Recommended)

**Turn your terminal into a Principal Software Engineer.** 

By linking `gerrit-agent` with the Gemini CLI, you can use natural language to interact with Gerrit and perform automated code reviews.

### Setup

Assuming you have the Gemini CLI installed, link this extension:

```bash
# If you cloned the repo locally
gemini extensions link ./gemini-cli-extensions

# Or via URL (once published)
# gemini extensions link https://github.com/madroid/gerrit-agent/gemini-cli-extensions
```

### Usage

**Automated Code Review:**
Ask the agent to review a specific change ID. It will fetch the diff, analyze it, and post inline comments directly to Gerrit.

```bash
gemini "Review change 12345"
# or use the command alias
gemini /code-review 12345
```

**Summarize Changes:**
```bash
gemini "Summarize what change 12345 does"
```

---

## 💻 Mode 2: Standalone CLI

For precise control, use the `gerrit` command directly. It mimics the GitHub CLI (`gh`) experience.

> 📖 **Full Documentation**: For a complete list of commands, flags, and advanced usage (including checkout options and query syntax), please see the [**CLI Reference Guide**](docs/CLI_REFERENCE.md).

### Common Commands

| Action | Command | Alias |
|--------|---------|-------|
| **List** | `gerrit list` | `gerrit change list` |
| **Show** | `gerrit show <id>` | `gerrit change view` |
| **Checkout** | `gerrit checkout <id>` | `gerrit change checkout` |
| **Review** | `gerrit review <id>` | |

### Quick Examples

```bash
# List open changes assigned to you
gerrit list --owner me --status open

# Checkout a change to a local branch
gerrit checkout 12345

# Submit a +2 Code-Review
gerrit review 12345 --code-review +2 -m "LGTM!"
```

---

## 🧠 Mode 3: Claude Code Agent (Coming Soon)

We are actively working on an **MCP (Model Context Protocol)** server implementation. This will allow `gerrit-agent` to serve as a tool for Claude Code and other MCP-compatible assistants.

*   **Capabilities:** Claude will be able to search Gerrit, read file content, and understand the context of large relation chains.
*   **Status:** 🚧 In Development

---

## 📦 Project Structure

```
gerrit-agent/
├── gemini-cli-extensions/  # Configuration for Gemini CLI
├── src/gerrit_cli/         # Core Python Logic
│   ├── client/             # Gerrit REST API Client
│   ├── commands/           # Click CLI Commands
│   └── ...
└── tests/                  # Pytest Suite
```

## 🤝 Contributing

Contributions are welcome! Please check the [issues](https://github.com/madroid/gerrit-agent/issues) for planned features like Draft Comments and Batch Operations.

## License

MIT License
