"""Create update and change db use excel document"""
import pickle
from typing import Sequence

from redis.asyncio.client import Redis
from sqlalchemy import RowMapping, String, cast, delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from db.cache_repo import CacheMenuAppKeys
from db.database import get_async_session, get_redis_session
from menu_app.models import Dish, Menu, Submenu


class ExcelRedisKeys(CacheMenuAppKeys):
    """Class for store excel redis keys """
    @staticmethod
    def get_excel_menu_key() -> str:
        """return excel menu redis key"""
        return 'excel_menu_key'

    @staticmethod
    def get_excel_submenu_key() -> str:
        """return excel submenu redis key"""
        return 'excel_submenu_key'

    @staticmethod
    def get_excel_dish_key() -> str:
        """return excel dish redis key"""
        return 'excel_dish_key'

    @staticmethod
    async def delete_by_pattern(redis_session: Redis, key: str) -> None:
        """return excel dish redis key"""
        [await redis_session.delete(key) for key in await redis_session.keys(f'{key}*')]


class DBSelector(ExcelRedisKeys):
    """Class for select menu objects instance and redis instance"""

    def __init__(
            self,
            session: AsyncSession,
            redis_session: Redis,
    ) -> None:
        self.session = session
        self.redis_session = redis_session
        super().__init__()

    async def get_menu_objects(
            self
    ) -> tuple[Sequence[RowMapping], Sequence[RowMapping], Sequence[RowMapping]]:
        """Get current menus, submenus, dishes from db"""
        menus = (await self.session.execute(
            select(cast(Menu.id, String), Menu.title, Menu.description)
            .order_by(Menu.id))).mappings().all()
        submenus = (await self.session.execute(
            select(cast(Submenu.id, String), Submenu.title, Submenu.description, cast(Submenu.menu_id, String))
            .order_by(Submenu.id))).mappings().all()
        dishes = (await self.session.execute(
            select(cast(Dish.id, String), Dish.title, Dish.description, Dish.price, cast(Dish.submenu_id, String))
            .order_by(Dish.id))).mappings().all()
        return menus, submenus, dishes

    async def get_saved_menu_excel_objects(
            self
    ) -> tuple[list[dict], list[dict], list[dict]] | tuple[list, list, list]:
        """Get current excel menus, excel submenus, excel dishes from redis"""
        bytes_menu_array = await self.redis_session.get(name=self.get_excel_menu_key())
        bytes_submenu_array = await self.redis_session.get(self.get_excel_submenu_key())
        bytes_dish_array = await self.redis_session.get(self.get_excel_dish_key())
        if bytes_menu_array is None or bytes_submenu_array is None or bytes_dish_array is None:
            return [], [], []
        return pickle.loads(bytes_menu_array), pickle.loads(bytes_submenu_array), pickle.loads(bytes_dish_array)


class DBCreator(ExcelRedisKeys):
    """Class for fill tables in db"""

    def __init__(
            self,
            session: AsyncSession,
            redis_session: Redis,
            excel_menu: list[dict],
            excel_submenu: list[dict],
            excel_dish: list[dict]
    ) -> None:
        self.session = session
        self.redis_session = redis_session

        self.excel_menu = excel_menu
        self.excel_submenu = excel_submenu
        self.excel_dish = excel_dish
        super().__init__()

    async def check_db_state(self) -> bool:
        """Check if db empty insert data from Excel and clean db if Excel empty"""
        if not (await self.session.execute(select(Menu))).scalars().all():
            return False
        if not (self.excel_menu and self.excel_submenu and self.excel_dish):
            await self.session.execute(delete(Menu))
            await self.session.execute(delete(Submenu))
            await self.session.execute(delete(Dish))
            await self.session.commit()

            await self.redis_session.delete(self.get_excel_menu_key())
            await self.redis_session.delete(self.get_excel_submenu_key())
            await self.redis_session.delete(self.get_excel_dish_key())
            return False
        return True

    async def create_menu(self) -> None:
        """create menu from list excel menu"""
        for excel_menu in self.excel_menu:
            stmt = insert(Menu).values(
                id=excel_menu.get('id'),
                title=excel_menu.get('title'),
                description=excel_menu.get('description'),
            )
            await self.session.execute(stmt)
        await self.session.commit()

    async def create_submenu(self) -> None:
        """create submenu from list excel submenu"""
        for excel_submenu in self.excel_submenu:
            stmt = insert(Submenu).values(
                id=excel_submenu.get('id'),
                title=excel_submenu.get('title'),
                description=excel_submenu.get('description'),
                menu_id=excel_submenu.get('menu_id')
            )
            await self.session.execute(stmt)
        await self.session.commit()

    async def create_dish(self) -> None:
        """create dish from list excel dish"""
        for excel_dish in self.excel_dish:
            stmt = insert(Dish).values(
                id=excel_dish.get('id'),
                title=excel_dish.get('title'),
                description=excel_dish.get('description'),
                price=excel_dish.get('price'),
                submenu_id=excel_dish.get('submenu_id'),
            ).returning(Dish)
            await self.session.execute(stmt)
        await self.session.commit()

    async def update_redis_excel_data(self) -> bool:
        """Update redis excel keys"""
        menu_bytes = await self.redis_session.get(self.get_excel_menu_key())
        submenu_bytes = await self.redis_session.get(self.get_excel_submenu_key())
        dish_bytes = await self.redis_session.get(self.get_excel_dish_key())
        if menu_bytes is not None and submenu_bytes is not None and dish_bytes is not None:
            menu = pickle.loads(menu_bytes)
            submenu = pickle.loads(submenu_bytes)
            dish = pickle.loads(dish_bytes)
            if len(menu) != len(self.excel_menu) or \
                    len(menu) != len(self.excel_menu) or \
                    len(menu) != len(self.excel_menu):
                return False
            for (index, obj) in enumerate(menu):
                obj['title'] = self.excel_menu[index].get('title')
                obj['description'] = self.excel_menu[index].get('description')
            for (index, obj) in enumerate(submenu):
                obj['title'] = self.excel_submenu[index].get('title')
                obj['description'] = self.excel_submenu[index].get('description')
            for (index, obj) in enumerate(dish):
                obj['title'] = self.excel_dish[index].get('title')
                obj['description'] = self.excel_dish[index].get('description')
                obj['price'] = self.excel_dish[index].get('price')

            await self.redis_session.set(self.get_excel_menu_key(), pickle.dumps(menu))
            await self.redis_session.set(self.get_excel_submenu_key(), pickle.dumps(submenu))
            await self.redis_session.set(self.get_excel_dish_key(), pickle.dumps(dish))
        return True

    async def create_data_in_db(self) -> bool:
        """create menu, submenu, dish instance and create records with them in redis"""
        await self.update_redis_excel_data()
        if await self.check_db_state():
            return False
        await self.create_menu()
        await self.create_submenu()
        await self.create_dish()

        await self.redis_session.set(self.get_excel_menu_key(), pickle.dumps(self.excel_menu))
        await self.redis_session.set(self.get_excel_submenu_key(), pickle.dumps(self.excel_submenu))
        await self.redis_session.set(self.get_excel_dish_key(), pickle.dumps(self.excel_dish))
        return True


class DBChanger(ExcelRedisKeys):
    """Class DB changer"""

    def __init__(
            self,
            session: AsyncSession,
            redis_session: Redis,
            menus: Sequence[RowMapping],
            submenus: Sequence[RowMapping],
            dishes: Sequence[RowMapping],
            excel_saved_menus: list[dict],
            excel_saved_submenus: list[dict],
            excel_saved_dishes: list[dict],
    ) -> None:
        self.session = session
        self.redis_session = redis_session
        self.db_menus = menus
        self.db_submenus = submenus
        self.db_dishes = dishes
        self.excel_menus = excel_saved_menus
        self.excel_submenus = excel_saved_submenus
        self.excel_dishes = excel_saved_dishes
        super().__init__()

    async def change_menu(self) -> None:
        """Change menu model"""
        if len(self.db_menus) > len(self.excel_menus):
            for db_menu_model in self.db_menus:
                if db_menu_model not in self.excel_menus:
                    await self.session.execute(delete(Menu).where(Menu.id == db_menu_model.get('id')))
                    await self.delete_by_pattern(self.redis_session, self.get_list_common_key)

        elif len(self.db_menus) < len(self.excel_menus):
            for excel_menu in self.excel_menus:
                if excel_menu not in self.db_menus:
                    await self.session.execute(insert(Menu).values(**excel_menu))
            await self.session.commit()
            await self.delete_by_pattern(self.redis_session, self.get_list_common_key)

    async def change_submenu(self) -> None:
        """Change submenu model"""
        if len(self.db_submenus) > len(self.excel_submenus):
            for db_submenu_model in self.db_submenus:
                if db_submenu_model not in self.excel_submenus:
                    await self.session.execute(delete(Submenu).where(Submenu.id == db_submenu_model.get('id')))
                    await self.delete_by_pattern(self.redis_session, self.get_list_common_key)
        elif len(self.db_submenus) < len(self.excel_submenus):
            for excel_submenu in self.excel_submenus:
                if excel_submenu not in self.db_submenus:
                    await self.session.execute(insert(Submenu).values(**excel_submenu))

            await self.delete_by_pattern(self.redis_session, self.get_list_common_key)
            await self.session.commit()

    async def change_dish(self) -> None:
        """Change dish model"""
        if len(self.db_dishes) > len(self.excel_dishes):
            for db_dish_model in self.db_dishes:
                if db_dish_model not in self.excel_dishes:
                    await self.session.execute(delete(Dish).where(Dish.id == db_dish_model.get('id')))
                    await self.delete_by_pattern(self.redis_session, self.get_list_dishes_key)
                    await self.delete_by_pattern(self.redis_session, self.get_list_menus_nested_key)
        elif len(self.db_dishes) < len(self.excel_dishes):
            for excel_dish in self.excel_dishes:
                if excel_dish not in self.db_dishes:
                    await self.session.execute(insert(Dish).values(**excel_dish))
            await self.session.commit()
            await self.delete_by_pattern(self.redis_session, self.get_list_dishes_key)
            await self.delete_by_pattern(self.redis_session, self.get_list_menus_nested_key)

    async def check_db_change(self) -> None:
        """Check db check_db_change"""
        await self.change_menu()
        await self.change_submenu()
        await self.change_dish()


class DBUpdater(ExcelRedisKeys):
    """Class DB updated"""

    def __init__(
            self,
            session: AsyncSession,
            redis_session: Redis,
            menus: Sequence[RowMapping],
            submenus: Sequence[RowMapping],
            dishes: Sequence[RowMapping],
            excel_menus: list[dict],
            excel_submenus: list[dict],
            excel_dishes: list[dict],
    ) -> None:
        self.session = session
        self.redis_session = redis_session
        self.db_menus = menus
        self.db_submenus = submenus
        self.db_dishes = dishes
        self.excel_menus = excel_menus
        self.excel_submenus = excel_submenus
        self.excel_dishes = excel_dishes
        super().__init__()

    async def sorted_dict_by_id(self, sequence: list[dict]):
        if not sequence:
            return []
        return sorted(sequence, key=lambda obj: obj.get('id'))

    async def check_menu_update(self) -> bool:
        """Check menu models and update it from excel menus"""
        if len(self.db_menus) != len(self.excel_menus) or not self.excel_menus:
            return False
        sorted_menu = await self.sorted_dict_by_id(self.excel_menus)
        for menu_obj, excel_menu in zip(self.db_menus, sorted_menu):
            if (menu_obj.get('title') != excel_menu.get('title')) or \
                    (menu_obj.get('description') != excel_menu.get('description')):
                await self.session.execute(update(Menu).where(Menu.id == excel_menu.get('id'))
                                           .values(
                    title=excel_menu.get('title'),
                    description=excel_menu.get('description')
                ))
                await self.delete_by_pattern(self.redis_session, self.get_menu_key)
                await self.delete_by_pattern(self.redis_session, self.get_list_menus_key)
                await self.delete_by_pattern(self.redis_session, self.get_list_menus_nested_key)
        await self.session.commit()
        return True

    async def check_submenu_update(self) -> bool:
        """Check submenu models and update it from excel submenus"""
        if len(self.db_submenus) != len(self.excel_submenus):
            return False
        sorted_submenu = await self.sorted_dict_by_id(self.excel_submenus)
        for submenu_obj, excel_submenu in zip(self.db_submenus, sorted_submenu):
            if submenu_obj.get('title') != excel_submenu.get('title') or \
                    submenu_obj.get('description') != excel_submenu.get('description'):
                await self.session.execute(update(Submenu).where(Submenu.id == excel_submenu.get('id'))
                                           .values(
                    title=excel_submenu.get('title'),
                    description=excel_submenu.get('description')
                ))
                await self.delete_by_pattern(self.redis_session, self.get_menu_key)
                await self.delete_by_pattern(self.redis_session, self.get_submenu_key)
                await self.delete_by_pattern(self.redis_session, self.get_list_submenus_key)
                await self.delete_by_pattern(self.redis_session, self.get_list_menus_nested_key)
        await self.session.commit()
        return True

    async def check_dish_update(self) -> bool:
        """Check dish models and update it from Excel dishes"""
        if len(self.db_dishes) != len(self.excel_dishes):
            return False
        sorted_dish = await self.sorted_dict_by_id(self.excel_dishes)
        for dish_obj, excel_dish in zip(self.db_dishes, sorted_dish):
            if dish_obj.get('title') != excel_dish.get('title') or \
                    dish_obj.get('description') != excel_dish.get('description') or \
                    dish_obj.get('price') != excel_dish.get('price'):

                await self.session.execute(update(Dish).where(Dish.id == excel_dish.get('id'))
                                           .values(
                    title=excel_dish.get('title'),
                    description=excel_dish.get('description'),
                    price=excel_dish.get('price')
                ))
                await self.delete_by_pattern(self.redis_session, self.get_menu_key)
                await self.delete_by_pattern(self.redis_session, self.get_submenu_key)
                await self.delete_by_pattern(self.redis_session, self.get_dish_key)
                await self.delete_by_pattern(self.redis_session, self.get_list_dishes_key)
                await self.delete_by_pattern(self.redis_session, self.get_list_menus_nested_key)
        await self.session.commit()
        return True

    async def check_db_update(self) -> None:
        """Check menu objects for invalid data and update"""
        await self.check_menu_update()
        await self.check_submenu_update()
        await self.check_dish_update()


async def run_update_base(excel_menu, excel_submenu, excel_dish) -> None:
    """Run creator changer and updater for db from Excel"""
    gen_async_session = get_async_session()
    session = await gen_async_session.__anext__()

    gen_redis_session = get_redis_session()
    redis_session = await gen_redis_session.__anext__()

    creator = DBCreator(session, redis_session, excel_menu, excel_submenu, excel_dish)
    await creator.create_data_in_db()

    selector = DBSelector(session, redis_session)
    db_menu, db_submenu, db_dish = await selector.get_menu_objects()
    excel_saved_menus, excel_saved_submenus, excel_saved_dishes = await selector.get_saved_menu_excel_objects()
    changer = DBChanger(
        session, redis_session, db_menu, db_submenu, db_dish,
        excel_saved_menus, excel_saved_submenus, excel_saved_dishes
    )
    updater = DBUpdater(
        session, redis_session, db_menu, db_submenu, db_dish,
        excel_saved_menus, excel_saved_submenus, excel_saved_dishes
    )

    await changer.check_db_change()
    await updater.check_db_update()
