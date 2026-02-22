# Release Skill

This skill handles the complete release process for sqla-repository.

## When to Use

Use this skill when the user asks to:
- "Create a release"
- "Release version X.X.X"
- "Bump version and release"
- "Publish a new version"

## Release Process

Follow these steps in order, when no outstanding changes exist skip to step 2 and 3

1. **Update Version**
   - Edit `pyproject.toml` and update the `version` field to the target version
   - Use semantic versioning (e.g., 0.1.4, 0.2.0, 1.0.0)

2. **Commit Changes**
   - Stage all outstanding changes: `git add -A`
   - Commit with message format:
     ```
     Release v{VERSION}
     
     Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
     ```
   - Or if only version bump: `Version Bump` as the message

3. **Push Changes**
   - Push to main branch: `git push`

4. **Create and Push Tag**
   - Create annotated tag: `git tag v{VERSION}`
   - Push tag: `git push origin v{VERSION}`

5. **Create GitHub Release**
   - Use GitHub CLI: `gh release create v{VERSION} --title "v{VERSION}" --generate-notes`
   - This automatically generates release notes from commits

## Important Notes

- Always check `git status` first to see what changes exist
- Ensure that we are on the main branch before pushing
- The version in `pyproject.toml` must match the tag version
- Ensure all tests pass before releasing (run `poetry run pytest` if unsure)
- The GitHub CLI (`gh`) must be authenticated to create releases
- Review the diff of outstanding changes before committing
- The version in pyproject.toml must match the tag version
- Ensure all tests pass before releasing (run `poetry run pytest` if unsure)
- The GitHub CLI (`gh`) must be authenticated

## Example Commands

For version 0.1.4:
```bash
# Update pyproject.toml version to 0.1.4
poetry version 0.1.4
git add -A
git commit -m "Release v0.1.4

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
git push
git tag v0.1.4
git push origin v0.1.4
gh release create v0.1.4 --title "v0.1.4" --generate-notes
```

## Success Indicators

- Commit created and pushed successfully
- Tag created and pushed successfully
- GitHub release URL returned (https://github.com/cstotzer/sqla-repository/releases/tag/v{VERSION})
