const difficultyStyles: Record<string, string> = {
  easy: "text-success border-success/30 bg-success/10",
  medium: "text-amber border-amber/30 bg-amber/10",
  hard: "text-ember border-ember/30 bg-ember/10",
};

const difficultyLabels: Record<string, string> = {
  easy: "лёгкая",
  medium: "средняя",
  hard: "сложная",
};

export default function Badge({ difficulty }: { difficulty: string }) {
  return (
    <span
      className={`rounded border px-2 py-0.5 font-mono text-xs uppercase tracking-wide ${
        difficultyStyles[difficulty] ?? "text-muted border-line bg-surface"
      }`}
    >
      {difficultyLabels[difficulty] ?? difficulty}
    </span>
  );
}
