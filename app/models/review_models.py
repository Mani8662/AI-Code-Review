from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class ReviewIssue(BaseModel):
    severity: Literal[
        "critical",
        "high",
        "medium",
        "low",
        "info"
    ]

    category: str
    file: str
    line: Optional[int] = None
    title: str
    description: str
    suggestion: str


class CodeReview(BaseModel):
    overall_status: Literal[
        "approve",
        "request_changes",
        "comment"
    ]

    summary: str

    issues: List[ReviewIssue] = Field(
        default_factory=list
    )


class PullRequestInput(BaseModel):
    repository: str = ""
    pull_request_number: Optional[int] = None
    title: str = ""
    description: str = ""
    diff: str = ""
    branch: Optional[str] = None
    commit_sha: Optional[str] = None


class GitHubPRRequest(BaseModel):
    url: str