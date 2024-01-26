# Menu app
## Функции в которых присутствует сложный запрос на получение submenus_count, dishes_count
```
src > menu > utils > set_counters_for_menu
src > menu > utils > set_counters_for_submenu
```
## Алгоритм запуска

```shell
git clone https://github.com/ByAvatarOff/test-menu-app.git
cd test-menu-app
```
### Создание переменных окружения
```
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

DB_HOST_TEST=localhost
DB_PORT_TEST=<POSTGRES_PORT>
DB_NAME_TEST=<POSTGRES_DB_NAME>
DB_USER_TEST=<POSTGRES_USER>
DB_PASS_TEST=<POSTGRES_PASSWORD>
```
## Запуск использую docker-compose
### Запуск тестов
```shell
docker-compose -f docker-compose-tests.yaml up --build
```
### Запуск прилодения
```shell
docker-compose -f docker-compose-main.yaml up --build
```