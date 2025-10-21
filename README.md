# Canaicode Git Extractor

Extract Git commits from repositories and export to Excel, with built-in GitHub Actions support.

## GitHub Actions (Recommended)

The easiest way to use this tool is via the **reusable workflow** - no files to copy, no maintenance needed!

### Quick Start

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

**That's it!** No Python files to copy. See [SETUP.md](SETUP.md) for detailed setup instructions.

### What You Get
- Automatic daily extraction (or manual trigger)
- Analyzes the current repository by default
- Excel file uploaded to your endpoint
- Backup artifact stored in GitHub Actions (30 days)
- Version pinning (`@main`, `@v1`, etc.)
- Centralized updates (no maintenance in your repos)

---

## CLI Usage (Local/Advanced)

If you want to run the extractor locally or outside GitHub Actions:

### Requirements

- Python 3.10+
- Git

### Installation

```bash
pip install -r requirements.txt
# or
pip install gitpython pandas pydantic xlsxwriter
```

### Usage

**Single repository:**
```bash
python scripts/canaicode_git_extractor.py /path/to/repo -s 2024-01-01 -e 2024-12-31
python scripts/canaicode_git_extractor.py https://github.com/user/repo.git -s 2024-01-01 -e 2024-12-31
```

**Multiple repositories from file:**
```bash
python scripts/canaicode_git_extractor.py -f repos.txt -s 2024-01-01 -e 2024-12-31
```

**Verbose output:**
```bash
python scripts/canaicode_git_extractor.py /path/to/repo -s 2024-01-01 -e 2024-12-31 -v
```

**Upload to endpoint:**
```bash
python scripts/upload_to_endpoint.py commits_2024-01-01_to_2024-12-31.xlsx \
  --url https://api.example.com/upload \
  --key YOUR_API_KEY
```

## Output

Creates `commits_YYYY-MM-DD_to_YYYY-MM-DD.xlsx` with one sheet per repository.

**Columns:** hash, repository, date, author, language, added_lines, removed_lines

Each row represents a file modified in a commit.
