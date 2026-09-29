from app.services.hindsight_service import HindsightService


def test_hindsight_retain():
    hindsight = HindsightService()

    try:
        result = hindsight.retain_review(
            review="""
Team coding standard:
All authentication code must verify credentials explicitly.
Never allow username-only authentication shortcuts.
Security-sensitive changes should include clear validation and tests.
""",
            repository="demo/team-repo",
            pull_request_number=1,
        )

        print()
        print("=" * 60)
        print("HINDSIGHT RETAIN TEST")
        print("=" * 60)
        print(result)
        print("=" * 60)

        assert result is not None

    finally:
        hindsight.close()