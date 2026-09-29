const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"
).replace(/\/$/, "");

async function request(endpoint, options = {}) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  const text = await response.text();

  let data;

  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = text;
  }

  if (!response.ok) {
    throw new Error(
      data?.detail || data?.message || text || `HTTP ${response.status}`,
    );
  }

  return data;
}

export async function getBranches(repositoryUrl) {
  const params = new URLSearchParams({
    repository_url: repositoryUrl,
  });

  const data = await request(`/api/branches?${params.toString()}`);

  return data.branches || [];
}

export async function reviewLatestCommit({
  repositoryUrl,
  branchName,
  teamInstruction = "",
}) {
  return request("/api/review/latest-commit", {
    method: "POST",

    body: JSON.stringify({
      repository_url: repositoryUrl,
      branch_name: branchName,
      team_instruction: teamInstruction,
    }),
  });
}
