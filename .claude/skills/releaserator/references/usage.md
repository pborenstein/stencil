# Releaserator

Automated release management with semantic versioning, changelog generation, and GitHub releases.

## What It Does

Releaserator automates the entire release process:

1. **Analyzes commits** since last release using Conventional Commits
2. **Determines version bump** (MAJOR.MINOR.PATCH) based on commit types
3. **Generates CHANGELOG.md** in Keep A Changelog format
4. **Updates version** in the project's version file (auto-detected)
5. **Creates git tag** (vX.Y.Z)
6. **Pushes to remote** (with confirmation)
7. **Creates GitHub release** with generated notes

## When to Use

Use releaserator when you're ready to publish a new version:

- After completing a development phase
- When significant features or fixes have accumulated
- Before announcing the project to users
- On a regular schedule (monthly, quarterly, etc.)

## Prerequisites

Before running releaserator:

1. **Clean working directory**
   - No uncommitted changes
   - Run `git status` to verify

2. **Session wrapped up**
   - Run `/session-wrapup` to update documentation
   - Ensure docs/CONTEXT.md is current

3. **GitHub CLI installed**
   - Install: `brew install gh`
   - Authenticate: `gh auth login`

4. **On main branch** (or confirm release from current branch)

## Usage

```bash
/releaserator
```

The command will guide you through the process and ask for confirmation before pushing.

## How It Works

### Version Bumping

Releaserator follows **Semantic Versioning** based on **Conventional Commits**:

**MAJOR bump** (X.0.0) - Breaking changes:
- Commits with `BREAKING CHANGE:` in body/footer
- Commits with exclamation mark before colon (e.g., `feat!: new API`)

**MINOR bump** (x.X.0) - New features:
- Commits starting with `feat:`

**PATCH bump** (x.x.X) - Bug fixes:
- Commits starting with `fix:` or `perf:`

**No bump** - Documentation/chores only:
- Commits starting with `docs:`, `chore:`, `refactor:`, `test:`, `ci:`

**Priority**: If multiple bump types exist, highest wins: MAJOR > MINOR > PATCH

**Example**:
```
Current version: 1.2.3
Commits since last release:
  - feat: add OAuth support
  - fix: handle null values
  - docs: update README

Result: MINOR bump → 1.3.0
```

### Changelog Generation

Releaserator generates Keep A Changelog formatted entries:

**Sections**:
- **Added**: `feat:` commits (new features)
- **Changed**: `refactor:` commits (behavior changes)
- **Deprecated**: Commits mentioning deprecation
- **Removed**: Commits removing features
- **Fixed**: `fix:` commits (bug fixes)
- **Security**: Commits mentioning security/CVE

**Format**:
```markdown
## [1.3.0] - 2026-01-11

### Added

- Add OAuth support ([#42](link)) ([abc1234](link))
- Add password reset flow ([def5678](link))

### Fixed

- Handle null values in user data ([#43](link)) ([789abcd](link))
```

**Breaking changes** are marked with ⚠️:
```markdown
### Added

- ⚠️ **BREAKING**: New API authentication method
```

### What Gets Created/Updated

**Files modified**:
- `CHANGELOG.md` - New entry prepended (or file created)
- Version file updated (auto-detected: `plugin.json`, `package.json`, `pyproject.toml`, or `Cargo.toml`)

**Git operations**:
- Commit: `chore: bump version to X.Y.Z`
- Tag: `vX.Y.Z` (annotated, not lightweight)
- Push: Commit and tag to remote

**GitHub**:
- Release created at tag
- Release notes from changelog entry
- Auto-generated notes from PRs

## Workflow Integration

Releaserator fits into the session workflow:

```bash
# 1. Start session
/session-pickup

# 2. Do work...

# 3. End session
/session-wrapup

# 4. Verify clean state
git status

# 5. Create release
/releaserator
```

**Pre-flight checks**:
- Working directory must be clean
- CONTEXT.md should be recent (< 24 hours)
- Current branch should be main (or you'll be asked to confirm)

## Examples

### First Release

```bash
$ /releaserator

Checking pre-flight...
✅ Working directory clean
✅ Session up-to-date (CONTEXT.md updated today)
✅ GitHub CLI installed and authenticated
✅ No existing tags (first release)

Analyzing commits...
Found 44 commits:
- 15 feat: commits
- 8 fix: commits
- 12 docs: commits
- 9 other commits

Version bump: MINOR (1.0.0 → 1.1.0)

Generating CHANGELOG.md...
✅ Created CHANGELOG.md with 23 entries

Updating plugin.json...
✅ Updated version: 1.0.0 → 1.1.0

Committing changes...
✅ Commit: abc1234 "chore: bump version to 1.1.0"

Creating tag...
✅ Created tag v1.1.0

Ready to push to remote?
- Commit: abc1234 "chore: bump version to 1.1.0"
- Tag: v1.1.0

Continue? (y/N): y

Pushing to remote...
✅ Pushed commit to main
✅ Pushed tag v1.1.0

Creating GitHub release...
✅ Release created: https://github.com/owner/repo/releases/tag/v1.1.0

🎉 Release v1.1.0 created successfully!

View release: https://github.com/owner/repo/releases/tag/v1.1.0
View changelog: https://github.com/owner/repo/blob/main/CHANGELOG.md
```

### Subsequent Release with Breaking Change

```bash
$ /releaserator

Analyzing commits since v1.1.0...
Found 7 commits:
- 2 feat: commits (1 with BREAKING CHANGE)
- 3 fix: commits
- 2 docs: commits

⚠️ BREAKING CHANGE detected in:
  feat!: change authentication API (#45)

Version bump: MAJOR (1.1.0 → 2.0.0)

Breaking changes will be marked with ⚠️ in changelog.

Continue? (y/N): y

Updating CHANGELOG.md...
✅ Prepended entry for v2.0.0

[... rest of release process ...]

🎉 Release v2.0.0 created successfully!
```

### No Version Bump Needed

```bash
$ /releaserator

Analyzing commits since v1.1.0...
Found 3 commits:
- docs: update README
- docs: fix typo
- chore: update gitignore

⚠️ No version bump needed (only documentation/chore commits).

Do you want to create a release anyway? This will keep version at 1.1.0. (y/N): n

Release canceled. No changes made.
```

## Error Scenarios

### Uncommitted Changes

```
❌ Working directory has uncommitted changes.
Please commit or stash changes before creating a release.

Run: git status
```

**Solution**: Commit or stash your changes first.

### GitHub CLI Not Found

```
❌ GitHub CLI (gh) not found.

Install with: brew install gh

After installing, run: gh auth login
```

**Solution**: Install and authenticate gh CLI.

### GitHub CLI Not Authenticated

```
❌ GitHub CLI authentication failed.

Run: gh auth login

Then try creating the release again.
```

**Solution**: Authenticate with GitHub.

### Not on GitHub

```
❌ This repository is not hosted on GitHub.

Remote URL: https://gitlab.com/owner/repo.git

The releaserator currently only supports GitHub.
GitLab and Gitea support coming soon!
```

**Solution**: Currently, releaserator only works with GitHub repositories.

## Troubleshooting

### Issue: Tag already exists

**Symptom**: Error about tag vX.Y.Z already existing

**Cause**: Version in the version file might have been manually changed

**Solution**:
1. Check existing tags: `git tag -l`
2. Either delete the old tag if it was created in error:
   ```bash
   git tag -d vX.Y.Z
   git push origin :refs/tags/vX.Y.Z
   ```
3. Or manually update the version file to a higher version

### Issue: Push fails

**Symptom**: Git push fails with authentication error

**Cause**: No push permission or authentication issue

**Solution**:
1. Check GitHub authentication: `gh auth status`
2. Re-authenticate: `gh auth login`
3. Verify you have push access to the repository

### Issue: Commits don't follow format

**Symptom**: Changelog has "Other changes" section or empty sections

**Cause**: Commit messages don't follow Conventional Commits format

**Solution**:
- Review commit message format: `type(scope): description`
- Example: `feat(auth): add OAuth support`
- Use types: feat, fix, docs, refactor, perf, test, chore, ci, build, style
- Rebase commits to fix messages if needed (before release)

### Issue: Wrong version bump

**Symptom**: Version bumped more/less than expected

**Cause**: Commit types might not match intent

**Solution**:
- Review commits: `git log vX.Y.Z..HEAD --oneline`
- Check commit types match changes (feat vs fix vs docs)
- Manually adjust the version in your project's version file if needed

## Platform Support

**Current**: GitHub only

**Future**: GitLab and Gitea support planned

Platform-specific code is isolated in `platforms/` directory for easy expansion.

## Advanced Usage

### Manual Version Override

If you need a specific version (not calculated):

1. Manually update the version in your project's version file
2. Run `/releaserator`
3. It will use your version instead of calculating

### Skipping Confirmation

Currently, releaserator always asks for confirmation before pushing. This is intentional for safety.

### Pre-release Versions

Pre-release versions (alpha, beta, rc) are not currently supported. This feature may be added in the future.

## Supported Version Files

Releaserator auto-detects the project's version file, checked in this order:

| File | Project Type |
|---|---|
| `.claude-plugin/plugin.json` | Claude Code plugin |
| `package.json` | Node.js |
| `pyproject.toml` | Python |
| `Cargo.toml` | Rust |

## Files Created

After running releaserator, you'll have:

- `CHANGELOG.md` - Project changelog (created or updated)
- Updated version in the project's version file
- Git commit for version bump
- Git tag (vX.Y.Z)
- GitHub release

## Keep A Changelog Format

The changelog follows the [Keep A Changelog](https://keepachangelog.com/) format:

- Human-readable
- Organized by version (newest first)
- Standard sections (Added, Changed, Fixed, etc.)
- ISO date format (YYYY-MM-DD)
- Links to releases and comparisons

**Example**:
```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.3.0] - 2026-01-11

### Added
- Feature 1
- Feature 2

### Fixed
- Bug fix 1

[Unreleased]: https://github.com/owner/repo/compare/v1.3.0...HEAD
[1.3.0]: https://github.com/owner/repo/releases/tag/v1.3.0
```

## Resources

**Semantic Versioning**: https://semver.org/

**Conventional Commits**: https://www.conventionalcommits.org/

**Keep A Changelog**: https://keepachangelog.com/

**GitHub CLI**: https://cli.github.com/

## Feedback

Found a bug or have a suggestion? Open an issue in the plinth repository.
