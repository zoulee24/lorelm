from typing import Annotated

from fastapi import Depends

from ..utils.oss import Minio, get_oss
from ..utils.vector import ElasticSearch, get_vdb

DependOSS = Annotated[Minio, Depends(get_oss)]
DependVDB = Annotated[ElasticSearch, Depends(get_vdb)]
