from flask import Flask, render_template, abort
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__)


def datetimeformat(value, timezone_offset=0, format='%Y-%m-%d %H:%M:%S'):
    try:
        # value: unix timestamp, timezone_offset: seconds
        dt = datetime.utcfromtimestamp(int(value))
        dt = dt + timedelta(seconds=timezone_offset)
        return dt.strftime(format)
    except Exception:
        return value

app.jinja_env.filters['datetimeformat'] = datetimeformat

DATA_FILE = os.path.join('flask_app', 'openweather_data.json')

import psycopg2

DB_HOST = os.environ.get('DB_HOST', 'db')
DB_PORT = os.environ.get('DB_PORT', 5432)
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'postgres')
DB_NAME = os.environ.get('DB_NAME', 'weather')

def load_weather_data():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=DB_NAME
    )
    cur = conn.cursor()
    cur.execute("SELECT city, timezone_offset, temp, feels_like, temp_min, temp_max, weather_main, weather_description, pressure, humidity, wind_speed, sunrise, sunset, current_time FROM weather.current")
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    data = [dict(zip(columns, row)) for row in rows]
    cur.close()
    conn.close()
    return data


def load_forecast_data():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=DB_NAME
    )
    cur = conn.cursor()
    cur.execute("SELECT * FROM weather.forecast")
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    data = [dict(zip(columns, row)) for row in rows]
    cur.close()
    conn.close()
    return data

@app.route('/')
def index():
    data = load_weather_data()  # List of dicts from weather.current
    table = []
    for row in data:
        table.append({
            'city': row['city'],
            'temp': row['temp'],
            'weather_main': row['weather_main'],
            'pressure': row['pressure'],
            'humidity': row['humidity'],
            'wind_speed': row['wind_speed'],
            'timezone': (datetime.utcnow() + timedelta(seconds=row.get('timezone_offset', 0))).strftime('%Y-%m-%d %H:%M (UTC%z)')
        })
    return render_template('index.html', cities=table)

@app.route('/city/<city>')
def city_page(city):
    city = city.lower()
    # Get current weather for this city
    current_list = [row for row in load_weather_data() if row['city'].lower() == city]
    if not current_list:
        abort(404)
    current = current_list[0]
    # Get forecast for this city
    forecast = [row for row in load_forecast_data() if row['city'].lower() == city]
    return render_template('city.html', city=city, current=current, forecast=forecast)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
