# Setup

## Prerequisites

- A GitHub repository
- Upload endpoint URL
- Authentication key for the endpoint

## Installation

### 1. Add GitHub Secrets

In your repository, go to **Settings** → **Secrets and variables** → **Actions**

Add these secrets:

| Name | Value |
|------|-------|
| `UPLOAD_ENDPOINT_URL` | Your endpoint URL |
| `UPLOAD_AUTH_KEY` | Your authentication key |

### 2. Create Workflow File

Create `.github/workflows/extract-commits.yml` in your repository:

```yaml
name: Extract Commits

on:
  schedule:
    - cron: '0 1 * * *'  # Daily at 1 AM UTC
  workflow_dispatch:

jobs:
  extract:
    uses: hfduran/canaicode-git-extractor/.github/workflows/extract-and-upload-reusable.yml@main
    secrets:
      upload_url: ${{ secrets.UPLOAD_ENDPOINT_URL }}
      upload_key: ${{ secrets.UPLOAD_AUTH_KEY }}
```

### 3. Done

Commit and push. The workflow will run daily at 1 AM UTC, or you can trigger it manually from the Actions tab.

## What It Does

- Extracts commits from your repository
- Creates an Excel file with commit data
- Uploads it to your endpoint
- Saves a backup in GitHub Actions artifacts (30 days)

## Options

**Analyze a different repository:**
```yaml
jobs:
  extract:
    uses: hfduran/canaicode-git-extractor/.github/workflows/extract-and-upload-reusable.yml@main
    with:
      repository: 'https://github.com/user/repo.git'
    secrets:
      upload_url: ${{ secrets.UPLOAD_ENDPOINT_URL }}
      upload_key: ${{ secrets.UPLOAD_AUTH_KEY }}
```

**Custom date range:**
```yaml
jobs:
  extract:
    uses: hfduran/canaicode-git-extractor/.github/workflows/extract-and-upload-reusable.yml@main
    with:
      start_date: '2024-01-01'
      end_date: '2024-12-31'
    secrets:
      upload_url: ${{ secrets.UPLOAD_ENDPOINT_URL }}
      upload_key: ${{ secrets.UPLOAD_AUTH_KEY }}
```

**Multiple repositories:** Create `repos.txt` in your repository with one URL per line, then:
```yaml
jobs:
  extract:
    uses: hfduran/canaicode-git-extractor/.github/workflows/extract-and-upload-reusable.yml@main
    with:
      use_repos_file: true
    secrets:
      upload_url: ${{ secrets.UPLOAD_ENDPOINT_URL }}
      upload_key: ${{ secrets.UPLOAD_AUTH_KEY }}
```
