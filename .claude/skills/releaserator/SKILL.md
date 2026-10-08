---
name: releaserator
description: Generate semantic versioned releases with changelog and GitHub releases
allowed-tools: Read, Write, Edit, Bash(git:*), Bash(gh:*), Bash(command:*), Bash(test:*), Grep, Glob, AskUserQuestion
---

# Releaserator Skill

Automate the release process with semantic versioning, Keep A Changelog format, and GitHub release creation.

## Implementation Steps

### Step 1: Pre-flight Checks

**Task**: Verify repository state is clean and ready for release

Run these checks:

```bash
# Check git status (must be clean)
git status --porcelain

# Check current branch
git branch --show-current

# Detect version file (check in priority order)
for f in .claude-plugin/plugin.json package.json pyproject.toml Cargo.toml; do
  test -f "$f" && echo "VERSION_FILE=$f" && break
done

# Check for gh CLI
command -v gh >/dev/null 2>&1 && echo "INSTALLED" || echo "NOT_FOUND"
```

**Validation**:

- Working directory MUST be clean (no uncommitted changes)
  - If dirty: Error with message: "Working directory has uncommitted changes. Please commit or stash changes before creating a release."
- Current branch SHOULD be main/master
  - If not: Ask user to confirm creating release from current branch
- A supported version file MUST exist (one of the following, checked in order):
  - `.claude-plugin/plugin.json` — Claude Code plugin
  - `package.json` — Node.js project
  - `pyproject.toml` — Python project (version in `[project]` or `[tool.poetry]`)
  - `Cargo.toml` — Rust project (version in `[package]`)
  - If none found: Error with message: "No supported version file found. Releaserator supports: plugin.json, package.json, pyproject.toml, Cargo.toml"
- gh CLI MUST be installed
  - If missing: Error with message: "GitHub CLI (gh) not found. Install with: brew install gh"

**Store**:
- `VERSION_FILE` = path to the detected version file

**Optional check**: Verify docs/CONTEXT.md is recent (< 24 hours old)
- If stale: Warn user and suggest running `/session-wrapup` first

### Step 2: Determine Current Version and Last Release

**Task**: Read current version and find last release tag

```bash
# Read current version from VERSION_FILE (use Read tool)
# Parse the version field based on file type (see below)

# Find last tag (if any)
git describe --tags --abbrev=0 2>/dev/null || echo "NO_TAGS"

# List all tags for reference
git tag --list --sort=-version:refname
```

**Version parsing by file type**:

| Version File | How to read version |
|---|---|
| `.claude-plugin/plugin.json` | JSON field `"version"` |
| `package.json` | JSON field `"version"` |
| `pyproject.toml` | `[project] version = "X.Y.Z"` or `[tool.poetry] version = "X.Y.Z"` |
| `Cargo.toml` | `[package] version = "X.Y.Z"` |

**Logic**:

- Read and parse version from VERSION_FILE
- If no tags exist, this is first release (baseline: use all commits)
- If tags exist, use latest tag as baseline for commit collection

**Store**:
- `CURRENT_VERSION` = version from VERSION_FILE
- `LAST_TAG` = latest git tag (or "NO_TAGS")
- `IS_FIRST_RELEASE` = true if no tags exist

### Step 3: Collect Commits Since Last Release

**Task**: Get all commits since last release for changelog generation

```bash
# If tags exist: commits since last tag
git log LAST_TAG..HEAD --oneline --no-merges

# If no tags: all commits (first release)
git log --oneline --no-merges
```

**Parse each commit**:

For each commit line, extract:
- **Commit hash** (first 7 characters)
- **Commit type** (feat, fix, docs, refactor, perf, chore, test, ci, build, style)
- **Scope** (optional, in parentheses)
- **Breaking change indicator** (exclamation mark before colon)
- **Description** (after colon)
- **PR reference** (look for PR number pattern)

**Example parsing**:
```
abc1234 feat(auth): add OAuth support (#42)
→ hash: abc1234
→ type: feat
→ scope: auth
→ breaking: false
→ description: add OAuth support
→ pr: 42
```

**Check commit body for BREAKING CHANGE**:

For commits that might have breaking changes, also check the full commit message:

```bash
git log LAST_TAG..HEAD --format="%H %s%n%b%n---" --no-merges
```

Look for `BREAKING CHANGE:` in commit body.

**Store parsed commits** in a data structure:
```
commits = [
  {hash, type, scope, breaking, description, pr},
  ...
]
```

### Step 4: Determine Version Bump

**Task**: Analyze commits to determine MAJOR.MINOR.PATCH bump

**Rules** (Conventional Commits):

1. **MAJOR bump** if ANY commit has:
   - BREAKING CHANGE in commit body/footer, OR
   - Exclamation mark before colon (e.g., feat!, fix!)

2. **MINOR bump** if (and no MAJOR):
   - ANY `feat:` commits exist

3. **PATCH bump** if (and no MAJOR/MINOR):
   - ANY `fix:` or `perf:` commits exist

4. **No bump** if only:
   - `docs:`, `refactor:`, `chore:`, `test:`, `ci:`, `build:`, `style:`

**Calculate new version**:

```python
# Pseudocode for version bump
def bump_version(current, bump_type):
    major, minor, patch = map(int, current.split('.'))

    if bump_type == 'MAJOR':
        return f"{major + 1}.0.0"
    elif bump_type == 'MINOR':
        return f"{major}.{minor + 1}.0"
    elif bump_type == 'PATCH':
        return f"{major}.{minor}.{patch + 1}"
    else:
        return current  # No bump
```

**Edge case**: If no version bump needed (only docs/chore commits), ask user:
```
⚠️ No version bump needed (only documentation/chore commits).
Do you want to create a release anyway? (y/N)
```

**Store**:
- `BUMP_TYPE` = "MAJOR" | "MINOR" | "PATCH" | "NONE"
- `NEW_VERSION` = calculated new version

### Step 5: Generate Changelog Entry

**Task**: Create Keep A Changelog formatted entry for this release

**Group commits by section**:

| Commit Type | Changelog Section | Variable |
|-------------|-------------------|----------|
| `feat:` | Added | ADDED |
| `refactor:` (behavior change) | Changed | CHANGED |
| Mentions "deprecat" | Deprecated | DEPRECATED |
| Mentions "remov" | Removed | REMOVED |
| `fix:` | Fixed | FIXED |
| Mentions "security" or "CVE" | Security | SECURITY |

**Format each commit line**:

```markdown
- Description ([#PR](https://github.com/OWNER/REPO/pull/PR)) ([hash](https://github.com/OWNER/REPO/commit/hash))
```

If no PR reference, omit PR link. Always include commit hash link.

**Breaking changes**:

Collect all breaking changes (commits with exclamation mark or BREAKING CHANGE) and add to the top of the relevant section with ⚠️:

```markdown
- ⚠️ **BREAKING**: Description of breaking change
```

**Extract repo info**:

```bash
# Get remote URL and parse owner/repo
git remote get-url origin
# Parse: git@github.com:owner/repo.git → owner/repo
# Or: https://github.com/owner/repo.git → owner/repo
```

**Load template**: Read `skills/releaserator/templates/changelog-entry.md`

**Substitute variables**:
- `{{VERSION}}` → NEW_VERSION
- `{{DATE}}` → today's date (ISO format: YYYY-MM-DD)
- `{{ADDED}}` → formatted commit lines (or empty if none)
- `{{CHANGED}}` → formatted commit lines (or empty if none)
- `{{DEPRECATED}}` → formatted commit lines (or empty if none)
- `{{REMOVED}}` → formatted commit lines (or empty if none)
- `{{FIXED}}` → formatted commit lines (or empty if none)
- `{{SECURITY}}` → formatted commit lines (or empty if none)
- `{{BREAKING}}` → breaking changes summary (or omit section if none)

**Remove empty sections**: If a section has no commits, remove the entire section heading and content.

**Store**: `CHANGELOG_ENTRY` = generated markdown

### Step 6: Update or Create CHANGELOG.md

**Task**: Prepend new version entry to CHANGELOG.md

**Check if CHANGELOG.md exists**:

```bash
test -f CHANGELOG.md && echo "EXISTS" || echo "MISSING"
```

**If CHANGELOG.md exists**:

1. Read existing CHANGELOG.md
2. Find insertion point:
   - If `## [Unreleased]` exists, insert after it
   - Otherwise, insert after the header (before first version)
3. Insert CHANGELOG_ENTRY
4. Update comparison links at bottom:
   - Add new version link: `[VERSION]: https://github.com/OWNER/REPO/releases/tag/vVERSION`
   - Update Unreleased link: `[Unreleased]: https://github.com/OWNER/REPO/compare/vVERSION...HEAD`

**If CHANGELOG.md doesn't exist**:

1. Load template: `skills/releaserator/templates/CHANGELOG.md`
2. Substitute variables:
   - `{{VERSION}}` → NEW_VERSION
   - `{{DATE}}` → today's date
   - `{{REPO}}` → owner/repo from git remote
   - `{{ADDED}}`, `{{CHANGED}}`, etc. → from CHANGELOG_ENTRY
3. Write new CHANGELOG.md

**Use Write tool** to create/update CHANGELOG.md

### Step 7: Update Version File

**Task**: Write new version to VERSION_FILE

**By file type**:

| Version File | How to update |
|---|---|
| `.claude-plugin/plugin.json` | Update JSON `"version"` field. Use 2-space indentation, trailing newline. |
| `package.json` | Update JSON `"version"` field. Preserve existing indentation and trailing newline. |
| `pyproject.toml` | Replace `version = "OLD"` with `version = "NEW"` in the correct section. |
| `Cargo.toml` | Replace `version = "OLD"` with `version = "NEW"` in the `[package]` section. |

**Use Read and Edit tools** for precise replacement.

### Step 8: Commit Version Bump

**Task**: Create commit for version and changelog changes

```bash
# Stage files (VERSION_FILE is the detected version file from Step 1)
git add VERSION_FILE CHANGELOG.md

# Create commit
git commit -m "chore: bump version to NEW_VERSION"
```

**Commit message format**: `chore: bump version to X.Y.Z`

This follows conventional commits (type: chore, as it's a release task).

**Store commit hash** for later reference:
```bash
git rev-parse HEAD
```

### Step 9: Create Git Tag

**Task**: Create annotated git tag for release

```bash
# Create annotated tag (not lightweight)
git tag -a vNEW_VERSION -m "Release vNEW_VERSION"
```

**Tag format**: `v` prefix + semantic version (e.g., `v1.2.3`)

**Annotated tags** are used (not lightweight) so they contain:
- Tagger name and email
- Tag date
- Tag message

### Step 10: Push Changes and Tag

**Task**: Push commit and tag to remote

**Ask user for confirmation**:

```
Ready to push release v1.2.3 to remote?
- Commit: abc1234 "chore: bump version to 1.2.3"
- Tag: v1.2.3

This will:
1. Push commit to main branch
2. Push tag v1.2.3
3. Trigger any CI/CD workflows

Continue? (y/N)
```

**If confirmed**:

```bash
# Push commit to current branch
git push origin $(git branch --show-current)

# Push tag
git push origin vNEW_VERSION
```

**If not confirmed**: Stop here and report that release is ready locally but not pushed.

### Step 11: Create GitHub Release

**Task**: Create GitHub release using gh CLI

**Prepare release notes file** (temporary file):

1. Load template: `skills/releaserator/templates/release-notes.md`
2. Substitute variables:
   - `{{VERSION}}` → NEW_VERSION
   - `{{CHANGELOG_ENTRY}}` → the changelog entry content
   - `{{REPO}}` → owner/repo
3. Write to temporary file (e.g., /tmp/release-notes-NEW_VERSION.md)

**Create GitHub release**:

```bash
gh release create vNEW_VERSION --title "vNEW_VERSION" --notes-file /tmp/release-notes-NEW_VERSION.md
```

**Flags explained**:
- `vNEW_VERSION`: Tag name (must already exist from step 9)
- `--title`: Release title shown on GitHub
- `--notes-file`: Release body (our changelog entry + links)

**Capture release URL**:

```bash
# Get release URL
gh release view vNEW_VERSION --json url --jq .url
```

**Store**: `RELEASE_URL` = GitHub release URL

### Step 12: Report Success

**Task**: Display release information to user

Output a summary:

```markdown
✅ Release vNEW_VERSION created successfully!

**Changes**:
- Updated VERSION_FILE (OLD_VERSION → NEW_VERSION)
- Created/updated CHANGELOG.md with entry for vNEW_VERSION
- Committed changes (abc1234: "chore: bump version to NEW_VERSION")
- Created git tag vNEW_VERSION
- Pushed commit and tag to remote
- Created GitHub release: RELEASE_URL

**Release includes**:
- X features added
- Y bugs fixed
- Z changes made

**Next steps**:
- Announce release to users
- Update plugin registry (if applicable)
- Monitor for issues in new release
- Continue development

View release: RELEASE_URL
View changelog: https://github.com/OWNER/REPO/blob/main/CHANGELOG.md
```

---

## Template Variables

Templates use `{{VARIABLE}}` substitution syntax:

| Variable | Description | Example |
|----------|-------------|---------|
| `{{VERSION}}` | New version number | "1.2.3" |
| `{{VERSION_TAG}}` | Version with v prefix | "v1.2.3" |
| `{{OLD_VERSION}}` | Previous version | "1.2.2" |
| `{{DATE}}` | Release date (ISO) | "2026-01-11" |
| `{{REPO}}` | GitHub owner/repo | "owner/repo" |
| `{{ADDED}}` | Added section content | "- New feature\n- Another feature" |
| `{{CHANGED}}` | Changed section content | "- Updated behavior" |
| `{{DEPRECATED}}` | Deprecated section | "- Old API deprecated" |
| `{{REMOVED}}` | Removed section | "- Dropped support for X" |
| `{{FIXED}}` | Fixed section | "- Bug fix" |
| `{{SECURITY}}` | Security section | "- CVE fix" |
| `{{BREAKING}}` | Breaking changes summary | "⚠️ **BREAKING**: API changed" |
| `{{CHANGELOG_ENTRY}}` | Full changelog entry | (entire entry content) |

---

## Error Handling

### Dirty Working Directory

**Error**: Git status shows uncommitted changes

**Message**:
```
❌ Working directory has uncommitted changes.
Please commit or stash changes before creating a release.

Run: git status
```

**Action**: Exit without making any changes

### No gh CLI

**Error**: `gh` command not found

**Message**:
```
❌ GitHub CLI (gh) not found.

Install with: brew install gh

After installing, run: gh auth login
```

**Action**: Exit without making any changes

### Version Conflict

**Error**: Tag vX.Y.Z already exists

**Message**:
```
❌ Version X.Y.Z already exists as git tag.
Current version in VERSION_FILE: X.Y.Z
Existing tag: vX.Y.Z

Please update the version manually in VERSION_FILE,
or delete the tag if it was created in error:
  git tag -d vX.Y.Z
  git push origin :refs/tags/vX.Y.Z
```

**Action**: Exit without making any changes

### No Commits Since Last Release

**Error**: No new commits found

**Message**:
```
⚠️ No commits found since last release vX.Y.Z

Current HEAD: abc1234
Last release tag: vX.Y.Z (abc1234)

These are the same commit. Nothing to release.
```

**Action**: Exit without making any changes

### No Version Bump Needed

**Warning**: Only docs/chore commits

**Message**:
```
⚠️ No version bump needed (only documentation/chore commits).

Commits since v1.2.3:
- docs: update README
- chore: fix typo in comment

Do you want to create a release anyway? This will keep version at 1.2.3. (y/N)
```

**Action**: Ask user to confirm, proceed if yes

### Plugin Not in GitHub

**Error**: Remote URL is not GitHub

**Message**:
```
❌ This plugin is not hosted on GitHub.

Remote URL: https://gitlab.com/owner/repo.git

The releaserator currently only supports GitHub.
GitLab and Gitea support coming soon!
```

**Action**: Exit without making any changes

---

## Platform Abstraction

**Current implementation**: GitHub-only

**GitHub-specific code** is isolated in:
- `skills/releaserator/platforms/github.md`

**Platform interface** (for future expansion):

1. **detect_platform()** - Detect hosting platform from git remote
2. **create_release(version, notes)** - Create platform release
3. **get_pr_link(number)** - Format PR link URL
4. **get_commit_link(hash)** - Format commit link URL
5. **check_cli()** - Check for platform CLI tool

**Platform detection logic**:

```bash
REMOTE_URL=$(git remote get-url origin 2>/dev/null)

if echo "$REMOTE_URL" | grep -q "github.com"; then
    PLATFORM="github"
elif echo "$REMOTE_URL" | grep -q "gitlab.com"; then
    PLATFORM="gitlab"
elif echo "$REMOTE_URL" | grep -qE "gitea|codeberg"; then
    PLATFORM="gitea"
else
    PLATFORM="unknown"
fi
```

**To add GitLab support**:

1. Create `skills/releaserator/platforms/gitlab.md`
2. Implement same interface methods for GitLab
3. Update SKILL.md to load platform-specific code based on detection
4. No changes needed to core logic (commit parsing, version bumping, changelog generation)

**Benefits**:
- GitHub implementation doesn't need refactoring when adding platforms
- Each platform has dedicated documentation file
- Core logic (steps 1-7, 9-12) stays unchanged
- Only step 8 (create release) and link formatting is platform-specific

---

## Common Issues and Solutions

### Issue: Tag already exists

**Cause**: Version bump calculation matched an existing tag

**Solution**: This shouldn't happen if logic is correct. If it does:
1. Check if plugin.json version was manually changed
2. Verify last tag detection works correctly
3. Ask user if they want to skip tagging or delete old tag

### Issue: Commit parsing fails

**Cause**: Commit messages don't follow Conventional Commits format

**Solution**:
- Parse commits that do follow format
- Group unparsed commits under "Other changes" section
- Warn user about non-standard commits

### Issue: Push fails (no permission)

**Cause**: User doesn't have push access to remote

**Solution**:
- Check git push output for authentication errors
- Suggest running `gh auth login` or setting up SSH keys
- Report that release is ready locally but not pushed

### Issue: GitHub release fails

**Cause**: `gh` CLI not authenticated

**Solution**:
```
❌ GitHub CLI authentication failed.

Run: gh auth login

Then try creating the release again.
```

### Issue: Can't determine repo owner/name

**Cause**: Git remote URL in unexpected format

**Solution**:
- Try multiple parsing patterns:
  - `git@github.com:owner/repo.git`
  - `https://github.com/owner/repo.git`
  - `https://github.com/owner/repo`
- Ask user to manually provide owner/repo if parsing fails

---

## Success Criteria

After running releaserator, verify:

- ✅ CHANGELOG.md created or updated with new entry
- ✅ CHANGELOG.md follows Keep A Changelog format
- ✅ Version file updated correctly (plugin.json, package.json, pyproject.toml, or Cargo.toml)
- ✅ Git commit created with conventional commit message
- ✅ Annotated git tag created (not lightweight)
- ✅ Tag pushed to remote
- ✅ GitHub release created with correct notes
- ✅ Release URL accessible and displays correctly
- ✅ All links in changelog work (commit hashes, PR numbers)
- ✅ Changelog sections correctly categorized (Added/Fixed/etc)
- ✅ Breaking changes marked with ⚠️ if present
- ✅ No errors or warnings during execution
