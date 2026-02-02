# from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import exception_handler
from rest_framework.exceptions import Throttled
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(ex: Throttled, context: dict) -> Response:
    logger.info("creating custom exception handler")
    response = exception_handler(ex, context)
    logger.info(f"{response=}")

    if isinstance(ex, Throttled):
        return Response(
            data={
                'success': False,
                'error': "Too many requests.",
                "message": "Rate limit exceeded. Please try again later.",
                "retry after": ex.wait
            },
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
    return response
