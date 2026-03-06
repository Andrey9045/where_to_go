# Where to Go - Карта интересных мест

Проект для отображения интересных мест на карте. Позволяет просматривать локации, их описания и фотографии.


## Технологии

- Python 3.10
- Django 5.2
- SQLite3
- Leaflet.js 
- TinyMCE 

## Установка и запуск
1. Скачайте репозиторий
2. Откройте коммандную строку, перейдите в директорию репозитория
```
cd Путь\до\репозитория
```
3. Создайте виртуальное окружение
```
python -m venv venv
```
4. Активируйте виртуальное окружение
```
venv\Scripts\activate
```
5. Установите зависимости командой
```
pip install -r requirements.txt
```
6.Создайте файл .env в корне проекта:

env
```
SECRET_KEY=ваш_секретный_ключ
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhos
```
7. Генерация SECRET_KEY
```
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
8.Применяем миграции
```
python manage.py migrate
```
9.Создайте суперпользователя (для доступа в админку)
```
python manage.py createsuperuser
```
10. Запустите сервер
```
python manage.py runserver

```
