import json
import requests
import datetime
import pymongo
import discord
from discord.ext import commands
from discord import app_commands
from prettytable import PrettyTable


towns = {
            "zurich": [47.37, 8.55],
            "friesenberg": [47.36, 8.50],
            "dietikon": [47.40, 8.40],
            "altstetten": [47.39, 8.49],
            "uster": [47.35, 8.72],
            "greifensee": [47.37, 8.68],
            "belgrade": [44.80, 20.47],
            "virine": [44.03, 21.42],
            "berlin": [52.52, 13.41],
            "rome": [41.89, 12.51],
            "moscow": [55.75, 37.62],
            "zagreb": [45.81, 15.98]}


class WeatherCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def write_file(self, content):
        f = open("message.json", "w")
        f.write(content)
        f.close()
        return f

    def get_hour(self):
        now = datetime.datetime.now()
        return now.hour

    def check_day(self):
        day = datetime.datetime.now().weekday()
        return day

    def order_days(self):
        days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
        today = 0
        while today < self.check_day():
            days.append(days[0])
            days.pop(0)
            today += 1
        return days

    def get_request(self, lat, long):
        response = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={long}&hourly=temperature_2m,rain,snowfall&daily=temperature_2m_max,temperature_2m_min,rain_sum,snowfall_sum&timezone=Europe%2FBerlin")
        json_resp = json.dumps(response.json(), sort_keys=True, indent=4)
        self.write_file(json_resp)
        return response

    def get_current_temp(self, resp):
        rain = resp.json()["hourly"]["rain"][self.get_hour()]
        temp = resp.json()["hourly"]["temperature_2m"][self.get_hour()]
        snow = resp.json()["hourly"]["snowfall"][self.get_hour()]
        time = resp.json()["hourly_units"]["time"]
        rtt = [rain, temp, snow, time]
        return rtt

    def get_weekly_min(self, resp):
        minimum = resp.json()["daily"]["temperature_2m_min"]
        return minimum

    def get_weekly_max(self, resp):
        maximum = resp.json()["daily"]["temperature_2m_max"]
        return maximum

    def get_weekly_rain(self, resp):
        rain = resp.json()["daily"]["rain_sum"]
        return rain

    def get_weekly_snow(self, resp):
        snow = resp.json()["daily"]["snowfall_sum"]
        return snow


    @app_commands.command(name="cities", description="shows you all the cities you can use for the weather")
    async def show_cities(self, interaction: discord.Interaction):
        # shows you all the cities you can use for the weather
        test = str(towns.keys()).replace("dict_keys", "")
        test1 = test.replace("([", "")
        test2 = test1.replace("])", "")
        test3 = test2.replace("'", "")
        test4 = test3.replace(",", "\n")
        await interaction.response.send_message(f"All cities for the weather commands:"
                                                f"\n {test4}")

    @app_commands.command(name="current-weather-in", description="returns the current temperature in °C (from Zurich)")
    @app_commands.describe(city="the city for which you want to know the current temperature")
    async def current_weather(self, interaction: discord.Interaction, city: str):
        # returns the current temperature, rain and snow with a pretty table
        if city.lower() in towns.keys():
            coords = towns.get(city)
            response = self.get_request(coords[0], coords[1])
            x = PrettyTable()
            x.field_names = ["Unit", "Amount"]
            x.add_row(["temperature:", f"{self.get_current_temp(response)[1]}°C"])
            x.add_row(["rain:", f"{self.get_current_temp(response)[0]}mm"])
            x.add_row(["snow:", f"{self.get_current_temp(response)[2]}cm"])
            message = f"""
```
Current Weather in {city.capitalize()}:
{x}
```
        """
            await interaction.response.send_message(message)
        else:
            await interaction.response.send_message(f"{city} wasn't found! Try another city or with different spelling."
                                                    f"\nTo see my list of cities write /cities")

    @app_commands.command(name="weekly-predict-for", description="shows the weather for the following week")
    @app_commands.describe(city="the city for which you want to see the weather prediction")
    async def weekly_weather(self, interaction: discord.Interaction, city: str):
        # shows the weather for the following week in a pretty table
        if city.lower() in towns.keys():
            coords = towns.get(city)
            response = self.get_request(coords[0], coords[1])
            weekly_max = self.get_weekly_max(response)
            weekly_min = self.get_weekly_min(response)
            weekly_rain = self.get_weekly_rain(response)
            weekly_snow = self.get_weekly_snow(response)
            correct_days = self.order_days()
            x = PrettyTable()
            x.field_names = ["Units", correct_days[0], correct_days[1], correct_days[2], correct_days[3], correct_days[4], correct_days[5], correct_days[6]]
            x.add_row(["max °C", weekly_max[0], weekly_max[1], weekly_max[2], weekly_max[3], weekly_max[4], weekly_max[5], weekly_max[6]])
            x.add_row(["min °C", weekly_min[0], weekly_min[1], weekly_min[2], weekly_min[3], weekly_min[4], weekly_min[5], weekly_min[6]])
            x.add_row(["rain mm", weekly_rain[0], weekly_rain[1], weekly_rain[2], weekly_rain[3], weekly_rain[4], weekly_rain[5], weekly_rain[6]])
            x.add_row(["snow cm", weekly_snow[0], weekly_snow[1], weekly_snow[2], weekly_snow[3], weekly_snow[4], weekly_snow[5], weekly_snow[6]])
            message = f"""
```
Weather in {city.capitalize()} for the next 7 days:
{x}
```
"""
            await interaction.response.send_message(message)
        else:
            await interaction.response.send_message(f"{city} wasn't found! Try another city or with different spelling."
                                                    f"\nTo see my list of cities write /cities")

