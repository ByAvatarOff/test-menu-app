"""Create update and change db use excel document"""
import pickle

from redis.asyncio.client import Redis
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_async_session, get_redis_session
from menu_app.models import Dish, Menu, Submenu
from menu_app.utils import ModelToJson


class ExcelRedisKeys:
    """Class for store excel redis keys """
    @staticmethod
    def get_excel_menu_key():
        """return excel menu redis key"""
        return 'excel_menu_key'

    @staticmethod
    def get_excel_submenu_key():
        """return excel submenu redis key"""
        return 'excel_submenu_key'

    @staticmethod
    def get_excel_dish_key():
        """return excel dish redis key"""
        return 'excel_dish_key'


class DBSelector(ExcelRedisKeys):
    """Class for select menu objects instance and redis instance"""

    def __init__(
            self,
            session: AsyncSession,
            redis_session: Redis,
    ) -> None:
        self.session = session
        self.redis_session = redis_session

    async def get_menu_objects(self):
        """Get current menus, submenus, dishes from db"""
        menus = (await self.session.execute(select(Menu).order_by(Menu.id))).scalars().all()
        submenus = (await self.session.execute(select(Submenu).order_by(Submenu.id))).scalars().all()
        dishes = (await self.session.execute(select(Dish).order_by(Dish.id))).scalars().all()
        return menus, submenus, dishes

    async def get_saved_menu_excel_objects(self):
        """Get current excel menus, excel submenus, excel dishes from redis"""
        excel_saved_menus = pickle.loads(await self.redis_session.get(self.get_excel_menu_key()))
        excel_saved_submenus = pickle.loads(await self.redis_session.get(self.get_excel_submenu_key()))
        excel_saved_dishes = pickle.loads(await self.redis_session.get(self.get_excel_dish_key()))
        return excel_saved_menus, excel_saved_submenus, excel_saved_dishes


class DBCreator(ExcelRedisKeys):
    """Class for fill tables in db"""

    def __init__(
            self,
            session: AsyncSession,
            redis_session: Redis,
            db_menu,
            excel_menu: list[dict],
            excel_submenu: list[dict],
            excel_dish: list[dict]
    ) -> None:
        self.session = session
        self.redis_session = redis_session

        self.db_menu = db_menu
        self.excel_menu = excel_menu
        self.excel_submenu = excel_submenu
        self.excel_dish = excel_dish

    async def check_db_state(self):
        """Check if db empty insert data from Excel and clean db if Excel empty"""
        if not self.db_menu:
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

    async def create_menu(self):
        """create menu from list excel menu"""
        for excel_menu in self.excel_menu:
            stmt = insert(Menu).values(
                id=excel_menu.get('id'),
                title=excel_menu.get('title'),
                description=excel_menu.get('description'),
            )
            await self.session.execute(stmt)
        await self.session.commit()

    async def create_submenu(self):
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

    async def create_dish(self):
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

    async def create_data_in_db(self):
        """create menu, submenu, dish instance and create records with them in redis"""
        if await self.check_db_state():
            return False
        await self.create_menu()
        await self.create_submenu()
        await self.create_dish()

        await self.redis_session.set(self.get_excel_menu_key(), pickle.dumps(self.excel_menu))
        await self.redis_session.set(self.get_excel_submenu_key(), pickle.dumps(self.excel_submenu))
        await self.redis_session.set(self.get_excel_dish_key(), pickle.dumps(self.excel_dish))


class DBChanger:
    """Class DB changer"""

    def __init__(
            self,
            session: AsyncSession,
            redis_session: Redis,
            menus,
            submenus,
            dishes,
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

    async def change_menu(self):
        """Change menu model"""
        dict_menu_models = [await ModelToJson.model_object_2_dict(obj) for obj in self.db_menus]
        if len(self.db_menus) > len(self.excel_menus):
            for db_model in dict_menu_models:
                if db_model not in self.excel_menus:
                    await self.session.execute(delete(Menu).where(Menu.id == db_model.get('id')))
        elif len(self.db_menus) < len(self.excel_menus):
            for excel_menu in self.excel_menus:
                if excel_menu not in dict_menu_models:
                    await self.session.execute(insert(Menu).values(**excel_menu))
                    await self.session.commit()

    async def change_submenu(self):
        """Change submenu model"""
        dict_submenu_models = [await ModelToJson.model_object_2_dict(obj) for obj in self.db_submenus]
        if len(self.db_submenus) > len(self.excel_submenus):
            for db_model in dict_submenu_models:
                if db_model not in self.excel_submenus:
                    await self.session.execute(delete(Submenu).where(Submenu.id == db_model.get('id')))
        elif len(self.db_submenus) < len(self.excel_submenus):
            for excel_submenu in self.excel_submenus:
                if excel_submenu not in dict_submenu_models:
                    await self.session.execute(insert(Submenu).values(**excel_submenu))
                    await self.session.commit()

    async def change_dish(self):
        """Change dish model"""
        dict_dish_models = [await ModelToJson.model_object_2_dict(obj) for obj in self.db_dishes]
        if len(self.db_dishes) > len(self.excel_dishes):
            for db_model in dict_dish_models:
                if db_model not in self.excel_dishes:
                    await self.session.execute(delete(Dish).where(Dish.id == db_model.get('id')))
        elif len(self.db_dishes) < len(self.excel_dishes):
            for excel_dish in self.excel_dishes:
                if excel_dish not in dict_dish_models:
                    await self.session.execute(insert(Dish).values(**excel_dish))
                    await self.session.commit()

    async def check_db_change(self):
        """Check db check_db_change"""
        await self.change_menu()
        await self.change_submenu()
        await self.change_dish()


class DBUpdater:
    """Class DB updated"""

    def __init__(
            self,
            session: AsyncSession,
            redis_session: Redis,
            menus,
            submenus,
            dishes,
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

    async def check_menu_update(self):
        """Check menu models and update it from excel menus"""
        if len(self.db_menus) != len(self.excel_menus):
            return False
        for menu, excel_menu in zip(self.db_menus, self.excel_menus):
            if (menu.title != excel_menu.get('title')) or (menu.description != excel_menu.get('description')):
                await self.session.execute(update(Menu).where(Menu.id == menu.id).values(
                    title=excel_menu.get('title'),
                    description=excel_menu.get('description'),
                ))
        await self.session.commit()
        return True

    async def check_submenu_update(self):
        """Check submenu models and update it from excel submenus"""
        if len(self.db_submenus) != len(self.excel_submenus):
            return False
        for submenu, excel_submenu in zip(self.db_submenus, self.excel_submenus):
            if submenu.title != excel_submenu.get('title') or submenu.description != excel_submenu.get('description'):

                await self.session.execute(update(Submenu).where(Submenu.id == submenu.id).values(
                    title=excel_submenu.get('title'),
                    description=excel_submenu.get('description'),
                ))
        await self.session.commit()
        return True

    async def check_dish_update(self):
        """Check dish models and update it from Excel dishes"""
        if len(self.db_dishes) != len(self.excel_dishes):
            return False
        for dish, excel_dish in zip(self.db_dishes, self.excel_dishes):
            if dish.title != excel_dish.get('title') or \
                    dish.description != excel_dish.get('description') or \
                    dish.price != excel_dish.get('price'):

                await self.session.execute(update(Dish).where(Dish.id == dish.id).values(
                    title=excel_dish.get('title'),
                    description=excel_dish.get('description'),
                    price=excel_dish.get('price'),
                ))
                await self.session.commit()
        return True

    async def check_db_update(self):
        """Check menu objects for invalid data and update"""
        await self.check_menu_update()
        await self.check_submenu_update()
        await self.check_dish_update()


async def run_update_base(excel_menu, excel_submenu, excel_dish):
    """Run creator changer and updater for db from Excel"""
    gen_async_session = get_async_session()
    session = await gen_async_session.__anext__()

    gen_redis_session = get_redis_session()
    redis_session = await gen_redis_session.__anext__()

    selector = DBSelector(session, redis_session)
    db_menu, db_submenu, db_dish = await selector.get_menu_objects()

    creator = DBCreator(session, redis_session, db_menu, excel_menu, excel_submenu, excel_dish)
    await creator.create_data_in_db()

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
