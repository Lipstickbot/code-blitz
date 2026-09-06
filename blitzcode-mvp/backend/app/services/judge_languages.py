from __future__ import annotations


JUDGE_LANGUAGES = [
    {
        "id": "javascript",
        "label": "JavaScript",
        "status": "executable",
        "runtime": "node",
        "notes": "Dynamic solve(...) runner with JSON test arguments.",
    },
    {
        "id": "typescript",
        "label": "TypeScript",
        "status": "executable",
        "runtime": "node",
        "notes": "TS-light mode strips simple type annotations before running solve(...).",
    },
    {
        "id": "python",
        "label": "Python",
        "status": "executable",
        "runtime": "python",
        "notes": "Dynamic solve(...) runner with JSON test arguments.",
    },
    {
        "id": "cpp",
        "label": "C++",
        "status": "planned",
        "runtime": "gcc",
        "notes": "Needs a typed adapter contract before safe judging.",
    },
    {
        "id": "java",
        "label": "Java",
        "status": "planned",
        "runtime": "jdk",
        "notes": "Needs a typed adapter contract before safe judging.",
    },
    {
        "id": "go",
        "label": "Go",
        "status": "planned",
        "runtime": "go",
        "notes": "Needs a typed adapter contract before safe judging.",
    },
    {
        "id": "rust",
        "label": "Rust",
        "status": "planned",
        "runtime": "rust",
        "notes": "Needs a typed adapter contract before safe judging.",
    },
]


def executable_language_ids() -> set[str]:
    return {language["id"] for language in JUDGE_LANGUAGES if language["status"] == "executable"}
