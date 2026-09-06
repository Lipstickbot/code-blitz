# BlitzCode frontend (Next.js + TypeScript + Tailwind)

## Запуск

```bash
npm install
cp .env.local.example .env.local
npm run dev
```

Открыть http://localhost:3000. Blitz Game работает даже без запущенного
backend (использует локальный мок-пул задач как fallback), но для реальной
проверки решений и персистентного рейтинга нужен FastAPI backend (см.
`../backend/README.md`).

## Визуалы (Higgsfield MCP)

В этом чате были сгенерированы два фоновых изображения через Higgsfield MCP:
- **hero background** — фон hero-секции лендинга
- **blitz banner** — промо-баннер режима Blitz Game

Сохраните их (кнопка скачивания в виджете генерации выше в чате) как:
```
public/images/hero-bg.jpg
public/images/blitz-banner.jpg
```
Без них страницы всё равно рендерятся корректно — просто без фонового изображения
(тёмный фон + сетка остаются).

## Структура

```
app/
  page.tsx              — лендинг (hero + фичи + промо-баннер)
  problems/              — список задач и страница задачи с редактором
  blitz/                 — Blitz Game (выбор длительности → матч → результаты)
  leaderboard/           — общий и Blitz-лидерборд
  login/, register/      — формы аутентификации (UI, ещё не подключены к API)
components/
  Navbar.tsx
  CountdownRing.tsx      — сигнатурный элемент дизайна (таймер)
  ProblemWorkspace.tsx   — редактор кода + отправка решения
  Badge.tsx
lib/
  api.ts                 — единый клиент к FastAPI backend
  mockData.ts            — мок-данные для демонстрации без backend
```
