from app.services.github_service import GitHubService
from app.services.hindsight_service import HindsightService
from app.services.llm_service import LLMService
import traceback


class ReviewService:
    """
    Complete AI code review workflow.

    Commit workflow:

    GitHub
        ↓
    Selected branch
        ↓
    Latest commit
        ↓
    Hindsight recall
        ↓
    LLM review
        ↓
    Hindsight retain
    """

    def __init__(self):
        self.github = GitHubService()
        self.hindsight = HindsightService()
        self.llm = LLMService()

    # =========================================================
    # REVIEW LATEST COMMIT
    # =========================================================

    def review_latest_commit(
    self,
    repository_url: str,
    branch_name: str,
    team_instruction: str = "",
    ) -> dict:
        """
        Review the latest commit on the selected branch.
        """

        # -----------------------------------------------------
        # 1. Get latest commit
        # -----------------------------------------------------

        latest_commit = (
            self.github.get_latest_commit(
                repository_url=repository_url,
                branch_name=branch_name,
            )
        )

        # -----------------------------------------------------
        # 2. Build review input from commit
        # -----------------------------------------------------

        commit_input = (
            self.github.get_commit_review_input(
                repository_url=repository_url,
                branch_name=branch_name,
            )
        )

        # -----------------------------------------------------
        # 3. Recall team memory
        # -----------------------------------------------------

        memory_query = (
            "What team coding standards, security practices, "
            "architectural preferences, recurring mistakes, "
            "and previous code-review lessons are relevant "
            "to reviewing this code change?"
        )

        team_memory = (
            self.hindsight.recall_team_memory(
                memory_query
            )
        )

        # -----------------------------------------------------
        # 4. Review with selected LLM
        # -----------------------------------------------------
        print("=" * 70)
        print("DEBUG: BEFORE LLM REVIEW")
        print("DIFF CHARACTERS:", len(commit_input.diff))
        print("APPROX TOKENS:", len(commit_input.diff) // 4)
        print("=" * 70)

        review = self.llm.review(
        commit_input,
        team_memory=team_memory,
        team_instruction=team_instruction,
            )
        # -----------------------------------------------------
        # 5. Store review in Hindsight
        # -----------------------------------------------------

        self.hindsight.retain_review(
            review=review.model_dump_json(),
            repository=commit_input.repository,
            pull_request_number=None,
        )

        # -----------------------------------------------------
        # 6. Return result
        # -----------------------------------------------------

        return {
            "commit": latest_commit,
            "pull_request": commit_input.model_dump(),
            "review": review.model_dump(),
            "team_memory": team_memory,
        }

    # =========================================================
    # ORIGINAL PR REVIEW
    # =========================================================

    def review_pr(
        self,
        repository_url: str,
        pull_request_number: int,
    ) -> dict:
        """
        Keep the original PR review workflow available.
        """

        # -----------------------------------------------------
        # 1. Fetch PR
        # -----------------------------------------------------

        pr = self.github.get_pull_request(
            repository_url=repository_url,
            pull_request_number=pull_request_number,
        )

        # -----------------------------------------------------
        # 2. Recall team memory
        # -----------------------------------------------------

        memory_query = (
            "What team coding standards, security practices, "
            "architectural preferences, recurring mistakes, "
            "and previous code-review lessons are relevant "
            "to reviewing this pull request?"
        )

        team_memory = (
            self.hindsight.recall_team_memory(
                memory_query
            )
        )

        # -----------------------------------------------------
        # 3. Review
        # -----------------------------------------------------

        review = self.llm.review(
            pr,
            team_memory=team_memory,
        )

        # -----------------------------------------------------
        # 4. Store review
        # -----------------------------------------------------

        self.hindsight.retain_review(
            review=review.model_dump_json(),
            repository=pr.repository,
            pull_request_number=(
                pr.pull_request_number
            ),
        )

        # -----------------------------------------------------
        # 5. Return
        # -----------------------------------------------------

        return {
            "pull_request": pr.model_dump(),
            "review": review.model_dump(),
            "team_memory": team_memory,
        }

    # =========================================================
    # CLOSE
    # =========================================================

    def close(self):
        """Close all external service clients."""

        self.github.close()
        self.hindsight.close()