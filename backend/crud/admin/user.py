from sqlalchemy import and_, func

from ...models import admin as models
from ...schemas import admin as schemas
from ..base import CrudBase


class UserCrud(CrudBase[models.User, schemas.UserResponse]):
    """
    用户管理
    """

    _DBModelType = models.User
    _DBSchemaType = schemas.UserResponse

    async def login(self, username: str, password: str):
        user = await self.get_data(
            wheres=and_(self.model.email == username, self.model.password == password),
            strict=True,
            scalar=True,
        )
        user.login_at = func.current_timestamp()
        return await self.update_data(user)
