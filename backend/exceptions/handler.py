from logging import getLogger
from typing import List, Tuple

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import ORJSONResponse
from sqlalchemy.exc import IntegrityError

from .common import CustomException, ErrorCode

logger = getLogger("lorelm.exception")


async def CustomExcHandle(req: Request, exc: CustomException):
    content = dict(code=exc.code, message=exc.msg, data=None)
    logger.warning(f"{req.url.path} 抛出异常 {exc.code} {exc.msg}")
    return ORJSONResponse(content, status_code=200)


async def IntegrityErrorHandle(req: Request, exc: IntegrityError):
    logger.warning(req.url.path, "外键关系错误")
    msg = exc.detail
    raise CustomException(ErrorCode.Params, msg)


async def RequestValidationHandle(req: Request, exc: RequestValidationError):
    errs_loc = []
    msg = ""
    logger.exception(exc)

    for err in exc.errors():
        err_type = err.get("type")
        if err_type == "json_invalid":
            msg = "请求 body 错误"
            break
        loc = err.get("loc")
        if loc and isinstance(loc, (List, Tuple)):
            if loc[0] == "body":
                errs_loc.append(".".join(map(str, loc)))
            else:
                logger.warning(f"未处理 {err_type} 参数错误: {exc}")
        else:
            logger.warning(f"未处理 {err_type} 参数错误: {exc}")
    if not msg and errs_loc:
        msg = f"请求参数 {' '.join(map(str, errs_loc))}"
    logger.warning(msg)
    raise CustomException(ErrorCode.Params, msg)


async def ResponseValidationHandle(req: Request, exc: ResponseValidationError):
    errs_loc = []
    msg = ""
    # logger.exception(exc)

    for err in exc.errors():
        err_type = err.get("type")
        if err_type == "json_invalid":
            msg = "响应 body 错误"
            break
        loc = err.get("loc")
        if loc and isinstance(loc, (List, Tuple)):
            if loc[0] == "body":
                errs_loc.append(".".join(map(str, loc)))
            else:
                logger.warning(f"未处理 {err_type} 参数错误: {exc}")
        else:
            logger.warning(f"未处理 {err_type} 参数错误: {exc}")
    if not msg and errs_loc:
        msg = f"响应参数 {' '.join(map(str, errs_loc))}"
    logger.warning(msg)
    raise CustomException(ErrorCode.Params, msg)


def register_exceptions(app: FastAPI):
    # app.add_exception_handler(HTTPException, HttpExcHandle)
    app.add_exception_handler(RequestValidationError, RequestValidationHandle)
    app.add_exception_handler(ResponseValidationError, ResponseValidationHandle)
    app.add_exception_handler(CustomException, CustomExcHandle)
    app.add_exception_handler(IntegrityError, IntegrityErrorHandle)
