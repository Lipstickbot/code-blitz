"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import type { FormEvent } from "react";

export default function LoginPage() {
  const router = useRouter();

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    document.cookie =
      "blitzcode_auth=1; path=/; max-age=2592000; SameSite=Lax";
    router.push("/blitz");
  }

  return (
    <div className="workspace-shell flex min-h-[calc(100vh-64px)] items-center justify-center px-5 py-12">
      <div className="w-full max-w-md rounded-3xl border border-line bg-surface p-6 shadow-2xl shadow-black/30 sm:p-8">
        <h1 className="text-2xl font-extrabold text-ink">Вход</h1>
        <p className="mt-2 text-sm text-muted">Войди, чтобы перейти в онлайн-арену, лобби и контесты.</p>

        <form onSubmit={handleSubmit} className="mt-8 flex flex-col gap-4">
          <Field label="Email" type="email" name="email" />
          <Field label="Пароль" type="password" name="password" />
          <button
            type="submit"
            className="mt-2 rounded-xl bg-blitz px-4 py-3 text-sm font-bold text-void transition hover:shadow-glow"
          >
            Войти в онлайн-арену
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-muted">
          Нет аккаунта?{" "}
          <Link href="/register" className="font-semibold text-blitz hover:underline">
            Зарегистрироваться
          </Link>
        </p>
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
        className="rounded-xl border border-line bg-void px-3 py-3 text-ink outline-none transition focus:border-blitz"
      />
    </label>
  );
}
