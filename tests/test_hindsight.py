from app.services.hindsight_service import HindsightService


def test_hindsight_connection():
    hindsight = HindsightService()

    try:
        memory = hindsight.recall_team_memory(
            "What coding standards and review practices does our team follow?"
        )

        print()
        print("=" * 60)
        print("HINDSIGHT RECALL TEST")
        print("=" * 60)
        print(memory)
        print("=" * 60)

        assert memory is not None

    finally:
        hindsight.close()