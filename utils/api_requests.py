import httpx
import requests
from datetime import datetime, timedelta

def extract_results(data):
    utc_time = datetime.fromtimestamp(data['dt'])
    timezone_offset = timedelta(seconds=data['timezone'])
    local_time_month = (utc_time + timezone_offset).month
    if local_time_month in [3, 4, 5]:
        season = 'spring'
    elif local_time_month in [6, 7, 8]:
        season = 'summer'
    elif local_time_month in [9, 10, 11]:
        season = 'autumn'
    else:
        season = 'winter'

    return data['main']['temp'], season

url = "https://api.openweathermap.org/data/2.5/weather?q={}&appid={}&units=metric"
def curr_temperature_sync(api_key, city_name):
    request_url = url.format(city_name, api_key)
    response = requests.get(request_url)
    response.raise_for_status()
    data = response.json()
    return extract_results(data)

async def curr_temperature_async(api_key, city_name):
    request_url = url.format(city_name, api_key)
    async with httpx.AsyncClient() as client:
        response = await client.get(request_url)
        response.raise_for_status()
        data = response.json()
        return extract_results(data)
