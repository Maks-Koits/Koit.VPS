#!/usr/bin/env python3
"""
Скрипт для очистки базы данных аналитики
Использование: docker exec maks-koits-cv-analytics python3 /app/clear_db.py
"""

import sqlite3
import os
import sys

def clear_database(db_path='/data/analytics.db', reset_counter=False):
    """Очистить базу данных"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Удалить все записи
        cursor.execute('DELETE FROM visits')
        deleted_count = cursor.rowcount
        
        # Сбросить счетчик автоинкремента (опционально)
        if reset_counter:
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='visits'")
        
        conn.commit()
        
        # Проверить количество записей
        cursor.execute('SELECT COUNT(*) FROM visits')
        remaining_count = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"✅ База данных очищена!")
        print(f"   Удалено записей: {deleted_count}")
        print(f"   Осталось записей: {remaining_count}")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == '__main__':
    db_path = os.environ.get('DATABASE_PATH', '/data/analytics.db')
    reset_counter = '--reset-counter' in sys.argv
    
    if not os.path.exists(db_path):
        print(f"❌ Файл базы данных не найден: {db_path}")
        sys.exit(1)
    
    clear_database(db_path, reset_counter)
