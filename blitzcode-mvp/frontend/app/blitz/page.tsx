"use client";

import { useEffect, useState } from "react";
import Editor from "@monaco-editor/react";
import BlitzArena from "@/components/BlitzArena";
import CountdownRing from "@/components/CountdownRing";
import Badge from "@/components/Badge";
import { problems } from "@/lib/mockData";
import { startBlitzSession } from "@/lib/api";

type Stage = "select" | "playing" | "finished";
type ConsoleState = "idle" | "running" | "accepted";
type ExtensionVote = "waiting" | "accepted" | "declined";

const durations = [5, 10, 15];
const starterCode = "def solve():\n    # РќР°РїРёС€РёС‚Рµ СЂРµС€РµРЅРёРµ Р·РґРµСЃСЊ\n    pass\n";

export default function BlitzPage() {
  return <BlitzArena />;

  const [stage, setStage] = useState<Stage>("select");
  const [duration, setDuration] = useState(5);
  const [pool, setPool] = useState<typeof problems>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [solvedIds, setSolvedIds] = useState<string[]>([]);
  const [drafts, setDrafts] = useState<Record<string, string>>({});
  const [code, setCode] = useState(starterCode);
  const [score, setScore] = useState(0);
  const [opponentSolvedCount, setOpponentSolvedCount] = useState(0);
  const [consoleState, setConsoleState] = useState<ConsoleState>("idle");
  const [timeLimitSeconds, setTimeLimitSeconds] = useState(duration * 60);
  const [timeLeftSeconds, setTimeLeftSeconds] = useState(duration * 60);
  const [extensionRequest, setExtensionRequest] = useState(false);
  const [userExtensionVote, setUserExtensionVote] =
    useState<ExtensionVote>("waiting");
  const [opponentExtensionVote, setOpponentExtensionVote] =
    useState<ExtensionVote>("waiting");

  const currentProblem = pool[currentIndex];
  const opponentScore = pool
    .slice(0, opponentSolvedCount)
    .reduce(
      (total, problem) =>
        total + { easy: 100, medium: 200, hard: 350 }[problem.difficulty],
      0
    );

  useEffect(() => {
    if (stage !== "playing" || pool.length === 0) return;
    const interval = window.setInterval(() => {
      setOpponentSolvedCount((count) => Math.min(count + 1, pool.length));
    }, 22000);
    return () => window.clearInterval(interval);
  }, [stage, pool.length]);

  useEffect(() => {
    if (stage !== "playing" || extensionRequest || timeLeftSeconds <= 0) return;
    const timer = window.setInterval(() => {
      setTimeLeftSeconds((seconds) => {
        if (seconds <= 1) {
          window.clearInterval(timer);
          setExtensionRequest(true);
          setUserExtensionVote("waiting");
          setOpponentExtensionVote("waiting");
          window.setTimeout(() => setOpponentExtensionVote("accepted"), 800);
          return 0;
        }
        return seconds - 1;
      });
    }, 1000);

    return () => window.clearInterval(timer);
  }, [stage, extensionRequest, timeLeftSeconds <= 0]);

  function handleStart(minutes: number) {
    setDuration(minutes);
    setTimeLimitSeconds(minutes * 60);
    setTimeLeftSeconds(minutes * 60);
    // Server is the source of truth for timing and the problem pool.
    // Falls back to a local mock pool if the FastAPI backend isn't running yet.
    void startBlitzSession(minutes).catch(() => {
      // backend not reachable вЂ” continue with local mock pool for the demo
    });
    setPool([...problems]);
    setCurrentIndex(0);
    setSolvedIds([]);
    setDrafts({});
    setScore(0);
    setOpponentSolvedCount(0);
    setExtensionRequest(false);
    setUserExtensionVote("waiting");
    setOpponentExtensionVote("waiting");
    setCode(starterCode);
    setConsoleState("idle");
    window.scrollTo(0, 0);
    setStage("playing");
  }

  function finishMatch() {
    setExtensionRequest(false);
    setStage("finished");
  }

  function handleExtensionAgree() {
    setUserExtensionVote("accepted");
    if (opponentExtensionVote !== "accepted") return;
    setTimeLimitSeconds((seconds) => seconds + 30);
    setTimeLeftSeconds(30);
    setExtensionRequest(false);
    setUserExtensionVote("waiting");
    setOpponentExtensionVote("waiting");
  }

  function handleExtensionDecline() {
    setUserExtensionVote("declined");
    setOpponentExtensionVote("declined");
    window.setTimeout(finishMatch, 450);
  }

  function selectProblem(index: number) {
    if (!currentProblem) return;
    setDrafts((current) => ({ ...current, [currentProblem.id]: code }));
    setCurrentIndex(index);
    setCode(drafts[pool[index].id] ?? starterCode);
    setConsoleState("idle");
  }

  function handleCodeChange(value: string) {
    setCode(value);
    if (currentProblem) {
      setDrafts((current) => ({ ...current, [currentProblem.id]: value }));
    }
  }

  function handleRun() {
    setConsoleState("running");
    window.setTimeout(() => setConsoleState("idle"), 450);
  }

  function handleSolve() {
    if (!currentProblem || solvedIds.includes(currentProblem.id)) return;
    setConsoleState("running");

    window.setTimeout(() => {
      const nextSolved = [...solvedIds, currentProblem.id];
      const points = { easy: 100, medium: 200, hard: 350 }[
        currentProblem.difficulty
      ];
      setSolvedIds(nextSolved);
      setScore((value) => value + points);
      setConsoleState("accepted");

      const nextIndex = pool.findIndex(
        (problem, index) =>
          index > currentIndex && !nextSolved.includes(problem.id)
      );
      if (nextSolved.length === pool.length) {
        window.setTimeout(finishMatch, 700);
      } else if (nextIndex !== -1) {
        window.setTimeout(() => selectProblem(nextIndex), 650);
      }
    }, 550);
  }

  if (stage === "select") {
    return (
      <section className="relative isolate min-h-[calc(100vh-65px)] overflow-hidden px-6 py-16">
        <div className="absolute inset-0 -z-10 bg-hero-grid bg-grid opacity-40" />
        <div className="absolute left-1/2 top-20 -z-10 h-72 w-72 -translate-x-1/2 rounded-full bg-blitz/10 blur-[90px]" />
        <div className="mx-auto flex max-w-4xl flex-col items-center text-center">
          <span className="mb-5 rounded-full border border-blitz/30 bg-blitz/10 px-4 py-1.5 font-mono text-xs uppercase tracking-[0.24em] text-blitz">
            СЂРµР№С‚РёРЅРіРѕРІС‹Р№ СЃРїСЂРёРЅС‚
          </span>
          <h1 className="font-mono text-4xl font-extrabold tracking-tight text-ink md:text-6xl">
            Blitz <span className="text-blitz">Arena</span>
          </h1>
          <p className="mt-5 max-w-2xl text-base leading-7 text-muted">
            Р РµС€Р°Р№С‚Рµ Р·Р°РґР°С‡Рё РЅР° СЃРєРѕСЂРѕСЃС‚СЊ. Р§РµРј РІС‹С€Рµ СЃР»РѕР¶РЅРѕСЃС‚СЊ, С‚РµРј Р±РѕР»СЊС€Рµ РѕС‡РєРѕРІ.
            Р’СЃРµ Р·Р°РґР°С‡Рё РґРѕСЃС‚СѓРїРЅС‹ СЃСЂР°Р·Сѓ вЂ” РІС‹Р±РёСЂР°Р№С‚Рµ С‚Р°РєС‚РёРєСѓ Рё СЃР»РµРґРёС‚Рµ Р·Р° С‚Р°Р№РјРµСЂРѕРј.
          </p>

          <div className="mt-12 grid w-full gap-4 md:grid-cols-3">
          {durations.map((minutes) => (
            <button
              key={minutes}
              onClick={() => handleStart(minutes)}
              className="group rounded-2xl border border-line bg-surface/90 p-6 text-left transition-all hover:-translate-y-1 hover:border-blitz/60 hover:shadow-glow"
            >
              <div className="flex items-start justify-between">
                <span className="font-mono text-4xl font-extrabold text-ink">{minutes}</span>
                <span className="rounded-md bg-elevated px-2 py-1 font-mono text-[10px] uppercase tracking-widest text-muted group-hover:text-blitz">
                  {minutes === 5 ? "С‚СѓСЂР±Рѕ" : minutes === 10 ? "СЃС‚Р°РЅРґР°СЂС‚" : "РјР°СЂР°С„РѕРЅ"}
                </span>
              </div>
              <div className="mt-1 font-mono text-xs uppercase tracking-[0.2em] text-muted">
                РјРёРЅСѓС‚
              </div>
              <div className="mt-6 flex items-center justify-between border-t border-line pt-4 text-sm text-muted">
                <span>{problems.length} Р·Р°РґР°С‡</span>
                <span className="font-mono text-blitz">РќР°С‡Р°С‚СЊ в†’</span>
              </div>
            </button>
          ))}
          </div>
        </div>
      </section>
    );
  }

  if (stage === "playing" && currentProblem) {
    return (
      <div className="flex h-[calc(100vh-65px)] min-h-[600px] flex-col overflow-hidden bg-void">
        <header className="grid min-h-[92px] grid-cols-[1fr_auto_1fr] items-center border-b border-line bg-surface px-3 md:px-5">
          <div className="flex min-w-0 items-center gap-3">
            <div className="hidden h-10 w-10 shrink-0 place-items-center rounded-xl border border-blitz/40 bg-blitz/10 font-mono text-sm font-extrabold text-blitz sm:grid">
              Y
            </div>
            <div className="min-w-0">
              <div className="mb-2 flex items-center gap-2">
                <span className="rounded bg-blitz px-1.5 py-0.5 font-mono text-[8px] font-extrabold uppercase text-void">Р’С‹</span>
                <span className="truncate font-mono text-xs font-bold text-ink">you</span>
                <span className="hidden font-mono text-[9px] text-muted xl:inline">1980</span>
                <span className="font-mono text-[10px] font-bold text-blitz">{score}</span>
              </div>
              <div className="flex items-center gap-1">
                {pool.map((problem, index) => {
                  const solved = solvedIds.includes(problem.id);
                  return (
                    <button
                      key={problem.id}
                      onClick={() => selectProblem(index)}
                      aria-label={`Р—Р°РґР°С‡Р° ${index + 1}${solved ? ", СЂРµС€РµРЅР°" : ""}`}
                      className={`grid h-6 w-6 place-items-center rounded border font-mono text-[9px] font-bold transition-colors ${
                        solved
                          ? "border-success/50 bg-success/15 text-success"
                          : index === currentIndex
                          ? "border-blitz bg-blitz/10 text-blitz"
                          : "border-line bg-elevated text-muted hover:border-muted"
                      }`}
                    >
                      {solved ? <CheckIcon /> : index + 1}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>

          <div className="flex flex-col items-center">
            <span className="mb-1 font-mono text-[9px] uppercase tracking-[0.22em] text-muted">РѕСЃС‚Р°Р»РѕСЃСЊ</span>
            <CountdownRing
              durationSeconds={timeLimitSeconds}
              remainingSeconds={timeLeftSeconds}
              size="compact"
            />
          </div>

          <div className="flex min-w-0 items-center justify-end gap-3">
            <div className="min-w-0 text-right">
              <div className="mb-2 flex items-center justify-end gap-2">
                <span className="font-mono text-[10px] font-bold text-ember">{opponentScore}</span>
                <span className="hidden font-mono text-[9px] text-muted xl:inline">2841</span>
                <span className="truncate font-mono text-xs font-bold text-ink">nikolay_fast</span>
                <span className="rounded bg-ember px-1.5 py-0.5 font-mono text-[8px] font-extrabold uppercase text-void">РЎРѕРїРµСЂРЅРёРє</span>
              </div>
              <div className="flex items-center justify-end gap-1">
                {pool.map((problem, index) => {
                  const solved = index < opponentSolvedCount;
                  return (
                    <span
                      key={problem.id}
                      aria-label={`РЎРѕРїРµСЂРЅРёРє, Р·Р°РґР°С‡Р° ${index + 1}${solved ? ", СЂРµС€РµРЅР°" : ""}`}
                      className={`grid h-6 w-6 place-items-center rounded border font-mono text-[9px] font-bold ${
                        solved
                          ? "border-success/50 bg-success/15 text-success"
                          : index === opponentSolvedCount
                          ? "border-ember/50 bg-ember/10 text-ember"
                          : "border-line bg-elevated text-muted"
                      }`}
                    >
                      {solved ? <CheckIcon /> : index + 1}
                    </span>
                  );
                })}
              </div>
            </div>
            <div className="hidden h-10 w-10 shrink-0 place-items-center rounded-xl border border-ember/40 bg-ember/10 font-mono text-sm font-extrabold text-ember sm:grid">
              N
            </div>
          </div>
        </header>

        {extensionRequest && (
          <div className="fixed inset-0 z-[80] grid place-items-center bg-void/80 px-5 backdrop-blur-sm">
            <div className="w-full max-w-md rounded-2xl border border-line bg-surface p-6 text-center shadow-2xl shadow-black/40">
              <div className="mx-auto grid h-12 w-12 place-items-center rounded-2xl border border-amber/35 bg-amber/10 font-mono text-lg font-extrabold text-amber">
                +30
              </div>
              <h2 className="mt-5 text-2xl font-extrabold text-ink">
                Время закончилось
              </h2>
              <p className="mt-3 text-sm leading-6 text-muted">
                Можно добавить ещё 30 секунд, но только если оба участника
                согласны. Если один игрок против — матч завершается.
              </p>

              <div className="mt-5 grid grid-cols-2 gap-3 text-left">
                <VoteStatus label="Вы" status={userExtensionVote} />
                <VoteStatus label="Соперник" status={opponentExtensionVote} />
              </div>

              <div className="mt-6 grid grid-cols-2 gap-3">
                <button
                  onClick={handleExtensionDecline}
                  className="rounded-xl border border-line bg-elevated px-4 py-3 text-sm font-bold text-ink transition hover:border-ember hover:text-ember"
                >
                  Не согласен
                </button>
                <button
                  onClick={handleExtensionAgree}
                  disabled={opponentExtensionVote !== "accepted"}
                  className="rounded-xl bg-blitz px-4 py-3 text-sm font-extrabold text-void transition hover:shadow-glow disabled:cursor-not-allowed disabled:bg-muted"
                >
                  Добавить 30 сек
                </button>
              </div>
            </div>
          </div>
        )}

        <div className="grid min-h-0 flex-1 grid-cols-1 gap-2 p-2 md:grid-cols-[minmax(280px,0.9fr)_minmax(380px,1.25fr)] lg:grid-cols-[220px_minmax(300px,0.9fr)_minmax(420px,1.25fr)]">
          <aside className="hidden min-h-0 flex-col overflow-hidden rounded-lg border border-line bg-surface lg:flex">
            <div className="border-b border-line px-4 py-3">
              <div className="font-mono text-xs font-bold uppercase tracking-[0.15em] text-ink">Р—Р°РґР°С‡Рё СЂР°СѓРЅРґР°</div>
              <div className="mt-1 text-xs text-muted">Р’С‹Р±РµСЂРёС‚Рµ Р»СЋР±СѓСЋ Р·Р°РґР°С‡Сѓ</div>
            </div>
            <div className="flex-1 overflow-y-auto p-2">
              {pool.map((problem, index) => {
                const solved = solvedIds.includes(problem.id);
                return (
                  <button
                    key={problem.id}
                    onClick={() => selectProblem(index)}
                    className={`mb-1.5 flex w-full items-start gap-3 rounded-md border px-3 py-3 text-left transition-colors ${
                      index === currentIndex
                        ? "border-blitz/40 bg-blitz/10"
                        : "border-transparent hover:border-line hover:bg-elevated"
                    }`}
                  >
                    <span className={`mt-0.5 grid h-5 w-5 shrink-0 place-items-center rounded border font-mono text-[10px] ${solved ? "border-success/50 bg-success/15 text-success" : "border-line text-muted"}`}>
                      {solved ? <CheckIcon /> : index + 1}
                    </span>
                    <span className="min-w-0">
                      <span className={`block truncate text-xs font-medium ${solved ? "text-success" : "text-ink"}`}>{problem.title}</span>
                      <span className="mt-1 block font-mono text-[10px] capitalize text-muted">{problem.difficulty} В· {problem.acceptanceRate}%</span>
                    </span>
                  </button>
                );
              })}
            </div>
            <div className="border-t border-line p-3">
              <div className="mb-2 flex justify-between font-mono text-[10px] text-muted">
                <span>РџСЂРѕРіСЂРµСЃСЃ</span>
                <span>{Math.round((solvedIds.length / pool.length) * 100)}%</span>
              </div>
              <div className="h-1.5 overflow-hidden rounded-full bg-line">
                <div className="h-full rounded-full bg-success transition-all" style={{ width: `${(solvedIds.length / pool.length) * 100}%` }} />
              </div>
            </div>
          </aside>

          <section className="min-h-0 overflow-y-auto rounded-lg border border-line bg-surface">
            <div className="sticky top-0 z-10 flex items-center gap-6 border-b border-line bg-surface/95 px-5 backdrop-blur">
              <button className="border-b-2 border-blitz py-3 font-mono text-xs font-bold text-ink">РЈСЃР»РѕРІРёРµ</button>
              <button className="py-3 font-mono text-xs text-muted">Р РµС€РµРЅРёСЏ</button>
              <button className="py-3 font-mono text-xs text-muted">РћР±СЃСѓР¶РґРµРЅРёРµ</button>
            </div>
            <div className="p-5 md:p-6">
              <div className="mb-4 flex flex-wrap items-center gap-3">
                <span className="font-mono text-xs text-muted">{currentIndex + 1}.</span>
                <h1 className="font-mono text-xl font-bold text-ink">{currentProblem.title}</h1>
                <Badge difficulty={currentProblem.difficulty} />
              </div>
              <div className="mb-6 flex flex-wrap gap-2">
                {currentProblem.tags.map((tag) => (
                  <span key={tag} className="rounded-md bg-elevated px-2 py-1 text-[11px] text-muted">{tag}</span>
                ))}
              </div>
              <p className="text-sm leading-7 text-ink/90">{currentProblem.description}</p>

              <h2 className="mb-3 mt-8 font-mono text-sm font-bold text-ink">РџСЂРёРјРµСЂ 1</h2>
              <div className="rounded-lg border border-line bg-void/60 p-4 font-mono text-xs leading-6">
                <div><span className="text-muted">Р’РІРѕРґ:</span> <span className="text-ink">{currentProblem.examples[0].input}</span></div>
                <div><span className="text-muted">Р’С‹РІРѕРґ:</span> <span className="text-blitz">{currentProblem.examples[0].output}</span></div>
              </div>

              <h2 className="mb-3 mt-8 font-mono text-sm font-bold text-ink">РћРіСЂР°РЅРёС‡РµРЅРёСЏ</h2>
              <ul className="space-y-2 font-mono text-xs text-muted">
                <li className="rounded bg-elevated px-3 py-2">1 в‰¤ СЂР°Р·РјРµСЂ РІС…РѕРґРЅС‹С… РґР°РЅРЅС‹С… в‰¤ 10вЃµ</li>
                <li className="rounded bg-elevated px-3 py-2">Р’С…РѕРґРЅС‹Рµ РґР°РЅРЅС‹Рµ РІСЃРµРіРґР° СЃРѕРѕС‚РІРµС‚СЃС‚РІСѓСЋС‚ СѓСЃР»РѕРІРёСЋ</li>
              </ul>
            </div>
          </section>

          <section className="flex min-h-[560px] min-w-0 flex-col overflow-hidden rounded-lg border border-line bg-elevated md:min-h-0">
            <div className="flex h-11 items-center justify-between border-b border-line px-3">
              <select className="rounded-md border border-line bg-surface px-2.5 py-1.5 font-mono text-xs text-ink outline-none focus:border-blitz">
                <option>Python 3</option>
                <option>JavaScript</option>
                <option>C++17</option>
              </select>
              <div className="flex items-center gap-1 text-[10px] text-muted">
                <span className="h-1.5 w-1.5 rounded-full bg-success" /> Р°РІС‚РѕСЃРѕС…СЂР°РЅРµРЅРёРµ
              </div>
            </div>

            <div className="min-h-[320px] flex-1">
              <Editor
                height="100%"
                theme="vs-dark"
                language="python"
                value={code}
                onChange={(value?: string) => handleCodeChange(value ?? "")}
                options={{
                  fontFamily: "JetBrains Mono, monospace",
                  fontSize: 14,
                  lineHeight: 22,
                  minimap: { enabled: false },
                  scrollBeyondLastLine: false,
                  padding: { top: 16 },
                }}
              />
            </div>

            <div className="h-32 border-t border-line bg-surface">
              <div className="flex h-9 items-center gap-5 border-b border-line px-4 font-mono text-[11px]">
                <span className="border-b border-blitz py-2.5 text-ink">Р РµР·СѓР»СЊС‚Р°С‚</span>
                <span className="text-muted">РўРµСЃС‚С‹</span>
              </div>
              <div className="flex h-[92px] items-center px-4 font-mono text-xs">
                {consoleState === "idle" && <span className="text-muted">Р—Р°РїСѓСЃС‚РёС‚Рµ РєРѕРґ РёР»Рё РѕС‚РїСЂР°РІСЊС‚Рµ СЂРµС€РµРЅРёРµ.</span>}
                {consoleState === "running" && <span className="animate-pulse text-amber">РџСЂРѕРІРµСЂСЏРµРј С‚РµСЃС‚С‹...</span>}
                {consoleState === "accepted" && (
                  <div>
                    <div className="flex items-center gap-2 font-bold text-success"><CheckIcon /> Accepted</div>
                    <div className="mt-1 text-[10px] text-muted">Р’СЃРµ С‚РµСЃС‚С‹ РїСЂРѕР№РґРµРЅС‹ В· 42 ms В· 13.7 MB</div>
                  </div>
                )}
              </div>
            </div>

            <div className="flex items-center justify-between border-t border-line bg-surface px-3 py-2">
              <span className="font-mono text-[10px] text-muted">вЊ Enter вЂ” РѕС‚РїСЂР°РІРёС‚СЊ</span>
              <div className="flex gap-2">
                <button onClick={handleRun} className="rounded-md border border-line bg-elevated px-4 py-2 font-mono text-xs font-bold text-ink transition-colors hover:border-muted">Р—Р°РїСѓСЃС‚РёС‚СЊ</button>
                <button
                  onClick={handleSolve}
                  disabled={solvedIds.includes(currentProblem.id) || consoleState === "running"}
                  className="rounded-md bg-blitz px-4 py-2 font-mono text-xs font-extrabold text-void transition-shadow hover:shadow-glow disabled:cursor-not-allowed disabled:bg-success/60"
                >
                  {solvedIds.includes(currentProblem.id) ? "вњ“ Р РµС€РµРЅРѕ" : "РћС‚РїСЂР°РІРёС‚СЊ"}
                </button>
              </div>
            </div>
          </section>
        </div>
      </div>
    );
  }

  const playerSolvedCount = solvedIds.length;
  const opponentFinalSolvedCount = Math.min(opponentSolvedCount, pool.length);
  const resultTitle =
    playerSolvedCount > opponentFinalSolvedCount
      ? "Вы выиграли"
      : playerSolvedCount < opponentFinalSolvedCount
      ? "Победил соперник"
      : "Ничья";
  const resultTone =
    playerSolvedCount > opponentFinalSolvedCount
      ? "text-success"
      : playerSolvedCount < opponentFinalSolvedCount
      ? "text-ember"
      : "text-amber";

  return (
    <div className="relative isolate flex min-h-[calc(100vh-65px)] items-center justify-center overflow-hidden px-6 py-16 text-center">
      <div className="absolute inset-0 -z-10 bg-hero-grid bg-grid opacity-30" />
      <div className="absolute left-1/2 top-1/2 -z-10 h-80 w-80 -translate-x-1/2 -translate-y-1/2 rounded-full bg-blitz/10 blur-[100px]" />
      <div className="w-full max-w-xl rounded-2xl border border-line bg-surface/90 p-8 shadow-2xl md:p-12">
        <div className="mx-auto mb-6 grid h-16 w-16 place-items-center rounded-2xl border border-success/40 bg-success/10 text-success shadow-glow">
          <TrophyIcon />
        </div>
        <span className="font-mono text-xs uppercase tracking-[0.24em] text-muted">Матч завершён</span>
        <h1 className={`mt-3 text-4xl font-extrabold ${resultTone}`}>{resultTitle}</h1>
        <div className="mt-2 text-sm leading-6 text-muted">
          Победитель определяется по количеству решённых задач за отведённое время.
        </div>
        <div className="mt-8 grid grid-cols-2 gap-3">
          <Stat label="Вы решили" value={`${playerSolvedCount} / ${pool.length}`} />
          <Stat label="Соперник решил" value={`${opponentFinalSolvedCount} / ${pool.length}`} />
          <Stat label="Ваши очки" value={`${score}`} />
          <Stat label="Время матча" value={`${Math.floor(timeLimitSeconds / 60)}:${String(timeLimitSeconds % 60).padStart(2, "0")}`} />
        </div>
        <button
          onClick={() => setStage("select")}
          className="mt-8 w-full rounded-lg bg-blitz px-6 py-3 font-mono text-sm font-extrabold text-void transition-shadow hover:shadow-glow"
        >
          Сыграть ещё раз
        </button>
      </div>
    </div>
  );
}

function CheckIcon() {
  return (
    <svg viewBox="0 0 20 20" className="h-3.5 w-3.5" fill="none" stroke="currentColor" strokeWidth="2.5">
      <path d="m4 10 4 4 8-9" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function TrophyIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-8 w-8" fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="M8 4h8v4c0 3-1.8 5-4 5s-4-2-4-5V4Z" />
      <path d="M8 6H5v1c0 2 1.2 3.5 3.5 4M16 6h3v1c0 2-1.2 3.5-3.5 4M12 13v4M8.5 20h7M10 17h4" strokeLinecap="round" />
    </svg>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-line bg-elevated px-4 py-4">
      <div className="font-mono text-xl font-bold text-ink">{value}</div>
      <div className="mt-1 text-[10px] uppercase tracking-wider text-muted">{label}</div>
    </div>
  );
}

function VoteStatus({
  label,
  status,
}: {
  label: string;
  status: ExtensionVote;
}) {
  const text =
    status === "accepted"
      ? "согласен"
      : status === "declined"
      ? "не согласен"
      : "ожидание";
  const color =
    status === "accepted"
      ? "text-success"
      : status === "declined"
      ? "text-ember"
      : "text-amber";

  return (
    <div className="rounded-xl border border-line bg-elevated p-3">
      <div className="text-xs font-semibold text-muted">{label}</div>
      <div className={`mt-1 font-mono text-sm font-bold ${color}`}>{text}</div>
    </div>
  );
}
