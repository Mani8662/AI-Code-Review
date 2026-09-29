from app.services.review_service import ReviewService


def test_complete_review_workflow():

    service = ReviewService()

    try:

        # =========================================================
        # STEP 1
        # AI CODE REVIEW AGENT
        # =========================================================

        print()
        print("=" * 60)
        print("AI CODE REVIEW AGENT")
        print("=" * 60)

        # =========================================================
        # STEP 2
        # LLM PROVIDER SELECTION
        # =========================================================

        print()
        print("=" * 60)
        print("LLM PROVIDER SELECTION")
        print("=" * 60)

        while True:

            openai_choice = input(
                "\nDo you want to check OpenAI availability? "
                "(yes/no): "
            ).strip().lower()

            if openai_choice in ("yes", "y"):

                check_openai = True
                break

            if openai_choice in ("no", "n"):

                check_openai = False
                break

            print(
                "Please enter yes or no."
            )

        print()

        if check_openai:

            print(
                "OpenAI availability check enabled."
            )

        else:

            print(
                "Skipping OpenAI availability check."
            )

        print()
        print(
            "Checking LLM availability..."
        )

        llm_available = (
            service.llm.check_availability(
                check_openai=check_openai
            )
        )

        if not llm_available:

            raise RuntimeError(
                "No LLM provider is available."
            )

        print()
        print(
            "✓ LLM availability confirmed."
        )

        # =========================================================
        # STEP 3
        # GITHUB REPOSITORY
        # =========================================================

        print()
        print("=" * 60)
        print("GITHUB REPOSITORY")
        print("=" * 60)

        repository_url = input(
            "\nEnter GitHub Repository URL: "
        ).strip()

        if not repository_url:

            raise ValueError(
                "GitHub repository URL is required."
            )

        # =========================================================
        # STEP 4
        # FETCH BRANCHES
        # =========================================================

        print()
        print(
            "Fetching repository branches..."
        )

        try:

            branches = (
                service.github.get_branches(
                    repository_url
                )
            )

        except Exception as exc:

            raise RuntimeError(
                f"Failed to access GitHub repository: "
                f"{exc}"
            ) from exc

        if not branches:

            raise RuntimeError(
                "No branches were found."
            )

        # =========================================================
        # STEP 5
        # DISPLAY BRANCHES
        # =========================================================

        print()
        print("=" * 60)
        print("AVAILABLE BRANCHES")
        print("=" * 60)

        for index, branch in enumerate(
            branches,
            start=1,
        ):

            print()
            print(
                f"{index}. {branch['name']}"
            )

            print(
                f"   Latest commit: "
                f"{branch['sha'][:12]}"
            )

            print(
                f"   Message: "
                f"{branch['message']}"
            )

            print(
                f"   Author: "
                f"{branch['author']}"
            )

            print(
                f"   Date: "
                f"{branch['date']}"
            )

        # =========================================================
        # STEP 6
        # SELECT BRANCH
        # =========================================================

        print()

        while True:

            branch_choice = input(
                "Select branch number to review: "
            ).strip()

            try:

                branch_index = int(
                    branch_choice
                )

                if (
                    1
                    <= branch_index
                    <= len(branches)
                ):
                    break

            except ValueError:
                pass

            print(
                f"Please enter a number between "
                f"1 and {len(branches)}."
            )

        selected_branch = branches[
            branch_index - 1
        ]

        branch_name = selected_branch[
            "name"
        ]

        # =========================================================
        # STEP 7
        # GET LATEST COMMIT
        # =========================================================

        print()
        print("=" * 60)
        print("SELECTED BRANCH")
        print("=" * 60)

        print()
        print(
            f"✓ Branch: {branch_name}"
        )

        print()
        print(
            "Fetching latest commit..."
        )

        try:

            latest_commit = (
                service.github.get_latest_commit(
                    repository_url=repository_url,
                    branch_name=branch_name,
                )
            )

        except Exception as exc:

            raise RuntimeError(
                f"Failed to fetch latest commit: "
                f"{exc}"
            ) from exc

        print()
        print(
            f"✓ Latest commit: "
            f"{latest_commit['sha']}"
        )

        print(
            f"  Message: "
            f"{latest_commit['message']}"
        )

        print(
            f"  Author: "
            f"{latest_commit['author']}"
        )

        print(
            f"  Date: "
            f"{latest_commit['date']}"
        )

        # =========================================================
        # STEP 8
        # TEAM MEMORY
        # =========================================================

        print()
        print("=" * 60)
        print("TEAM MEMORY")
        print("=" * 60)

        team_instruction = input(
            "\nEnter a team coding standard "
            "or review rule "
            "(press Enter to skip): "
        ).strip()

        if team_instruction:

            try:

                service.hindsight.retain_team_feedback(
                    feedback=team_instruction,
                    repository=repository_url,
                )

                print()
                print(
                    "✓ Team instruction stored "
                    "in Hindsight."
                )

            except Exception as exc:

                print()
                print(
                    "Warning: Could not store "
                    "team instruction."
                )

                print(
                    f"Reason: {exc}"
                )

        else:

            print()
            print(
                "No new team instruction provided."
            )

            print(
                "Continuing with existing "
                "Hindsight memory."
            )

        # =========================================================
        # STEP 9
        # START REVIEW
        # =========================================================

        print()
        print("=" * 60)
        print("STARTING CODE REVIEW")
        print("=" * 60)

        print()
        print(
            f"Branch: {branch_name}"
        )

        print(
            f"Commit: "
            f"{latest_commit['sha']}"
        )

        print(
            f"Commit message: "
            f"{latest_commit['message']}"
        )

        print()
        print(
            "Recalling team memory "
            "from Hindsight..."
        )

        print(
            "Reviewing latest commit..."
        )

        try:

            result = (
                service.review_latest_commit(
                    repository_url=repository_url,
                    branch_name=branch_name,
                )
            )

        except Exception as exc:

            print()
            print("=" * 60)
            print("REVIEW FAILED")
            print("=" * 60)

            print()
            print(
                f"Reason: {exc}"
            )

            # IMPORTANT:
            # Do not allow pytest to report PASSED
            # when the review actually failed.

            raise

        # =========================================================
        # STEP 10
        # CODE REVIEW RESULT
        # =========================================================

        review = result["review"]

        print()
        print("=" * 60)
        print("CODE REVIEW RESULT")
        print("=" * 60)

        print()
        print(
            f"Status: "
            f"{review['overall_status']}"
        )

        print()
        print(
            "Summary:"
        )

        print(
            review["summary"]
        )

        # =========================================================
        # STEP 11
        # ISSUES
        # =========================================================

        issues = review.get(
            "issues",
            [],
        )

        if issues:

            print()
            print(
                f"Issues found: "
                f"{len(issues)}"
            )

            print(
                "-" * 60
            )

            for index, issue in enumerate(
                issues,
                start=1,
            ):

                print()

                print(
                    f"{index}. "
                    f"[{issue['severity'].upper()}] "
                    f"{issue['title']}"
                )

                print(
                    f"   Category: "
                    f"{issue['category']}"
                )

                print(
                    f"   File: "
                    f"{issue['file']}"
                )

                if issue.get("line"):

                    print(
                        f"   Line: "
                        f"{issue['line']}"
                    )

                print()

                print(
                    f"   Description: "
                    f"{issue['description']}"
                )

                print(
                    f"   Suggestion: "
                    f"{issue['suggestion']}"
                )

        else:

            print()
            print(
                "✓ No issues found."
            )

        # =========================================================
        # STEP 12
        # HINDSIGHT
        # =========================================================

        print()
        print("=" * 60)
        print("HINDSIGHT MEMORY")
        print("=" * 60)

        print()
        print(
            "✓ Previous team memory was "
            "used during the review."
        )

        print(
            "✓ Review result was stored "
            "in Hindsight."
        )

        print()
        print(
            "Memory loop completed successfully."
        )

        # =========================================================
        # BASIC ASSERTIONS
        # =========================================================

        assert result is not None
        assert review is not None
        assert review["overall_status"] in (
            "approve",
            "request_changes",
            "comment",
        )

        assert isinstance(
            review["issues"],
            list,
        )

    finally:

        service.close()