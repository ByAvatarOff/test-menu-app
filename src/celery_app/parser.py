"""Parse excel document with menu"""
import pickle
from pathlib import Path
from uuid import uuid4

import gspread
from gspread.client import Client
from gspread.spreadsheet import Spreadsheet
from gspread.worksheet import Worksheet

from db.cache_repo import CacheMenuAppKeys
from db.database import get_redis_session


class ExcelParser:
    """Excel menu parser"""

    def __init__(self) -> None:
        self.wb: Client = gspread.service_account(filename=Path(__file__).parents[2] / 'test_service.json')
        self.sheets: Spreadsheet = self.wb.open('Menu')
        self.sheet: Worksheet = self.sheets.get_worksheet(0)
        self.redis_session = get_redis_session()
        self.menu_app_keys = CacheMenuAppKeys()

    async def build_menu(self):
        """Read excel document and build 3 list of dict: menu. submenu, dish """
        menu_list = []
        submenu_list = []
        dish_list = []
        dish_list_with_discount = []
        menu_id = ''
        submenu_id = ''
        all_values = self.sheet.get_all_values()
        for rowNumber, row in enumerate(all_values, start=1):
            if row[0].isnumeric():
                menu_id = uuid4()
                menu_list.append(
                    {
                        'id': str(menu_id),
                        'title': row[1],
                        'description': row[2],
                    })
                continue
            if row[1].isnumeric():
                submenu_id = uuid4()
                submenu_list.append(
                    {
                        'id': str(submenu_id),
                        'title': row[2],
                        'description': row[3],
                        'menu_id': str(menu_id),
                    })
                continue
            if row[2].isnumeric():
                dish_id = uuid4()
                dish_list.append(
                    {
                        'id': str(dish_id),
                        'title': row[3],
                        'description': row[4],
                        'price': str(row[5]).replace(',', '.'),
                        'submenu_id': str(submenu_id),
                    })
                dish_list_with_discount.append(
                    {
                        'title': row[3],
                        'discount': row[6],
                    }
                )
                continue
        dish_discount_key = self.menu_app_keys.get_dish_discount_key
        session = await self.redis_session.__anext__()
        await session.set(dish_discount_key, pickle.dumps(dish_list_with_discount))
        return (
            menu_list,
            submenu_list,
            dish_list,
        )
