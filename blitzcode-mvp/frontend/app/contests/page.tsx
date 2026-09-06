"use client";

import Link from "next/link";
import { useState } from "react";

type Period = "week" | "month";

const leaderboards = {
  week: [
    { rank: 1, name: "nikolay_fast", points: 1840, solved: 6, avatar: "N" },
    { rank: 2, name: "ayana.dev", points: 1690, solved: 6, avatar: "A" },
    { rank: 3, name: "speedforce", points: 1425, solved: 5, avatar: "S" },
    { rank: 4, name: "quantum_qi", points: 1180, solved: 5, avatar: "Q" },
    { rank: 8, name: "you", points: 480, solved: 3, avatar: "Y", isMe: true },
  ],
  month: [
    { rank: 1, name: "ayana.dev", points: 8940, solved: 24, avatar: "A" },
    { rank: 2, name: "nikolay_fast", points: 8710, solved: 23, avatar: "N" },
    { rank: 3, name: "dark_horse", points: 7290, solved: 21, avatar: "D" },
    { rank: 4, name: "quantum_qi", points: 6880, solved: 20, avatar: "Q" },
    { rank: 24, name: "you", points: 1320, solved: 8, avatar: "Y", isMe: true },
  ],
};

export default function ContestsPage() {
  const [period, setPeriod] = useState<Period>("week");
  const rows = leaderboards[period];

  return (
    <div className="workspace-shell px-5 py-8">
      <div className="mx-auto max-w-7xl">
        <div className="mb-6 grid gap-4 lg:grid-cols-[1fr_310px]">
          <section className="rounded-2xl border border-line bg-surface p-6">
            <div className="text-xs font-bold uppercase tracking-[0.18em] text-blitz">Соревновательный режим</div>
            <h1 className="mt-3 text-3xl font-extrabold text-ink">Контесты BlitzCode</h1>
            <p className="mt-3 max-w-3xl text-sm leading-6 text-muted">
              Недельные и месячные турниры дают очки за решённые задачи. Интерфейс остаётся рабочим и спокойным: таблица лидеров, прогресс, правила начисления и быстрый вход в задачи.
            </p>
          </section>

          <section className="rounded-2xl border border-blitz/25 bg-blitz/10 p-6">
            <div className="text-xs font-bold uppercase tracking-widest text-blitz">Ваш сезон</div>
            <div className="mt-3 text-3xl font-extrabold text-ink">1 800</div>
            <div className="text-sm text-muted">очков за текущий сезон</div>
            <div className="mt-5 h-2 overflow-hidden rounded-full bg-void">
              <div className="h-full w-[58%] rounded-full bg-blitz" />
            </div>
          </section>
        </div>

        <section className="grid gap-4 lg:grid-cols-2">
          <ContestCard
            label="Недельный турнир"
            title="Weekly Sprint #27"
            description="Шесть задач разной сложности. Быстрые решения и серия без ошибок дают бонус к очкам."
            remaining="2 дня 04:18"
            participants="42 участника"
            progress="3 / 6"
            points="480"
            rank="#8"
            accent="blitz"
          />
          <ContestCard
            label="Месячный чемпионат"
            title="July Championship"
            description="Большой сезонный зачёт: новые задачи открываются каждую неделю июля."
            remaining="25 дней"
            participants="186 участников"
            progress="8 / 24"
            points="1 320"
            rank="#24"
            accent="amber"
          />
        </section>

        <div className="mt-6 grid gap-4 lg:grid-cols-[1fr_310px]">
          <section className="overflow-hidden rounded-2xl border border-line bg-surface">
            <div className="flex flex-col justify-between gap-4 border-b border-line px-5 py-4 sm:flex-row sm:items-center">
              <div>
                <h2 className="font-bold text-ink">Таблица лидеров</h2>
                <p className="mt-1 text-xs text-muted">Текущие результаты участников</p>
              </div>
              <div className="flex rounded-xl border border-line bg-void p-1">
                <PeriodButton active={period === "week"} onClick={() => setPeriod("week")}>Неделя</PeriodButton>
                <PeriodButton active={period === "month"} onClick={() => setPeriod("month")}>Месяц</PeriodButton>
              </div>
            </div>

            <div className="px-2 py-2 sm:px-4">
              <div className="grid grid-cols-[52px_1fr_90px_120px] px-3 py-2 text-xs font-bold uppercase tracking-wider text-muted">
                <span>Место</span><span>Участник</span><span className="text-center">Решено</span><span className="text-right">Очки</span>
              </div>
              {rows.map((row) => (
                <div
                  key={row.name}
                  className={`mb-1 grid grid-cols-[52px_1fr_90px_120px] items-center rounded-xl border px-3 py-3 ${
                    row.isMe ? "border-blitz/35 bg-blitz/10" : "border-transparent hover:bg-elevated/70"
                  }`}
                >
                  <span className={`font-mono text-sm font-extrabold ${row.rank <= 3 ? "text-amber" : "text-muted"}`}>#{row.rank}</span>
                  <div className="flex min-w-0 items-center gap-3">
                    <span className={`grid h-8 w-8 shrink-0 place-items-center rounded-lg border text-xs font-bold ${row.isMe ? "border-blitz/40 bg-blitz/10 text-blitz" : "border-line bg-elevated text-ink"}`}>{row.avatar}</span>
                    <div className="min-w-0">
                      <div className="truncate text-sm font-semibold text-ink">{row.name}</div>
                      {row.isMe && <div className="text-[10px] uppercase text-blitz">это вы</div>}
                    </div>
                  </div>
                  <span className="text-center font-mono text-xs text-muted">{row.solved}</span>
                  <span className="text-right font-mono text-sm font-extrabold text-ink">{row.points.toLocaleString("ru-RU")}</span>
                </div>
              ))}
            </div>
          </section>

          <aside className="space-y-4">
            <div className="rounded-2xl border border-line bg-surface p-5">
              <h3 className="font-bold text-ink">Как начисляются очки</h3>
              <div className="mt-5 space-y-3">
                <ScoreRule color="bg-success" label="Лёгкая задача" points="+100" />
                <ScoreRule color="bg-amber" label="Средняя задача" points="+200" />
                <ScoreRule color="bg-ember" label="Сложная задача" points="+350" />
              </div>
              <div className="mt-5 rounded-xl border border-blitz/20 bg-blitz/5 p-3 text-xs leading-5 text-muted">
                <span className="font-bold text-blitz">Комбо +15%</span><br />за три решения подряд без ошибки.
              </div>
            </div>

            <div className="rounded-2xl border border-line bg-surface p-5">
              <div className="text-xs font-bold uppercase tracking-widest text-muted">Следующий турнир</div>
              <div className="mt-2 text-lg font-bold text-ink">Night Blitz</div>
              <div className="mt-1 text-xs text-muted">Пятница · 21:00 · 15 минут</div>
              <Link href="/blitz" className="mt-4 block rounded-xl border border-line bg-void px-3 py-2 text-center text-xs font-bold text-ink transition hover:border-blitz hover:text-blitz">
                Открыть режим
              </Link>
            </div>
          </aside>
        </div>
      </div>
    </div>
  );
}

function ContestCard({ label, title, description, remaining, participants, progress, points, rank, accent }: {
  label: string; title: string; description: string; remaining: string; participants: string;
  progress: string; points: string; rank: string; accent: "blitz" | "amber";
}) {
  const isBlitz = accent === "blitz";
  return (
    <article className={`relative overflow-hidden rounded-2xl border bg-surface p-6 ${isBlitz ? "border-blitz/30" : "border-amber/30"}`}>
      <div className={`absolute -right-16 -top-20 h-48 w-48 rounded-full blur-[70px] ${isBlitz ? "bg-blitz/10" : "bg-amber/10"}`} />
      <div className="relative">
        <div className="flex items-start justify-between gap-4">
          <div>
            <span className={`text-xs font-bold uppercase tracking-[0.18em] ${isBlitz ? "text-blitz" : "text-amber"}`}>{label}</span>
            <h2 className="mt-2 text-xl font-extrabold text-ink">{title}</h2>
          </div>
          <span className={`rounded-full border px-2.5 py-1 text-xs font-bold uppercase ${isBlitz ? "border-blitz/30 bg-blitz/10 text-blitz" : "border-amber/30 bg-amber/10 text-amber"}`}>идёт сейчас</span>
        </div>
        <p className="mt-3 max-w-xl text-sm leading-6 text-muted">{description}</p>

        <div className="mt-5 grid grid-cols-3 gap-2 border-y border-line py-4">
          <Metric label="Ваши очки" value={points} />
          <Metric label="Ваше место" value={rank} />
          <Metric label="Решено" value={progress} />
        </div>

        <div className="mt-5 flex flex-wrap items-center justify-between gap-3">
          <div className="text-xs text-muted">
            <span className="text-ink">Осталось: {remaining}</span> · {participants}
          </div>
          <Link href="/blitz" className={`rounded-xl px-4 py-2 text-xs font-extrabold text-void transition ${isBlitz ? "bg-blitz hover:shadow-glow" : "bg-amber hover:shadow-[0_0_24px_rgba(255,184,77,0.25)]"}`}>
            Решать задачи →
          </Link>
        </div>
      </div>
    </article>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return <div><div className="font-mono text-lg font-extrabold text-ink">{value}</div><div className="mt-1 text-xs text-muted">{label}</div></div>;
}

function PeriodButton({ active, onClick, children }: { active: boolean; onClick: () => void; children: React.ReactNode }) {
  return <button onClick={onClick} className={`rounded-lg px-4 py-1.5 text-xs font-bold transition ${active ? "bg-blitz text-void" : "text-muted hover:text-ink"}`}>{children}</button>;
}

function ScoreRule({ color, label, points }: { color: string; label: string; points: string }) {
  return <div className="flex items-center justify-between text-sm"><span className="flex items-center gap-2 text-muted"><i className={`h-2 w-2 rounded-full ${color}`} />{label}</span><span className="font-mono font-bold text-ink">{points}</span></div>;
}
