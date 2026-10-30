from fastapi import HTTPException


def err(code: int, msg) -> HTTPException:
    return HTTPException(status_code=code, detail=msg)
