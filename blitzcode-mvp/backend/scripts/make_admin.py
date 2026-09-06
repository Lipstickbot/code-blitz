import argparse
import asyncio
import socket
import re
import sys
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Promote an existing Code Blitz user to admin.")
    parser.add_argument("--email", help="User email to promote or create.")
    parser.add_argument("--username", help="Username to promote or create.")
    parser.add_argument("--create", action="store_true", help="Create the user as admin if it does not exist.")
    parser.add_argument("--set-password", action="store_true", help="Update password for an existing user.")
    parser.add_argument("--check-password", action="store_true", help="Verify a password for an existing user.")
    parser.add_argument("--password", help="Password for --create.")
    parser.add_argument("--list-users", action="store_true", help="Show recent users and admin status.")
    parser.add_argument("--limit", type=int, default=20, help="How many users to show with --list-users.")
    return parser


def normalize_selector(args: argparse.Namespace) -> tuple[str, str] | None:
    if args.list_users:
        return None
    if args.email:
        return ("email", args.email.strip().lower())
    if args.username:
        return ("username", args.username.strip())
    return None


def validate_password(password: str) -> str | None:
    if len(password) < 8 or len(password) > 128:
        return "Password must be 8-128 characters."
    if not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
        return "Password must contain at least one letter and one digit."
    return None


async def list_users(limit: int) -> int:
    from sqlalchemy import select

    from app.database import AsyncSessionLocal
    from app.models import User

    safe_limit = max(1, min(limit, 100))
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).order_by(User.created_at.desc()).limit(safe_limit))
        users = result.scalars().all()

    if not users:
        print("No users found.")
        return 0

    for user in users:
        role = "admin" if user.is_admin else user.role
        print(f"{user.username}\t{user.email}\t{role}")
    return 0


async def promote_admin(field_name: str, value: str) -> int:
    from sqlalchemy import select

    from app.database import AsyncSessionLocal
    from app.models import User

    async with AsyncSessionLocal() as db:
        field = User.email if field_name == "email" else User.username
        result = await db.execute(select(User).where(field == value))
        user = result.scalar_one_or_none()
        if not user:
            print(f"User not found by {field_name}: {value}", file=sys.stderr)
            return 1

        user.is_admin = True
        user.role = "admin"
        await db.commit()
        print(f"Admin enabled for {user.username} <{user.email}>.")
        return 0


async def set_user_password(field_name: str, value: str, password: str) -> int:
    from sqlalchemy import select

    from app.auth import hash_password
    from app.database import AsyncSessionLocal
    from app.models import User

    async with AsyncSessionLocal() as db:
        field = User.email if field_name == "email" else User.username
        result = await db.execute(select(User).where(field == value))
        user = result.scalar_one_or_none()
        if not user:
            print(f"User not found by {field_name}: {value}", file=sys.stderr)
            return 1

        user.password_hash = hash_password(password)
        await db.commit()
        print(f"Password updated for {user.username} <{user.email}>.")
        return 0


async def check_user_password(field_name: str, value: str, password: str) -> int:
    from sqlalchemy import select

    from app.auth import verify_password
    from app.database import AsyncSessionLocal
    from app.models import User

    async with AsyncSessionLocal() as db:
        field = User.email if field_name == "email" else User.username
        result = await db.execute(select(User).where(field == value))
        user = result.scalar_one_or_none()
        if not user:
            print(f"User not found by {field_name}: {value}", file=sys.stderr)
            return 1

        if not user.password_hash or not verify_password(password, user.password_hash):
            print("Password check failed.", file=sys.stderr)
            return 1
        role = "admin" if user.is_admin else user.role
        print(f"Password check passed for {user.username} <{user.email}> ({role}).")
        return 0


async def create_or_promote_admin(email: str, username: str, password: str) -> int:
    from sqlalchemy import select

    from app.auth import hash_password
    from app.database import AsyncSessionLocal
    from app.models import User, UserStats

    async with AsyncSessionLocal() as db:
        existing_email = await db.execute(select(User).where(User.email == email))
        user = existing_email.scalar_one_or_none()
        if user:
            user.is_admin = True
            user.role = "admin"
            await db.commit()
            print(f"Existing user promoted to admin: {user.username} <{user.email}>.")
            return 0

        existing_username = await db.execute(select(User).where(User.username == username))
        if existing_username.scalar_one_or_none():
            print(f"Username already belongs to another user: {username}", file=sys.stderr)
            return 1

        user = User(
            email=email,
            username=username,
            password_hash=hash_password(password),
            role="admin",
            is_admin=True,
        )
        user.stats = UserStats(rating=1200)
        db.add(user)
        await db.commit()
        print(f"Admin user created: {username} <{email}>.")
        return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.list_users:
            return asyncio.run(list_users(args.limit))

        if args.create:
            email = (args.email or "").strip().lower()
            username = (args.username or "").strip()
            password = args.password or ""
            if not email or not username or not password:
                print("--create requires --email, --username and --password.", file=sys.stderr)
                return 2
            password_error = validate_password(password)
            if password_error:
                print(password_error, file=sys.stderr)
                return 2
            return asyncio.run(create_or_promote_admin(email, username, password))

        selector = normalize_selector(args)
        if selector is None:
            print("Use --email, --username, --create, or --list-users.", file=sys.stderr)
            return 2
        field_name, value = selector
        if not value:
            print(f"{field_name} cannot be empty.", file=sys.stderr)
            return 2
        if args.set_password:
            password = args.password or ""
            password_error = validate_password(password)
            if password_error:
                print(password_error, file=sys.stderr)
                return 2
            return asyncio.run(set_user_password(field_name, value, password))
        if args.check_password:
            password = args.password or ""
            if not password:
                print("--check-password requires --password.", file=sys.stderr)
                return 2
            return asyncio.run(check_user_password(field_name, value, password))
        return asyncio.run(promote_admin(field_name, value))
    except (ConnectionRefusedError, OSError, socket.gaierror) as error:
        print(
            f"Database is not reachable: {error}. "
            "Start PostgreSQL or set DATABASE_URL to the running database.",
            file=sys.stderr,
        )
        return 1
    except (ModuleNotFoundError, ImportError) as error:
        print(
            f"Backend dependencies are not ready: {error}. "
            "Install requirements or run this script from the backend virtualenv.",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
