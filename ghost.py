import requests
import jwt
from datetime import datetime
import json
from darksky.api import DarkSky
from darksky.types import weather
from dotenv import load_dotenv
import os
import logging

# Setup logging config
logging.basicConfig(filename='post_log.log', level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Load Environmental Variables from '.env' file
load_dotenv()

# Ghost Admin API key
key = os.getenv("GHOST_API_KEY")

# Split the key into ID and SECRET
id, secret = key.split(':')

# Prepare header and payload
iat = int(datetime.now().timestamp())

header = {'alg': 'HS256', 'typ': 'JWT', 'kid': id}
payload = {
    'iat': iat,
    'exp': iat + 5 * 60,
    'aud': '/v3/admin/'
}

# Create the token
token = jwt.encode(payload, bytes.fromhex(secret), algorithm='HS256', headers=header)

# Function create_post authenticates, authorizes and the create post on Ghost Blog
def create_post(class_name, time, room, summary, temp_high, temp_low):
    url = '{}/ghost/api/v3/admin/posts/?source=html'.format(os.getenv("GHOST_DOMAIN"))
    headers = {'Authorization': 'Ghost {}'.format(token.decode())}
    post = 'Class: {}<br/>Time: {}<br/>Room: {}<br/>Weather: {}<br/>Temp High: {} \u2109<br/>Temp Low: {} \u2109'.format(class_name, time, room, summary, temp_high, temp_low)
    now = datetime.now()
    convert_to_day = now.strftime('%m/%d/%Y %I:%M %p')
    title = 'You have ' + class_name + ' today.'
    body = {"posts": [{"title": "", "status": "published", "html": ""}]}
    body["posts"][0]["html"] = post
    body["posts"][0]["title"] = title
    r = requests.post(url, json=body, headers=headers)
    if str(r) == '<Response [201]>':
      logging.info("Successfully created post!")
    else:
      logging.info("Failed with error " + str(r))

# Location using Lat/Long
DARKSKY_API_KEY = os.getenv("DARK_SKY_API")
latitude = os.getenv("DARK_SKY_LAT")
longitude = os.getenv("DARK_SKY_LONG")

def get_weather():
    darksky = DarkSky(DARKSKY_API_KEY)
    forecast = darksky.get_forecast(latitude, longitude)
    todays_forecast = forecast.daily.data[0]
    summary = todays_forecast.summary
    temp_high = str(round(todays_forecast.temperature_high))
    temp_low = str(round(todays_forecast.temperature_low))
    return summary, temp_high, temp_low
