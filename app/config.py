import os

class Config:
    """Конфигурация приложения."""
    # Секретный ключ для защиты сессий и формы (CSRF)
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_secret_key')
    # Строка подключения к базе данных (по умолчанию SQLite в текущей директории)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Другие настройки (при необходимости)
    # e.g., DEBUG = True
