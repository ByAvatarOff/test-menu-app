# Menu app
## Алгоритм запуска

```shell
git clone https://github.com/ByAvatarOff/test-menu-app.git
cd test-menu-app
``` 
### Установка виртуального окружения и активация
```shell
python -m venv venv
venv\scripts\activate  # Активация в ОС Windows
source venv/bin/activate  # Активация в ОС Linux
```
### Установка зависимостей
```shell
pip install -r requirements.txt
```
### Создание переменных окружения
```
cd src
echo > .env  # Создание файла в ОС Windows
touch .env  # Создание файла в ОС Linux
```
### Скопировать и подставить значения в .env ->
```
DB_HOST=localhost
DB_PORT=<POSTGRES_PORT>
DB_NAME=<POSTGRES_DB_NAME>
DB_USER=<POSTGRES_USER>
DB_PASS=<POSTGRES_PASSWORD>
```
### Создать базу данных postgres c заданным в .env именем
```postgresql
CREATE DATABASE POSTGRES_DB_NAME;
```
### Создание миграций
```
cd ..
alembic revision --autogenerate -m "init"
alembic upgrade head
```
### Запуск сервера
```
cd src
uvicorn main:app --reload
```
