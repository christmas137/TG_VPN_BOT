import sqlite3
import os

# Определение абсолютного пути к файлу базы данных
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(BASE_DIR, 'db', 'vpn_bot_db.sqlite')

# Подключение к файлу базы данных
conn = sqlite3.connect(db_path)

cur = conn.cursor()

# Создание таблицы подписок, если она еще не существует

# Сохранение изменений и закрытие подключения к базе данных
conn.commit()
conn.close()