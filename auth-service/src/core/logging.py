import json
import logging
from typing import Callable

from fastapi import Request, Response
from fastapi.routing import APIRoute

from core.settings import settings

LOG_FORMAT = (
    "[%(asctime)s] [%(process)d] [%(levelname)s] [%(name)s] %(message)s"  # noqa: E501
)
LOG_DEFAULT_HANDLERS = [
    "console",
]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": LOG_FORMAT},
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s %(message)s",
            "use_colors": None,
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": "%(levelprefix)s %(client_addr)s - '%(request_line)s' %(status_code)s",  # noqa: E501
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "": {
            "handlers": LOG_DEFAULT_HANDLERS,
            "level": "INFO",
        },
        "uvicorn.error": {
            "level": "INFO",
        },
        "uvicorn.access": {
            "handlers": ["access"],
            "level": "INFO",
            "propagate": False,
        },
    },
    "root": {
        "level": settings.log_level,
        "formatter": "verbose",
        "handlers": LOG_DEFAULT_HANDLERS,
    },
}


# По мотивам https://github.com/tiangolo/fastapi/issues/4683
# https://fastapi.tiangolo.com/advanced/custom-request-and-route/
class LoggingRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            msg = f"{request.method} {request.url.path} {request.query_params}"
            request_body = await request.body()
            if request_body:
                msg += f" {json.loads(request_body)}"
            logging.debug(msg)
            return await original_route_handler(request)

        return custom_route_handler
