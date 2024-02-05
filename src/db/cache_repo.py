"""Cache repository"""
import pickle
from typing import Sequence
from uuid import UUID

from fastapi import Depends
from redis.asyncio.client import Redis
from sqlalchemy import Row, RowMapping

from db.database import get_redis_session


class CacheRepository:
    """Create abstract cache repo"""

    def __init__(
            self,
            redis_session: Redis = Depends(get_redis_session),
    ) -> None:
        self.redis_session = redis_session

    async def get(
            self,
            key: str
    ) -> Sequence[Row] | RowMapping | None:
        """Get value from redis"""
        cache_value = await self.redis_session.get(name=key)
        if not cache_value:
            return None
        return pickle.loads(cache_value)

    async def set(
            self,
            key: str,
            value: Sequence[Row]
    ) -> None:
        """Set value from redis"""
        await self.redis_session.set(
            name=key,
            value=pickle.dumps(value)
        )

    async def delete(
            self,
            *key: str
    ) -> None:
        """Delete value from redis"""
        await self.redis_session.delete(*key)


class CacheMenuAppKeys:
    """Class for cache named keys for menu app"""

    def __init__(self):
        self.__list_menus_key = 'list_menus'
        self.__list_submenus_key = 'list_submenus'
        self.__list_dishes_key = 'list_dishes'

        self.__menu_key = 'menu'
        self.__submenu_key = 'submenu'
        self.__dish_key = 'dish'

    @property
    def get_list_menus_key(self) -> str:
        """get cache name key for list menus"""
        return self.__list_menus_key

    @property
    def get_list_submenus_key(self) -> str:
        """get cache name key for list submenus"""
        return self.__list_submenus_key

    @property
    def get_list_dishes_key(self) -> str:
        """get cache name key for list dishes"""
        return self.__list_dishes_key

    @property
    def get_menu_key(self) -> str:
        """get cache name key for list menus"""
        return self.__menu_key

    @property
    def get_submenu_key(self) -> str:
        """get cache name key for list submenus"""
        return self.__submenu_key

    @property
    def get_dish_key(self) -> str:
        """get cache name key for list dishes"""
        return self.__dish_key

    @staticmethod
    def generate_key(key: str, identifier: UUID) -> str:
        """Generate key for redis key cache"""
        return f'{key}_{identifier}'
