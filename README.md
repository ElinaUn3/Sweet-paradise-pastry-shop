# Сладкий рай — Кондитерская

Веб-приложение для управления каталогом тортов и заказами кондитерской «Сладкий рай».

## Стек

- **Backend:** Python 3.9, Django 4.2
- **БД:** PostgreSQL
- **Frontend:** HTML/CSS (Times New Roman, цвета: `#FC34C8`, `#31EBFF`)

## Роли

| Роль | Возможности |
|------|------------|
| Гость | Просмотр каталога |
| Клиент | Каталог с фильтрами/поиском + свои заказы |
| Менеджер | Все заказы, смена статусов |
| Администратор | Полный CRUD товаров, заказов, пользователей |

## Запуск

```bash
cd project
pip install -r requirements.txt

# Создать БД PostgreSQL
createdb cake_shop

# Применить миграции и импортировать данные
python manage.py migrate
python manage.py import_data

python manage.py runserver
```

Приложение будет доступно на `http://127.0.0.1:8000`

## Тестовые аккаунты

| Роль | Email | Пароль |
|------|-------|--------|
| Администратор | `kondratieva@cake-shop.ru` | `AdCk76#` |
| Менеджер | `kremov@cake-shop.ru` | `Mn7@gP23` |
| Клиент | `saharova.client@mail.ru` | `Cli3nt#9` |
