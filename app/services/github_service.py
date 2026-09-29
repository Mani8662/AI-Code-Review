import os
import re

from dotenv import load_dotenv
from github import Github, Auth

from app.models.review_models import PullRequestInput


load_dotenv()


class GitHubService:
    """Fetch GitHub repositories, branches, commits and pull requests."""

    def __init__(self):
        token = os.getenv("GITHUB_TOKEN")

        if not token:
            raise ValueError("GITHUB_TOKEN is not configured")

        self.token = token
        self.client = Github(auth=Auth.Token(token))

    def parse_repository_url(self, url: str) -> str:
        pattern = r"^https?://github\.com/([^/]+/[^/]+)/?$"

        match = re.match(pattern, url.strip())

        if not match:
            raise ValueError(
                "Invalid GitHub repository URL. "
                "Expected: https://github.com/owner/repository"
            )

        return match.group(1)

    # =========================================================
    # BRANCHES
    # =========================================================

    def get_branches(
        self,
        repository_url: str,
    ) -> list[dict]:
        """
        Get repository branches and their latest commits.

        Each branch includes:
        - branch name
        - latest commit SHA
        - latest commit message
        - commit author
        - commit date
        """

        repository = self.parse_repository_url(repository_url)

        repo = self.client.get_repo(repository)

        branches = repo.get_branches()

        results = []

        for branch in branches:
            try:
                commit = repo.get_commit(branch.name)

                commit_message = (
                    commit.commit.message.split("\n")[0]
                    if commit.commit.message
                    else ""
                )

                author = ""

                if commit.author:
                    author = commit.author.login

                elif commit.commit.author:
                    author = (
                        commit.commit.author.name
                        or ""
                    )

                commit_date = None

                if commit.commit.author:
                    commit_date = commit.commit.author.date

                results.append(
                    {
                        "name": branch.name,
                        "sha": commit.sha,
                        "message": commit_message,
                        "author": author,
                        "date": commit_date,
                    }
                )

            except Exception as exc:
                print(
                    f"Warning: Could not inspect branch "
                    f"{branch.name}: {exc}"
                )

        return results

    # =========================================================
    # LATEST COMMIT
    # =========================================================

    def get_latest_commit(
        self,
        repository_url: str,
        branch_name: str,
    ) -> dict:
        """
        Get the latest commit for a specific branch.
        """

        repository = self.parse_repository_url(repository_url)

        repo = self.client.get_repo(repository)

        commit = repo.get_commit(branch_name)

        commit_message = (
            commit.commit.message.split("\n")[0]
            if commit.commit.message
            else ""
        )

        author = ""

        if commit.author:
            author = commit.author.login

        elif commit.commit.author:
            author = (
                commit.commit.author.name
                or ""
            )

        commit_date = None

        if commit.commit.author:
            commit_date = commit.commit.author.date

        return {
            "branch": branch_name,
            "sha": commit.sha,
            "message": commit_message,
            "author": author,
            "date": commit_date,
        }

    # =========================================================
    # COMMIT REVIEW
    # =========================================================

    def get_commit_review_input(
        self,
        repository_url: str,
        branch_name: str,
    ) -> PullRequestInput:
        """
        Build a PullRequestInput representing the latest commit
        on the selected branch.

        The existing LLM review pipeline expects PullRequestInput,
        so we reuse that model for commit reviews.
        """

        repository = self.parse_repository_url(repository_url)

        repo = self.client.get_repo(repository)

        commit = repo.get_commit(branch_name)

        diff = self._get_commit_diff(commit)

        commit_message = (
            commit.commit.message
            if commit.commit.message
            else "Latest commit"
        )

        return PullRequestInput(
            repository=repository,
            pull_request_number=0,
            title=f"[Commit Review] {commit_message.splitlines()[0]}",
            description=(
                f"Branch: {branch_name}\n"
                f"Commit: {commit.sha}\n"
                f"Commit message:\n"
                f"{commit_message}"
            ),
            diff=diff,
        )

    # =========================================================
    # COMMIT DIFF
    # =========================================================

    def _get_commit_diff(
        self,
        commit,
    ) -> str:
        """
        Build a reviewable diff from files changed by a commit.
        """

        diff_parts = []

        files = commit.files

        if not files:
            return (
                "[No changed files were returned for this commit]"
            )

        for file in files:

            filename = file.filename
            status = file.status
            additions = file.additions
            deletions = file.deletions
            patch = file.patch

            diff_parts.append(
                f"diff --git a/{filename} b/{filename}\n"
                f"status: {status}\n"
                f"additions: {additions}\n"
                f"deletions: {deletions}\n"
            )

            if patch:
                diff_parts.append(patch)
            else:
                diff_parts.append(
                    "[Patch unavailable for this file]"
                )

            diff_parts.append("\n")

        return "\n".join(diff_parts)

    # =========================================================
    # PULL REQUESTS
    # =========================================================

    def get_pull_requests(
        self,
        repository_url: str,
    ) -> list[dict]:

        repository = self.parse_repository_url(
            repository_url
        )

        repo = self.client.get_repo(repository)

        pull_requests = repo.get_pulls(
            state="open",
            sort="created",
            direction="desc",
        )

        results = []

        for pr in pull_requests:
            results.append(
                {
                    "number": pr.number,
                    "title": pr.title,
                    "author": pr.user.login,
                    "url": pr.html_url,
                    "created_at": pr.created_at,
                    "updated_at": pr.updated_at,
                }
            )

        return results

    # =========================================================
    # SINGLE PULL REQUEST
    # =========================================================

    def get_pull_request(
        self,
        repository_url: str,
        pull_request_number: int,
    ) -> PullRequestInput:

        repository = self.parse_repository_url(
            repository_url
        )

        repo = self.client.get_repo(repository)

        pr = repo.get_pull(
            pull_request_number
        )

        diff = self._get_pull_request_diff(pr)

        return PullRequestInput(
            repository=repository,
            pull_request_number=pull_request_number,
            title=pr.title,
            description=pr.body or "",
            diff=diff,
        )

    # =========================================================
    # PR DIFF
    # =========================================================

    def _get_pull_request_diff(
        self,
        pr,
    ) -> str:

        diff_parts = []

        files = pr.get_files()

        for file in files:

            filename = file.filename
            status = file.status
            additions = file.additions
            deletions = file.deletions
            patch = file.patch

            diff_parts.append(
                f"diff --git a/{filename} b/{filename}\n"
                f"status: {status}\n"
                f"additions: {additions}\n"
                f"deletions: {deletions}\n"
            )

            if patch:
                diff_parts.append(patch)
            else:
                diff_parts.append(
                    "[Patch unavailable for this file]"
                )

            diff_parts.append("\n")

        return "\n".join(diff_parts)

    # =========================================================
    # CLOSE
    # =========================================================

    def close(self):
        """Close the GitHub client cleanly."""

        self.client.close()