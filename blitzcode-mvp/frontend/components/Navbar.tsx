import Link from "next/link";

const navLinks = [
  { href: "/blitz", label: "Онлайн" },
  { href: "/contests", label: "Контесты" },
];

export default function Navbar() {
  return (
    <header className="sticky top-0 z-50 border-b border-line/80 bg-void/92 backdrop-blur-xl">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-5">
        <Link href="/" className="flex items-center gap-2.5">
          <span className="grid h-8 w-8 place-items-center rounded-lg bg-blitz text-lg font-black text-void shadow-glow">
            B
          </span>
          <span className="text-lg font-bold tracking-tight text-ink">
            Blitz<span className="text-blitz">Code</span>
          </span>
        </Link>

        <nav className="hidden items-center gap-1 md:flex">
          {navLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="rounded-lg px-3 py-2 text-sm font-medium text-muted transition hover:bg-elevated hover:text-ink"
            >
              {link.label}
            </Link>
          ))}
        </nav>

        <div className="flex items-center gap-2">
          <Link
            href="/login"
            className="rounded-lg px-3 py-2 text-sm font-semibold text-muted transition hover:bg-elevated hover:text-ink"
          >
            Войти
          </Link>
          <Link
            href="/register"
            className="rounded-lg bg-blitz px-4 py-2 text-sm font-bold text-void transition hover:shadow-glow"
          >
            Начать
          </Link>
        </div>
      </div>
    </header>
  );
}
