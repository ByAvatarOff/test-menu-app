"""Parse excel document with menu"""
import openpyxl
import pickle
from openpyxl import Workbook
from openpyxl.worksheet.worksheet import Worksheet
from pathlib import Path
from uuid import uuid4
from db.cache_repo import CacheMenuAppKeys
from db.database import get_redis_session


class ExcelParser:
    """Excel menu parser"""
    def __init__(self):
        self.wb: Workbook = openpyxl.load_workbook(Path(__file__).parents[2] / 'admin/Menu.xlsx', data_only=True)
        self.sheet: Worksheet = self.wb.active
        self.redis_session = get_redis_session()
        self.menu_app_keys = CacheMenuAppKeys()

    async def sorted_menu(self, menu_obj):
        return sorted(menu_obj, key=lambda obj: obj.get('title'))

    async def build_menu(self):
        menu_list = []
        submenu_list = []
        dish_list = []
        dish_list_with_discount = []
        menu_id = ''
        submenu_id = ''
        for rowNumber in range(1, self.sheet.max_row + 1):
            if isinstance(self.sheet[f'A{rowNumber}'].value, int):
                menu_id = uuid4()
                menu_list.append(
                    {
                        "id": str(menu_id),
                        "title": self.sheet[f'B{rowNumber}'].value,
                        "description": self.sheet[f'C{rowNumber}'].value,
                     })
                continue
            if isinstance(self.sheet[f'B{rowNumber}'].value, int):
                submenu_id = uuid4()
                submenu_list.append(
                    {
                        "id": str(submenu_id),
                        "title": self.sheet[f'C{rowNumber}'].value,
                        "description": self.sheet[f'D{rowNumber}'].value,
                        "menu_id": str(menu_id),
                    })
                continue
            if isinstance(self.sheet[f'C{rowNumber}'].value, int):
                dish_id = uuid4()
                dish_list.append(
                    {
                        "id": str(dish_id),
                        "title": self.sheet[f'D{rowNumber}'].value,
                        "description": self.sheet[f'E{rowNumber}'].value,
                        "price": str(self.sheet[f'F{rowNumber}'].value).replace(',', '.'),
                        "submenu_id": str(submenu_id),
                    })
                dish_list_with_discount.append(
                    {
                        "title": self.sheet[f'D{rowNumber}'].value,
                        "discount": self.sheet[f'G{rowNumber}'].value,
                    }
                )
                continue
        dish_discount_key = self.menu_app_keys.get_dish_discount_key
        session = await self.redis_session.__anext__()
        await session.set(dish_discount_key, pickle.dumps(dish_list_with_discount))
        return (
            await self.sorted_menu(menu_list),
            await self.sorted_menu(submenu_list),
            await self.sorted_menu(dish_list),
        )