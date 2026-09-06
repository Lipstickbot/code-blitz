# BlitzCode — монорепозиторий MVP

Платформа спортивного программирования с игровым Blitz-режимом.

## Структура

```
frontend/   Next.js + TypeScript + Tailwind (тёмный соревновательный UI)
backend/    FastAPI + PostgreSQL + JWT + Mock Judge
```

## Быстрый старт

1. **Backend** — см. `backend/README.md` (docker compose up для Postgres,
   pip install, seed.py, uvicorn)
2. **Frontend** — см. `frontend/README.md` (npm install, npm run dev)
3. **CI/CD** — см. `../docs/ci-cd.md` (GitHub Actions, Docker image, deploy secrets)

Frontend работает и без backend (Blitz Game и список задач используют
локальные мок-данные как fallback), но для сохранения прогресса, реального
рейтинга и Mock Judge через API нужен запущенный backend.

## Что реализовано в этом первом коммите

- Полный дизайн-стиль: тёмная соревновательная тема, токены в
  `frontend/tailwind.config.ts`, сигнатурный элемент — таймер `CountdownRing`
- Два фоновых визуала сгенерированы через Higgsfield MCP (см.
  `frontend/README.md` → как сохранить их в `public/images/`)
- Лендинг, список задач, страница задачи с редактором кода (Monaco),
  Blitz Game (выбор длительности → матч → результаты), лидерборд,
  формы входа/регистрации
- FastAPI backend: auth (JWT), CRUD задач + admin, submissions + Mock Judge,
  Blitz Game с серверным контролем времени, лидерборд
- Проверено: `npm run build` собирается чисто, все Python-модули backend
  импортируются без ошибок

## Дальше по плану (см. предыдущие сообщения в чате)

- Подключить формы логина/регистрации к `/api/auth`
- Заменить Mock Judge на Judge0/Piston
- Blitz-лидерборд (агрегация по BlitzSession)
- Alembic-миграции
