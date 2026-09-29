# AI Code Review Frontend

React + Vite frontend for the AI GitHub code review workflow.

## Workflow

1. Enter a GitHub repository URL.
2. Load all branches.
3. Inspect the latest commit for every branch.
4. Select the branch to review.
5. Optionally provide a team instruction.
6. Start the AI review.
7. View status, summary, findings, file/line locations, suggestions, and Hindsight team memory.

## Requirements

- Node.js 18+
- A running backend API

## Setup

```bash
npm install
copy .env.example .env
npm run dev
```

On macOS/Linux:

```bash
cp .env.example .env
npm install
npm run dev
```

The frontend runs at:

http://localhost:5173

## Backend API contract

The default frontend expects:

### Get branches

`GET /api/branches?repository_url=https://github.com/owner/repository`

Response:

```json
{
  "branches": [
    {
      "name": "main",
      "sha": "abc123...",
      "message": "Latest commit message",
      "author": "github-user",
      "date": "2026-09-29T12:00:00Z"
    }
  ]
}
```

### Review latest commit

`POST /api/review/latest-commit`

Body:

```json
{
  "repository_url": "https://github.com/owner/repository",
  "branch_name": "main",
  "team_instruction": "Pay special attention to security."
}
```

The expected response can contain:

```json
{
  "commit": {
    "branch": "main",
    "sha": "abc123...",
    "message": "Latest commit"
  },
  "review": {
    "overall_status": "request_changes",
    "summary": "Review summary",
    "issues": [
      {
        "severity": "high",
        "category": "security",
        "file": "app/auth.py",
        "line": 10,
        "title": "Authentication bypass",
        "description": "Problem description",
        "suggestion": "Suggested fix"
      }
    ]
  },
  "team_memory": "Relevant team review memory"
}
```

If your backend routes differ, edit only `src/api.js`.

## Build

```bash
npm run build
```

The production files are generated in `dist/`.
