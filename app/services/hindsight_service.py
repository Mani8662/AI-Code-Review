import json
import os
from typing import Any

from dotenv import load_dotenv
from hindsight_client import Hindsight


load_dotenv()


class HindsightService:
    """
    Handles persistent team memory for the code review agent.
    """

    def __init__(self):

        # =========================================================
        # CONFIGURATION
        # =========================================================

        base_url = os.getenv(
            "HINDSIGHT_BASE_URL"
        )

        api_key = os.getenv(
            "HINDSIGHT_API_KEY"
        ) or None

        self.bank_id = os.getenv(
            "HINDSIGHT_BANK_ID",
            "code-review-team",
        )

        if not base_url:

            raise ValueError(
                "HINDSIGHT_BASE_URL is not configured"
            )

        print()
        print("=" * 70)
        print("INITIALIZING HINDSIGHT")
        print("=" * 70)

        print(
            f"Hindsight URL: {base_url}"
        )

        print(
            f"Hindsight bank: {self.bank_id}"
        )

        print(
            f"Hindsight API key: "
            f"{'configured' if api_key else 'not configured'}"
        )

        # =========================================================
        # CLIENT
        # =========================================================

        self.client = Hindsight(
            base_url=base_url,
            api_key=api_key,
        )

        print(
            "✓ Hindsight client initialized"
        )

        print("=" * 70)

    # =============================================================
    # RECALL TEAM MEMORY
    # =============================================================

    def recall_team_memory(
        self,
        query: str,
    ) -> str:
        """
        Recall relevant team knowledge from Hindsight.
        """

        print()
        print("=" * 70)
        print("HINDSIGHT RECALL")
        print("=" * 70)

        print(
            f"Bank: {self.bank_id}"
        )

        print(
            f"Query: {query}"
        )

        try:

            response = self.client.recall(
                bank_id=self.bank_id,
                query=query,
                max_tokens=3000,
                budget="mid",
            )

            print(
                "✓ Hindsight recall request completed"
            )

        except Exception as exc:

            print()
            print(
                "✗ Hindsight recall failed"
            )

            print(
                f"Reason: {exc}"
            )

            print("=" * 70)

            # Do not stop the complete code review
            # if memory recall fails.

            return (
                "No relevant team memory was found."
            )

        # =========================================================
        # EXTRACT RESULTS
        # =========================================================

        results = getattr(
            response,
            "results",
            None,
        )

        if not results:

            print(
                "No memories found."
            )

            print("=" * 70)

            return (
                "No relevant team memory was found."
            )

        memories = []

        for result in results:

            text = getattr(
                result,
                "text",
                None,
            )

            if text:

                memories.append(
                    text
                )

        if not memories:

            print(
                "Hindsight returned results, "
                "but no memory text was found."
            )

            print("=" * 70)

            return (
                "No relevant team memory was found."
            )

        print(
            f"✓ Retrieved {len(memories)} memory item(s)"
        )

        print("=" * 70)

        return "\n\n".join(
            memories
        )

    # =============================================================
    # RETAIN REVIEW
    # =============================================================

    def retain_review(
        self,
        review: str,
        repository: str = "",
        pull_request_number: int | None = None,
    ) -> Any:
        """
        Store a completed code review in Hindsight.
        """

        print()
        print("=" * 70)
        print("HINDSIGHT RETAIN")
        print("=" * 70)

        print(
            f"Bank: {self.bank_id}"
        )

        print(
            f"Repository: {repository}"
        )

        print(
            f"Pull request: {pull_request_number}"
        )

        print(
            f"Review characters: {len(review)}"
        )

        # =========================================================
        # CONTEXT
        # =========================================================

        context = json.dumps(
            {
                "repository": repository,
                "pull_request_number": pull_request_number,
                "source": "code-review-agent",
            }
        )

        print(
            f"Context: {context}"
        )

        # =========================================================
        # RETAIN
        # =========================================================

        try:

            response = self.client.retain(
                bank_id=self.bank_id,
                content=review,
                context=context,
            )

            print()
            print(
                "✓ REVIEW SUCCESSFULLY STORED IN HINDSIGHT"
            )

            print(
                f"Bank: {self.bank_id}"
            )

            print("=" * 70)

            return response

        except Exception as exc:

            print()
            print(
                "✗ HINDSIGHT RETAIN FAILED"
            )

            print(
                f"Reason: {exc}"
            )

            print("=" * 70)

            # Important:
            # Re-raise the exception so we know the memory
            # was NOT successfully stored.

            raise

    # =============================================================
    # RETAIN TEAM FEEDBACK
    # =============================================================

    def retain_team_feedback(
        self,
        feedback: str,
        repository: str = "",
    ) -> Any:
        """
        Store explicit team feedback so future reviews
        can learn from it.
        """

        print()
        print("=" * 70)
        print("HINDSIGHT TEAM FEEDBACK")
        print("=" * 70)

        print(
            f"Bank: {self.bank_id}"
        )

        print(
            f"Repository: {repository}"
        )

        print(
            f"Feedback characters: {len(feedback)}"
        )

        context = json.dumps(
            {
                "repository": repository,
                "source": "team-feedback",
            }
        )

        try:

            response = self.client.retain(
                bank_id=self.bank_id,
                content=feedback,
                context=context,
            )

            print()
            print(
                "✓ TEAM FEEDBACK SUCCESSFULLY STORED"
            )

            print("=" * 70)

            return response

        except Exception as exc:

            print()
            print(
                "✗ HINDSIGHT TEAM FEEDBACK FAILED"
            )

            print(
                f"Reason: {exc}"
            )

            print("=" * 70)

            raise

    # =============================================================
    # CLOSE
    # =============================================================

    def close(self):

        """
        Close the Hindsight client cleanly.
        """

        try:

            self.client.close()

            print(
                "✓ Hindsight client closed"
            )

        except Exception as exc:

            print(
                f"Warning: could not close Hindsight client: {exc}"
            )