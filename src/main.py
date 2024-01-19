from fastapi import FastAPI

from menu.routers import menu_router, submenu_router, dish_router

app = FastAPI(
    title="Menu App"
)

app.include_router(menu_router.menu_router)
app.include_router(submenu_router.submenu_router)
app.include_router(dish_router.dish_router)
