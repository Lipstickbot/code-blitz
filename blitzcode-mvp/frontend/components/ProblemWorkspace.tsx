"use client";

import { useState } from "react";
import Editor from "@monaco-editor/react";
import { submitSolution, SubmissionResult } from "@/lib/api";

const languages = [
  { id: "python", label: "Python 3", template: "def solve():\n    pass\n" },
  { id: "javascript", label: "JavaScript", template: "function solve() {\n\n}\n" },
  { id: "cpp", label: "C++17", template: "#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n\n}\n" },
];

export default function ProblemWorkspace({ problemId }: { problemId: string }) {
  const [language, setLanguage] = useState(languages[0].id);
  const [code, setCode] = useState(languages[0].template);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<SubmissionResult | null>(null);

  function handleLanguageChange(id: string) {
    setLanguage(id);
    setCode(languages.find((l) => l.id === id)?.template ?? "");
  }

  async function handleSubmit() {
    setSubmitting(true);
    setResult(null);
    try {
      const res = await submitSolution({ problemId, language, code });
      setResult(res);
    } catch (e) {
      setResult({
        status: "error",
        message:
          "Не удалось связаться с backend. Убедитесь, что FastAPI сервер запущен (см. backend/README.md).",
      });
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex h-full min-h-[560px] flex-col overflow-hidden rounded-lg border border-line bg-elevated">
      <div className="flex items-center justify-between border-b border-line px-4 py-3">
        <select
          value={language}
          onChange={(e) => handleLanguageChange(e.target.value)}
          className="rounded border border-line bg-surface px-2 py-1 font-mono text-sm text-ink"
        >
          {languages.map((l) => (
            <option key={l.id} value={l.id}>
              {l.label}
            </option>
          ))}
        </select>
        <button
          onClick={handleSubmit}
          disabled={submitting}
          className="rounded-md bg-blitz px-4 py-1.5 font-mono text-sm font-bold text-void transition-shadow hover:shadow-glow disabled:opacity-50"
        >
          {submitting ? "Проверка..." : "Отправить решение"}
        </button>
      </div>

      <div className="min-h-[360px] flex-1">
        <Editor
          height="100%"
          theme="vs-dark"
          language={language === "cpp" ? "cpp" : language}
          value={code}
          onChange={(v?: string) => setCode(v ?? "")}
          options={{
            fontFamily: "JetBrains Mono, monospace",
            fontSize: 14,
            minimap: { enabled: false },
            scrollBeyondLastLine: false,
          }}
        />
      </div>

      {result && (
        <div
          className={`border-t border-line px-4 py-3 font-mono text-sm ${
            result.status === "accepted"
              ? "text-success"
              : result.status === "error"
              ? "text-muted"
              : "text-danger"
          }`}
        >
          {result.status === "accepted" && "✓ Accepted — все тесты пройдены"}
          {result.status === "wrong_answer" && "✗ Wrong Answer"}
          {result.status === "error" && result.message}
        </div>
      )}
    </div>
  );
}
