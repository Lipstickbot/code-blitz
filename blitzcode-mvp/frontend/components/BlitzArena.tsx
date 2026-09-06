"use client";

import { useEffect, useState } from "react";
import Editor from "@monaco-editor/react";
import Badge from "@/components/Badge";
import CountdownRing from "@/components/CountdownRing";
import { problems, type Problem } from "@/lib/mockData";
import { getProblemTests, runJavaScriptSolution, type JudgeProgress, type LocalJudgeResult } from "@/lib/problemTests";

type Stage = "setup" | "playing" | "finished";
type ConsoleState = "idle" | "running" | "accepted" | "rejected";
type LanguageId = "javascript" | "python" | "cpp";
type JudgeRowStatus = "pending" | "running" | "passed" | "failed";

const durations = [5, 10, 20];
const scoreMap = { easy: 100, medium: 200, hard: 350 } as const;

const languages: Record<LanguageId, { label: string; monaco: string; runnable: boolean; template: string }> = {
  javascript: {
    label: "JavaScript",
    monaco: "javascript",
    runnable: true,
    template: `function solve() {
  // напишите решение здесь
}
`,
  },
  python: {
    label: "Python 3",
    monaco: "python",
    runnable: false,
    template: `def solve():
    # напишите решение здесь
    pass
`,
  },
  cpp: {
    label: "C++17",
    monaco: "cpp",
    runnable: false,
    template: `#include <bits/stdc++.h>
using namespace std;

int main() {
    return 0;
}
`,
  },
};

export default function BlitzArena() {
  const [stage, setStage] = useState<Stage>("setup");
  const [duration, setDuration] = useState(10);
  const [selectedIds, setSelectedIds] = useState(problems.slice(0, 4).map((p) => p.id));
  const [pool, setPool] = useState<Problem[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [solvedIds, setSolvedIds] = useState<string[]>([]);
  const [opponentSolved, setOpponentSolved] = useState(0);
  const [timeLimit, setTimeLimit] = useState(600);
  const [timeLeft, setTimeLeft] = useState(600);
  const [language, setLanguage] = useState<LanguageId>("javascript");
  const [code, setCode] = useState(languages.javascript.template);
  const [consoleState, setConsoleState] = useState<ConsoleState>("idle");
  const [result, setResult] = useState<LocalJudgeResult | null>(null);
  const [progress, setProgress] = useState<JudgeProgress | null>(null);
  const [needExtraTime, setNeedExtraTime] = useState(false);

  const currentProblem = pool[currentIndex];
  const currentTests = currentProblem ? getProblemTests(currentProblem.id) : [];
  const currentLanguage = languages[language];
  const playerScore = solvedIds.reduce((sum, id) => {
    const problem = pool.find((p) => p.id === id);
    return problem ? sum + scoreMap[problem.difficulty] : sum;
  }, 0);

  useEffect(() => {
    if (stage !== "playing") return;
    const timer = window.setInterval(() => {
      setTimeLeft((value) => {
        if (value <= 1) {
          window.clearInterval(timer);
          setNeedExtraTime(true);
          return 0;
        }
        return value - 1;
      });
    }, 1000);
    return () => window.clearInterval(timer);
  }, [stage, timeLimit]);

  useEffect(() => {
    if (stage !== "playing" || pool.length === 0) return;
    const bot = window.setInterval(() => setOpponentSolved((v) => Math.min(v + 1, pool.length)), 26000);
    return () => window.clearInterval(bot);
  }, [stage, pool.length]);

  function resetEditor(nextLanguage = language) {
    setCode(languages[nextLanguage].template);
    setConsoleState("idle");
    setResult(null);
    setProgress(null);
  }

  function changeLanguage(next: LanguageId) {
    setLanguage(next);
    resetEditor(next);
  }

  function toggleProblem(id: string) {
    setSelectedIds((ids) => ids.includes(id) ? (ids.length === 1 ? ids : ids.filter((x) => x !== id)) : [...ids, id]);
  }

  function startMatch(minutes = duration, ids = selectedIds) {
    const nextPool = problems.filter((p) => ids.includes(p.id));
    setPool(nextPool.length ? nextPool : problems.slice(0, 4));
    setCurrentIndex(0);
    setSolvedIds([]);
    setOpponentSolved(0);
    setTimeLimit(minutes * 60);
    setTimeLeft(minutes * 60);
    setNeedExtraTime(false);
    resetEditor(language);
    setStage("playing");
    window.scrollTo(0, 0);
  }

  async function runCurrentProblem(markAsSolved: boolean) {
    if (!currentProblem || solvedIds.includes(currentProblem.id)) return;
    setConsoleState("running");
    setResult(null);
    setProgress({ current: 0, total: currentTests.length, phase: "queued", passedTests: [] });

    if (!currentLanguage.runnable) {
      await wait(900);
      setResult({
        status: "error",
        message: "Этот язык уже можно выбрать и писать код. Реальный запуск тестов пока подключён для JavaScript; Python и C++ будут работать через серверный runner.",
        testsPassed: 0,
        testsTotal: currentTests.length,
      });
      setProgress({ current: 0, total: currentTests.length, phase: "done", passedTests: [] });
      setConsoleState("rejected");
      return;
    }

    const nextResult = await runJavaScriptSolution(currentProblem.id, code, {
      delayMs: 540,
      onProgress: setProgress,
    });
    setResult(nextResult);

    if (nextResult.status !== "accepted") {
      setConsoleState("rejected");
      return;
    }

    setConsoleState("accepted");
    if (!markAsSolved) return;

    window.setTimeout(() => {
      const nextSolved = [...solvedIds, currentProblem.id];
      setSolvedIds(nextSolved);
      const nextIndex = pool.findIndex((p, i) => i > currentIndex && !nextSolved.includes(p.id));
      if (nextSolved.length === pool.length) {
        setStage("finished");
      } else if (nextIndex !== -1) {
        setCurrentIndex(nextIndex);
        resetEditor(language);
      }
    }, 450);
  }

  if (stage === "playing" && currentProblem) {
    const progressPercent = progress?.total
      ? Math.round((progress.current / progress.total) * 100)
      : consoleState === "running"
        ? 8
        : 0;
    const judgeTitle = getJudgeTitle(consoleState, progress);

    return (
      <div className="flex h-[calc(100vh-64px)] min-h-[650px] flex-col overflow-hidden bg-void">
        <header className="grid min-h-[94px] grid-cols-[1fr_auto_1fr] items-center border-b border-line bg-surface px-4">
          <PlayerProgress name="you" label="Вы" score={playerScore} solved={solvedIds.length} total={pool.length} accent="blitz" />
          <div className="flex flex-col items-center">
            <span className="mb-1 text-[10px] font-bold uppercase tracking-[0.2em] text-muted">Онлайн-матч</span>
            <CountdownRing durationSeconds={timeLimit} remainingSeconds={timeLeft} size="compact" />
          </div>
          <PlayerProgress name="online_rival" label="Соперник" score={opponentSolved * 180} solved={opponentSolved} total={pool.length} accent="ember" align="right" />
        </header>

        {needExtraTime && (
          <div className="fixed inset-0 z-[80] grid place-items-center bg-void/80 px-5 backdrop-blur-sm">
            <div className="w-full max-w-md rounded-2xl border border-line bg-surface p-6 text-center shadow-2xl shadow-black/40">
              <div className="mx-auto grid h-12 w-12 place-items-center rounded-2xl border border-amber/35 bg-amber/10 font-mono text-lg font-extrabold text-amber">+30</div>
              <h2 className="mt-5 text-2xl font-extrabold text-ink">Время закончилось</h2>
              <p className="mt-3 text-sm leading-6 text-muted">Если оба игрока согласны — добавляется 30 секунд. Если один против — матч завершается.</p>
              <div className="mt-6 grid grid-cols-2 gap-3">
                <button onClick={() => setStage("finished")} className="rounded-xl border border-line bg-elevated px-4 py-3 text-sm font-bold text-ink transition hover:border-ember hover:text-ember">Не согласен</button>
                <button onClick={() => { setTimeLimit((v) => v + 30); setTimeLeft(30); setNeedExtraTime(false); }} className="rounded-xl bg-blitz px-4 py-3 text-sm font-extrabold text-void transition hover:shadow-glow">Добавить 30 сек</button>
              </div>
            </div>
          </div>
        )}

        <div className="grid min-h-0 flex-1 gap-2 p-2 xl:grid-cols-[280px_minmax(360px,0.9fr)_minmax(480px,1.1fr)]">
          <aside className="hidden min-h-0 overflow-hidden rounded-xl border border-line bg-surface xl:flex xl:flex-col">
            <div className="border-b border-line p-4">
              <div className="text-xs font-bold uppercase tracking-widest text-muted">Задачи матча</div>
              <div className="mt-1 text-sm font-bold text-ink">{pool.length} задач · {solvedIds.length} решено</div>
            </div>
            <div className="flex-1 overflow-y-auto p-2">
              {pool.map((problem, index) => {
                const solved = solvedIds.includes(problem.id);
                return (
                  <button key={problem.id} onClick={() => { setCurrentIndex(index); resetEditor(language); }} className={`mb-2 flex w-full items-start gap-3 rounded-xl border p-3 text-left transition ${index === currentIndex ? "border-blitz/45 bg-blitz/10" : "border-transparent hover:border-line hover:bg-elevated"}`}>
                    <span className={`grid h-6 w-6 shrink-0 place-items-center rounded-full border text-xs font-bold ${solved ? "border-success/50 bg-success/15 text-success" : "border-line text-muted"}`}>{solved ? "✓" : index + 1}</span>
                    <span className="min-w-0"><span className="block truncate text-sm font-semibold text-ink">{problem.title}</span><span className="mt-1 block text-xs capitalize text-muted">{problem.difficulty} · {getProblemTests(problem.id).length} теста</span></span>
                  </button>
                );
              })}
            </div>
          </aside>

          <section className="min-h-0 overflow-y-auto rounded-xl border border-line bg-surface">
            <div className="sticky top-0 z-10 border-b border-line bg-surface/95 px-5 py-4 backdrop-blur">
              <div className="flex flex-wrap items-center gap-3"><span className="font-mono text-xs text-muted">{currentIndex + 1}.</span><h1 className="text-xl font-extrabold text-ink">{currentProblem.title}</h1><Badge difficulty={currentProblem.difficulty} /></div>
            </div>
            <div className="space-y-5 p-5">
              <div className="grid grid-cols-3 gap-2"><InfoTile label="Тесты" value={`${currentTests.length}`} /><InfoTile label="Очки" value={`${scoreMap[currentProblem.difficulty]}`} /><InfoTile label="Проход" value={`${currentProblem.acceptanceRate}%`} /></div>
              <p className="text-sm leading-7 text-ink/90">Решите задачу и отправьте код. Побеждает игрок, который решит больше задач за выбранное время.</p>
              <div className="rounded-xl border border-line bg-void/60 p-4"><div className="text-xs font-bold uppercase tracking-widest text-muted">Пример</div><div className="mt-3 font-mono text-xs leading-6"><div><span className="text-muted">Ввод:</span> <span className="text-ink">{currentProblem.examples[0].input}</span></div><div><span className="text-muted">Вывод:</span> <span className="text-blitz">{currentProblem.examples[0].output}</span></div></div></div>
              <div className="flex flex-wrap gap-2">{currentProblem.tags.map((tag) => <span key={tag} className="rounded-full bg-elevated px-3 py-1 text-xs text-muted">{tag}</span>)}</div>
            </div>
          </section>
          <section className="flex min-h-[560px] min-w-0 flex-col overflow-hidden rounded-xl border border-line bg-elevated lg:min-h-0">
            <div className="flex flex-wrap items-center justify-between gap-3 border-b border-line px-3 py-2">
              <div className="flex items-center gap-2">
                {(Object.keys(languages) as LanguageId[]).map((id) => (
                  <button key={id} onClick={() => changeLanguage(id)} className={`rounded-lg px-3 py-1.5 font-mono text-xs font-bold transition ${language === id ? "bg-blitz text-void" : "bg-surface text-muted hover:text-ink"}`}>{languages[id].label}</button>
                ))}
              </div>
              <span className="text-xs text-muted">{currentLanguage.runnable ? "реальная проверка тестов" : "шаблон языка · runner скоро"}</span>
            </div>

            <div className="min-h-[320px] flex-1">
              <Editor height="100%" theme="vs-dark" language={currentLanguage.monaco} value={code} onChange={(value?: string) => setCode(value ?? "")} options={{ fontFamily: "JetBrains Mono, monospace", fontSize: 14, lineHeight: 22, minimap: { enabled: false }, scrollBeyondLastLine: false, padding: { top: 16 } }} />
            </div>

            <div className="border-t border-line bg-surface px-4 py-3">
              <div className="mb-3 flex items-center justify-between gap-3 text-xs">
                <span className="font-bold uppercase tracking-widest text-muted">Judge</span>
                <span className="font-mono text-muted">{progress ? `${progress.current}/${progress.total}` : `${currentTests.length} теста`}</span>
              </div>
              <div className="mb-3 h-2 overflow-hidden rounded-full bg-void">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${consoleState === "rejected" ? "bg-ember" : "bg-blitz"}`}
                  style={{ width: `${consoleState === "idle" ? 0 : progressPercent || 8}%` }}
                />
              </div>
              <div className="max-h-44 overflow-y-auto rounded-xl border border-line bg-void/70 p-3 font-mono text-xs">
                <div className="mb-3 flex items-center justify-between gap-3">
                  <span className={`${consoleState === "running" ? "animate-pulse text-amber" : consoleState === "accepted" ? "text-success" : consoleState === "rejected" ? "text-ember" : "text-muted"}`}>
                    {judgeTitle}
                  </span>
                  {result?.executionTimeMs ? <span className="text-[10px] text-muted">{result.executionTimeMs} ms</span> : null}
                </div>

                {consoleState === "idle" ? (
                  <div className="text-muted">Нажмите «Запустить тесты» или «Отправить». Проверка пройдёт по нескольким sample и hidden тестам.</div>
                ) : (
                  <div className="grid gap-1.5">
                    {currentTests.map((test, index) => {
                      const number = index + 1;
                      const status: JudgeRowStatus =
                        result?.failedCase && progress?.activeTest === number && consoleState === "rejected"
                          ? "failed"
                          : progress?.passedTests.includes(number)
                            ? "passed"
                            : progress?.activeTest === number && consoleState === "running"
                              ? "running"
                              : "pending";

                      return (
                        <JudgeTestRow
                          key={`${currentProblem.id}-${number}`}
                          name={test.name ?? `${number <= 2 ? "Sample" : "Hidden"} test ${number}`}
                          status={status}
                        />
                      );
                    })}
                  </div>
                )}

                {consoleState === "accepted" && (
                  <div className="mt-3 rounded-lg border border-success/25 bg-success/10 p-2 text-success">
                    ✓ Accepted · все тесты пройдены · {result?.testsPassed ?? 0}/{result?.testsTotal ?? 0}
                  </div>
                )}
                {consoleState === "rejected" && result && (
                  <div className="mt-3 rounded-lg border border-ember/25 bg-ember/10 p-2">
                    <div className="font-bold text-ember">{result.status === "wrong_answer" ? "✕ Wrong Answer" : "✕ Error"}</div>
                    <div className="mt-1 text-[10px] text-muted">Пройдено: {result.testsPassed}/{result.testsTotal}. {result.message}</div>
                    {result.failedCase && <div className="mt-2 space-y-1 text-[10px] leading-5"><div><span className="text-muted">input:</span> <span className="text-ink">{formatValue(result.failedCase.input)}</span></div><div><span className="text-muted">expected:</span> <span className="text-success">{formatValue(result.failedCase.expected)}</span></div><div><span className="text-muted">received:</span> <span className="text-ember">{formatValue(result.failedCase.received)}</span></div></div>}
                  </div>
                )}
              </div>
            </div>

            <div className="flex items-center justify-between gap-2 border-t border-line bg-surface px-3 py-2">
              <button onClick={() => resetEditor(language)} disabled={consoleState === "running"} className="rounded-lg border border-line bg-elevated px-4 py-2 text-xs font-bold text-muted transition hover:text-ink disabled:opacity-60">Сбросить</button>
              <div className="flex gap-2"><button onClick={() => void runCurrentProblem(false)} disabled={consoleState === "running"} className="rounded-lg border border-line bg-elevated px-4 py-2 text-xs font-bold text-ink transition hover:border-muted disabled:opacity-60">Запустить тесты</button><button onClick={() => void runCurrentProblem(true)} disabled={solvedIds.includes(currentProblem.id) || consoleState === "running"} className="rounded-lg bg-blitz px-4 py-2 text-xs font-extrabold text-void transition hover:shadow-glow disabled:cursor-not-allowed disabled:bg-success/60">{solvedIds.includes(currentProblem.id) ? "✓ Решено" : "Отправить"}</button></div>
            </div>
          </section>
        </div>
      </div>
    );
  }

  if (stage === "finished") {
    const playerSolved = solvedIds.length;
    const rivalSolved = Math.min(opponentSolved, pool.length);
    const title = playerSolved > rivalSolved ? "Вы выиграли" : playerSolved < rivalSolved ? "Победил соперник" : "Ничья";
    return <div className="workspace-shell flex min-h-[calc(100vh-64px)] items-center justify-center px-5 py-12 text-center"><div className="w-full max-w-xl rounded-3xl border border-line bg-surface p-8 shadow-2xl shadow-black/30"><div className="mx-auto grid h-16 w-16 place-items-center rounded-2xl border border-blitz/35 bg-blitz/10 text-3xl">🏆</div><div className="mt-5 text-xs font-bold uppercase tracking-[0.2em] text-muted">Матч завершён</div><h1 className="mt-3 text-4xl font-extrabold text-ink">{title}</h1><p className="mt-3 text-sm text-muted">Победитель определяется по количеству решённых задач за выбранное время.</p><div className="mt-8 grid grid-cols-2 gap-3"><ResultStat label="Вы решили" value={`${playerSolved} / ${pool.length}`} /><ResultStat label="Соперник" value={`${rivalSolved} / ${pool.length}`} /><ResultStat label="Очки" value={`${playerScore}`} /><ResultStat label="Время" value={`${Math.floor(timeLimit / 60)}:${String(timeLimit % 60).padStart(2, "0")}`} /></div><button onClick={() => setStage("setup")} className="mt-8 w-full rounded-xl bg-blitz px-5 py-3 text-sm font-extrabold text-void transition hover:shadow-glow">Вернуться в онлайн-арену</button></div></div>;
  }

  return (
    <div className="workspace-shell min-h-[calc(100vh-64px)] overflow-hidden px-5 py-8">
      <div className="mx-auto flex min-h-[calc(100vh-110px)] max-w-7xl flex-col items-center justify-center">
        <section className="relative w-full overflow-hidden rounded-[36px] border border-line bg-surface px-5 py-10 shadow-2xl shadow-black/30 md:px-10 md:py-14">
          <div className="pointer-events-none absolute left-1/2 top-1/2 h-[560px] w-[560px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-blitz/10 blur-3xl" />
          <div className="pointer-events-none absolute left-1/2 top-1/2 h-[380px] w-[380px] -translate-x-1/2 -translate-y-1/2 rounded-full border border-blitz/10" />
          <div className="pointer-events-none absolute left-1/2 top-1/2 h-[520px] w-[520px] -translate-x-1/2 -translate-y-1/2 rounded-full border border-line/70" />

          <div className="relative z-10 mx-auto max-w-3xl text-center">
            <span className="inline-flex rounded-full border border-blitz/25 bg-blitz/10 px-4 py-1.5 text-xs font-bold uppercase tracking-[0.2em] text-blitz">
              Онлайн-блиц
            </span>
            <h1 className="mt-6 text-4xl font-extrabold tracking-tight text-ink md:text-6xl">
              Выбери время и жми старт.
            </h1>
            <p className="mx-auto mt-4 max-w-2xl text-sm leading-7 text-muted md:text-base">
              Быстрый матч один на один: таймер сверху, задачи в раунде, тесты в редакторе и победа по количеству решённых задач.
            </p>
          </div>

          <div className="relative z-10 mt-10 flex flex-col items-center">
            <button
              onClick={() => startMatch()}
              className="group relative grid h-56 w-56 place-items-center rounded-full border border-blitz/50 bg-blitz text-void shadow-[0_0_80px_rgba(76,242,192,0.22)] transition duration-300 hover:scale-105 hover:shadow-[0_0_110px_rgba(76,242,192,0.34)] md:h-64 md:w-64"
              aria-label="Начать онлайн-блиц"
            >
              <span className="absolute inset-3 rounded-full border border-void/20" />
              <span className="absolute -inset-4 rounded-full border border-blitz/20 transition group-hover:-inset-6" />
              <span className="text-center">
                <span className="block font-mono text-5xl font-extrabold uppercase tracking-tight md:text-6xl">Start</span>
                <span className="mt-2 block text-xs font-extrabold uppercase tracking-[0.22em] text-void/70">{duration} минут</span>
              </span>
            </button>

            <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
              {durations.map((minutes) => (
                <button
                  key={minutes}
                  onClick={() => setDuration(minutes)}
                  className={`grid h-20 w-20 place-items-center rounded-full border text-center transition hover:-translate-y-1 md:h-24 md:w-24 ${
                    duration === minutes
                      ? "border-blitz bg-blitz/15 text-blitz shadow-glow"
                      : "border-line bg-void text-muted hover:border-blitz/50 hover:text-ink"
                  }`}
                  aria-pressed={duration === minutes}
                >
                  <span>
                    <span className="block font-mono text-2xl font-extrabold">{minutes}</span>
                    <span className="block text-[10px] font-bold uppercase tracking-widest">мин</span>
                  </span>
                </button>
              ))}
            </div>

            <div className="mt-8 grid w-full max-w-3xl gap-3 md:grid-cols-3">
              <MiniStat label="формат" value="1 vs 1" />
              <MiniStat label="выбрано задач" value={`${selectedIds.length}`} />
              <MiniStat label="в базе" value={`${problems.length}`} />
            </div>
          </div>
        </section>

        <section className="mt-5 grid w-full gap-5 lg:grid-cols-[1fr_360px]">
          <div className="rounded-3xl border border-line bg-surface p-5 md:p-6">
            <div className="flex flex-col justify-between gap-3 md:flex-row md:items-end">
              <div>
                <h2 className="text-xl font-extrabold text-ink">Задачи для раунда</h2>
                <p className="mt-2 text-sm text-muted">Можно оставить стандартный набор или выбрать задачи вручную.</p>
              </div>
              <button
                onClick={() => setSelectedIds(problems.slice(0, 4).map((problem) => problem.id))}
                className="rounded-xl border border-line bg-elevated px-4 py-2 text-xs font-bold text-muted transition hover:text-ink"
              >
                Сбросить набор
              </button>
            </div>
            <div className="mt-5 grid max-h-72 gap-2 overflow-y-auto pr-1 md:grid-cols-2 xl:grid-cols-3">
              {problems.map((problem) => (
                <button
                  key={problem.id}
                  onClick={() => toggleProblem(problem.id)}
                  className={`flex items-center justify-between rounded-xl border p-3 text-left transition ${
                    selectedIds.includes(problem.id)
                      ? "border-blitz/45 bg-blitz/10"
                      : "border-line bg-void hover:border-muted"
                  }`}
                >
                  <span className="min-w-0">
                    <span className="block truncate text-sm font-semibold text-ink">{problem.title}</span>
                    <span className="mt-1 block text-xs capitalize text-muted">{problem.difficulty} · {getProblemTests(problem.id).length} теста</span>
                  </span>
                  <span className="ml-3 text-blitz">{selectedIds.includes(problem.id) ? "✓" : "+"}</span>
                </button>
              ))}
            </div>
          </div>

          <aside className="rounded-3xl border border-line bg-surface p-6">
            <h3 className="font-bold text-ink">Как работает онлайн-блиц</h3>
            <div className="mt-4 space-y-3 text-sm leading-6 text-muted">
              <p>1. Выбираешь 5, 10 или 20 минут.</p>
              <p>2. Нажимаешь центральный Start.</p>
              <p>3. Решаете задачи параллельно, а победитель определяется по числу Accepted.</p>
            </div>
          </aside>
        </section>
      </div>
    </div>
  );
}

function getJudgeTitle(consoleState: ConsoleState, progress: JudgeProgress | null) {
  if (consoleState === "idle") return "Ready";
  if (consoleState === "accepted") return "Accepted";
  if (consoleState === "rejected") return "Finished with error";
  if (progress?.phase === "queued") return "В очереди на проверку...";
  if (progress?.phase === "compile") return "Компиляция и подготовка sandbox...";
  if (progress?.phase === "running") return `Запускаем тест ${progress.activeTest ?? progress.current}/${progress.total}...`;
  return "Завершаем проверку...";
}

function JudgeTestRow({ name, status }: { name: string; status: JudgeRowStatus }) {
  const styles: Record<JudgeRowStatus, string> = {
    pending: "border-line bg-surface text-muted",
    running: "border-amber/35 bg-amber/10 text-amber",
    passed: "border-success/35 bg-success/10 text-success",
    failed: "border-ember/35 bg-ember/10 text-ember",
  };
  const icon = status === "passed" ? "✓" : status === "failed" ? "✕" : status === "running" ? "…" : "•";

  return (
    <div className={`flex items-center justify-between rounded-lg border px-2.5 py-2 transition ${styles[status]}`}>
      <span className="truncate">{name}</span>
      <span className="ml-3 font-bold">{icon}</span>
    </div>
  );
}

function PlayerProgress({ name, label, score, solved, total, accent, align = "left" }: { name: string; label: string; score: number; solved: number; total: number; accent: "blitz" | "ember"; align?: "left" | "right" }) {
  const accentClass = accent === "blitz" ? "text-blitz" : "text-ember";
  const badgeClass = accent === "blitz" ? "bg-blitz text-void" : "bg-ember text-void";
  return <div className={`min-w-0 ${align === "right" ? "text-right" : ""}`}><div className={`mb-2 flex items-center gap-2 ${align === "right" ? "justify-end" : ""}`}><span className={`rounded px-1.5 py-0.5 text-[9px] font-extrabold ${badgeClass}`}>{label}</span><span className="truncate text-xs font-bold text-ink">{name}</span><span className={`font-mono text-[11px] font-bold ${accentClass}`}>{score}</span></div><div className={`flex gap-1 ${align === "right" ? "justify-end" : ""}`}>{Array.from({ length: total }).map((_, i) => <span key={i} className={`grid h-6 w-6 place-items-center rounded border text-[10px] font-bold ${i < solved ? "border-success/50 bg-success/15 text-success" : "border-line bg-elevated text-muted"}`}>{i < solved ? "✓" : i + 1}</span>)}</div></div>;
}

function InfoTile({ label, value }: { label: string; value: string }) {
  return <div className="rounded-xl border border-line bg-void px-3 py-3"><div className="font-mono text-lg font-extrabold text-ink">{value}</div><div className="mt-1 text-[10px] uppercase tracking-widest text-muted">{label}</div></div>;
}

function MiniStat({ label, value }: { label: string; value: string }) {
  return <div className="min-w-20 rounded-xl bg-surface px-3 py-2 text-center"><div className="font-mono text-lg font-extrabold text-ink">{value}</div><div className="text-[10px] uppercase tracking-widest text-muted">{label}</div></div>;
}

function ResultStat({ label, value }: { label: string; value: string }) {
  return <div className="rounded-xl border border-line bg-elevated px-4 py-4"><div className="font-mono text-xl font-bold text-ink">{value}</div><div className="mt-1 text-[10px] uppercase tracking-wider text-muted">{label}</div></div>;
}

function formatValue(value: unknown) {
  return JSON.stringify(value);
}

function wait(ms: number) {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}

