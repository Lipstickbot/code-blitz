"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import type { FormEvent } from "react";

export default function RegisterPage() {
  const router = useRouter();

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    document.cookie =
      "blitzcode_auth=1; path=/; max-age=2592000; SameSite=Lax";
    router.push("/blitz");
  }

  return (
    <div className="workspace-shell flex min-h-[calc(100vh-64px)] items-center justify-center px-5 py-12">
      <div className="grid w-full max-w-5xl overflow-hidden rounded-3xl border border-line bg-surface shadow-2xl shadow-black/30 md:grid-cols-[1fr_420px]">
        <section className="hidden border-r border-line bg-void/60 p-10 md:block">
          <span className="rounded-full border border-blitz/25 bg-blitz/10 px-3 py-1 text-xs font-bold uppercase tracking-[0.18em] text-blitz">
            Добро пожаловать
          </span>
          <h1 className="mt-6 text-3xl font-extrabold leading-tight text-ink">
            После регистрации ты сразу попадёшь в онлайн-арену.
          </h1>
          <p className="mt-4 text-sm leading-6 text-muted">
            Там можно выбрать время, создать своё лобби, собрать набор задач и
            начать матч против соперника.
          </p>
          <div className="mt-8 rounded-2xl border border-line bg-surface/70 p-5">
            <div className="flex items-center justify-between">
              <div className="text-xs font-semibold uppercase tracking-widest text-muted">
                Онлайн-арена
              </div>
              <span className="rounded-full bg-blitz/10 px-2 py-1 font-mono text-[10px] font-bold text-blitz">
                live
              </span>
            </div>
            <div className="mt-4 grid grid-cols-3 gap-2">
              {["5 мин", "10 мин", "30 мин"].map((time) => (
                <div key={time} className="rounded-xl border border-line bg-void px-3 py-3 text-center">
                  <div className="font-mono text-sm font-extrabold text-ink">{time}</div>
                  <div className="mt-1 text-[9px] uppercase tracking-widest text-muted">матч</div>
                </div>
              ))}
            </div>
            <div className="mt-4 space-y-2">
              {["Создать лобби", "Выбрать задачи", "Играть онлайн"].map((item, index) => (
                <div key={item} className="flex items-center justify-between rounded-xl border border-line bg-void px-3 py-2">
                  <span className="text-xs font-semibold text-ink">{item}</span>
                  <span className="font-mono text-[10px] text-blitz">0{index + 1}</span>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="p-6 sm:p-10">
          <h2 className="text-2xl font-extrabold text-ink">Создать аккаунт</h2>
          <p className="mt-2 text-sm text-muted">Заполни форму, и мы откроем онлайн-арену BlitzCode.</p>

          <form onSubmit={handleSubmit} className="mt-8 flex flex-col gap-4">
            <Field label="Никнейм" type="text" name="username" />
            <Field label="Email" type="email" name="email" />
            <Field label="Пароль" type="password" name="password" />
            <button
              type="submit"
              className="mt-2 rounded-xl bg-blitz px-4 py-3 text-sm font-bold text-void transition hover:shadow-glow"
            >
              Зарегистрироваться и открыть арену
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-muted">
            Уже есть аккаунт?{" "}
            <Link href="/login" className="font-semibold text-blitz hover:underline">
              Войти
            </Link>
          </p>
        </section>
      </div>
    </div>
  );
}

function Field({
  label,
  type,
  name,
}: {
  label: string;
  type: string;
  name: string;
}) {
  return (
    <label className="flex flex-col gap-1.5">
      <span className="text-xs font-bold uppercase tracking-wide text-muted">
        {label}
      </span>
      <input
        required
        type={type}
        name={name}
        className="rounded-xl border border-line bg-void px-3 py-3 text-ink outline-none transition placeholder:text-muted/60 focus:border-blitz"
      />
    </label>
  );
}
