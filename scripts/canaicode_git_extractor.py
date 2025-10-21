import argparse
import os
import tempfile
import shutil
import pandas as pd
from datetime import date, datetime, time, timedelta
from typing import List, Dict
from git import Repo
from pydantic import BaseModel


class CommitMetrics(BaseModel):
    hash: str
    repository: str
    date: datetime
    author: str | None
    language: str
    added_lines: int
    removed_lines: int


class GitRepoConsumer:
    __DEFAULT_LANG = "Other"
    __EXT_TO_LANG = {
        ".py": "Python", ".ts": "TypeScript", ".js": "JavaScript",
        ".tsx": "TypeScript", ".jsx": "JavaScript", ".java": "Java",
        ".rb": "Ruby", ".go": "Go", ".rs": "Rust", ".cpp": "C++",
        ".c": "C", ".cs": "C#", ".php": "PHP", ".html": "HTML",
        ".css": "CSS", ".json": "JSON", ".txt": "Plain Text",
        ".md": "Markdown"
    }
    __NULL_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"

    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.repo = Repo(self.repo_path)

    def get_commits_by_date(self, date: date) -> List[CommitMetrics]:
        result: List[CommitMetrics] = []

        for commit in self.repo.iter_commits("--all"):
            commit_date = datetime.fromtimestamp(commit.committed_date).date()
            if commit_date != date:
                continue

            if not commit.parents:
                diff = self.repo.git.diff(self.__NULL_TREE, commit.hexsha, "--numstat")
            else:
                diff = self.repo.git.diff(
                    commit.parents[0].hexsha, commit.hexsha, "--numstat"
                )

            author: str | None = commit.author.email

            for line in diff.splitlines():
                parts = line.strip().split("\t")
                if len(parts) != 3:
                    continue

                added, removed, filename = parts
                if added == "-":
                    added = 0
                if removed == "-":
                    removed = 0

                language = self.__get_language(filename)
                result.append(
                    CommitMetrics(
                        added_lines=int(added),
                        author=author,
                        date=datetime.combine(commit_date, time.min),
                        hash=commit.hexsha,
                        language=language,
                        removed_lines=int(removed),
                        repository=os.path.basename(os.path.normpath(self.repo_path)),
                    )
                )
        return result

    def __get_language(self, filename: str) -> str:
        _, ext = os.path.splitext(filename)
        return self.__EXT_TO_LANG.get(ext, self.__DEFAULT_LANG)


def parse_date(input_str: str) -> date:
    try:
        return datetime.strptime(input_str, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Invalid date. Use the format YYYY-MM-DD.")


def process_repository(repo_input: str, start_date: date, end_date: date, verbose: bool = False) -> List[CommitMetrics]:
    # Check if input is a local path or a URL
    is_local_path = os.path.isdir(repo_input)

    if is_local_path:
        # Use local repository directly
        repo_path = os.path.abspath(repo_input)
        repo_name = os.path.basename(os.path.normpath(repo_path))
        temp_dir = None

        if verbose:
            print(f"Using local repository: {repo_path}")

        try:
            consumer = GitRepoConsumer(repo_path)
            all_commits: List[CommitMetrics] = []

            current_date = start_date
            while current_date <= end_date:
                if verbose:
                    print(f"Fetching commits from {repo_name} on {current_date}...")
                commits = consumer.get_commits_by_date(current_date)
                all_commits.extend(commits)
                current_date += timedelta(days=1)

            return all_commits
        except Exception as e:
            print(f"Error processing local repository {repo_path}: {e}")
            return []
    else:
        # Clone remote repository
        temp_dir = tempfile.mkdtemp()
        repo_name = os.path.splitext(os.path.basename(repo_input.rstrip("/")))[0]
        repo_path = os.path.join(temp_dir, repo_name)

        try:
            if verbose:
                print(f"Cloning {repo_input}...")
            Repo.clone_from(repo_input, repo_path)

            consumer = GitRepoConsumer(repo_path)
            all_commits: List[CommitMetrics] = []

            current_date = start_date
            while current_date <= end_date:
                if verbose:
                    print(f"Fetching commits from {repo_name} on {current_date}...")
                commits = consumer.get_commits_by_date(current_date)
                all_commits.extend(commits)
                current_date += timedelta(days=1)

            return all_commits
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract Git commits from repositories and export to Excel",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single repository
  %(prog)s /path/to/repo --start 2024-01-01 --end 2024-12-31
  %(prog)s https://github.com/user/repo.git -s 2024-01-01 -e 2024-12-31

  # Multiple repositories from file
  %(prog)s --file repos.txt --start 2024-01-01 --end 2024-12-31
  %(prog)s -f repos.txt -s 2024-01-01 -e 2024-12-31
        """
    )

    # Repository input (mutually exclusive group)
    repo_group = parser.add_mutually_exclusive_group(required=False)
    repo_group.add_argument(
        "repository",
        nargs="?",
        help="Repository URL or local path (single repository)"
    )
    repo_group.add_argument(
        "-f", "--file",
        metavar="FILE",
        help="Path to file containing multiple repository URLs/paths (one per line)"
    )

    # Date range arguments
    parser.add_argument(
        "-s", "--start",
        required=True,
        metavar="YYYY-MM-DD",
        help="Start date"
    )
    parser.add_argument(
        "-e", "--end",
        required=True,
        metavar="YYYY-MM-DD",
        help="End date"
    )

    # Verbose flag
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )

    args = parser.parse_args()

    # Custom validation for mutually exclusive group
    if not args.repository and not args.file:
        parser.error("Please provide either a repository path/URL or use --file to specify a file with repositories")

    if args.repository and args.file:
        parser.error("Cannot use both a repository argument and --file option at the same time")

    try:
        start_date = parse_date(args.start)
        end_date = parse_date(args.end)
    except ValueError as e:
        print(f"Error: {e}")
        return

    if start_date > end_date:
        print("Error: Start date is later than end date.")
        return

    repo_data: Dict[str, List[CommitMetrics]] = {}

    if args.file:
        # Process multiple repositories from file
        if not os.path.isfile(args.file):
            print(f"Error: File not found: {args.file}")
            return

        with open(args.file, "r", encoding="utf-8") as f:
            repo_inputs = [line.strip() for line in f if line.strip()]

        if not repo_inputs:
            print("Error: File is empty or contains no valid entries.")
            return
    else:
        # Process single repository
        repo_inputs = [args.repository]

    for repo_input in repo_inputs:
        commits = process_repository(repo_input, start_date, end_date, args.verbose)
        if commits:
            repo_name = commits[0].repository
            repo_data[repo_name] = commits

    if not repo_data:
        print("No commits found in the date range.")
        return

    output_file = f"commits_{start_date}_to_{end_date}.xlsx"
    with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:
        for repo_name, commits in repo_data.items():
            df = pd.DataFrame([c.model_dump() for c in commits])
            df.to_excel(writer, sheet_name=repo_name[:31], index=False)

    print(f"Export completed successfully: {output_file}")


if __name__ == "__main__":
    main()
