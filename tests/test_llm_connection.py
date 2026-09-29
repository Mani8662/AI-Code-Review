from app.services.llm_service import LLMService


def test_openai_connection():
    llm = LLMService()

    response = llm.create_response(
        instructions="You are a test assistant.",
        input="Reply with exactly: OPENAI_OK",
        max_output_tokens=100,
    )

    print()
    print("=" * 60)
    print("OPENAI CONNECTION TEST")
    print("=" * 60)
    print(response.output_text)
    print("=" * 60)

    assert response.output_text.strip()