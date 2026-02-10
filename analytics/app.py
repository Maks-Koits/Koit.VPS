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
        #map { height: 500px; width: 100%; border-radius: 8px; margin: 20px 0; }
        .map-container { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .ip-info { font-size: 12px; color: #666; }
        .ip-info strong { color: #333; }
    </style>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
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

        <h2 style="margin: 30px 0 20px 0;">🗺️ Карта посещений</h2>
        <div class="map-container">
            <div id="map"></div>
        </div>
        <script>
            var map = L.map('map').setView([20, 0], 2);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors'
            }).addTo(map);
            
            var markers = [];
            {% for visit in recent_visits %}
            {% if visit.latitude and visit.longitude %}
            var marker = L.marker([{{ visit.latitude }}, {{ visit.longitude }}]).addTo(map);
            marker.bindPopup(`
                <strong>IP:</strong> {{ visit.ip }}<br>
                <strong>Страна:</strong> {{ visit.country }}<br>
                <strong>Город:</strong> {{ visit.city or 'N/A' }}<br>
                <strong>Регион:</strong> {{ visit.region or 'N/A' }}<br>
                <strong>Провайдер:</strong> {{ visit.isp or 'N/A' }}<br>
                <strong>Время:</strong> {{ visit.timestamp }}
            `);
            markers.push(marker);
            {% endif %}
            {% endfor %}
            
            if (markers.length > 0) {
                var group = new L.featureGroup(markers);
                map.fitBounds(group.getBounds().pad(0.1));
            }
        </script>

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
                    <td>{{ country.country }}</td>
                    <td><span class="badge badge-primary">{{ country.visits }}</span></td>
                    <td><span class="badge badge-success">{{ country.unique_ip_count }}</span></td>
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
                    <td><span class="badge badge-success">{{ page.unique_visitor_count }}</span></td>
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
                    <th>Местоположение</th>
                    <th>Провайдер</th>
                    <th>Страница</th>
                </tr>
            </thead>
            <tbody>
                {% for visit in recent_visits %}
                <tr>
                    <td>{{ visit.timestamp }}</td>
                    <td>
                        <strong>{{ visit.ip }}</strong>
                        {% if visit.asn %}
                        <br><span class="ip-info">AS{{ visit.asn }}</span>
                        {% endif %}
                    </td>
                    <td>
                        <strong>{{ visit.country }}</strong>
                        {% if visit.region %}
                        <br><span class="ip-info">{{ visit.region }}</span>
                        {% endif %}
                        {% if visit.city %}
                        <br><span class="ip-info">{{ visit.city }}</span>
                        {% endif %}
                        {% if visit.latitude and visit.longitude %}
                        <br><span class="ip-info">📍 {{ "%.4f"|format(visit.latitude) }}, {{ "%.4f"|format(visit.longitude) }}</span>
                        {% endif %}
                    </td>
                    <td>
                        {% if visit.isp %}
                        <strong>{{ visit.isp }}</strong>
                        {% endif %}
                        {% if visit.org and visit.org != visit.isp %}
                        <br><span class="ip-info">{{ visit.org }}</span>
                        {% endif %}
                    </td>
                    <td>{{ visit.path }}</td>
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
    db_dir = os.path.dirname(db_path)
    
    # Создаем директорию с правами на запись
    try:
        if db_dir and db_dir != '.':
            os.makedirs(db_dir, exist_ok=True, mode=0o755)
            logger.info(f"Директория БД создана/проверена: {db_dir}")
        else:
            db_path = '/data/analytics.db'
            db_dir = '/data'
            os.makedirs(db_dir, exist_ok=True, mode=0o755)
            logger.info(f"Используем стандартный путь: {db_path}")
    except Exception as e:
        logger.error(f"Ошибка создания директории {db_dir}: {e}")
        # Пробуем создать в текущей директории как fallback
        db_path = '/tmp/analytics.db'
        logger.warning(f"Используем fallback путь: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path, timeout=10.0)
        cursor = conn.cursor()
        logger.info(f"Подключение к БД установлено: {db_path}")
        
        # Таблица посещений
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS visits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip_address TEXT NOT NULL,
                country TEXT,
                country_code TEXT,
                region TEXT,
                city TEXT,
                latitude REAL,
                longitude REAL,
                isp TEXT,
                org TEXT,
                asn TEXT,
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
        
        # Добавляем новые колонки если их нет (для существующих БД)
        try:
            cursor.execute('ALTER TABLE visits ADD COLUMN country_code TEXT')
        except:
            pass
        try:
            cursor.execute('ALTER TABLE visits ADD COLUMN region TEXT')
        except:
            pass
        try:
            cursor.execute('ALTER TABLE visits ADD COLUMN latitude REAL')
        except:
            pass
        try:
            cursor.execute('ALTER TABLE visits ADD COLUMN longitude REAL')
        except:
            pass
        try:
            cursor.execute('ALTER TABLE visits ADD COLUMN isp TEXT')
        except:
            pass
        try:
            cursor.execute('ALTER TABLE visits ADD COLUMN org TEXT')
        except:
            pass
        try:
            cursor.execute('ALTER TABLE visits ADD COLUMN asn TEXT')
        except:
            pass
        
        # Индексы для быстрого поиска
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ip ON visits(ip_address)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON visits(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_country ON visits(country)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_path ON visits(path)')
        
        conn.commit()
        conn.close()
        logger.info(f"База данных инициализирована: {db_path}")
    except Exception as e:
        logger.error(f"Ошибка инициализации БД {db_path}: {e}")
        raise


def get_db():
    """Получить соединение с БД"""
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def get_geo_info_by_ip(ip_address):
    """
    Определение геолокации и информации об IP адресе
    Использует бесплатный API ip-api.com (без регистрации, до 45 запросов/минуту)
    Возвращает словарь с полной информацией: страна, город, координаты, провайдер и т.д.
    """
    try:
        # Пропускаем локальные IP
        ip = ipaddress.ip_address(ip_address)
        if ip.is_private or ip.is_loopback or ip.is_link_local:
            return {
                'country': 'Local',
                'country_code': None,
                'region': None,
                'city': None,
                'latitude': None,
                'longitude': None,
                'isp': None,
                'org': None,
                'asn': None
            }
        
        import requests
        # Запрашиваем полную информацию об IP
        response = requests.get(
            f'http://ip-api.com/json/{ip_address}?fields=status,country,countryCode,regionName,city,lat,lon,isp,org,as,query',
            timeout=3
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                return {
                    'country': data.get('country', 'Unknown'),
                    'country_code': data.get('countryCode'),
                    'region': data.get('regionName'),
                    'city': data.get('city'),
                    'latitude': data.get('lat'),
                    'longitude': data.get('lon'),
                    'isp': data.get('isp'),
                    'org': data.get('org'),
                    'asn': data.get('as', '').replace('AS', '') if data.get('as') else None
                }
    except Exception as e:
        logger.warning(f"Ошибка определения геолокации для {ip_address}: {e}")
    
    return {
        'country': 'Unknown',
        'country_code': None,
        'region': None,
        'city': None,
        'latitude': None,
        'longitude': None,
        'isp': None,
        'org': None,
        'asn': None
    }


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
        
        # Получаем полную геоинформацию об IP
        geo_info = get_geo_info_by_ip(ip_address)
        
        # Сохраняем посещение
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO visits 
            (ip_address, country, country_code, region, city, latitude, longitude, isp, org, asn,
             path, referer, user_agent, language, screen_width, screen_height, timezone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            ip_address,
            geo_info.get('country'),
            geo_info.get('country_code'),
            geo_info.get('region'),
            geo_info.get('city'),
            geo_info.get('latitude'),
            geo_info.get('longitude'),
            geo_info.get('isp'),
            geo_info.get('org'),
            geo_info.get('asn'),
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
        
        logger.info(f"Visit tracked: IP={ip_address}, Path={data.get('path', '/')}, Country={geo_info.get('country')}, City={geo_info.get('city')}, ISP={geo_info.get('isp')}")
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
        
        cursor.execute('SELECT COUNT(DISTINCT ip_address) as unique_count FROM visits')
        unique_visitors = cursor.fetchone()['unique_count']
        
        today = datetime.now().date()
        cursor.execute('SELECT COUNT(*) as today FROM visits WHERE DATE(timestamp) = ?', (today,))
        today_visits = cursor.fetchone()['today']
        
        # Статистика по странам
        cursor.execute('''
            SELECT 
                country,
                COUNT(*) as visits,
                COUNT(DISTINCT ip_address) as unique_ip_count,
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
                COUNT(DISTINCT ip_address) as unique_visitor_count
            FROM visits
            GROUP BY path
            ORDER BY visits DESC
            LIMIT 20
        ''')
        pages = [dict(row) for row in cursor.fetchall()]
        
        # Последние посещения с полной геоинформацией
        cursor.execute('''
            SELECT 
                timestamp,
                ip_address as ip,
                country,
                country_code,
                region,
                city,
                latitude,
                longitude,
                isp,
                org,
                asn,
                path,
                user_agent
            FROM visits
            WHERE latitude IS NOT NULL AND longitude IS NOT NULL
            ORDER BY timestamp DESC
            LIMIT 100
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
                COUNT(DISTINCT ip_address) as unique_visitor_count
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
                COUNT(DISTINCT ip_address) as unique_ip_count
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
