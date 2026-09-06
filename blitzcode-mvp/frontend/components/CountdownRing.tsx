"use client";

import { useEffect, useState } from "react";

function formatTime(totalSeconds: number) {
  const m = Math.floor(totalSeconds / 60)
    .toString()
    .padStart(2, "0");
  const s = Math.floor(totalSeconds % 60)
    .toString()
    .padStart(2, "0");
  return `${m}:${s}`;
}

/**
 * The Blitz Countdown — this page's signature element.
 * A monospace digital clock fused with a draining trace bar that shifts
 * cyan -> amber -> ember as time runs out. Used in the hero, and in the
 * live Blitz Game session screen.
 */
export default function CountdownRing({
  durationSeconds,
  remainingSeconds,
  running = true,
  size = "lg",
  onComplete,
}: {
  durationSeconds: number;
  remainingSeconds?: number;
  running?: boolean;
  size?: "lg" | "md" | "compact";
  onComplete?: () => void;
}) {
  const [remaining, setRemaining] = useState(durationSeconds);
  const displayRemaining = remainingSeconds ?? remaining;
  const isControlled = remainingSeconds !== undefined;

  useEffect(() => {
    setRemaining(durationSeconds);
  }, [durationSeconds]);

  useEffect(() => {
    if (isControlled) return;
    if (!running || remaining <= 0) return;
    const id = setInterval(() => {
      setRemaining((prev) => {
        if (prev <= 1) {
          clearInterval(id);
          onComplete?.();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(id);
  }, [isControlled, running, remaining <= 0]); // eslint-disable-line react-hooks/exhaustive-deps

  const ratio = displayRemaining / durationSeconds;
  const color =
    ratio > 0.5 ? "#4CF2C0" : ratio > 0.2 ? "#FFB84D" : "#FF5C4D";
  const glow =
    ratio > 0.5
      ? "shadow-glow"
      : ratio > 0.2
      ? "shadow-[0_0_24px_rgba(255,184,77,0.3)]"
      : "shadow-glow-ember";

  const digitSize =
    size === "lg"
      ? "text-7xl md:text-8xl"
      : size === "md"
      ? "text-4xl"
      : "text-xl";

  if (size === "compact") {
    return (
      <div className="flex min-w-[172px] flex-col items-center gap-1.5">
        <span
          className={`font-mono font-extrabold tabular-nums tracking-[0.08em] ${digitSize}`}
          style={{ color, transition: "color 0.5s ease" }}
        >
          {formatTime(displayRemaining)}
        </span>
        <div className="h-1 w-full overflow-hidden rounded-full bg-line">
          <div
            className="h-full rounded-full transition-all duration-1000 ease-linear"
            style={{
              width: `${Math.max(ratio * 100, 0)}%`,
              backgroundColor: color,
              boxShadow: `0 0 10px ${color}`,
            }}
          />
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center gap-4">
      <div
        className={`rounded-2xl border border-line bg-elevated px-10 py-6 transition-shadow duration-500 ${glow}`}
      >
        <span
          className={`font-mono font-extrabold tabular-nums tracking-tight ${digitSize}`}
          style={{ color, transition: "color 0.5s ease" }}
        >
          {formatTime(displayRemaining)}
        </span>
      </div>
      <div className="h-1.5 w-64 overflow-hidden rounded-full bg-line">
        <div
          className="h-full rounded-full transition-all duration-1000 ease-linear"
          style={{
            width: `${Math.max(ratio * 100, 0)}%`,
            backgroundColor: color,
          }}
        />
      </div>
    </div>
  );
}
