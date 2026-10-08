---
name: git-workflow-hooks
description: Install git hooks to prevent common workflow mistakes
allowed-tools: Read, Write, Bash(chmod:*), Bash(test:*), Bash(cp:*), Bash(git:*)
---

# Git Workflow Hooks Skill

Install git hooks that prevent common workflow mistakes in your development process.

## What This Does

Installs a pre-push git hook that:

- **Blocks manual version tag pushes**: Prevents pushing tags like `v1.2.3` without using `/plinth:releaserator`
- **Ensures proper release process**: Guarantees changelog generation, version bumping, and release notes
- **Provides clear error messages**: Explains why the push was blocked and how to do it correctly
- **Allows emergency override**: Use `git push --no-verify` if you absolutely must bypass

## When To Use This

Run this skill once per project to install the hooks:

- **New projects**: Set up workflow guardrails from the start
- **After manual tag incidents**: Prevent recurrence of accidentally pushing tags
- **Team projects**: Ensure all contributors follow the same release process

## Implementation Steps

### Step 1: Verify Git Repository

Check that we're in a git repository with a hooks directory:

```bash
# Check for .git directory
test -d .git && echo "GIT_REPO" || echo "NOT_GIT"

# Check hooks directory
test -d .git/hooks && echo "HOOKS_EXIST" || echo "HOOKS_MISSING"
```

**Validation**:

- MUST be in a git repository
  - If not: Error with "Not a git repository. Run this from the project root."
- Hooks directory MUST exist (it should by default)
  - If missing: Create it with `mkdir -p .git/hooks`

### Step 2: Check for Existing pre-push Hook

Check if a pre-push hook already exists:

```bash
test -f .git/hooks/pre-push && echo "EXISTS" || echo "MISSING"
```

**If hook exists**:

1. Read the existing hook file
2. Check if it was installed by plinth (look for "Installed by: /plinth:git-workflow-hooks")
3. If plinth-installed: Ask user if they want to overwrite
4. If not plinth-installed: **Stop and ask user** how to proceed:
   - Backup existing hook and install ours
   - Append our hook logic to existing file
   - Skip installation

**Example user prompt** (if non-plinth hook exists):

```
⚠️ Existing pre-push hook detected

Your .git/hooks/pre-push file already contains a hook that wasn't installed by plinth.

How would you like to proceed?

1. Backup existing hook to .git/hooks/pre-push.backup and install plinth hook
2. Skip installation (keep existing hook)

Choose an option (1-2):
```

### Step 3: Install pre-push Hook

Copy the hook from the skill directory to the git hooks directory:

```bash
# Copy hook file
cp skills/git-workflow-hooks/pre-push .git/hooks/pre-push

# Make executable
chmod +x .git/hooks/pre-push
```

**Verify installation**:

```bash
# Check file exists
test -f .git/hooks/pre-push && echo "INSTALLED" || echo "FAILED"

# Check executable
test -x .git/hooks/pre-push && echo "EXECUTABLE" || echo "NOT_EXECUTABLE"
```

**If backup was requested** (from Step 2):

```bash
# Backup existing hook first
cp .git/hooks/pre-push .git/hooks/pre-push.backup
```

### Step 4: Test Hook Installation

Verify the hook works by checking its output:

```bash
# Test that the hook script is valid bash
bash -n .git/hooks/pre-push && echo "VALID" || echo "SYNTAX_ERROR"
```

**If syntax error**: Report the error and suggest manual inspection.

### Step 5: Report Success

Display installation summary to user:

```
✅ Git workflow hooks installed successfully!

**Installed hooks**:
- pre-push: Blocks manual version tag pushes

**What this means**:
- You cannot push version tags (v*.*.*)  directly
- Use /plinth:releaserator to create releases properly
- Emergency override: git push --no-verify

**Testing the hook**:
Try pushing a version tag to see it in action:
  git tag v99.99.99
  git push origin v99.99.99
  (This should be blocked with a helpful error message)

**Removing the hook**:
If you need to uninstall:
  rm .git/hooks/pre-push
```

**If backup was created**:

Add to output:
```
**Backup created**:
- Your original hook saved to: .git/hooks/pre-push.backup
```

---

## Hook Behavior Details

### Pre-Push Hook

**Triggers**: When you run `git push`

**Checks**:

1. Is this a tag push? (refs/tags/*)
2. Does the tag match version pattern? (v*.*.*)

**Action if match**:

- Block the push (exit 1)
- Display error message with:
  - What was blocked
  - Why it was blocked
  - Correct way to do it (/plinth:releaserator)
  - Emergency override (--no-verify)

**Allows**:

- All branch pushes
- Non-version tags (v0.0.1-alpha, feature-tags, etc. are allowed)
- Pushes with --no-verify flag

**Version tag pattern**:

```regex
^v[0-9]+\.[0-9]+\.[0-9]+
```

Matches:
- `v1.0.0` ✓
- `v1.2.3` ✓
- `v10.20.30` ✓

Does not match:
- `v1.0.0-alpha` ✗ (pre-release allowed)
- `v1.0.0-rc.1` ✗ (release candidate allowed)
- `feature-v1` ✗ (not a version tag)
- `1.0.0` ✗ (missing v prefix)

This intentionally allows pre-release tags since they may have different workflows.

---

## Error Handling

### Not a Git Repository

**Error**: No .git directory found

**Message**:
```
❌ Not a git repository

This skill must be run from the root of a git repository.

Run: git init
```

**Action**: Exit without making changes

### Non-Plinth Hook Exists

**Warning**: Existing pre-push hook not installed by plinth

**Message**:
```
⚠️ Existing pre-push hook detected

Your .git/hooks/pre-push file contains a hook not installed by plinth.
```

**Action**: Ask user how to proceed (backup vs skip)

### Hook Installation Failed

**Error**: Failed to copy or chmod hook

**Message**:
```
❌ Failed to install pre-push hook

Could not copy hook file to .git/hooks/pre-push or make it executable.

Check permissions on .git/hooks/ directory.
```

**Action**: Report failure and suggest manual inspection

### Hook Syntax Error

**Error**: Hook file has bash syntax error

**Message**:
```
❌ Hook has syntax errors

The installed hook at .git/hooks/pre-push has bash syntax errors.

Please report this issue: https://github.com/pborenstein/plinth/issues
```

**Action**: Report error but don't remove hook (let user inspect)

---

## Future Enhancements

This skill can be extended with additional hooks:

### Pre-Commit Hook Ideas

- **Prevent docs/ commits without session-wrapup**: Remind user to use `/plinth:session-wrapup`
- **Block .DS_Store commits**: Auto-add to .gitignore instead
- **Check for merge conflict markers**: Prevent accidental commits of `<<<<<<`

### Commit-Msg Hook Ideas

- **Enforce conventional commits**: Validate commit message format
- **Suggest using releaserator**: If message is "bump version" or similar

### Post-Merge Hook Ideas

- **Remind to run session-pickup**: After pulling changes, suggest reading context
- **Check for dependency updates**: Alert if package.json changed

**Adding new hooks**:

1. Create new hook script in `skills/git-workflow-hooks/`
2. Update Step 3 to install multiple hooks
3. Document the new hook in this file
4. Test on real projects

---

## Success Criteria

After running this skill, verify:

- ✅ pre-push hook installed at `.git/hooks/pre-push`
- ✅ Hook is executable (`-x` permission)
- ✅ Hook contains plinth identification comment
- ✅ Hook blocks version tag pushes (test with dummy tag)
- ✅ Hook allows normal branch pushes
- ✅ Hook displays helpful error messages
- ✅ Emergency override works (`--no-verify`)
- ✅ Existing hooks backed up if present
