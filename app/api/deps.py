from fastapi import HTTPException
from fastapi.params import Depends
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError
from starlette import status
from starlette.requests import Request

from app.service.user import UserService
from app.uow.uow import UnitOfWork


def get_uow(requset: Request):
    sql_session_factory = requset.app.state.sql_session_factory
    try:
        with UnitOfWork(sql_session_factory=sql_session_factory) as uow:
            yield uow
    except SQLAlchemyError as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=" ".join(e.args)
        )


def get_user_service(
    uow: UnitOfWork = Depends(get_uow),
) -> UserService:
    yield UserService(uow.user_repository)
