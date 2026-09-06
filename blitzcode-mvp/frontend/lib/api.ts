const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface SubmissionResult {
  status: "accepted" | "wrong_answer" | "error";
  message?: string;
  executionTimeMs?: number;
}

export async function submitSolution(payload: {
  problemId: string;
  language: string;
  code: string;
}): Promise<SubmissionResult> {
  const res = await fetch(`${API_URL}/api/submissions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      problem_id: payload.problemId,
      language: payload.language,
      code: payload.code,
    }),
  });
  if (!res.ok) throw new Error("submission failed");
  return res.json();
}

export interface BlitzStartResponse {
  sessionId: string;
  endsAt: string; // ISO timestamp — server is the source of truth
  problemIds: string[];
}

export async function startBlitzSession(
  durationMinutes: number
): Promise<BlitzStartResponse> {
  const res = await fetch(`${API_URL}/api/blitz/start`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ duration_minutes: durationMinutes }),
  });
  if (!res.ok) throw new Error("failed to start blitz session");
  return res.json();
}
