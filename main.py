import os
import requests
import jwt
import json
import csv
import fnmatch
import logging
from datetime import datetime
from dotenv import load_dotenv
from darksky.api import DarkSky

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
    title = 'You have ' + class_name + ' today.'
    body = {"posts": [{"title": "", "status": "published", "html": ""}]}
    body["posts"][0]["html"] = post
    body["posts"][0]["title"] = title
    r = requests.post(url, json=body, headers=headers)
    if str(r) == '<Response [201]>':
      logging.info("Successfully created post!")
    else:
      logging.info("Failed with error " + str(r))

# Funcation get_weather authenticates and gets weather based on latitude and longitude define in .env
def get_weather():
    darksky = DarkSky(os.getenv("DARK_SKY_API"))
    forecast = darksky.get_forecast(os.getenv("DARK_SKY_LAT"), os.getenv("DARK_SKY_LONG"))
    todays_forecast = forecast.daily.data[0]
    summary = todays_forecast.summary
    temp_high = str(round(todays_forecast.temperature_high))
    temp_low = str(round(todays_forecast.temperature_low))
    return summary, temp_high, temp_low

# Call get_weather function to get weather from DarkSky API
get_weather()

# Store values returned from the get_weather() function
summary = get_weather()[0]
temp_high = get_weather()[1]
temp_low = get_weather()[2]

now = datetime.now()
convert_to_day = now.strftime('%A')
weekday_wildcard = ('*' + convert_to_day + '*')

# Function check_schedule checks the schedule text file for match and creates a post if a match is found.
def check_schedule():
    with open('schedule.txt') as schedule:
        readCSV = csv.reader(schedule, delimiter='.')
        for row in readCSV:
            if fnmatch.fnmatch(row[3], weekday_wildcard):
                create_post(row[1], row[4], row[5], summary, temp_high, temp_low)

# Call the check_schedule() function to begin execution
check_schedule()
