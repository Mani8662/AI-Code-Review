import json
import logging
import os
import time
from typing import Optional

from dotenv import load_dotenv
from google import genai
from google.genai import types
from openai import OpenAI

from app.models.review_models import CodeReview, PullRequestInput
from app.prompts.review_prompt import build_review_prompt


load_dotenv()

logger = logging.getLogger(__name__)


class LLMService:

    def __init__(self):

        # =========================================================
        # MODELS
        # =========================================================

        self.openai_model = os.getenv(
            "OPENAI_MODEL",
            "gpt-5.6",
        )

        self.gemini_model = os.getenv(
            "GEMINI_MODEL",
            "gemini-2.5-flash",
        )

        self.gemini_fallback_model = os.getenv(
            "GEMINI_FALLBACK_MODEL",
            "gemini-2.0-flash",
        )

        # =========================================================
        # OPENAI API KEYS
        # =========================================================

        self.openai_keys = []

        for env_name in (
            "OPENAI_API_KEY_1",
            "OPENAI_API_KEY_2",
        ):

            key = os.getenv(env_name)

            if key:
                self.openai_keys.append(key)

        # Backward compatibility with old .env configuration.
        legacy_openai_key = os.getenv(
            "OPENAI_API_KEY"
        )

        if (
            legacy_openai_key
            and legacy_openai_key not in self.openai_keys
        ):
            self.openai_keys.append(
                legacy_openai_key
            )

        # =========================================================
        # OPENAI CLIENTS
        # =========================================================

        self.openai_clients = []

        for key in self.openai_keys:

            self.openai_clients.append(
                OpenAI(api_key=key)
            )

        # =========================================================
        # GEMINI
        # =========================================================

        self.gemini_api_key = os.getenv(
            "GEMINI_API_KEY"
        )

        self.gemini_client = None

        if self.gemini_api_key:

            self.gemini_client = genai.Client(
                api_key=self.gemini_api_key
            )

        # =========================================================
        # SELECTED PROVIDER
        # =========================================================

        self.selected_provider: Optional[str] = None
        self.selected_model: Optional[str] = None
        self.selected_openai_client = None

        print(
            f"LLM providers configured: "
            f"{len(self.openai_keys)} OpenAI key(s), "
            f"{'Gemini' if self.gemini_client else 'no Gemini'}"
        )

        print(
            f"OpenAI model: "
            f"{self.openai_model}"
        )

        print(
            f"Gemini model: "
            f"{self.gemini_model}"
        )

        print(
            f"Gemini fallback model: "
            f"{self.gemini_fallback_model}"
        )

    # =============================================================
    # LLM AVAILABILITY
    # =============================================================

    def check_availability(
        self,
        check_openai: bool = True,
    ) -> bool:

        print()
        print("=" * 60)
        print("CHECKING LLM AVAILABILITY")
        print("=" * 60)

        # Reset previous selection.
        self.selected_provider = None
        self.selected_model = None
        self.selected_openai_client = None

        if not check_openai:

            print()
            print("OpenAI availability check skipped.")
            print("Gemini will be checked directly.")

        # =========================================================
        # CHECK OPENAI
        # =========================================================

        if check_openai:

            for index, client in enumerate(
                self.openai_clients,
                start=1,
            ):

                print()
                print(
                    f"Checking OpenAI API key "
                    f"{index}/{len(self.openai_clients)}..."
                )

                try:

                    response = client.responses.create(
                        model=self.openai_model,
                        input="Reply with OK.",
                        max_output_tokens=16,
                    )

                    self.selected_provider = "openai"

                    self.selected_model = (
                        self.openai_model
                    )

                    self.selected_openai_client = client

                    print(
                        f"✓ OpenAI API key {index}: AVAILABLE"
                    )

                    print()
                    print(
                        f"✓ LLM available through "
                        f"OpenAI ({self.openai_model})"
                    )

                    return True

                except Exception as exc:

                    error_text = str(exc).lower()

                    if any(
                        phrase in error_text
                        for phrase in (
                            "quota",
                            "insufficient_quota",
                            "billing",
                            "exceeded",
                            "rate limit",
                            "rate_limit",
                        )
                    ):

                        print(
                            f"✗ OpenAI API key {index}: "
                            f"NO QUOTA"
                        )

                    else:

                        print(
                            f"✗ OpenAI API key {index}: "
                            f"API ERROR"
                        )

                        print(
                            f"  {exc}"
                        )

        # =========================================================
        # CHECK GEMINI
        # =========================================================

        if self.gemini_client:

            print()
            print(
                f"Checking Gemini "
                f"({self.gemini_model})..."
            )

            try:

                response = (
                    self.gemini_client.models.generate_content(
                        model=self.gemini_model,
                        contents="Reply with OK.",
                        config=types.GenerateContentConfig(
                            max_output_tokens=5,
                        ),
                    )
                )

                self.selected_provider = "gemini"

                self.selected_model = (
                    self.gemini_model
                )

                print(
                    f"✓ Gemini ({self.gemini_model}): "
                    f"AVAILABLE"
                )

                print()
                print(
                    f"✓ LLM available through Gemini "
                    f"({self.gemini_model})"
                )

                return True

            except Exception as exc:

                print(
                    f"✗ Gemini ({self.gemini_model}): "
                    f"API ERROR"
                )

                print(
                    f"  {exc}"
                )

            # =====================================================
            # GEMINI FALLBACK
            # =====================================================

            if (
                self.gemini_fallback_model
                and self.gemini_fallback_model
                != self.gemini_model
            ):

                print()
                print(
                    f"Checking Gemini fallback "
                    f"({self.gemini_fallback_model})..."
                )

                try:

                    response = (
                        self.gemini_client.models.generate_content(
                            model=self.gemini_fallback_model,
                            contents="Reply with OK.",
                            config=types.GenerateContentConfig(
                                max_output_tokens=5,
                            ),
                        )
                    )

                    self.selected_provider = "gemini"

                    self.selected_model = (
                        self.gemini_fallback_model
                    )

                    print(
                        f"✓ Gemini fallback "
                        f"({self.gemini_fallback_model}): "
                        f"AVAILABLE"
                    )

                    print()
                    print(
                        f"✓ LLM available through Gemini "
                        f"({self.gemini_fallback_model})"
                    )

                    return True

                except Exception as exc:

                    print(
                        f"✗ Gemini fallback "
                        f"({self.gemini_fallback_model}): "
                        f"UNAVAILABLE"
                    )

                    print(
                        f"  {exc}"
                    )

        # =========================================================
        # NOTHING AVAILABLE
        # =========================================================

        print()
        print(
            "✗ No LLM provider is available."
        )

        return False

    # =============================================================
    # CREATE RESPONSE
    # =============================================================

    def create_response(
        self,
        prompt: str,
        max_output_tokens: int = 6000,
    ) -> str:

        # =========================================================
        # REQUIRE AVAILABILITY CHECK FIRST
        # =========================================================

        if not self.selected_provider:

            raise RuntimeError(
                "No LLM provider has been selected. "
                "Call check_availability() before "
                "creating a response."
            )

        # =========================================================
        # OPENAI
        # =========================================================

        if self.selected_provider == "openai":

            if not self.selected_openai_client:

                raise RuntimeError(
                    "OpenAI was selected but no "
                    "OpenAI client is available."
                )

            print()
            print(
                f"Using selected LLM: "
                f"OpenAI ({self.selected_model})"
            )

            try:

                response = (
                    self.selected_openai_client
                    .responses.create(
                        model=self.selected_model,
                        input=prompt,
                        max_output_tokens=(
                            max_output_tokens
                        ),
                    )
                )

                text = response.output_text

                if not text:

                    raise ValueError(
                        "OpenAI returned an empty response."
                    )

                print(
                    f"✓ OpenAI succeeded using "
                    f"{self.selected_model}."
                )

                return text

            except Exception as exc:

                print()
                print(
                    "✗ Selected OpenAI provider "
                    "failed during review."
                )

                print(
                    f"Reason: {exc}"
                )

                raise

        # =========================================================
        # GEMINI
        # =========================================================

        if self.selected_provider == "gemini":

            if not self.gemini_client:

                raise RuntimeError(
                    "Gemini was selected but the "
                    "Gemini client is unavailable."
                )

            print()
            print(
                f"Using selected LLM: "
                f"Gemini ({self.selected_model})"
            )

            try:

                print(
                    "Gemini attempt 1/2..."
                )

                response = (
                    self.gemini_client.models
                    .generate_content(
                        model=self.selected_model,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            max_output_tokens=(
                                max_output_tokens
                            ),
                            response_mime_type="application/json",
                            response_schema=CodeReview,
                        ),
                    )
                )

                text = response.text

                if not text:

                    raise ValueError(
                        "Gemini returned an empty response."
                    )

                print(
                    f"✓ Gemini succeeded using "
                    f"{self.selected_model}."
                )

                return text

            except Exception as first_exc:

                error_text = str(
                    first_exc
                ).lower()

                temporary_error = any(
                    phrase in error_text
                    for phrase in (
                        "503",
                        "unavailable",
                        "high demand",
                        "overloaded",
                        "resource exhausted",
                        "temporarily",
                    )
                )

                if not temporary_error:

                    print()
                    print(
                        "✗ Selected Gemini provider "
                        "failed during review."
                    )

                    print(
                        f"Reason: {first_exc}"
                    )

                    raise

                print()
                print(
                    "Gemini temporary error."
                )

                print(
                    "Retrying selected Gemini model "
                    "after 2 seconds..."
                )

                time.sleep(2)

                try:

                    print(
                        "Gemini attempt 2/2..."
                    )

                    response = (
                        self.gemini_client.models
                        .generate_content(
                            model=self.selected_model,
                            contents=prompt,
                            config=types.GenerateContentConfig(
                                max_output_tokens=(
                                    max_output_tokens
                                ),
                                response_mime_type="application/json",
                                response_schema=CodeReview,
                            ),
                        )
                    )

                    text = response.text

                    if not text:

                        raise ValueError(
                            "Gemini returned an empty response."
                        )

                    print(
                        f"✓ Gemini succeeded using "
                        f"{self.selected_model}."
                    )

                    return text

                except Exception as second_exc:

                    print()
                    print(
                        "✗ Selected Gemini provider "
                        "failed after retry."
                    )

                    print(
                        f"Reason: {second_exc}"
                    )

                    raise

        # =========================================================
        # UNKNOWN PROVIDER
        # =========================================================

        raise RuntimeError(
            f"Unknown selected LLM provider: "
            f"{self.selected_provider}"
        )

    # =============================================================
    # REVIEW
    # =============================================================

    def review(
    self,
    pr: PullRequestInput,
    team_memory: str = "",
    team_instruction: str = "",
        ) -> CodeReview:    

        # =========================================================
        # SELECT AN AVAILABLE LLM PROVIDER
        # =========================================================

        print()
        print("=" * 60)
        print("SELECTING LLM PROVIDER")
        print("=" * 60)

        available = self.check_availability()

        if not available:

            raise RuntimeError(
                "No LLM provider is currently available."
            )

        # =========================================================
        # BUILD REVIEW PROMPT
        # =========================================================

        prompt = build_review_prompt(
    pr,
    team_memory=team_memory,
    team_instruction=team_instruction,
)

        # =========================================================
        # DEBUG INFORMATION
        # =========================================================

        print()
        print("=" * 60)
        print("LLM REVIEW")
        print("=" * 60)

        print(
            f"Selected provider: "
            f"{self.selected_provider}"
        )

        print(
            f"Selected model: "
            f"{self.selected_model}"
        )

        print(
            f"Prompt characters: "
            f"{len(prompt)}"
        )

        print(
            f"Approx prompt tokens: "
            f"{len(prompt) // 4}"
        )

        print("=" * 60)

        # =========================================================
        # CREATE RESPONSE
        # =========================================================

        response_text = self.create_response(
            prompt,
            max_output_tokens=6000,
        )

        # =========================================================
        # CLEAN RESPONSE
        # =========================================================

        cleaned = response_text.strip()

        # Remove Markdown JSON fences if the model
        # unexpectedly returns them.

        if cleaned.startswith(
            "```json"
        ):

            cleaned = cleaned[
                len("```json"):
            ].strip()

        elif cleaned.startswith(
            "```"
        ):

            cleaned = cleaned[
                len("```"):
            ].strip()

        if cleaned.endswith(
            "```"
        ):

            cleaned = cleaned[
                :-len("```")
            ].strip()

        # =========================================================
        # PARSE JSON
        # =========================================================

        try:

            data = json.loads(
                cleaned
            )

        except json.JSONDecodeError:

            extracted = self._extract_json_object(
                cleaned
            )

            if not extracted:

                raise ValueError(
                    "LLM returned invalid JSON.\n"
                    f"Response:\n{response_text}"
                )

            try:

                data = json.loads(
                    extracted
                )

            except json.JSONDecodeError as exc:

                raise ValueError(
                    "LLM returned incomplete or "
                    "invalid JSON.\n"
                    f"Response:\n{response_text}"
                ) from exc

        # =========================================================
        # VALIDATE RESPONSE
        # =========================================================

        try:

            return CodeReview.model_validate(
                data
            )

        except Exception as exc:

            raise ValueError(
                "LLM response does not match "
                "the required CodeReview schema.\n"
                f"Response:\n{response_text}"
            ) from exc

    # =============================================================
    # EXTRACT JSON OBJECT
    # =============================================================

    @staticmethod
    def _extract_json_object(
        text: str,
    ) -> Optional[str]:

        start = text.find("{")

        if start == -1:

            return None

        depth = 0
        in_string = False
        escape = False

        for index in range(
            start,
            len(text),
        ):

            char = text[index]

            if escape:

                escape = False
                continue

            if char == "\\" and in_string:

                escape = True
                continue

            if char == '"':

                in_string = not in_string
                continue

            if in_string:
                continue

            if char == "{":

                depth += 1

            elif char == "}":

                depth -= 1

                if depth == 0:

                    return text[
                        start:index + 1
                    ]

        return None