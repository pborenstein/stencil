# GitHub Platform Adapter

Platform-specific operations for GitHub-hosted repositories.

## Platform Detection

**Check if repository is hosted on GitHub**:

```bash
REMOTE_URL=$(git remote get-url origin 2>/dev/null)

if echo "$REMOTE_URL" | grep -q "github.com"; then
    echo "GITHUB"
else
    echo "NOT_GITHUB"
fi
```

## Extract Repository Information

**Parse owner/repo from remote URL**:

```bash
REMOTE_URL=$(git remote get-url origin)

# Handle SSH format: git@github.com:owner/repo.git
# Handle HTTPS format: https://github.com/owner/repo.git
# Handle HTTPS without .git: https://github.com/owner/repo

REPO=$(echo "$REMOTE_URL" | sed -E 's#.*github\.com[:/]([^/]+/[^/]+)(\.git)?$#\1#' | sed 's/\.git$//')

echo "$REPO"  # Outputs: owner/repo
```

**Usage**:
```bash
REPO=$(git remote get-url origin | sed -E 's#.*github\.com[:/]([^/]+/[^/]+)(\.git)?$#\1#' | sed 's/\.git$//')
OWNER=$(echo "$REPO" | cut -d/ -f1)
REPO_NAME=$(echo "$REPO" | cut -d/ -f2)
```

## Check CLI Availability

**Verify GitHub CLI (gh) is installed**:

```bash
if command -v gh >/dev/null 2>&1; then
    echo "INSTALLED"
else
    echo "NOT_FOUND"
fi
```

**Check gh authentication status**:

```bash
gh auth status 2>&1
```

**Output interpretation**:
- If exits 0: Authenticated
- If exits 1: Not authenticated

## Format Links

### Get PR Link

Format: `https://github.com/{owner}/{repo}/pull/{number}`

```bash
REPO="owner/repo"
PR_NUMBER="123"

PR_LINK="https://github.com/${REPO}/pull/${PR_NUMBER}"
echo "$PR_LINK"
```

**In changelog markdown**:
```markdown
- Description ([#123](https://github.com/owner/repo/pull/123))
```

### Get Commit Link

Format: `https://github.com/{owner}/{repo}/commit/{hash}`

```bash
REPO="owner/repo"
COMMIT_HASH="abc1234"

COMMIT_LINK="https://github.com/${REPO}/commit/${COMMIT_HASH}"
echo "$COMMIT_LINK"
```

**In changelog markdown**:
```markdown
- Description ([abc1234](https://github.com/owner/repo/commit/abc1234))
```

### Get Comparison Link

Format: `https://github.com/{owner}/{repo}/compare/{base}...{head}`

```bash
REPO="owner/repo"
BASE_TAG="v1.0.0"
HEAD_TAG="v1.1.0"

COMPARE_LINK="https://github.com/${REPO}/compare/${BASE_TAG}...${HEAD_TAG}"
echo "$COMPARE_LINK"
```

**For Unreleased section**:
```markdown
[Unreleased]: https://github.com/owner/repo/compare/v1.1.0...HEAD
```

**For released versions**:
```markdown
[1.1.0]: https://github.com/owner/repo/compare/v1.0.0...v1.1.0
```

## Create Release

**Create GitHub release using gh CLI**:

```bash
VERSION_TAG="v1.2.3"
RELEASE_TITLE="v1.2.3"
NOTES_FILE="/tmp/release-notes-1.2.3.md"

gh release create "$VERSION_TAG" \
  --title "$RELEASE_TITLE" \
  --notes-file "$NOTES_FILE" \
  --generate-notes
```

**Flags**:
- `VERSION_TAG`: Git tag name (must already exist)
- `--title`: Release title displayed on GitHub
- `--notes-file`: Path to markdown file with release notes
- `--generate-notes`: GitHub auto-generates additional notes from PRs/commits

**Expected output**:
```
https://github.com/owner/repo/releases/tag/v1.2.3
```

**Error handling**:
```bash
if ! gh release create "$VERSION_TAG" --title "$RELEASE_TITLE" --notes-file "$NOTES_FILE" --generate-notes; then
    echo "❌ Failed to create GitHub release"
    echo "Tag exists but release creation failed. You can create it manually:"
    echo "  gh release create $VERSION_TAG"
    exit 1
fi
```

## Get Release URL

**Retrieve release URL after creation**:

```bash
VERSION_TAG="v1.2.3"

RELEASE_URL=$(gh release view "$VERSION_TAG" --json url --jq .url 2>/dev/null)

if [ -z "$RELEASE_URL" ]; then
    # Fallback: construct URL manually
    REPO=$(git remote get-url origin | sed -E 's#.*github\.com[:/]([^/]+/[^/]+)(\.git)?$#\1#' | sed 's/\.git$//')
    RELEASE_URL="https://github.com/${REPO}/releases/tag/${VERSION_TAG}"
fi

echo "$RELEASE_URL"
```

## List Releases

**Get list of existing releases**:

```bash
gh release list --limit 10
```

**Check if release exists**:

```bash
VERSION_TAG="v1.2.3"

if gh release view "$VERSION_TAG" >/dev/null 2>&1; then
    echo "Release $VERSION_TAG already exists"
else
    echo "Release $VERSION_TAG does not exist"
fi
```

## Error Messages

### Not Authenticated

```
❌ GitHub CLI authentication failed.

Run: gh auth login

Then try creating the release again.
```

### Not on GitHub

```
❌ This repository is not hosted on GitHub.

Remote URL: https://gitlab.com/owner/repo.git

The releaserator currently only supports GitHub.
GitLab and Gitea support coming soon!
```

### CLI Not Found

```
❌ GitHub CLI (gh) not found.

Install with:
  brew install gh

Or visit: https://cli.github.com/

After installing, authenticate with: gh auth login
```

## Platform-Specific Considerations

### GitHub-Specific Features

1. **Auto-generated release notes**: GitHub can auto-generate notes from PRs
   - Uses `--generate-notes` flag
   - Includes PR titles, authors, new contributors
   - Appended after custom notes

2. **PR references**: GitHub auto-links #123 patterns
   - In commit messages: "feat: add feature (#123)"
   - In changelog: Can use either `#123` or full URL

3. **Release assets**: Can attach files to releases
   - Not currently used by releaserator
   - Future feature: attach plugin ZIP

4. **Release types**: Draft, pre-release, latest
   - Releaserator creates latest releases
   - No draft or pre-release support yet

### Differences from GitLab

**GitHub** uses:
- `/pull/{number}` for PRs
- `gh` CLI tool
- `--generate-notes` flag

**GitLab** uses:
- `/-/merge_requests/{number}` for MRs
- `glab` CLI tool
- Different API structure

**Gitea/Forgejo** uses:
- `/pulls/{number}` for PRs
- `tea` CLI tool (for Gitea)
- Self-hosted, varying URL formats

## Testing

**Test platform detection**:
```bash
# Should return "owner/repo"
git remote get-url origin | sed -E 's#.*github\.com[:/]([^/]+/[^/]+)(\.git)?$#\1#' | sed 's/\.git$//'
```

**Test gh CLI**:
```bash
gh auth status
gh release list --limit 3
```

**Test link formatting**:
```bash
REPO="pborenstein/plinth"
echo "PR: https://github.com/${REPO}/pull/123"
echo "Commit: https://github.com/${REPO}/commit/abc1234"
echo "Compare: https://github.com/${REPO}/compare/v1.0.0...v1.1.0"
```

## Future Enhancements

**Potential additions**:

1. **Release assets**: Upload plugin ZIP to release
2. **Pre-release support**: Flag releases as beta/alpha
3. **Draft releases**: Create draft before publishing
4. **Discussion auto-creation**: Create discussion thread for release
5. **Announcement**: Post release to GitHub Discussions or Twitter

**For multi-platform support**:

Extract this adapter's interface and replicate for:
- GitLab (`platforms/gitlab.md`)
- Gitea (`platforms/gitea.md`)
- Codeberg (`platforms/codeberg.md`)
