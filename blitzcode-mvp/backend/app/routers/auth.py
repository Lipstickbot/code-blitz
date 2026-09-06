from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import hash_password, verify_password, create_access_token, get_current_user
from app.config import settings
from app.database import get_db
from app.models import User, UserStats
from app.schemas import RegisterRequest, LoginRequest, TokenResponse, UserOut
from app.services.rate_limiter import auth_rate_limiter

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
async def register(request: Request, payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    _check_auth_rate_limit(request, "register")
    existing = await db.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    existing_username = await db.execute(select(User).where(User.username == payload.username))
    if existing_username.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already taken")

    user = User(
        email=payload.email,
        username=payload.username,
        password_hash=hash_password(payload.password),
    )
    user.stats = UserStats(rating=1200)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return TokenResponse(access_token=create_access_token(user.id))


@router.post("/login", response_model=TokenResponse)
async def login(request: Request, payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    _check_auth_rate_limit(request, "login")
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return TokenResponse(access_token=create_access_token(user.id))


@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_user)):
    return current_user


def _check_auth_rate_limit(request: Request, action: str) -> None:
    client_host = request.client.host if request.client else "unknown"
    key = f"auth:{action}:ip:{client_host}"
    result = auth_rate_limiter.check(
        key,
        limit=settings.auth_rate_limit_count,
        window_seconds=settings.auth_rate_limit_window_seconds,
    )
    if not result.allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Too many auth attempts. Try again in {result.retry_after_seconds} seconds.",
            headers={"Retry-After": str(result.retry_after_seconds)},
        )
