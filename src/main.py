"""main endpoint"""

from fastapi import FastAPI

from menu_app.dish import dish_router
from menu_app.menu import menu_router
from menu_app.submenu import submenu_router


app = FastAPI(
    title='Menu App',
    description='Menu App for CRUD operations',
    version='3.1.0',
    openapi_tags=[
        {
            'name': 'Menu',
            'description': 'Menu CRUD',
        },
        {
            'name': 'Submenu',
            'description': 'Submenu CRUD',
        },
        {
            'name': 'Dish',
            'description': 'Dish CRUD',
        },
    ]
)

app.include_router(menu_router.menu_router)
app.include_router(submenu_router.submenu_router)
app.include_router(dish_router.dish_router)
