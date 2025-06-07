import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime, timezone
from load_data import load_weather_data

def format_unix_time(ts, tz_offset=0):
    if not ts:
        return "-"
    return datetime.fromtimestamp(ts + tz_offset, timezone.utc).strftime('%Y-%m-%d %H:%M')

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)
PDF_FILE = os.path.join(
    OUTPUT_DIR,
    f"weather_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
)

def main():
    """
    Generates a PDF weather report for multiple cities using data from a database.

    This function loads weather data from a PostgreSQL database, organizes the
    data into a PDF document using ReportLab, and saves the generated document
    to a specified output directory. The report includes current weather
    conditions and a deduplicated daily forecast for each city.

    The report includes:
    - A title and a header for each city.
    - A table with current weather conditions such as temperature, feels like
      temperature, weather description, pressure, humidity, wind speed, sunrise,
      and sunset times.
    - A deduplicated daily forecast with date, temperature, feels like
      temperature, weather, pressure, humidity, and wind speed.

    The PDF file is saved with a timestamp in the filename to ensure uniqueness.
    """
    data = load_weather_data()
    doc = SimpleDocTemplate(PDF_FILE, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("<b>Weather Report</b>", styles['Title']))
    elements.append(Spacer(1, 18))

    for city, citydata in data.items():
        current = citydata.get('current', {})
        forecast = citydata.get('forecast', [])
        # Process city data

        elements.append(Paragraph(f"<b>{city.capitalize()}</b>", styles['Heading2']))
        elements.append(Spacer(1, 12))

        curr_table_data = [
            ["Temperature (°C)", current.get('temp', '-')],
            ["Feels Like (°C)", current.get('feels_like', '-')],
            ["Weather", current.get('weather_main', '-')],
            ["Description", current.get('weather_description', '-')],
            ["Pressure (hPa)", current.get('pressure', '-')],
            ["Humidity (%)", current.get('humidity', '-')],
            ["Wind Speed (m/s)", current.get('wind_speed', '-')],
            ["Sunrise (UTC)", format_unix_time(current.get('sunrise'))],
            ["Sunset (UTC)", format_unix_time(current.get('sunset'))],
        ]
        curr_table = Table(curr_table_data, hAlign='LEFT')
        curr_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ]))
        elements.append(curr_table)
        elements.append(Spacer(1, 12))

        # Deduplicate forecast by day
        daily_forecast_dict = {}
        for entry in sorted(forecast, key=lambda e: e.get('dt') or 0):
            dt = entry.get('dt')
            if not dt:
                continue
            try:
                day_str = datetime.fromtimestamp(int(dt), timezone.utc).strftime('%Y-%m-%d')
            except Exception:
                continue
            daily_forecast_dict[day_str] = entry
        daily_forecast = list(daily_forecast_dict.values())

        if daily_forecast:
            elements.append(Paragraph("Forecast:", styles['Heading3']))
            forecast_table_data = [["Date", "Temp (°C)", "Feels Like", "Weather", "Pressure", "Humidity", "Wind Speed"]]
            for entry in daily_forecast:
                dt = entry.get('dt')
                try:
                    date_str = datetime.fromtimestamp(int(dt), timezone.utc).strftime('%Y-%m-%d') if dt else '-'
                except Exception:
                    date_str = '-'
                forecast_table_data.append([
                    date_str,
                    entry.get('temp', '-') ,
                    entry.get('feels_like', '-'),
                    entry.get('weather_main', '-'),
                    entry.get('pressure', '-'),
                    entry.get('humidity', '-'),
                    entry.get('wind_speed', '-')
                ])
            forecast_table = Table(forecast_table_data, hAlign='LEFT')
            forecast_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ]))
            elements.append(forecast_table)

    doc.build(elements)
    print(f"PDF report generated: {PDF_FILE}")

if __name__ == "__main__":
    main()
