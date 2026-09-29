from app.services.github_service import GitHubService


def test_github_repository():
    repository_url = input(
        "Enter GitHub Repository URL: "
    ).strip()

    github = GitHubService()

    try:
        pull_requests = github.get_pull_requests(
            repository_url
        )

        print()
        print("=" * 80)
        print("OPEN PULL REQUESTS")
        print("=" * 80)

        if not pull_requests:
            print("No open pull requests found.")
            return

        for pr in pull_requests:
            print()
            print(f"PR #{pr['number']}")
            print(f"Title : {pr['title']}")
            print(f"Author: {pr['author']}")
            print(f"URL   : {pr['url']}")

        print()
        print("=" * 80)

        pr_number = int(
            input("Enter PR number to review: ").strip()
        )

        pr = github.get_pull_request(
            repository_url=repository_url,
            pull_request_number=pr_number,
        )

        print()
        print("=" * 80)
        print("SELECTED PULL REQUEST")
        print("=" * 80)
        print("Repository:", pr.repository)
        print("PR Number:", pr.pull_request_number)
        print("Title:", pr.title)

        print()
        print("DESCRIPTION:")
        print(pr.description)

        print()
        print("DIFF:")
        print(pr.diff[:5000])

        print("=" * 80)

        assert pr.repository
        assert pr.pull_request_number
        assert pr.title
        assert pr.diff

    finally:
        github.close()