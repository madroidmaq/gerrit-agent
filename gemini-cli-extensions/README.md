# Gerrit Review Extension

This extension uses `gerrit-agent-skill` and Gemini to perform automated code reviews on Gerrit changes.

## Features
- Fetches code changes directly from Gerrit.
- Analyzes diffs using a "Principal Software Engineer" persona.
- Automatically posts findings as inline comments back to Gerrit.

## Installation
Run the following command in the project root:
```bash
gemini extensions link https://github.com/madroidmaq/gerrit-agent-skill/gemini-cli-extensions
```

## Usage
To review a change:
```bash
gemini /gerrit:review <change_id>
```
Example:
```bash
gemini /gerrit:review 12345
```
