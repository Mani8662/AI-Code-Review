from app.models.review_models import PullRequestInput
from app.services.llm_service import LLMService
from app.services.hindsight_service import HindsightService


def test_review_with_hindsight():
    pr = PullRequestInput(
        repository="demo/repository",
        pull_request_number=1,
        title="Test authentication change",
        description="Testing the AI code review agent.",
        diff="""
diff --git a/app/auth.py b/app/auth.py
index 123..456 100644
--- a/app/auth.py
+++ b/app/auth.py
@@ -1,5 +1,8 @@
 def login(username, password):
+    if username == "admin":
+        return True
+
     return check_password(username, password)
""",
    )

    hindsight = HindsightService()

    try:
        # 1. Recall real team memory from Hindsight
        team_memory = hindsight.recall_team_memory(
            "What coding standards, security practices, and recurring "
            "review issues should I consider for this pull request?"
        )

        print()
        print("=" * 80)
        print("HINDSIGHT TEAM MEMORY")
        print("=" * 80)
        print(team_memory)
        print("=" * 80)

        # 2. Send the recalled memory to OpenAI
        llm = LLMService()

        review = llm.review(
            pr,
            team_memory=team_memory,
        )

        print()
        print("=" * 80)
        print("CODE REVIEW RESULT")
        print("=" * 80)
        print(review.model_dump_json(indent=2))
        print("=" * 80)

        # 3. Store the completed review back in Hindsight
        result = hindsight.retain_review(
            review=review.model_dump_json(),
            repository=pr.repository,
            pull_request_number=pr.pull_request_number,
        )

        print()
        print("=" * 80)
        print("HINDSIGHT RETAIN")
        print("=" * 80)
        print(result)
        print("=" * 80)

        assert review is not None
        assert result is not None

    finally:
        hindsight.close()