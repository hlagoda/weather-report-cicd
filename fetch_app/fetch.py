import os
import requests
import psycopg2
from datetime import datetime, timedelta

API_KEY = os.getenv("OPENWEATHER_API_KEY")

if not API_KEY:
    raise ValueError("Please set the OPENWEATHER_API_KEY environment variable.")

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_NAME = os.getenv("DB_NAME", "weatherdb")


CITIES = ["poznan", "barcelona", "new york", "tokyo", "sydney"]

CITY_COORDS = {
    "poznan": {"lat": 52.4069, "lon": 16.9299},
    "barcelona": {"lat": 41.3888, "lon": 2.159},
    "new york": {"lat": 40.7128, "lon": -74.0060},
    "tokyo": {"lat": 35.6895, "lon": 139.6917},
    "sydney": {"lat": -33.8688, "lon": 151.2093},
}

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=DB_NAME
    )

def fetch_city_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()

def fetch_city_forecast(city):
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    forecasts = data.get('list', [])
    # one forecast per day, closest to 12:00
    daily = {}
    for entry in forecasts:
        dt = datetime.fromtimestamp(entry['dt'])
        date_str = dt.date().isoformat()
        target_time = datetime.combine(dt.date(), datetime.min.time()) + timedelta(hours=12)
        diff = abs((dt - target_time).total_seconds())
        if date_str not in daily or diff < daily[date_str]['_diff']:
            daily[date_str] = {**entry, '_diff': diff}
    for v in daily.values():
        v.pop('_diff', None)
    return [daily[k] for k in sorted(daily.keys())]

def insert_current_weather(conn, city, data):
    with conn.cursor() as cur:
        cur.execute(
            '''
            INSERT INTO weather.current
            (city, timezone_offset, temp, feels_like, temp_min, temp_max, weather_main, weather_description,
             pressure, humidity, wind_speed, sunrise, sunset, current_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, to_timestamp(%s), to_timestamp(%s), to_timestamp(%s))
            ON CONFLICT (city) DO UPDATE SET
                timezone_offset=EXCLUDED.timezone_offset,
                temp=EXCLUDED.temp,
                feels_like=EXCLUDED.feels_like,
                temp_min=EXCLUDED.temp_min,
                temp_max=EXCLUDED.temp_max,
                weather_main=EXCLUDED.weather_main,
                weather_description=EXCLUDED.weather_description,
                pressure=EXCLUDED.pressure,
                humidity=EXCLUDED.humidity,
                wind_speed=EXCLUDED.wind_speed,
                sunrise=EXCLUDED.sunrise,
                sunset=EXCLUDED.sunset,
                current_time=EXCLUDED.current_time
            ''',
            (
                city,
                data['timezone'],
                data['main']['temp'],
                data['main']['feels_like'],
                data['main']['temp_min'],
                data['main']['temp_max'],
                data['weather'][0]['main'],
                data['weather'][0]['description'],
                data['main']['pressure'],
                data['main']['humidity'],
                data['wind']['speed'],
                data['sys']['sunrise'],
                data['sys']['sunset'],
                data['dt']
            )
        )
    conn.commit()

def insert_forecast(conn, city, forecasts, timezone_offset):
    with conn.cursor() as cur:
        for entry in forecasts:
            cur.execute(
                '''
                INSERT INTO weather.forecast
                (city, forecast_time, temp, feels_like, temp_min, temp_max, weather_main, weather_description,
                 pressure, humidity, wind_speed, sunrise, sunset, timezone_offset, created_at)
                VALUES (%s, to_timestamp(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s, to_timestamp(%s), to_timestamp(%s), %s, NOW())
                ''',
                (
                    city,
                    entry['dt'],
                    entry['main']['temp'],
                    entry['main']['feels_like'],
                    entry['main']['temp_min'],
                    entry['main']['temp_max'],
                    entry['weather'][0]['main'],
                    entry['weather'][0]['description'],
                    entry['main']['pressure'],
                    entry['main']['humidity'],
                    entry['wind']['speed'],
                    entry.get('sys', {}).get('sunrise', None),
                    entry.get('sys', {}).get('sunset', None),
                    timezone_offset
                )
            )
    conn.commit()

def main():
    conn = get_db_connection()
    for city in CITY_COORDS.keys():
        print(f"Fetching data for {city}")
        current = fetch_city_weather(city)
        insert_current_weather(conn, city, current)
        forecast_list = fetch_city_forecast(city)
        timezone_offset = current['timezone']
        insert_forecast(conn, city, forecast_list, timezone_offset)
    conn.close()


if __name__ == "__main__":
    main()

