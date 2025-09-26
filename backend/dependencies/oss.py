from typing import Annotated

from fastapi import Depends

from ..utils.oss import Minio, get_oss

DependOSS = Annotated[Minio, Depends(get_oss)]
