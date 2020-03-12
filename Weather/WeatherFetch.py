import configparser
import json
import urllib.parse
import requests
import os
from datetime import datetime, timedelta, timezone, time
import pytz
from Config import Secret, Config

pst_tz = pytz.timezone('US/Pacific')

# number of days after now to get the forecast for (1 gets today's and tomorrow's forecast) - MAX 7
FORECAST_DAYS = 7

class WeatherParser():

    def __init__(self, db_instance):
        config = configparser.ConfigParser()
        config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))
        self.db = db_instance

    def update_weather(self):
        # datetime of last weather entry could be greater than now due to forecasts
        last_dt = self.db.get_last_weather_dt()  
        now_dt = datetime.now(tz=pst_tz)
        # the forecast should refresh, so, at most, start at now
        start_dt = now_dt
        if last_dt is not None:
            start_dt = min(last_dt, now_dt)

        end_dt = now_dt + timedelta(days=FORECAST_DAYS)
        self.store_weather_between_dates(start_dt, end_dt)

    # store the weather from the start_date to end_date (start_date & end_date are inclusive)
    def store_weather_between_dates(self, start_dt, end_dt):
        start_date = self.to_start_of_day(start_dt)
        end_date = self.to_start_of_day(end_dt)
        cur_date = start_date
        while cur_date <= end_date:
            self.store_weather_for_date(cur_date)
            cur_date += timedelta(days=1)
            print("GOT WEATHER: ", cur_date)

    # get and then store hourly weather in database
    def store_weather_for_date(self, dt):
        json_data = self.get_weather_for_date(dt)
        for hour_data in json_data["hourly"]["data"]:
            dt = datetime.fromtimestamp(hour_data["time"], pst_tz)
            feels_like_f = hour_data["apparentTemperature"]
            precip_intensity = 0
            if "precipIntensity" in hour_data:
                precip_intensity = hour_data["precipIntensity"]
            self.db.insert_weather(dt, feels_like_f, precip_intensity)

    # request weather for each hour of the date (max of 24 hours)
    def get_weather_for_date(self, dt):
        epochTime = str(int(dt.timestamp()))
        params = {
            "exclude": "currently,minutely,daily,alerts,flags"
        }
        headers = {
            "accept": "application/json"
        }
        get_url = "https://api.darksky.net/forecast/" + Secret.darksky_secret+ "/" + Config.loc_latitude + "," + Config.loc_longitude + "," + epochTime
        response = requests.get(get_url, params, headers=headers)
        jsonData = json.loads(response.text)
        return jsonData

    def to_start_of_day(self, dt):
        return datetime.combine(dt, time())
        