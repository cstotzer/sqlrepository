# Chore Skill

This skill handles infrastructure changes that don't affect functionality.

## When to Use

Use this skill when the user asks to commit changes that are:
- "Infrastructure changes"
- "Chore" or "chore changes"
- Documentation updates (non-user-facing)
- CI/CD workflow changes
- Build configuration updates
- Development tooling changes

## What Qualifies as a Chore

Infrastructure changes include:
- GitHub Actions workflow modifications
- Build system configuration (pyproject.toml metadata, not version)
- Development dependency updates
- Linting/formatting configuration
- Testing infrastructure
- Documentation for developers (README, CONTRIBUTING, etc.)
- Skills and Copilot instructions

## Chore Process

Follow these steps in order:

1. **Create Feature Branch**
   - Branch name format: `chore/descriptive-name`
   - Example: `chore/add-ci-workflow`, `chore/update-docs`
   - Command: `git checkout -b chore/{descriptive-name}`

2. **Review Changes**
   - Check status: `git status`
   - Review diff: `git diff`
   - Ensure only infrastructure files are modified

3. **Stage Changes**
   - Stage all changes: `git add -A`
   - Or stage specific files: `git add {file1} {file2}`

4. **Commit Changes**
   - Format:
     ```
     chore: brief description in lowercase
     
     - Bullet point describing change 1
     - Bullet point describing change 2
     - Bullet point describing change 3
     
     Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
     ```
   - The first line should be concise (under 60 chars)
   - Use bullet points to list specific changes

5. **Push Branch**
   - Push to origin: `git push -u origin chore/{descriptive-name}`

6. **Create Pull Request**
   - Use GitHub CLI: `gh pr create --fill --base main`
   - This uses the commit message for title and body
   - The PR will be created and URL returned

## Important Notes

- **NO** release or version bump - chores don't change functionality
- Always create a branch - never commit directly to main
- Keep commits focused on a single type of infrastructure change
- List all significant changes in bullet points
- PR is automatically created after pushing the branch

## Example Workflow

For adding a CI workflow:
```bash
# Create branch
git checkout -b chore/add-ci-workflow

# Review changes
git status
git diff

# Stage and commit
git add .github/workflows/ci.yml
git commit -m "chore: add CI workflow for automated testing

- Add .github/workflows/ci.yml with ruff and pytest
- Run checks on push to main and all pull requests
- Test on Python 3.11 and 3.12

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

# Push branch
git push -u origin chore/add-ci-workflow

# Create PR
gh pr create --fill --base main
```

## Success Indicators

- Branch created successfully
- Changes committed with proper format
- Branch pushed to remote
- Pull request created and URL returned
