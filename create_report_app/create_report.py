import json
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime
import os
import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.platypus import Image

DATA_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '../openweather_data.json'))
from datetime import datetime

PDF_FILE = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    f"../weather_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
))


from load_data import load_weather_data

def format_unix_time(ts, tz_offset=0):
    if not ts:
        return "-"
    return datetime.utcfromtimestamp(ts + tz_offset).strftime('%Y-%m-%d %H:%M')

def main():
    data = load_weather_data()
    doc = SimpleDocTemplate(PDF_FILE, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("<b>Weather Report</b>", styles['Title']))
    elements.append(Spacer(1, 18))

    for city, citydata in data.items():
        current = citydata.get('current', {})
        forecast = citydata.get('forecast', [])
        elements.append(Paragraph(f"<b>{city.capitalize()}</b>", styles['Heading2']))
        # Current weather table
        curr_table_data = [
            ["Temperature (°C)", current.get('main', {}).get('temp', '-')],
            ["Feels Like (°C)", current.get('main', {}).get('feels_like', '-')],
            ["Weather", current.get('weather', [{}])[0].get('main', '-')],
            ["Description", current.get('weather', [{}])[0].get('description', '-')],
            ["Pressure (hPa)", current.get('main', {}).get('pressure', '-')],
            ["Humidity (%)", current.get('main', {}).get('humidity', '-')],
            ["Wind Speed (m/s)", current.get('wind', {}).get('speed', '-')],
            ["Sunrise (UTC)", format_unix_time(current.get('sys', {}).get('sunrise'))],
            ["Sunset (UTC)", format_unix_time(current.get('sys', {}).get('sunset'))],
        ]
        curr_table = Table(curr_table_data, hAlign='LEFT')
        curr_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ]))
        elements.append(curr_table)
        elements.append(Spacer(1, 12))

        # Forecast table
        if forecast:
            elements.append(Paragraph("Forecast:", styles['Heading3']))
            forecast_data = [["Date", "Temp (°C)", "Feels Like", "Weather", "Pressure", "Humidity", "Wind Speed"]]
            dates = []
            temps = []
            for entry in forecast:
                dt = entry.get('dt')
                main = entry.get('main', {})
                weather = entry.get('weather', [{}])[0]
                forecast_data.append([
                    format_unix_time(dt),
                    main.get('temp', '-'),
                    main.get('feels_like', '-'),
                    weather.get('main', '-'),
                    main.get('pressure', '-'),
                    main.get('humidity', '-'),
                    entry.get('wind', {}).get('speed', '-')
                ])
                # Gather data for chart
                if dt and main.get('temp') is not None:
                    dates.append(datetime.utcfromtimestamp(dt))
                    temps.append(main.get('temp'))
            forecast_table = Table(forecast_data, hAlign='LEFT')
            forecast_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ]))
            elements.append(forecast_table)
            elements.append(Spacer(1, 12))

            # History section: one row per day
            elements.append(Paragraph("History (one entry per day):", styles['Heading3']))
            history_data = [["Date", "Temp (°C)", "Feels Like", "Weather", "Pressure", "Humidity", "Wind Speed"]]
            seen_days = set()
            for entry in sorted(forecast, key=lambda e: e.get('dt') or 0):
                dt = entry.get('dt')
                if not dt:
                    continue
                day_str = datetime.utcfromtimestamp(dt).strftime('%Y-%m-%d')
                if day_str in seen_days:
                    continue
                seen_days.add(day_str)
                main = entry.get('main', {})
                weather = entry.get('weather', [{}])[0]
                history_data.append([
                    day_str,
                    main.get('temp', '-'),
                    main.get('feels_like', '-'),
                    weather.get('main', '-'),
                    main.get('pressure', '-'),
                    main.get('humidity', '-'),
                    entry.get('wind', {}).get('speed', '-')
                ])
            history_table = Table(history_data, hAlign='LEFT')
            history_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgreen),
                ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ]))
            elements.append(history_table)
            elements.append(Spacer(1, 12))

            # Add chart
            if dates and temps:
                plt.figure(figsize=(4,2))
                plt.plot(dates, temps, marker='o')
                plt.title(f"Temperature Forecast for {city.capitalize()}")
                plt.xlabel("Date")
                plt.ylabel("Temperature (°C)")
                plt.grid(True)
                plt.tight_layout()
                buf = BytesIO()
                plt.savefig(buf, format='png')
                plt.close()
                buf.seek(0)
                img = Image(buf, width=300, height=150)
                elements.append(img)
                elements.append(Spacer(1, 18))
        else:
            elements.append(Paragraph("No forecast data available.", styles['Normal']))
            elements.append(Spacer(1, 18))

    doc.build(elements)
    print(f"PDF report generated: {PDF_FILE}")

if __name__ == "__main__":
    main()
