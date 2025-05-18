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

def load_weather_data():
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

@app.route('/')
def index():
    data = load_weather_data()
    table = []
    for city, citydata in data.items():
        current = citydata["current"]
        table.append({
            'city': city,
            'temp': current['main']['temp'],
            'weather_main': current['weather'][0]['main'],
            'pressure': current['main']['pressure'],
            'humidity': current['main']['humidity'],
            'wind_speed': current['wind']['speed'],
            'timezone': (datetime.utcnow() + timedelta(seconds=current['timezone'])).strftime('%Y-%m-%d %H:%M (UTC%z)')
        })
    return render_template('index.html', cities=table)

@app.route('/city/<city>')
def city_page(city):
    data = load_weather_data()
    city = city.lower()
    if city not in data:
        abort(404)
    current = data[city]["current"]
    forecast = data[city]["forecast"]
    return render_template('city.html', city=city, current=current, forecast=forecast)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
