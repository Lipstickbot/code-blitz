# BlitzCode backend (FastAPI)

## Запуск

```bash
# 1. Поднять PostgreSQL
docker compose up -d

# 2. Установить зависимости
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 3. Скопировать .env
cp .env.example .env

# 4. Применить миграции базы
alembic upgrade head

# 5. Наполнить базу стартовыми задачами
python seed.py

# 6. Запустить сервер
uvicorn app.main:app --reload --port 8000
```

API будет доступен на http://localhost:8000, документация — на http://localhost:8000/docs.
Быстрый статус API: `GET /api/health`.
Готовность backend к работе: `GET /api/health/ready` проверяет базу и runtime для judge.

Для быстрого локального MVP можно оставить `AUTO_CREATE_TABLES=true`: сервер сам создаст таблицы при старте.
Для более правильного режима поставь `AUTO_CREATE_TABLES=false` и обновляй базу командой `alembic upgrade head`.
Если `ENVIRONMENT=production`, backend проверяет безопасность настроек при старте: `JWT_SECRET` должен быть заменен, а `AUTO_CREATE_TABLES` должен быть выключен.
Production-шаблон лежит в `.env.production.example`, порядок выкладки описан в `../../docs/production-runbook.md`.
Production preflight можно запустить командой `python scripts/preflight_production.py --env-file .env.production`.
Staging-шаблон лежит в `.env.staging.example`, первый тестовый сервер описан в `../../docs/staging-runbook.md`.
Staging readiness можно проверить командой `python scripts/check_staging.py --env-file .env.staging --with-docker`.

## Первый админ

Сначала зарегистрируй обычный аккаунт через сайт или API, потом выдай ему права админа:

```bash
python scripts/make_admin.py --email you@example.com
```

Если не помнишь email/username локальных пользователей:

```bash
python scripts/make_admin.py --list-users
```

Скрипт ставит пользователю `is_admin=true` и `role=admin`, после этого admin endpoints `/api/admin/...` будут доступны по обычному JWT после входа.

Если аккаунта еще нет, можно создать первого админа сразу:

```bash
python scripts/make_admin.py --create --email you@example.com --username code_runner --password CodeRunner123
```

Пароль существующего пользователя можно поменять так:

```bash
python scripts/make_admin.py --email you@example.com --set-password --password NewPassword123
```

Проверить пароль без запуска всего API можно так:

```bash
python scripts/make_admin.py --email you@example.com --check-password --password NewPassword123
```

На Windows, если `venv` не создается из-за пути с кириллицей, можно поставить зависимости в локальную папку проекта:

```powershell
python -m pip install --target .run-deps -r requirements.txt
$env:PYTHONPATH=".run-deps;."
$env:PYTHONNOUSERSITE="1"
python scripts/make_admin.py --create --email you@example.com --username code_runner --password CodeRunner123
```

## Тесты

```bash
python -m unittest discover -s tests
```

Сейчас тестами покрыто ядро judge: accepted-решение, wrong answer, runtime error и случай, когда пользователь не объявил `solve(...)`.
Если `node` не доступен в PATH, укажи полный путь в `.env`: `NODE_BINARY=C:\path\to\node.exe`.

Обычный запуск пропускает database integration tests, чтобы быстрые тесты работали даже без PostgreSQL.
Когда Docker/PostgreSQL запущен, полный тест `/api/submissions` можно проверить так:

```powershell
$env:RUN_DB_INTEGRATION_TESTS="1"
$env:PYTHONPATH=".run-deps;."
$env:PYTHONNOUSERSITE="1"
python -m unittest tests.test_submissions_integration
```

Этот тест создает временную задачу, отправляет код в `/api/submissions`, проверяет `Run` на 5 sample cases, `Submit` на 50 hidden cases и убеждается, что wrong answer не проходит как accepted.

Matchmaking integration tests проверяют очередь игроков, подбор по рейтингу, создание online match и восстановление активного матча:

```powershell
$env:RUN_DB_INTEGRATION_TESTS="1"
$env:PYTHONPATH=".run-deps;."
$env:PYTHONNOUSERSITE="1"
python -m unittest tests.test_matchmaking_integration
```

## Миграции базы

Миграции лежат в `migrations/`. Это история изменений схемы базы:

```bash
# применить все миграции
alembic upgrade head

# откатить последнюю миграцию
alembic downgrade -1

# создать новую миграцию после изменения моделей
alembic revision --autogenerate -m "describe change"
```

Первая миграция `20260825_0001_initial_schema.py` создает текущую схему: users, profile stats, problems, test cases, online matches, submissions, match events, rating events и историю задач.
Вторая миграция `20260828_0002_query_indexes.py` добавляет индексы для частых запросов: matchmaking, leaderboard, submissions, test cases, match events и историю профиля.
Третья миграция `20260828_0003_problem_reviews.py` добавляет историю ревью задач.

## Что уже реализовано (MVP)

- Auth (JWT): `/api/auth/register`, `/api/auth/login`, `/api/auth/me`
- Health checks: `/api/health`, `/api/health/ready`
- Startup config validation для production-режима
- Production env template: `.env.production.example`
- Production preflight script: `scripts/preflight_production.py`
- Auth endpoints защищены rate limit настройками `AUTH_RATE_LIMIT_COUNT` и `AUTH_RATE_LIMIT_WINDOW_SECONDS`
- Rate limits могут работать через Redis: `RATE_LIMITER_BACKEND=auto|memory|redis`, `REDIS_URL=redis://localhost:6379/0`
- Регистрация валидирует email, username и password на backend: username 3-30 символов (`A-Z`, `a-z`, `0-9`, `_`), пароль 8-128 символов с буквами и цифрами
- Профиль: `/api/profile/me`, `/api/profile/{username}`, `/api/profile/me/rating-history`, `/api/profile/me/matches`, `/api/profile/me/problems`
- Задачи: `/api/problems`, `/api/admin/problems` (CRUD, требует `is_admin=true`)
- Active-задачи проходят quality gate: нужен уникальный slug, валидные difficulty/status/лимиты, starter code с `solve(...)`, хотя бы один sample test и хотя бы один hidden test
- Списки задач, профиля и лидерборда используют ограниченные `limit/offset`, чтобы API не отдавал всю базу разом
- Тесты задач для админа: `/api/admin/problems/{id}/tests`
- Ревью задач для админа: `/api/admin/problems/{id}/reviews`
- Отправка решений: `/api/submissions` + JavaScript/Python Judge (`app/services/judge.py`)
- Unit-тесты judge лежат в `tests/test_judge.py`
- Blitz Game: `/api/blitz/start`, `/api/blitz/session/{id}`, `/api/blitz/session/{id}/finish`
  — сервер хранит `started_at` и `duration_minutes`, дедлайн всегда считается на сервере
- Лидерборд: `/api/leaderboard/global`, `/api/leaderboard/blitz`

## Текущая архитектура

Активный frontend сейчас находится в корне репозитория: `index.html`, `app.js`, `styles.css`, `config.js`.
Backend работает по SQLAlchemy-моделям и Alembic-миграциям, а обзорная схема лежит в `../../db/schema.sql`:

- регистрация уже создает `user_stats` с рейтингом 1200;
- лидерборд читает рейтинг из `user_stats`;
- модели добавлены для online matches: `matches`, `match_participants`, `match_tasks`, `matchmaking_queue`, `match_events`;
- добавлены первые online endpoints: `/api/matchmaking/join`, `/api/matchmaking/status`, `/api/matchmaking/cancel`, `/api/matches/active`, `/api/matches/{id}`;
- задачи online match для арены доступны через `/api/matches/{id}/tasks`;
- replay online match доступен через `/api/matches/{id}/replay`: задачи, события и submission-метаданные без исходного кода;
- matchmaking расширяет рейтинг-окно ожидания: `±100`, `±200`, `±350`, `±600`;
- matchmaking endpoints защищены rate limit настройками `MATCHMAKING_RATE_LIMIT_COUNT` и `MATCHMAKING_RATE_LIMIT_WINDOW_SECONDS`;
- task picker выбирает ranked-набор `easy, easy, medium, easy, medium, hard`;
- frontend Start теперь может входить в `/api/matchmaking/join`, ждать `/api/matchmaking/status` и загружать real match tasks;
- matchmaking возвращает уже активный матч пользователя, вместо создания новой очереди поверх текущей игры;
- `/api/submissions` теперь различает `kind=run` и `kind=submit`: run берет sample tests, submit берет hidden tests;
- количество тестов для проверки задается настройками `RUN_TEST_LIMIT=5` и `SUBMIT_TEST_LIMIT=50`;
- frontend Run/Submit для backend-задач отправляет код в `/api/submissions`;
- match submissions валидируются до judge: пользователь должен быть участником матча, а `problem_id` должен совпадать с `match_task_id`;
- submit ограничивает размер кода через `MAX_SUBMISSION_CODE_BYTES`;
- submit/run ограничены rate limit настройками `SUBMISSION_RATE_LIMIT_COUNT` и `SUBMISSION_RATE_LIMIT_WINDOW_SECONDS`;
- rate limiter теперь использует Redis в production и memory fallback в local/dev режиме;
- judge timeout берется из `Problem.time_limit_ms`, но зажимается настройками `MIN_JUDGE_TIMEOUT_SECONDS` и `MAX_JUDGE_TIMEOUT_SECONDS`;
- judge поддерживает `JUDGE_EXECUTOR=local|docker`; production validation требует Docker executor;
- Docker judge запускает Python/JavaScript решения в одноразовых контейнерах без сети, с read-only filesystem и лимитами memory/CPU/pids;
- JavaScript judge берет runtime из `NODE_BINARY`, поэтому Node можно подключить полным путем без изменения кода;
- добавлен реальный JavaScript/Python judge contract в `app/services/judge.py` вместо случайного mock-результата;
- submit сохраняет `submission_case_results`, пишет `match_events` и обновляет `user_problem_history`;
- профильные `xp`, `solved_count`, `streak` обновляются через `app/services/scoring.py`;
- XP и solved_count начисляются только за первое accepted-решение конкретной задачи;
- завершение online match теперь проходит через `app/services/match_lifecycle.py`: победитель выбирается по задачам, затем по скорости;
- при завершении online match сервис `rating.py` пересчитывает Elo-рейтинг и пишет `rating_events`;
- события матча доступны через `/api/matches/{id}/events`;
- live-события матча доступны через WebSocket `/api/matches/{id}/stream?token=...`;
- активный матч после refresh страницы можно восстановить через `GET /api/matches/active`;
- `/api/matches/active`, `/api/matches/{id}` и submit автоматически закрывают матч, если серверный таймер уже вышел;
- frontend подключается к WebSocket match stream и обновляет прогресс по `snapshot`, `task_accepted`, `match_finished`;
- матч можно закрыть серверно через `POST /api/matches/{id}/finish`, а истечение времени тоже завершает матч и считает рейтинг;
- игрок может сдаться через `POST /api/matches/{id}/forfeit`: соперник становится победителем, рейтинг считается, событие уходит в WebSocket;
- добавлены database integration tests для matchmaking: очередь, рейтинг-окно, создание матча и восстановление active match;
- `seed.py` теперь берет 71 задачу из `../../db/seed_problems.json`;
- добавлен Alembic: первая миграция лежит в `migrations/versions/20260825_0001_initial_schema.py`;
- добавлена миграция индексов `migrations/versions/20260828_0002_query_indexes.py`;
- production startup validation не дает запустить API с дефолтным JWT secret или `AUTO_CREATE_TABLES=true`;
- добавлен production runbook `../../docs/production-runbook.md`;
- добавлен production preflight script `scripts/preflight_production.py`;
- admin API теперь умеет управлять тестами задачи отдельно от текста задачи:
  `GET/POST/PUT /api/admin/problems/{id}/tests`,
  `PATCH/DELETE /api/admin/problems/{id}/tests/{test_case_id}`;
- admin API не дает создать или оставить некачественную задачу: проверяются difficulty, status, лимиты, starter code, sample/hidden tests и уникальность slug;
- admin API хранит историю ревью задач: `approved`, `needs_changes`, `comment`;
- добавлены database integration tests для `/api/submissions`: запрос API, реальный judge и сохранение результата в БД;
- добавлен Blitz leaderboard: `/api/leaderboard/blitz?duration_minutes=10`;
- публичный список задач поддерживает `limit`, `offset`, `difficulty`, `tag`, `status`;
- профильные списки и leaderboard ограничивают `limit` диапазоном `1..100`;
- старые `BlitzSession` endpoints пока оставлены как совместимость для solo-blitz.

## Pagination и лимиты

Списки в API должны возвращать страницу данных, а не всю таблицу:

- `/api/problems?limit=50&offset=0` — первая страница задач;
- `/api/problems?difficulty=easy&tag=array&limit=20&offset=20` — следующая страница после фильтра;
- `/api/profile/me/matches?limit=20` — последние матчи профиля;
- `/api/leaderboard/global?limit=50` — топ игроков.

Backend ограничивает `limit` максимумом 100. Это защищает базу от тяжелых запросов и делает frontend быстрее, когда библиотека задач и история матчей вырастут.

## Как устроены тесты задачи

- `is_sample=true` — тест можно показывать игроку в интерфейсе.
- `is_hidden=true` — тест используется при `submit`, но не должен раскрываться игроку.
- `Run` проверяет sample tests, максимум `RUN_TEST_LIMIT` кейсов. По умолчанию это 5.
- `Submit` проверяет hidden tests, максимум `SUBMIT_TEST_LIMIT` кейсов. По умолчанию это 50.

Так игрок может понять формат задачи, но не может просто подогнать решение под все скрытые ответы.

## Контракт Judge

Сейчас backend реально проверяет `javascript`, `typescript` в TS-light режиме и `python`.

В обоих языках решение должно объявить функцию `solve(...)`:

```js
function solve(nums, target) {
  return [0, 1];
}
```

```py
def solve(nums, target):
    return [0, 1]
```

Аргументы берутся из `test_cases.input_json`, ожидаемый ответ — из `test_cases.expected_json`.

## Статистика профиля

`app/services/scoring.py` отвечает за попытки и прогресс задач:

- каждый `submit` пишет запись в `user_problem_history`;
- failed submit увеличивает `failed_count`;
- accepted submit увеличивает `solved_count` истории;
- профильный `xp` и общий `solved_count` начисляются только при первом accepted по задаче;
- ranked rating меняется отдельно, только через завершение online match.

## Rate limit

`app/services/rate_limiter.py` поддерживает Redis sliding window и local memory fallback.
В dev режиме можно оставить `RATE_LIMITER_BACKEND=auto`: backend попробует Redis и, если он недоступен, продолжит работать через память процесса.
В production нужно ставить `RATE_LIMITER_BACKEND=redis`, чтобы лимит одинаково работал на нескольких backend-инстансах.
Готовность rate limiter видна в `/api/health/ready`.

## Что оставлено на следующий этап

- Изоляция Judge через Docker/Judge0/Piston перед production-запуском
- Переключить production на `AUTO_CREATE_TABLES=false`, чтобы таблицы обновлялись только миграциями
- Первого админа можно назначить командой `python scripts/make_admin.py --email you@example.com`.
