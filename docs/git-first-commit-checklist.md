# Code Blitz Git First Commit Checklist

## Goal

Prepare the project for GitHub without uploading secrets, dependency folders, logs or local experiments.

## Before First Commit

1. Check ignored files:

```bash
git status --ignored --short
```

2. Check normal files that will be committed:

```bash
git status --short
```

3. Make sure these are not staged:

- `.env`
- `.env.staging`
- `.env.production`
- `node_modules`
- `.next`
- `.run-deps`
- log files
- downloaded `.tgz` archives
- local CSV/model experiment files

## First Commit

```bash
git init
git add .
git status --short
git commit -m "Initial Code Blitz MVP"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/code-blitz.git
git push -u origin main
```

## Normal Feature Flow

```bash
git checkout -b codex/feature-name
git add .
git commit -m "Add feature name"
git push -u origin codex/feature-name
```

Open a Pull Request, wait for checks, then merge to `main`.

## Deploy Flow Later

After staging secrets are configured in GitHub, pushing to `main` can:

1. run tests;
2. build backend image;
3. connect to the server;
4. pull latest code;
5. run migrations;
6. restart the site.
