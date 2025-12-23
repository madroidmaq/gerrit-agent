---
name: Gerrit Code Reviewer
description: >
  Automated code review for Gerrit changes with multi-agent analysis, confidence scoring,
  and inline comment posting. Use when users request to: (1) Review a Gerrit change or
  patch set, (2) Check code quality/security in Gerrit, (3) Analyze bugs in a change,
  (4) Get feedback on Gerrit code, (5) Perform code review on a change number. Supports
  CLAUDE.md guidelines, parallel review agents, and confidence-based filtering (≥80).
---

# Gerrit Code Review Workflow

This skill provides a comprehensive automated code review workflow for Gerrit changes using the gerrit CLI tool.

## Prerequisites

Before starting the review workflow, ensure:
- `gerrit` CLI is installed and configured
- Current directory is a git repository
- Environment variables are set: `GERRIT_URL`, `GERRIT_USERNAME`, `GERRIT_TOKEN` (or `GERRIT_PASSWORD`)
- User has access to the Gerrit server

## Complete Review Workflow

Follow these steps precisely to perform a comprehensive code review:

### Step 1: Validation and Pre-flight Checks

Use a Haiku agent to perform validation:

**Check change status:**
- (a) Is the change merged/abandoned? If so, warn but continue
- (b) Is the change accessible?
- (c) Does the change already have a Claude review? (check for "🤖 Generated with [Claude Code]" in comments and prompt to continue)

**Validate environment:**
- gerrit-cli is installed (`gerrit --version`)
- Current directory is a git repository (`git rev-parse --git-dir`)
- Can connect to Gerrit (`gerrit list -n 1`)
- Change exists (`gerrit show <change_id> --format json`)

**Failure handling:**
If validation fails, show helpful error messages and do not proceed.

### Step 2: Checkout and Context Gathering

Use a Haiku agent to:

**Checkout the change:**
```bash
gerrit checkout <change_id> --stash
```

**Gather context:**
- Change metadata via `gerrit show <change_id> --format json`
- Full diff via `git diff HEAD^ HEAD`
- Modified files list
- Relevant CLAUDE.md files (root and in modified directories)

### Step 3: Change Summary Generation

Use a Haiku agent to:
- Generate a 1-2 sentence change summary
- List modified files with their purpose

### Step 4: Parallel Review Agents

Launch 3 parallel Sonnet agents to independently code review the change. Each agent returns structured issues with:
- File path
- Line number or range
- Severity level
- Category
- Description
- Reason
- Suggested fix

**Agent #1: CLAUDE.md Compliance & Bug Scanner**
- Read CLAUDE.md files and modified file contents
- Focus on added/modified lines (lines with `+` in diff)
- Check for:
  - CLAUDE.md violations
  - Bugs (null checks, logic errors, edge cases)
  - Security issues (SQL injection, XSS, command injection, secrets)
  - Type errors

**Agent #2: Git History & Pattern Analyzer**
- Use `git log`, `git blame`, `gerrit list`, and `gerrit show --comments`
- Check for:
  - Historical bug patterns
  - Recurring issues
  - Code hot spots
  - Pattern inconsistencies

**Agent #3: Code Comment & Documentation Checker**
- Read modified files
- Search for TODO/FIXME/NOTE/HACK/XXX
- Check if changes:
  - Address existing TODOs
  - Add unexplained TODOs
  - Contradict comments
  - Lack documentation
- Verify docstrings and comment accuracy

### Step 5: Confidence Scoring

For each issue from step 4, launch a parallel Haiku agent to score confidence (0-100).

**Use this rubric verbatim:**
- **0**: Not confident at all. False positive, doesn't stand up to scrutiny, or pre-existing issue.
- **25**: Somewhat confident. Might be real, might be false positive. Cannot verify. Stylistic issues not in CLAUDE.md.
- **50**: Moderately confident. Real issue but may be nitpick or rare. Not very important relative to PR.
- **75**: Highly confident. Verified real issue likely hit in practice. Insufficient PR approach. Very important, impacts functionality, or directly mentioned in CLAUDE.md.
- **100**: Absolutely certain. Confirmed real issue that happens frequently. Evidence directly confirms.

**Important:**
- For CLAUDE.md issues, verify guidance exists before scoring ≥80
- Filter out issues with confidence <80
- If none remain, display "No issues found" and do not proceed

### Step 6: User Confirmation

Display review summary showing all issues ≥80 with:
- File path
- Line number/range
- Severity
- Category
- Issue description
- Reason
- Suggested fix

**Prompt user:**
```
Would you like to post these <N> inline comments to Gerrit change <change_id>? (yes/no)
```

**Handle response:**
- If "yes", proceed to step 7
- If "no", display cancellation message with manual posting example
- Re-prompt if invalid input

### Step 7: Post Review to Gerrit

After user confirms, post review using:

```bash
gerrit review <change_id> \
  --inline-comment "<file>#<line>" "[SEVERITY] description\n\nReason: ...\n\nSuggested fix:\n...\n\nCategory: ...\nConfidence: ..." \
  --inline-comment "<file>#<line>" "..." \
  -m "Review summary message"
```

**Location formats:**
- Single line: `file#42`
- Range: `file#10-20`
- Character range: `file#L12C13-L12C19`

**Post-submission:**
- Display success message with link to view comments
- Or display error message if posting fails

## Examples of False Positives

When reviewing code (steps 4 and 5), avoid flagging these as issues:

- Pre-existing issues (not introduced in this change)
- Something that looks like a bug but is not actually a bug
- Pedantic nitpicks that a senior engineer wouldn't call out
- Issues that linters, typecheckers, or compilers would catch (missing imports, type errors, broken tests, formatting issues, style issues) - these will run separately in CI
- General code quality issues (test coverage, general security, documentation), unless explicitly required in CLAUDE.md
- Issues called out in CLAUDE.md but silenced in code (lint ignore comments)
- Changes in functionality that are intentional or related to the broader change
- Real issues, but on lines NOT modified in this change (context lines in diff)

## Important Notes

- **Do not build, typecheck, or run tests** - these run separately in CI
- **Use `gerrit` CLI** to interact with Gerrit (not gh commands)
- **Make a todo list first** - track progress through the workflow
- **All issues must cite specific files and line numbers**
- **For CLAUDE.md violations**, quote the specific guidance
- **Focus review on modified/added lines only** (lines with `+` in diff)
- **Confidence scoring is critical** - when in doubt, score lower
- **User confirmation required before posting** - never auto-post

## Required Environment Variables

```bash
GERRIT_URL=https://gerrit.example.com
GERRIT_USERNAME=your-username
GERRIT_TOKEN=your-token  # or GERRIT_PASSWORD
```
