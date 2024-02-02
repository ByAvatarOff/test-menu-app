"""
main endpoint
"""

from fastapi import FastAPI

from menu_app.menu import menu_router
from menu_app.submenu import submenu_router
from menu_app.dish import dish_router


app = FastAPI(
    title="Menu App"
)

app.include_router(menu_router.menu_router)
app.include_router(submenu_router.submenu_router)
app.include_router(dish_router.dish_router)
