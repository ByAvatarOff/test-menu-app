# Menu app
## Описание задачи
Проект на FastAPI с использованием PostgreSQL в качестве БД. В проекте реализовано REST API по работе с меню ресторана, все CRUD операции.
Использованы 3 сущности:
+ Меню
+ Подменю
+ Блюдо.

Зависимости:
+ У меню есть подменю, которые к ней привязаны
+ У подменю есть блюда.

Условия:
+ Блюдо не может быть привязано напрямую к меню, минуя подменю.
+ Блюдо не может находиться в 2-х подменю одновременно.
+ Подменю не может находиться в 2-х меню одновременно.
+ Если удалить меню, должны удалиться все подменю и блюда этого меню.
+ Если удалить подменю, должны удалиться все блюда этого подменю.
+ Цены блюд выводить с округлением до 2 знаков после запятой.
+ Во время выдачи списка меню, для каждого меню добавлять кол-во подменю и блюд в этом меню.
+ Во время выдачи списка подменю, для каждого подменю добавлять кол-во блюд в этом подменю.

## Задания с *

+ ### tests/utils.py # аналог Django reverse()
+

## Алгоритм запуска

```shell
git clone https://github.com/ByAvatarOff/test-menu-app.git
cd test-menu-app
```
### Для создания переменных окружения необходимо переимновать файл .env.example > .env
```
mv .env.example .env  # OS Linux
ren ".env.example" ".env"  # OS Windows
```
## Запуск использую docker-compose
### Установить docker > `https://docs.docker.com/engine/install/`
### Запуск тестов
```shell
docker-compose -f docker-compose-tests.yaml up --build
```
### Запуск приложения
```shell
docker-compose -f docker-compose-main.yaml up --build
```
### Запуск приложения в фоновом режиме
```shell
docker-compose -f docker-compose-main.yaml create
docker-compose -f docker-compose-main.yaml start
```
### Остановка docker-compose
```shell
docker-compose -f docker-compose-main.yaml stop
```
### Видео демонстрация работы:
[Test_menu_app](https://youtu.be/ikLpG94U3n8)

## Endpoints
## Menu
### 1)  **[GET]** Просмотр списка меню
### ``` api/v1/menus ```

### Data
```
[
  {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "title": "string",
    "description": "string"
  }
]
```

### 2) **[POST]** Создание меню
### ``` api/v1/menus ```
### Body
```
{
  "title": "string",
  "description": "string"
}
```
### Data
```
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "title": "string",
  "description": "string"
}
```

### 3) **[GET]** Просмотр определенного меню
### ``` api/v1/menus/{menu_id} # menu_id > UUID4```

### Data
```
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "title": "string",
  "description": "string",
  "submenus_count": 0,
  "dishes_count": 0
}
```

### 4) **[PATCH]** Обновление определенного меню
### ``` api/v1/menus/{menu_id} # menu_id > UUID4```

### Body
```
{
  "title": "new_string",
  "description": "new_string"
}
```
### Data
```
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "title": "new_string",
  "description": "new_string"
}
```

### 5) **[DELETE]** Удаление определенного меню
### ``` api/v1/menus/{menu_id} # menu_id > UUID4```

### Data
```
{
  "message": "Success delete"
}
```

## Submenu
### 6) **[GET]** Просмотр списка подменю
### ``` api/v1/menus/{menu_id}/submenus # menu_id > UUID4```

### Data
```
[
  {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "title": "string",
    "description": "string"
  }
]
```

### 7) **[POST]** Создание подменю
### ``` api/v1/menus/{menu_id}/submenus # menu_id > UUID4```
### Body
```
{
  "title": "string",
  "description": "string"
}
```
### Data
```
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "title": "string",
  "description": "string"
}
```

### 8) **GET** Просмотр подменю
### ``` api/v1/menus/{menu_id}/submenus/{submenu_id} # menu_id > UUID4; submenu_id > UUID4```

### Data
```
[
  {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "title": "string",
    "description": "string",
    "dishes_count": 0
  }
]
```

### 9) **[PATCH]** Обновление подменю
### ```api/v1/menus/{menu_id}/submenus/{submenu_id} # menu_id > UUID4; submenu_id > UUID4```
### Body
```
{
  "title": "new_string",
  "description": "new_string"
}
```
### Data
```
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "title": "new_string",
  "description": "new_string"
}
```

### 10) **[DELETE]** Удаление подменю
### ``` api/v1/menus/{menu_id}/submenus/{submenu_id} # menu_id > UUID4; submenu_id > UUID4```

### Data
```
{
  "message": "Success delete"
}
```
## Dish
### 11) **[GET]** Просмотр списка блюд
### ```api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes # menu_id > UUID4; submenu_id > UUID4```

### Data
```
[
  {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "title": "string",
    "description": "string",
    "price": "12.50"
  }
]
```

### 12) **[POST]** Создание блюда
### ```api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes # menu_id > UUID4; submenu_id > UUID4```

### Body
```
{
  "title": "string",
  "description": "string",
  "price": "12.50"
}
```

### Data
```
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "title": "string",
  "description": "string",
  "price": "12.50"
}
```

### 13) **[GET]** Просмотр определенного блюда
### ```api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id} # menu_id > UUID4; submenu_id > UUID4; dish_id > UUID4```

### Data
```
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "title": "string",
  "description": "string",
  "price": "12.50"
}
```

### 13) **[PATCH]** Обновление определенного блюда
### ```api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id} # menu_id > UUID4; submenu_id > UUID4; dish_id > UUID4```

### Body
```
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "title": "new_string",
  "description": "new_string",
  "price": "1434.50"
}
```

### Data
```
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "title": "new_string",
  "description": "new_string",
  "price": "1434.50"
}
```

### 15) **[DELETE]** Удаление определенного блюда
### ```api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id} # menu_id > UUID4; submenu_id > UUID4; dish_id > UUID4```

### Data
```
{
  "message": "Success delete"
}
```
