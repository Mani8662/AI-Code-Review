import { useMemo, useState } from "react";
import {
  AlertCircle,
  ArrowRight,
  Check,
  ChevronDown,
  ChevronUp,
  Clock3,
  Code2,
  GitBranch,
  Github,
  Loader2,
  RefreshCw,
  ShieldCheck,
  Sparkles,
  User,
  XCircle
} from "lucide-react";
import { getBranches, reviewLatestCommit } from "./api";

function formatDate(value) {
  if (!value) return "Unknown date";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleString();
}

function shortSha(sha) {
  return sha ? sha.slice(0, 8) : "--------";
}

function severityClass(severity) {
  return `severity severity-${String(severity || "info").toLowerCase()}`;
}

function normalizeBranches(data) {
  if (!Array.isArray(data)) return [];

  return data.map((branch, index) => ({
    name: branch.name || branch.branch || `branch-${index + 1}`,
    sha: branch.sha || branch.commit_sha || branch.commit?.sha || "",
    message:
      branch.message ||
      branch.commit_message ||
      branch.commit?.message ||
      "No commit message",
    author:
      branch.author ||
      branch.commit_author ||
      branch.commit?.author ||
      "Unknown",
    date:
      branch.date ||
      branch.commit_date ||
      branch.commit?.date ||
      null
  }));
}

export default function App() {
  const [repositoryUrl, setRepositoryUrl] = useState("");
  const [branches, setBranches] = useState([]);
  const [selectedBranch, setSelectedBranch] = useState(null);
  const [teamInstruction, setTeamInstruction] = useState("");
  const [reviewResult, setReviewResult] = useState(null);

  const [loadingBranches, setLoadingBranches] = useState(false);
  const [reviewing, setReviewing] = useState(false);
  const [error, setError] = useState("");
  const [showMemory, setShowMemory] = useState(false);

  const normalizedBranches = useMemo(
    () => normalizeBranches(branches),
    [branches]
  );

  async function handleLoadBranches(event) {
    event?.preventDefault();

    setError("");
    setReviewResult(null);
    setSelectedBranch(null);

    if (!repositoryUrl.trim()) {
      setError("Enter a GitHub repository URL.");
      return;
    }

    setLoadingBranches(true);

    try {
      const data = await getBranches(repositoryUrl.trim());
      const nextBranches = normalizeBranches(data);

      if (!nextBranches.length) {
        throw new Error("No branches were returned for this repository.");
      }

      setBranches(nextBranches);
    } catch (err) {
      setBranches([]);
      setError(err.message || "Could not load repository branches.");
    } finally {
      setLoadingBranches(false);
    }
  }

  function chooseBranch(branch) {
    setSelectedBranch(branch);
    setReviewResult(null);
    setError("");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  async function handleReview() {
    if (!selectedBranch) {
      setError("Select a branch first.");
      return;
    }

    setError("");
    setReviewResult(null);
    setReviewing(true);

    try {
      const result = await reviewLatestCommit({
        repositoryUrl: repositoryUrl.trim(),
        branchName: selectedBranch.name,
        teamInstruction
      });

      setReviewResult(result);
      setTimeout(() => {
        document
          .getElementById("review-result")
          ?.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 50);
    } catch (err) {
      setError(err.message || "The code review failed.");
    } finally {
      setReviewing(false);
    }
  }

  function resetReview() {
    setSelectedBranch(null);
    setReviewResult(null);
    setError("");
  }

  const review = reviewResult?.review;
  const commit = reviewResult?.commit || selectedBranch;
  const issues = Array.isArray(review?.issues) ? review.issues : [];

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <div className="brand-icon">
            <Code2 size={22} />
          </div>
          <div>
            <div className="brand-name">AI Code Review</div>
            <div className="brand-subtitle">GitHub review agent</div>
          </div>
        </div>

        <div className="status-pill">
          <span className="status-dot" />
          AI reviewer ready
        </div>
      </header>

      <main className="page">
        <section className="hero">
          <div className="hero-badge">
            <Sparkles size={15} />
            Commit-based code review
          </div>
          <h1>Review the latest commit on any branch.</h1>
          <p>
            Connect a GitHub repository, inspect each branch's latest commit,
            select the branch you want, and let the AI reviewer analyze the
            change.
          </p>
        </section>

        <section className="card repository-card">
          <div className="section-heading">
            <div className="step-number">1</div>
            <div>
              <h2>GitHub repository</h2>
              <p>Enter the repository you want to review.</p>
            </div>
          </div>

          <form className="repo-form" onSubmit={handleLoadBranches}>
            <div className="input-wrap">
              <Github size={19} />
              <input
                value={repositoryUrl}
                onChange={(event) => setRepositoryUrl(event.target.value)}
                placeholder="https://github.com/owner/repository"
                spellCheck="false"
              />
            </div>
            <button
              className="primary-button"
              type="submit"
              disabled={loadingBranches}
            >
              {loadingBranches ? (
                <>
                  <Loader2 className="spin" size={18} />
                  Loading...
                </>
              ) : (
                <>
                  Load branches
                  <ArrowRight size={18} />
                </>
              )}
            </button>
          </form>
        </section>

        {error && (
          <div className="error-banner">
            <AlertCircle size={19} />
            <span>{error}</span>
            <button onClick={() => setError("")} aria-label="Dismiss">
              ×
            </button>
          </div>
        )}

        {normalizedBranches.length > 0 && (
          <section className="card">
            <div className="section-heading">
              <div className="step-number">2</div>
              <div>
                <h2>Choose a branch</h2>
                <p>
                  The commit shown for each branch is the latest commit
                  currently pointed to by that branch.
                </p>
              </div>
            </div>

            <div className="branch-list">
              {normalizedBranches.map((branch) => {
                const isSelected =
                  selectedBranch?.name === branch.name;

                return (
                  <button
                    type="button"
                    className={`branch-row ${isSelected ? "selected" : ""}`}
                    key={branch.name}
                    onClick={() => chooseBranch(branch)}
                  >
                    <div className="branch-main">
                      <div className="branch-title">
                        <GitBranch size={18} />
                        <strong>{branch.name}</strong>
                      </div>
                      <div className="commit-message">
                        {branch.message}
                      </div>
                      <div className="branch-meta">
                        <span>
                          <Code2 size={14} />
                          {shortSha(branch.sha)}
                        </span>
                        <span>
                          <User size={14} />
                          {branch.author}
                        </span>
                        <span>
                          <Clock3 size={14} />
                          {formatDate(branch.date)}
                        </span>
                      </div>
                    </div>

                    <div className="select-indicator">
                      {isSelected ? (
                        <>
                          <Check size={17} />
                          Selected
                        </>
                      ) : (
                        "Select"
                      )}
                    </div>
                  </button>
                );
              })}
            </div>
          </section>
        )}

        {selectedBranch && !reviewResult && (
          <section className="card selected-card">
            <div className="section-heading">
              <div className="step-number">3</div>
              <div>
                <h2>Review selected commit</h2>
                <p>Confirm the branch and optionally add team-specific guidance.</p>
              </div>
            </div>

            <div className="commit-preview">
              <div className="commit-icon">
                <GitBranch size={21} />
              </div>
              <div className="commit-info">
                <div className="commit-branch">
                  {selectedBranch.name}
                </div>
                <div className="commit-title">
                  {selectedBranch.message}
                </div>
                <div className="commit-meta">
                  <span>SHA {shortSha(selectedBranch.sha)}</span>
                  <span>{selectedBranch.author}</span>
                  <span>{formatDate(selectedBranch.date)}</span>
                </div>
              </div>
            </div>

            <label className="field-label" htmlFor="team-instruction">
              Team instruction <span>optional</span>
            </label>
            <textarea
              id="team-instruction"
              value={teamInstruction}
              onChange={(event) => setTeamInstruction(event.target.value)}
              placeholder="Example: Pay special attention to authentication, API security, and Python syntax."
              rows={4}
            />

            <div className="action-row">
              <button className="secondary-button" onClick={resetReview}>
                Choose another branch
              </button>
              <button
                className="primary-button review-button"
                onClick={handleReview}
                disabled={reviewing}
              >
                {reviewing ? (
                  <>
                    <Loader2 className="spin" size={18} />
                    Reviewing commit...
                  </>
                ) : (
                  <>
                    <ShieldCheck size={18} />
                    Start AI review
                  </>
                )}
              </button>
            </div>
          </section>
        )}

        {reviewing && (
          <section className="card progress-card">
            <div className="loader-ring">
              <Loader2 className="spin" size={30} />
            </div>
            <h2>Reviewing {selectedBranch?.name}</h2>
            <p>
              Fetching the latest commit, recalling team knowledge, and
              analyzing the code change.
            </p>
          </section>
        )}

        {reviewResult && (
          <section id="review-result" className="review-section">
            <div className="result-header">
              <div>
                <div className="result-kicker">
                  <Check size={15} />
                  Review complete
                </div>
                <h2>AI review result</h2>
                <p>
                  {commit?.branch || selectedBranch?.name} ·{" "}
                  {shortSha(commit?.sha || selectedBranch?.sha)}
                </p>
              </div>

              <button
                className="secondary-button"
                onClick={() => {
                  setReviewResult(null);
                  setSelectedBranch(null);
                }}
              >
                <RefreshCw size={17} />
                New review
              </button>
            </div>

            <div className="result-grid">
              <div className="card summary-card">
                <div className="card-label">Overall status</div>
                <div
                  className={`overall-status status-${String(
                    review?.overall_status || "comment"
                  ).toLowerCase()}`}
                >
                  {review?.overall_status === "approve" ? (
                    <Check size={21} />
                  ) : review?.overall_status === "request_changes" ? (
                    <XCircle size={21} />
                  ) : (
                    <AlertCircle size={21} />
                  )}
                  <span>
                    {String(
                      review?.overall_status || "comment"
                    ).replace("_", " ")}
                  </span>
                </div>

                <div className="card-label summary-label">Summary</div>
                <p className="summary-text">
                  {review?.summary || "No summary returned."}
                </p>

                <div className="commit-detail">
                  <span>Commit</span>
                  <code>{commit?.sha || selectedBranch?.sha || "N/A"}</code>
                </div>
              </div>

              <div className="card issues-card">
                <div className="issues-heading">
                  <div>
                    <div className="card-label">Findings</div>
                    <h3>
                      {issues.length} issue{issues.length === 1 ? "" : "s"}
                    </h3>
                  </div>
                  <div className="issue-count">{issues.length}</div>
                </div>

                {issues.length === 0 ? (
                  <div className="empty-state">
                    <Check size={26} />
                    <strong>No issues reported</strong>
                    <span>
                      The AI reviewer did not return any findings for this
                      commit.
                    </span>
                  </div>
                ) : (
                  <div className="issue-list">
                    {issues.map((issue, index) => (
                      <IssueCard issue={issue} key={`${issue.file}-${index}`} />
                    ))}
                  </div>
                )}
              </div>
            </div>

            {reviewResult.team_memory && (
              <div className="card memory-card">
                <button
                  className="memory-toggle"
                  onClick={() => setShowMemory((value) => !value)}
                >
                  <div>
                    <div className="card-label">Hindsight</div>
                    <h3>Team memory used for this review</h3>
                  </div>
                  {showMemory ? (
                    <ChevronUp size={20} />
                  ) : (
                    <ChevronDown size={20} />
                  )}
                </button>

                {showMemory && (
                  <pre className="memory-content">
                    {typeof reviewResult.team_memory === "string"
                      ? reviewResult.team_memory
                      : JSON.stringify(reviewResult.team_memory, null, 2)}
                  </pre>
                )}
              </div>
            )}
          </section>
        )}
      </main>

      <footer className="footer">
        <span>AI Code Review Agent</span>
        <span>GitHub · Hindsight · LLM</span>
      </footer>
    </div>
  );
}

function IssueCard({ issue }) {
  const [open, setOpen] = useState(true);

  return (
    <article className="issue-card">
      <button className="issue-top" onClick={() => setOpen((v) => !v)}>
        <div className="issue-title-wrap">
          <span className={severityClass(issue.severity)}>
            {issue.severity || "info"}
          </span>
          <h4>{issue.title || "Review finding"}</h4>
        </div>
        {open ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
      </button>

      <div className="issue-location">
        <code>{issue.file || "Unknown file"}</code>
        {issue.line != null && <span>line {issue.line}</span>}
        {issue.category && <span>{issue.category}</span>}
      </div>

      {open && (
        <div className="issue-body">
          <p>{issue.description || "No description provided."}</p>
          {issue.suggestion && (
            <div className="suggestion">
              <strong>Suggested fix</strong>
              <p>{issue.suggestion}</p>
            </div>
          )}
        </div>
      )}
    </article>
  );
}