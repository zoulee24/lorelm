from typing import Any, Mapping

from fastapi.responses import ORJSONResponse
from starlette.background import BackgroundTask


class SuccessResponse(ORJSONResponse):
    def render(self, content: Any) -> bytes:
        return b'{"code": 0, "data": ' + super().render(content) + b"}"
