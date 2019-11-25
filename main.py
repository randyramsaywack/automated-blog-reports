import csv
import fnmatch
from datetime import datetime
from ghost import *
from dotenv import load_dotenv
import os

# Call get_weather function to get weather from DarkSky API
get_weather()

# Store values returned from the get_weather() function
summary = get_weather()[0]
temp_high = get_weather()[1]
temp_low = get_weather()[2]

now = datetime.now()
convert_to_day = now.strftime('%A')
weekday_wildcard = ('*' + convert_to_day + '*')

def check_schedule():
    with open('schedule.txt') as schedule:
        readCSV = csv.reader(schedule, delimiter='.')
        for row in readCSV:
            if fnmatch.fnmatch(row[3], weekday_wildcard):
                create_post(row[1], row[4], row[5], summary, temp_high, temp_low)

check_schedule()
