from typing import NoReturn

from fastapi import HTTPException


def not_implemented_501() -> NoReturn:
    raise HTTPException(status_code=501, detail="Not implemented") from None


def bad_gateway_502(detail: str) -> NoReturn:
    raise HTTPException(status_code=502, detail=detail) from None


def gateway_timeout_504() -> NoReturn:
    raise HTTPException(status_code=504, detail="Server timeout") from None


def internal_server_error_500(e: Exception) -> NoReturn:
    raise HTTPException(status_code=500, detail=str(e)) from e


def bad_request_400(detail: str, e: Exception | None = None) -> NoReturn:
    raise HTTPException(status_code=400, detail=detail) from e


def not_found_404(detail: str) -> NoReturn:
    raise HTTPException(status_code=404, detail=detail) from None
