import logging.config

from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi import Depends, FastAPI, Request, status
from fastapi.responses import ORJSONResponse
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from httpx import AsyncClient as HttpxAsyncClient
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from redis.asyncio import Redis
from starlette.middleware.sessions import SessionMiddleware

from api.v1 import auth, registration, roles, sessions, social, user, users
from core.logging import LOGGING
from core.settings import settings
from core.tracing import configure_tracer
from db import redis
from utils import http

logging.config.dictConfig(LOGGING)

dependencies = []
if settings.enable_rate_limiter:
    dependencies.append(
        Depends(
            RateLimiter(
                times=settings.rate_limiter_times, seconds=settings.rate_limiter_seconds
            )
        )
    )

app = FastAPI(
    title="auth",
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
    dependencies=dependencies,
)
app.add_middleware(SessionMiddleware, secret_key=settings.session_secret_key)

if settings.enable_tracer:
    configure_tracer()
    FastAPIInstrumentor.instrument_app(app)


@app.on_event("startup")
async def startup():
    redis.redis = Redis.from_url(settings.redis_dsn)
    http.client = HttpxAsyncClient()
    await FastAPILimiter.init(redis.redis)


@app.on_event("shutdown")
async def shutdown():
    await redis.redis.close()
    await http.client.aclose()


@app.middleware("http")
async def before_request(request: Request, call_next):
    request_id = request.headers.get("X-Request-Id")
    if not request_id:
        return ORJSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "X-Request-Id is required"},
        )
    return await call_next(request)


app.include_router(registration.router, prefix="/api/v1", tags=["Регистрация"])
app.include_router(auth.router, prefix="/api/v1", tags=["Авторизация"])
app.include_router(social.router, prefix="/api/v1", tags=["Соцсети"])
app.include_router(user.router, prefix="/api/v1/user", tags=["Профиль пользователя"])
app.include_router(
    sessions.router, prefix="/api/v1/user/sessions", tags=["История входов в аккаунт"]
)
app.include_router(roles.router, prefix="/api/v1/roles", tags=["Управление ролями"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Управление доступами"])


@AuthJWT.load_config
def get_config():
    return settings


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return ORJSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@AuthJWT.token_in_denylist_loader
async def check_if_token_in_denylist(decrypted_token):
    return await redis.redis.get(decrypted_token["jti"])
