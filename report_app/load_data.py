import os
import psycopg2
import json
import time

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_NAME = os.getenv("DB_NAME", "weatherdb")

def get_db_connection():
    max_attempts = 10
    for attempt in range(1, max_attempts + 1):
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
            return conn
        except Exception as e:
            print(f"Attempt {attempt}/{max_attempts}: Database connection error: {e}")
            time.sleep(2)
    raise Exception(f"Could not connect to the database after {max_attempts} attempts.")

def to_unix_timestamp(dt):
    if dt is None:
        return None
    if hasattr(dt, "timestamp"):
        try:
            return int(dt.timestamp())
        except Exception:
            pass
    if isinstance(dt, str):
        try:
            from dateutil import parser
            return int(parser.parse(dt).timestamp())
        except Exception:
            pass
    try:
        return int(dt)
    except Exception:
        return None

def load_weather_data():
    conn = get_db_connection()
    data = {}
    try:
        with conn.cursor() as cur:
            # weather current data
            cur.execute("SELECT city, timezone_offset, temp, feels_like, temp_min, temp_max, weather_main, weather_description, pressure, humidity, wind_speed, sunrise, sunset, current_time FROM weather.current")
            current_rows = cur.fetchall()
            for row in current_rows:
                city = row[0]
                data[city] = {
                    "current": {
                        "timezone_offset": row[1],
                        "temp": row[2],
                        "feels_like": row[3],
                        "temp_min": row[4],
                        "temp_max": row[5],
                        "weather_main": row[6],
                        "weather_description": row[7],
                        "pressure": row[8],
                        "humidity": row[9],
                        "wind_speed": row[10],
                        "sunrise": to_unix_timestamp(row[11]),
                        "sunset": to_unix_timestamp(row[12]),
                        "dt": to_unix_timestamp(row[13])
                    },
                    "forecast": []
                }
            # forecast data
            forecast_query = "SELECT city, forecast_time, temp, feels_like, temp_min, temp_max, weather_main, weather_description, pressure, humidity, wind_speed, sunrise, sunset, timezone_offset FROM weather.forecast"
            cur.execute(forecast_query)
            forecast_rows = cur.fetchall()
            for row in forecast_rows:
                city = row[0]
                forecast_entry = {
                    "dt": to_unix_timestamp(row[1]),
                    "temp": row[2],
                    "feels_like": row[3],
                    "temp_min": row[4],
                    "temp_max": row[5],
                    "weather_main": row[6],
                    "weather_description": row[7],
                    "pressure": row[8],
                    "humidity": row[9],
                    "wind_speed": row[10],
                    "sunrise": to_unix_timestamp(row[11]),
                    "sunset": to_unix_timestamp(row[12]),
                    "timezone_offset": row[13] if len(row) > 13 else 0
                }
                if city in data:
                    data[city]["forecast"].append(forecast_entry)
                else:
                    data[city] = {"current": {}, "forecast": [forecast_entry]}
    finally:
        conn.close()
    return data

def main():
    data = load_weather_data()
    print(json.dumps(data, indent=2))

if __name__ == "__main__":
    main()