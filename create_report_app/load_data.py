import os
import psycopg2
import json

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_NAME = os.getenv("DB_NAME", "weatherdb")

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=DB_NAME
    )

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
                        "timezone": row[1],
                        "main": {
                            "temp": row[2],
                            "feels_like": row[3],
                            "temp_min": row[4],
                            "temp_max": row[5],
                            "pressure": row[8],
                            "humidity": row[9]
                        },
                        "weather": [{
                            "main": row[6],
                            "description": row[7]
                        }],
                        "wind": {"speed": row[10]},
                        "sys": {"sunrise": int(row[11]), "sunset": int(row[12])},
                        "dt": int(row[13].timestamp()) if row[13] else None
                    },
                    "forecast": []
                }
            # forecast data
            cur.execute("SELECT city, forecast_time, temp, feels_like, temp_min, temp_max, weather_main, weather_description, pressure, humidity, wind_speed, sunrise, sunset FROM weather.forecast")
            forecast_rows = cur.fetchall()
            for row in forecast_rows:
                city = row[0]
                forecast_entry = {
                    "dt": int(row[1].timestamp()) if row[1] else None,
                    "main": {
                        "temp": row[2],
                        "feels_like": row[3],
                        "temp_min": row[4],
                        "temp_max": row[5],
                        "pressure": row[8],
                        "humidity": row[9]
                    },
                    "weather": [{
                        "main": row[6],
                        "description": row[7]
                    }],
                    "wind": {"speed": row[10]},
                    "sys": {"sunrise": int(row[11]), "sunset": int(row[12])}
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