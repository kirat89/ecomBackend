
"""
Expection Handler
"""

import asyncio
from typing import Union
from functools import wraps

# from smtplib import SMTPException, SMTPConnectError, SMTPRecipientsRefused
from json import JSONDecodeError
from fastapi import HTTPException

from jwt.exceptions import (
    InvalidTokenError,
    ExpiredSignatureError,
    DecodeError,
    InvalidAlgorithmError,
    PyJWKError,
)
from minio.error import S3Error
from cryptography.fernet import InvalidToken
from pydantic import ValidationError
from utilities.log import logger_function

logger = logger_function()


class ExceptionHandler:
    """Class to check instance of exceptions being raised

    Raises:
        HTTPException: asyncio.TimeoutError
        HTTPException: TypeRrror
        HTTPException: JSONDecodeError
        HTTPException: ClientError
        HTTPException: SMTPRecipientsRefused, SMTPConnectError, SMTPException
        HTTPException: DuplicateLabelError, EmptyDataError
        HTTPException: AttributeError
        HTTPException: ValidationError
        HTTPException: UnicodeDecodeError, ValueError
        HTTPException: DBAPIError, SQLAlchemyError
        HTTPException: JWTError
        HTTPException: InvalidToken

    Returns:
        _type_: _description_
    """

    @staticmethod
    def handle_exception(err: Union[Exception, HTTPException]):
        if isinstance(err, asyncio.TimeoutError):
            raise HTTPException(
                detail="Gateway Timeout Error", status_code=504
            ) from err
        elif isinstance(err, TypeError):
            raise HTTPException(detail=str(err), status_code=500) from err
        elif isinstance(err, JSONDecodeError):
            raise HTTPException(detail=str(err), status_code=422) from err
        # elif isinstance(err, ClientError):
        #     LogHandler.logger.error("Error: %s", str(err))
        #     return None
        # elif isinstance(err, (SMTPRecipientsRefused, SMTPConnectError, SMTPException)):
        #     LogHandler.logger.error("Error: %s", str(err), stack_info=True)
        #     return False
        # elif isinstance(err, (DuplicateLabelError, EmptyDataError)):
        #     raise HTTPException(detail=str(err), status_code=500) from err
        elif isinstance(err, S3Error):
            raise HTTPException(detail=str(err), status_code=400) from err
        elif isinstance(err, AttributeError):
            raise HTTPException(detail=str(err), status_code=404) from err
        elif isinstance(err, ValidationError):
            raise HTTPException(detail=str(err), status_code=500) from err
        elif isinstance(err, (UnicodeDecodeError, ValueError)):
            raise HTTPException(detail=str(err), status_code=400) from err
        # elif isinstance(err, (DBAPIError, SQLAlchemyError)):
        #     raise HTTPException(detail=str(err), status_code=500) from err
        elif isinstance(
            err,
            (
                InvalidAlgorithmError,
                ExpiredSignatureError,
                DecodeError,
                InvalidTokenError,
                PyJWKError,
            ),
        ):
            raise HTTPException(detail=str(err), status_code=400) from err
        elif isinstance(err, InvalidToken):
            logger.error(f"Error decrypting request_id: {err}")
            raise HTTPException(
                detail="Invalid encrypted request_id", status_code=400
            ) from err
        elif isinstance(err, HTTPException):
            logger.error("Error: %s", str(err.detail))
            raise HTTPException(
                detail=str(err.detail), status_code=err.status_code
            ) from err
        else:
            logger.error("Error: %s", str(err), stack_info=True)
            raise HTTPException(
                detail={"Internal server error: %s", str(err)}, status_code=500
            ) from err

    @staticmethod
    async def async_handle_exception(err: Union[Exception, HTTPException]):
        """Handle Exception raised by async function

        Args:
            err (Union[Exception, HTTPException]): _description_
        """
        ExceptionHandler.handle_exception(err)

    @staticmethod
    def sync_handle_exception(err: Union[Exception, HTTPException]):
        """Handle Exception raised by sync function

        Args:
            err (Union[Exception, HTTPException]): _description_
        """
        ExceptionHandler.handle_exception(err)


def async_try_except_decorator(func):
    """async decorator"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as err:
            await ExceptionHandler.async_handle_exception(err)

    return wrapper


def sync_try_except_decorator(func):
    """sync decorator"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as err:
            ExceptionHandler.sync_handle_exception(err)

    return wrapper
