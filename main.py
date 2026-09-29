import traceback

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.services.review_service import ReviewService


app = FastAPI(
    title="AI Code Review Agent API",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST MODELS
# ============================================================

class ReviewRequest(BaseModel):
    repository_url: str
    branch_name: str
    team_instruction: str = ""


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "AI Code Review Agent API is running"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/api/health")
def health():
    return {
        "status": "healthy"
    }


# ============================================================
# GET BRANCHES
# ============================================================

@app.get("/api/branches")
def get_branches(repository_url: str):

    service = ReviewService()

    try:
        branches = service.github.get_branches(
            repository_url=repository_url
        )

        return {
            "branches": branches
        }

    except Exception as exc:

        print("\n" + "=" * 70)
        print("GET BRANCHES FAILED")
        print("=" * 70)

        traceback.print_exc()

        print("=" * 70 + "\n")

        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

    finally:
        service.close()


# ============================================================
# REVIEW LATEST COMMIT
# ============================================================

@app.post("/api/review/latest-commit")
def review_latest_commit(request: ReviewRequest):

    service = ReviewService()

    try:

        print("\n" + "=" * 70)
        print("STARTING AI CODE REVIEW")
        print("=" * 70)

        print("Repository:")
        print(request.repository_url)

        print("Branch:")
        print(request.branch_name)

        print("Team instruction:")
        print(request.team_instruction)

        print("=" * 70)

        result = service.review_latest_commit(
    repository_url=request.repository_url,
    branch_name=request.branch_name,
    team_instruction=request.team_instruction,
)

        print("\n" + "=" * 70)
        print("AI CODE REVIEW COMPLETED")
        print("=" * 70 + "\n")

        return result

    except Exception as exc:

        print("\n" + "=" * 70)
        print("REVIEW FAILED")
        print("=" * 70)

        print("ERROR:")
        print(str(exc))

        print("\nFULL TRACEBACK:")

        traceback.print_exc()

        print("=" * 70 + "\n")

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )

    finally:
        service.close()