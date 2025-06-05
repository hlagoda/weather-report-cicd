CREATE SCHEMA IF NOT EXISTS weather;

CREATE TABLE IF NOT EXISTS weather.current (
    id SERIAL PRIMARY KEY,
    city VARCHAR(255) NOT NULL UNIQUE,
    timezone_offset INT, 
    temp FLOAT,
    feels_like FLOAT,
    temp_min FLOAT,
    temp_max FLOAT,
    weather_main VARCHAR(255),
    weather_description VARCHAR(255),
    pressure INT,
    humidity INT,
    wind_speed FLOAT,
    sunrise TIMESTAMP,
    sunset TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS weather.history (
    id SERIAL PRIMARY KEY,
    city VARCHAR(255) NOT NULL,
    timezone_offset INT, 
    temp FLOAT,
    feels_like FLOAT,
    temp_min FLOAT,
    temp_max FLOAT,
    weather_main VARCHAR(255),
    weather_description VARCHAR(255),
    pressure INT,
    humidity INT,
    wind_speed FLOAT,
    sunrise TIMESTAMP,
    sunset TIMESTAMP,
    created_at TIMESTAMP NOT NULL
);


CREATE TABLE IF NOT EXISTS weather.forecast (
    id SERIAL PRIMARY KEY,
    city VARCHAR(255) NOT NULL,
    forecast_time TIMESTAMP NOT NULL,
    temp FLOAT,
    feels_like FLOAT,
    temp_min FLOAT,
    temp_max FLOAT,
    weather_main VARCHAR(255),
    weather_description VARCHAR(255),
    pressure INT,
    humidity INT,
    wind_speed FLOAT,
    sunrise TIMESTAMP,
    sunset TIMESTAMP,
    timezone_offset INT, 
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

