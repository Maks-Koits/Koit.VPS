#!/usr/bin/env python3
"""
Легковесный сервис аналитики для maks-koits.cv
Собирает статистику посещений, IP адреса, страны, страницы и т.д.
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import sqlite3
import os
import json
from datetime import datetime, timedelta
from collections import defaultdict
import ipaddress
import logging

app = Flask(__name__)
app.config['DATABASE'] = os.environ.get('DATABASE_PATH', '/data/analytics.db')
app.config['LOG_LEVEL'] = os.environ.get('LOG_LEVEL', 'INFO')

# Включаем CORS для JavaScript трекера
CORS(app, resources={
    r"/track": {"origins": ["https://maks-koits.cv", "https://cv.maks-koits.cv", "http://localhost:*"]},
    r"/api/*": {"origins": "*"}
})

logging.basicConfig(level=getattr(logging, app.config['LOG_LEVEL']))
logger = logging.getLogger(__name__)

# HTML шаблон для веб-интерфейса статистики
STATS_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Статистика посещений - maks-koits.cv</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: #f5f5f5;
            padding: 20px;
            color: #333;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { margin-bottom: 30px; color: #2c3e50; }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .stat-card h3 {
            font-size: 14px;
            color: #666;
            margin-bottom: 10px;
            text-transform: uppercase;
        }
        .stat-card .value {
            font-size: 32px;
            font-weight: bold;
            color: #2c3e50;
        }
        table {
            width: 100%;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }
        th {
            background: #2c3e50;
            color: white;
            font-weight: 600;
        }
        tr:hover { background: #f9f9f9; }
        .country-flag { margin-right: 8px; }
        .badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
        }
        .badge-primary { background: #3498db; color: white; }
        .badge-success { background: #2ecc71; color: white; }
        .badge-warning { background: #f39c12; color: white; }
        .filter-bar {
            margin-bottom: 20px;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        .filter-bar select, .filter-bar input {
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
        }
        .refresh-btn {
            padding: 8px 16px;
            background: #3498db;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }
        .refresh-btn:hover { background: #2980b9; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Статистика посещений maks-koits.cv</h1>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Всего посещений</h3>
                <div class="value">{{ total_visits }}</div>
            </div>
            <div class="stat-card">
                <h3>Уникальных посетителей</h3>
                <div class="value">{{ unique_visitors }}</div>
            </div>
            <div class="stat-card">
                <h3>Посещений сегодня</h3>
                <div class="value">{{ today_visits }}</div>
            </div>
            <div class="stat-card">
                <h3>Стран</h3>
                <div class="value">{{ countries_count }}</div>
            </div>
        </div>

        <h2 style="margin: 30px 0 20px 0;">🌍 Посещения по странам</h2>
        <table>
            <thead>
                <tr>
                    <th>Страна</th>
                    <th>Посещений</th>
                    <th>Уникальных IP</th>
                    <th>Последнее посещение</th>
                </tr>
            </thead>
            <tbody>
                {% for country in countries %}
                <tr>
                    <td>{{ country.name }}</td>
                    <td><span class="badge badge-primary">{{ country.visits }}</span></td>
                    <td><span class="badge badge-success">{{ country.unique_ips }}</span></td>
                    <td>{{ country.last_visit }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>

        <h2 style="margin: 30px 0 20px 0;">📄 Популярные страницы</h2>
        <table>
            <thead>
                <tr>
                    <th>Страница</th>
                    <th>Посещений</th>
                    <th>Уникальных посетителей</th>
                </tr>
            </thead>
            <tbody>
                {% for page in pages %}
                <tr>
                    <td>{{ page.path }}</td>
                    <td><span class="badge badge-primary">{{ page.visits }}</span></td>
                    <td><span class="badge badge-success">{{ page.unique_visitors }}</span></td>
                </tr>
                {% endfor %}
            </tbody>
        </table>

        <h2 style="margin: 30px 0 20px 0;">🔍 Последние посещения</h2>
        <table>
            <thead>
                <tr>
                    <th>Время</th>
                    <th>IP адрес</th>
                    <th>Страна</th>
                    <th>Страница</th>
                    <th>User Agent</th>
                </tr>
            </thead>
            <tbody>
                {% for visit in recent_visits %}
                <tr>
                    <td>{{ visit.timestamp }}</td>
                    <td>{{ visit.ip }}</td>
                    <td>{{ visit.country }}</td>
                    <td>{{ visit.path }}</td>
                    <td style="font-size: 12px; max-width: 300px; overflow: hidden; text-overflow: ellipsis;">{{ visit.user_agent }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</body>
</html>
"""


def init_db():
    """Инициализация базы данных"""
    db_path = app.config['DATABASE']
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Таблица посещений
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_address TEXT NOT NULL,
            country TEXT,
            city TEXT,
            path TEXT NOT NULL,
            referer TEXT,
            user_agent TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            language TEXT,
            screen_width INTEGER,
            screen_height INTEGER,
            timezone TEXT
        )
    ''')
    
    # Индексы для быстрого поиска
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_ip ON visits(ip_address)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON visits(timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_country ON visits(country)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_path ON visits(path)')
    
    conn.commit()
    conn.close()
    logger.info(f"База данных инициализирована: {db_path}")


def get_db():
    """Получить соединение с БД"""
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def get_country_by_ip(ip_address):
    """
    Определение страны по IP адресу
    Использует бесплатный API ip-api.com (без регистрации, до 45 запросов/минуту)
    Для production лучше использовать GeoIP2 или платный сервис
    """
    try:
        # Пропускаем локальные IP
        ip = ipaddress.ip_address(ip_address)
        if ip.is_private or ip.is_loopback or ip.is_link_local:
            return "Local", None
        
        import requests
        response = requests.get(f'http://ip-api.com/json/{ip_address}?fields=status,country,countryCode,city', timeout=2)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                return data.get('country', 'Unknown'), data.get('city')
    except Exception as e:
        logger.warning(f"Ошибка определения страны для {ip_address}: {e}")
    
    return "Unknown", None


@app.route('/track', methods=['POST', 'OPTIONS'])
def track():
    """Endpoint для трекинга посещений (вызывается из JavaScript)"""
    if request.method == 'OPTIONS':
        # Обработка preflight запроса для CORS
        return '', 200
    
    try:
        # Получаем данные из JSON или из FormData (для sendBeacon)
        if request.is_json:
            data = request.json or {}
        else:
            # Для sendBeacon данные приходят как raw body
            try:
                data = json.loads(request.data.decode('utf-8'))
            except:
                data = {}
        
        # Получаем IP адрес (учитываем прокси и заголовки nginx-proxy)
        ip_address = (
            request.headers.get('X-Real-IP') or 
            request.headers.get('X-Forwarded-For', '').split(',')[0].strip() or 
            request.remote_addr
        )
        
        # Определяем страну
        country, city = get_country_by_ip(ip_address)
        
        # Сохраняем посещение
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO visits 
            (ip_address, country, city, path, referer, user_agent, language, screen_width, screen_height, timezone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            ip_address,
            country,
            city,
            data.get('path', '/'),
            data.get('referer', request.headers.get('Referer', '')),
            data.get('userAgent', request.headers.get('User-Agent', '')),
            data.get('language', ''),
            data.get('screenWidth'),
            data.get('screenHeight'),
            data.get('timezone', '')
        ))
        conn.commit()
        conn.close()
        
        return jsonify({'status': 'ok'}), 200
    except Exception as e:
        logger.error(f"Ошибка при сохранении посещения: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/stats', methods=['GET'])
def stats():
    """Веб-интерфейс со статистикой"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Общая статистика
        cursor.execute('SELECT COUNT(*) as total FROM visits')
        total_visits = cursor.fetchone()['total']
        
        cursor.execute('SELECT COUNT(DISTINCT ip_address) as unique FROM visits')
        unique_visitors = cursor.fetchone()['unique']
        
        today = datetime.now().date()
        cursor.execute('SELECT COUNT(*) as today FROM visits WHERE DATE(timestamp) = ?', (today,))
        today_visits = cursor.fetchone()['today']
        
        # Статистика по странам
        cursor.execute('''
            SELECT 
                country,
                COUNT(*) as visits,
                COUNT(DISTINCT ip_address) as unique_ips,
                MAX(timestamp) as last_visit
            FROM visits
            WHERE country IS NOT NULL AND country != 'Local'
            GROUP BY country
            ORDER BY visits DESC
            LIMIT 20
        ''')
        countries = [dict(row) for row in cursor.fetchall()]
        countries_count = len(countries)
        
        # Популярные страницы
        cursor.execute('''
            SELECT 
                path,
                COUNT(*) as visits,
                COUNT(DISTINCT ip_address) as unique_visitors
            FROM visits
            GROUP BY path
            ORDER BY visits DESC
            LIMIT 20
        ''')
        pages = [dict(row) for row in cursor.fetchall()]
        
        # Последние посещения
        cursor.execute('''
            SELECT 
                timestamp,
                ip_address as ip,
                country,
                path,
                user_agent
            FROM visits
            ORDER BY timestamp DESC
            LIMIT 50
        ''')
        recent_visits = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return render_template_string(STATS_TEMPLATE,
            total_visits=total_visits,
            unique_visitors=unique_visitors,
            today_visits=today_visits,
            countries_count=countries_count,
            countries=countries,
            pages=pages,
            recent_visits=recent_visits
        )
    except Exception as e:
        logger.error(f"Ошибка при получении статистики: {e}")
        return f"Ошибка: {e}", 500


@app.route('/api/stats', methods=['GET'])
def api_stats():
    """JSON API для статистики"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Параметры фильтрации
        days = request.args.get('days', type=int, default=30)
        start_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor.execute('''
            SELECT 
                DATE(timestamp) as date,
                COUNT(*) as visits,
                COUNT(DISTINCT ip_address) as unique_visitors
            FROM visits
            WHERE timestamp >= ?
            GROUP BY DATE(timestamp)
            ORDER BY date DESC
        ''', (start_date,))
        
        daily_stats = [dict(row) for row in cursor.fetchall()]
        
        cursor.execute('''
            SELECT 
                country,
                COUNT(*) as visits,
                COUNT(DISTINCT ip_address) as unique_ips
            FROM visits
            WHERE country IS NOT NULL AND country != 'Local' AND timestamp >= ?
            GROUP BY country
            ORDER BY visits DESC
        ''', (start_date,))
        
        country_stats = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'daily': daily_stats,
            'countries': country_stats
        })
    except Exception as e:
        logger.error(f"Ошибка API: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok'}), 200


if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
