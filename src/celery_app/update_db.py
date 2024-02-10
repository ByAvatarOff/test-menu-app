from sqlalchemy import insert, select, update

from db.database import get_async_session
from menu_app.models import Dish, Menu, Submenu


class DBCreator:

    def __init__(self, session, excel_menu: list, excel_submenu: list, excel_dish: list):
        self.session = session
        self.excel_menu = excel_menu
        self.excel_submenu = excel_submenu
        self.excel_dish = excel_dish

    async def check_db_state(self):
        result = await self.session.execute(select(Menu))
        if result.scalars().all():
            return True
        return False

    async def create_dish(self):
        for dish in self.excel_dish:
            stmt = insert(Dish).values(
                id=dish.get('id'),
                title=dish.get('title'),
                description=dish.get('description'),
                price=dish.get('price'),
                submenu_id=dish.get('submenu_id'),
            ).returning(Dish)
            await self.session.execute(stmt)
        await self.session.commit()

    async def create_submenu(self):
        for submenu in self.excel_submenu:
            stmt = insert(Submenu).values(
                id=submenu.get('id'),
                title=submenu.get('title'),
                description=submenu.get('description'),
                menu_id=submenu.get('menu_id')
            )
            await self.session.execute(stmt)
        await self.session.commit()

    async def create_menu(self):
        for menu in self.excel_menu:
            stmt = insert(Menu).values(
                id=menu.get('id'),
                title=menu.get('title'),
                description=menu.get('description'),
            )
            await self.session.execute(stmt)
        await self.session.commit()

    async def create_data_in_db(self):
        if await self.check_db_state():
            return False
        await self.create_menu()
        await self.create_submenu()
        await self.create_dish()


class DBUpdater:
    def __init__(self, session, excel_menu, excel_submenu, excel_dish):
        self.session = session
        self.excel_menu = excel_menu
        self.excel_submenu = excel_submenu
        self.excel_dish = excel_dish

    async def check_menu_update(self):
        menus = (await self.session.execute(select(Menu).order_by(Menu.title))).scalars().all()
        for menu, excel_menu in zip(menus, self.excel_menu):
            if (menu.title != excel_menu.get('title')
                    or menu.description != excel_menu.get('description')):

                await self.session.execute(update(Menu).where(Menu.id == menu.id).values(
                    title=excel_menu.get('title'),
                    description=excel_menu.get('description'),
                ))
        await self.session.commit()
        return True

    async def check_submenu_update(self):
        submenus = (await self.session.execute(select(Submenu).order_by(Submenu.title))).scalars().all()
        for submenu, excel_submenu in zip(submenus, self.excel_submenu):
            if (submenu.title != excel_submenu.get('title') or
                    submenu.description != excel_submenu.get('description')):

                await self.session.execute(update(Submenu).where(Submenu.id == submenu.id).values(
                    title=excel_submenu.get('title'),
                    description=excel_submenu.get('description'),
                ))
        await self.session.commit()
        return True

    async def check_dish_update(self):
        dishes = (await self.session.execute(select(Dish))).scalars().all()
        for dish, excel_dish in zip(dishes, self.excel_dish):
            if (dish.title != excel_dish.get('title') or
                    dish.description != excel_dish.get('description') or
                    dish.price != excel_dish.get('price')):

                await self.session.execute(update(Dish).where(Dish.id == dish.id).values(
                    title=excel_dish.get('title'),
                    description=excel_dish.get('description'),
                    price=excel_dish.get('price'),
                ))
                await self.session.commit()
        return True

    async def check_db_update(self):
        await self.check_menu_update()
        await self.check_submenu_update()
        await self.check_dish_update()


async def run_update_base(excel_menu, excel_submenu, excel_dish):
    gen = get_async_session()
    session = await gen.__anext__()
    creator = DBCreator(session, excel_menu, excel_submenu, excel_dish)
    updater = DBUpdater(session, excel_menu, excel_submenu, excel_dish)
    await creator.create_data_in_db()
    await updater.check_db_update()
