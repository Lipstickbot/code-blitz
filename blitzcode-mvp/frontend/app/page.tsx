import Link from "next/link";

const stats = [
  ["2 игрока", "онлайн-дуэль"],
  ["5–30 мин", "выбор времени"],
  ["лобби", "свои правила"],
];

const workflow = [
  {
    title: "Выбери формат",
    body: "Быстрый матч для мгновенной игры или своё лобби, где ты сам задаёшь время и набор задач.",
  },
  {
    title: "Играй против человека",
    body: "В матче сверху виден таймер, твой прогресс и прогресс соперника. Побеждает тот, кто решил больше за время.",
  },
  {
    title: "Заходи в контесты",
    body: "Недельные и месячные соревнования дают понятную цель, очки сезона и повод возвращаться каждый день.",
  },
];

const platformDetails = [
  {
    title: "Онлайн-арена",
    body: "Главный режим платформы. Игрок выбирает время, заходит в матч и соревнуется с другим участником в реальном интерфейсе с таймером.",
    points: ["быстрый матч", "виден прогресс соперника", "победа по решённым задачам"],
  },
  {
    title: "Лобби",
    body: "Если не хочется случайный матч, можно создать своё лобби: выбрать длительность, собрать набор задач и отправить ссылку сопернику.",
    points: ["своё название", "5–30 минут", "выбор задач вручную"],
  },
  {
    title: "Контесты",
    body: "Отдельное место для недельных и месячных соревнований. Там можно видеть очки сезона, активные турниры и таблицы участников.",
    points: ["недельные турниры", "месячные сезоны", "очки за решения"],
  },
];

const matchRules = [
  ["Кто побеждает", "Тот, кто решил больше задач за выбранное время."],
  ["Если время вышло", "Оба игрока могут согласиться добавить ещё 30 секунд."],
  ["Если один против", "Матч завершается, и результат фиксируется сразу."],
  ["Если ничья", "Показывается равный результат по количеству решений."],
];

const afterRegister = [
  "откроется онлайн-арена",
  "можно создать своё лобби",
  "можно выбрать время матча",
  "можно участвовать в контестах",
];

export default function HomePage() {
  return (
    <div className="home-hero relative overflow-hidden">
      <div className="hero-aurora" aria-hidden="true" />
      <div className="hero-grid" aria-hidden="true" />
      <div className="hero-scanline" aria-hidden="true" />

      <section className="mx-auto grid min-h-[calc(100vh-64px)] max-w-7xl items-center gap-12 px-5 py-16 lg:grid-cols-[1.02fr_0.98fr]">
        <div className="animate-reveal">
          <span className="pulse-badge inline-flex rounded-full border border-blitz/25 bg-blitz/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-blitz">
            Онлайн-арена для кодинга
          </span>
          <h1 className="mt-6 max-w-3xl text-4xl font-extrabold leading-tight tracking-tight text-ink md:text-6xl">
            Входи в матч, выбирай время и{" "}
            <span className="animated-gradient-text">побеждай кодом.</span>
          </h1>
          <p className="mt-5 max-w-2xl text-lg leading-8 text-muted">
            BlitzCode — это платформа для быстрых онлайн-соревнований:
            создавай лобби, выбирай набор задач, играй против соперника и
            участвуй в сезонных контестах.
          </p>

          <div className="mt-8 flex flex-wrap items-center gap-3">
            <Link
              href="/register"
              className="magnetic-button rounded-xl bg-blitz px-6 py-3 text-sm font-bold text-void transition hover:shadow-glow"
            >
              Начать играть онлайн
            </Link>
            <span className="rounded-xl border border-line bg-surface/70 px-4 py-3 text-xs font-semibold text-muted">
              регистрация откроет арену
            </span>
          </div>

          <div className="mt-10 grid max-w-2xl gap-3 sm:grid-cols-3">
            {stats.map(([value, label], index) => (
              <div
                key={value}
                className="stat-card rounded-2xl border border-line bg-surface/70 p-4"
                style={{ animationDelay: `${160 + index * 90}ms` }}
              >
                <div className="font-mono text-xl font-extrabold text-ink">{value}</div>
                <div className="mt-1 text-xs leading-5 text-muted">{label}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="workspace-preview arena-preview animate-float rounded-3xl border border-line bg-surface/90 p-3 shadow-2xl shadow-black/30">
          <div className="relative overflow-hidden rounded-2xl border border-line bg-void">
            <div className="preview-sheen" aria-hidden="true" />
            <div className="flex items-center justify-between border-b border-line px-4 py-3">
              <div>
                <div className="text-xs font-semibold text-muted">Онлайн-лобби</div>
                <div className="mt-1 text-sm font-bold text-ink">Blitz Duel · 10 минут</div>
              </div>
              <div className="accepted-pill rounded-full bg-blitz/10 px-3 py-1 font-mono text-xs font-bold text-blitz">
                live
              </div>
            </div>
            <div className="min-h-[460px] p-5">
              <div className="grid gap-3 sm:grid-cols-3">
                {["5 мин", "10 мин", "30 мин"].map((time, index) => (
                  <div
                    key={time}
                    className={`rounded-2xl border p-4 text-center ${
                      index === 1
                        ? "border-blitz/50 bg-blitz/10"
                        : "border-line bg-surface"
                    }`}
                  >
                    <div className="font-mono text-xl font-extrabold text-ink">{time}</div>
                    <div className="mt-1 text-[10px] uppercase tracking-widest text-muted">
                      время
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-5 rounded-2xl border border-line bg-surface p-4">
                <div className="mb-4 flex items-center justify-between">
                  <div>
                    <div className="text-xs font-bold uppercase tracking-widest text-muted">
                      игроки
                    </div>
                    <div className="mt-1 text-sm font-bold text-ink">ожидание соперника</div>
                  </div>
                  <div className="flex -space-x-2">
                    <span className="grid h-9 w-9 place-items-center rounded-full border border-blitz/40 bg-blitz/15 font-mono text-xs font-bold text-blitz">
                      Y
                    </span>
                    <span className="grid h-9 w-9 place-items-center rounded-full border border-ember/40 bg-ember/15 font-mono text-xs font-bold text-ember">
                      ?
                    </span>
                  </div>
                </div>

                <div className="space-y-3">
                  {["Two Sum", "Binary Search", "Course Schedule"].map((task, index) => (
                    <div
                      key={task}
                      className="lobby-row flex items-center justify-between rounded-xl border border-line bg-void px-3 py-3"
                      style={{ animationDelay: `${index * 160}ms` }}
                    >
                      <span className="text-sm font-semibold text-ink">{task}</span>
                      <span className="rounded-full bg-elevated px-2 py-1 text-[10px] text-muted">
                        {index === 0 ? "easy" : index === 1 ? "easy" : "medium"}
                      </span>
                    </div>
                  ))}
                </div>

                <div className="mt-5 h-2 overflow-hidden rounded-full bg-void">
                  <div className="matchmaking-bar h-full rounded-full bg-blitz" />
                </div>
                <div className="mt-3 text-center text-xs font-semibold text-muted">
                  подбор соперника и подготовка матча
                </div>
              </div>

              <div className="mt-5 grid grid-cols-2 gap-3">
                <div className="rounded-2xl border border-line bg-surface p-4">
                  <div className="font-mono text-2xl font-extrabold text-blitz">03</div>
                  <div className="mt-1 text-xs text-muted">задачи в лобби</div>
                </div>
                <div className="rounded-2xl border border-line bg-surface p-4">
                  <div className="font-mono text-2xl font-extrabold text-amber">+30</div>
                  <div className="mt-1 text-xs text-muted">сек при согласии</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-5 pb-10">
        <div className="rounded-3xl border border-line bg-surface/80 p-5 md:p-6">
          <div className="grid gap-4 md:grid-cols-4">
            {["создай лобби", "выбери время", "собери задачи", "играй онлайн"].map(
              (step, index) => (
                <div key={step} className="timeline-step rounded-2xl bg-void p-4">
                  <div className="font-mono text-sm font-extrabold text-blitz">
                    0{index + 1}
                  </div>
                  <div className="mt-2 text-sm font-bold text-ink">{step}</div>
                </div>
              )
            )}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-5 pb-20">
        <div className="grid gap-4 md:grid-cols-3">
          {workflow.map((item, index) => (
            <article
              key={item.title}
              className="workflow-card rounded-2xl border border-line bg-surface p-6"
              style={{ animationDelay: `${220 + index * 110}ms` }}
            >
              <div className="mb-5 grid h-10 w-10 place-items-center rounded-xl bg-blitz/10 font-mono font-extrabold text-blitz">
                {index + 1}
              </div>
              <h2 className="text-lg font-bold text-ink">{item.title}</h2>
              <p className="mt-3 text-sm leading-6 text-muted">{item.body}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-5 pb-20">
        <div className="mb-8 max-w-3xl">
          <span className="text-xs font-bold uppercase tracking-[0.18em] text-blitz">
            Что внутри платформы
          </span>
          <h2 className="mt-3 text-3xl font-extrabold tracking-tight text-ink md:text-4xl">
            Всё вокруг онлайн-соревнования, без лишних разделов.
          </h2>
          <p className="mt-4 text-sm leading-6 text-muted">
            Главная идея BlitzCode — быстро зайти, выбрать формат и начать
            соревноваться. Интерфейс не перегружен: онлайн-матчи, лобби и
            контесты находятся рядом и работают как единая система.
          </p>
        </div>

        <div className="grid gap-4 lg:grid-cols-3">
          {platformDetails.map((detail, index) => (
            <article
              key={detail.title}
              className="info-card rounded-3xl border border-line bg-surface p-6"
              style={{ animationDelay: `${index * 120}ms` }}
            >
              <div className="mb-5 flex h-11 w-11 items-center justify-center rounded-2xl bg-blitz/10 font-mono text-sm font-extrabold text-blitz">
                0{index + 1}
              </div>
              <h3 className="text-xl font-extrabold text-ink">{detail.title}</h3>
              <p className="mt-3 text-sm leading-6 text-muted">{detail.body}</p>
              <div className="mt-5 space-y-2">
                {detail.points.map((point) => (
                  <div
                    key={point}
                    className="flex items-center gap-2 rounded-xl bg-void px-3 py-2 text-xs font-semibold text-muted"
                  >
                    <span className="h-1.5 w-1.5 rounded-full bg-blitz" />
                    {point}
                  </div>
                ))}
              </div>
            </article>
          ))}
        </div>
      </section>

      <section className="mx-auto grid max-w-7xl gap-5 px-5 pb-20 lg:grid-cols-[1fr_0.9fr]">
        <div className="rounded-3xl border border-line bg-surface p-6 md:p-8">
          <span className="text-xs font-bold uppercase tracking-[0.18em] text-blitz">
            Правила матча
          </span>
          <h2 className="mt-3 text-3xl font-extrabold text-ink">
            Простые правила, чтобы сразу понимать результат.
          </h2>
          <div className="mt-6 grid gap-3">
            {matchRules.map(([title, body]) => (
              <div
                key={title}
                className="rule-row rounded-2xl border border-line bg-void p-4"
              >
                <div className="font-bold text-ink">{title}</div>
                <div className="mt-1 text-sm leading-6 text-muted">{body}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-3xl border border-blitz/25 bg-blitz/10 p-6 md:p-8">
          <span className="text-xs font-bold uppercase tracking-[0.18em] text-blitz">
            После регистрации
          </span>
          <h2 className="mt-3 text-3xl font-extrabold text-ink">
            Пользователь сразу попадает туда, где можно играть.
          </h2>
          <p className="mt-4 text-sm leading-6 text-muted">
            Регистрация нужна, чтобы открыть закрытые режимы. После неё
            платформа ведёт не в отдельный список задач, а сразу в онлайн-арену.
          </p>
          <div className="mt-6 space-y-3">
            {afterRegister.map((item, index) => (
              <div
                key={item}
                className="flex items-center gap-3 rounded-2xl border border-blitz/20 bg-void/60 px-4 py-3"
              >
                <span className="grid h-7 w-7 place-items-center rounded-full bg-blitz font-mono text-xs font-extrabold text-void">
                  {index + 1}
                </span>
                <span className="text-sm font-semibold text-ink">{item}</span>
              </div>
            ))}
          </div>
          <Link
            href="/register"
            className="magnetic-button mt-7 inline-flex rounded-xl bg-blitz px-5 py-3 text-sm font-extrabold text-void transition hover:shadow-glow"
          >
            Зарегистрироваться
          </Link>
        </div>
      </section>
    </div>
  );
}
