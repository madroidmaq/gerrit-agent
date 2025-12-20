# Gerrit Agent CLI Reference

This document provides a comprehensive guide for using the standalone `gerrit` command-line interface.

## Installation

### Using uv (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd gerrit-agent

# Install dependencies
uv sync

# Run using uv run
uv run gerrit --help
```

### Using pip

```bash
# Clone the repository
git clone <repository-url>
cd gerrit-agent

# Install
pip install -e .

# Run directly
gerrit --help
```

## Configuration

Gerrit Agent uses environment variables for configuration. You can configure it in two ways:

### Option 1: Environment Variables

```bash
export GERRIT_URL=https://gerrit.example.com
export GERRIT_USERNAME=your_username
export GERRIT_PASSWORD=your_password
```

### Option 2: .env File (Recommended)

Copy `.env.example` to `.env` and modify the configuration:

```bash
cp .env.example .env
```

Edit the `.env` file:

```bash
# Gerrit Server Configuration
GERRIT_URL=https://gerrit.example.com
GERRIT_USERNAME=your_username
GERRIT_PASSWORD=your_password

# Or use HTTP Token (Generated in Gerrit Settings -> HTTP Credentials)
# GERRIT_TOKEN=your_http_token
```

## Usage

### View Help

```bash
gerrit --help
gerrit change --help
gerrit review --help
```

### List Changes

> **Shortcut**: `gerrit list` is an alias for `gerrit change list`.

```bash
# List all open changes
gerrit list

# List your own changes
gerrit list --owner me

# Filter by project
gerrit list --project myproject

# Custom query
gerrit list -q "status:merged branch:main"

# Limit results
gerrit list -n 50

# JSON format output
gerrit list --format json
```

### View Change Details

> **Shortcut**: `gerrit show` is an alias for `gerrit change view`.

```bash
# View change details (using numeric ID)
gerrit show 12345

# View change details (using Change-Id)
gerrit show I1234567890abcdef

# Show comments
gerrit show 12345 --comments

# JSON format output
gerrit show 12345 --format json
```

### Checkout Change to Local

> **Shortcut**: `gerrit checkout` is an alias for `gerrit change checkout`.

```bash
# Checkout change to a new local branch for testing or review
gerrit checkout 12345

# Specify custom branch name
gerrit checkout 12345 -b my-review-branch

# Force delete and recreate if branch exists
gerrit checkout 12345 --force

# Fetch only, do not checkout (stay on current branch)
gerrit checkout 12345 --no-checkout

# Auto stash uncommitted changes
gerrit checkout 12345 --stash

# Do not stash, force continue (changes may be lost)
gerrit checkout 12345 --no-stash
```

**Handling Uncommitted Changes:**

The checkout command checks your working directory status. If there are uncommitted changes, it will offer the following options:

1. **Stash changes (Recommended)**: Automatically runs `git stash`. You can use `git stash pop` to restore them after checkout.
2. **Cancel operation**: Allows you to manually handle current changes first.
3. **Force continue**: Switch branches directly (uncommitted changes may be lost).

You can also use `--stash` or `--no-stash` options to skip the prompt.

**Repository Verification:**

The checkout command intelligently checks if the current repository matches the Change:

1. **Not in a Git repository**: Prompts you to cd into a Git repository directory.
2. **No origin remote**: Warns and asks if you want to continue.
3. **Repository mismatch**: Warns if the remote URL doesn't seem to match the Change's project, preventing you from fetching into the wrong repository.

These checks ensure you don't perform fetch operations in the wrong directory or repository.

### Add Comments

```bash
# Add information comment
gerrit change comment 12345 -m "LGTM"

# Read comment from file
gerrit change comment 12345 -f comment.txt
```

### Submit Review

```bash
# Code-Review +2
gerrit review 12345 --code-review +2 -m "Looks good to me!"

# Code-Review -1 with message
gerrit review 12345 --code-review -1 -m "Please fix the following issues..."

# Code-Review +2 and Verified +1
gerrit review 12345 --code-review +2 --verified +1 -m "LGTM and verified"

# Read review message from file
gerrit review 12345 --code-review +2 -f review.txt
```

## Gerrit API Query Syntax

The `-q/--query` option supports Gerrit's query syntax. Common query conditions:

- `status:open` - Open changes
- `status:merged` - Merged changes
- `status:abandoned` - Abandoned changes
- `owner:username` - Filter by owner
- `owner:me` - Changes owned by current user
- `project:projectname` - Filter by project
- `branch:branchname` - Filter by branch
- `is:watched` - Changes being watched
- `is:reviewer` - Changes where you are a reviewer

You can combine multiple conditions:

```bash
gerrit change list -q "status:open project:myproject branch:main"
```

## FAQ

### Authentication Failed

Ensure your username and password are correct. Using Gerrit HTTP Token is recommended instead of account password.

Generate HTTP Token:
1. Log in to Gerrit
2. Go to Settings -> HTTP Credentials
3. Click "GENERATE NEW PASSWORD"
4. Set the generated token as `GERRIT_TOKEN` environment variable

### Network Timeout

If your Gerrit server is slow, you might encounter timeout issues. Current timeout is set to 30 seconds. To adjust, modify the `timeout` parameter in `src/gerrit_cli/client/api.py`.

### Query Syntax Error

Ensure your query conditions comply with Gerrit query syntax. Refer to [Gerrit Official Documentation](https://gerrit-review.googlesource.com/Documentation/user-search.html).
