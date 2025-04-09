API_KEY = 'cd599e348f1146e9ba9621fb7322bbbe'

city = 'Portland,US-OR'

current_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=imperial&appid={API_KEY}"
current_response = requests.get(current_url)

if current_response.status_code == 200:
    current_data = current_response.json()
    lat = current_data['coord']['lat']
    lon = current_data['coord']['lon']
    
    forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units=imperial&appid={API_KEY}"
    forecast_response = requests.get(forecast_url)
    
    if forecast_response.status_code == 200:
        forecast_data = forecast_response.json()
        
        current_time = datetime.now().strftime("%A, %B %d, %Y %I:%M %p")
        print(f"\nCurrent Time: {current_time}")
        
        print(f"\nCurrent Weather for {current_data['name']}, {current_data['sys']['country']}")
        print(f"----------------------------------------")
        print(f"Weather: {current_data['weather'][0]['main']} - {current_data['weather'][0]['description']}")
        print(f"Temperature: {current_data['main']['temp']}°F")
        print(f"Humidity: {current_data['main']['humidity']}%")
        
        print(f"\n3-Day Forecast:")
        print(f"----------------------------------------")
        
        days = {}
        for item in forecast_data['list']:
            date = datetime.fromtimestamp(item['dt']).strftime("%Y-%m-%d")
            
            if date not in days:
                days[date] = {
                    'temp_max': item['main']['temp_max'],
                    'temp_min': item['main']['temp_min'],
                    'humidity': item['main']['humidity'],
                    'weather': item['weather'][0]
                }
            else:
                days[date]['temp_max'] = max(days[date]['temp_max'], item['main']['temp_max'])
                days[date]['temp_min'] = min(days[date]['temp_min'], item['main']['temp_min'])
        
        count = 0
        today = datetime.now().strftime("%Y-%m-%d")
        for date in sorted(days.keys()):
            if date > today and count < 3: 
                day_data = days[date]
                display_date = datetime.strptime(date, "%Y-%m-%d").strftime("%A, %B %d")
                print(f"\n{display_date}")
                print(f"Weather: {day_data['weather']['main']} - {day_data['weather']['description']}")
                print(f"High: {day_data['temp_max']}°F, Low: {day_data['temp_min']}°F")
                print(f"Humidity: {day_data['humidity']}%")
                count += 1
    else:
        print(f"Error fetching forecast data. Status code: {forecast_response.status_code}")
else:
    print(f"Error fetching weather data. Status code: {current_response.status_code}")
    print(f"Response: {current_response.text}")