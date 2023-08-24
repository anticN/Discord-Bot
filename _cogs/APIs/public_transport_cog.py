import json
import requests
import datetime
import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime

url = "http://transport.opendata.ch/v1/"

class PublicTransportCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def write_stationboard(self, content):
        f = open("station.json", "w")
        f.write(content)
        f.close()
        return f

    def write_connection(self, content):
        f = open("connection.json", "w")
        f.write(content)
        f.close()
        return f

    def write_location(self, content):
        f = open("location.json", "w")
        f.write(content)
        f.close()
        return f

    def get_location(self, location):
        response = requests.get(f"{url}locations?query={location}")
        json_resp = json.dumps(response.json(), sort_keys=True, indent=5)
        self.write_location(json_resp)
        return response

    def get_station(self, station, limit):
        response = requests.get(f"{url}stationboard?station={station}&limit={limit}")
        json_resp = json.dumps(response.json(), sort_keys=True, indent=5)
        self.write_stationboard(json_resp)
        return response

    def get_connection(self, depart, arrive, date, time, via, limit):
        response = requests.get(f"{url}connections?from={depart}&to={arrive}&date={date}&limit=10")
        json_resp = json.dumps(response.json(), sort_keys=True, indent=5)
        self.write_connection(json_resp)
        return response


    "Station section"
    def category_number(self, resp, limit):
        categories = []
        numbers = []
        for i in range(limit):
            category = resp.json()["stationboard"][i]["category"]
            number = resp.json()["stationboard"][i]["number"]
            categories.append(category)
            numbers.append(number)
        return [categories, numbers]

    def direction(self, resp, limit):
        directions = []
        for i in range(limit):
            direction_to = resp.json()["stationboard"][i]["to"]
            directions.append(direction_to)
        return directions


    def depart(self, resp):
        departure = resp.json()["station"]["name"]
        return departure

    def depart_time(self, resp, limit):
        departure_times = []
        for i in range(limit):
            timestamp = resp.json()["stationboard"][i]["passList"][0]["departureTimestamp"]
            dep_time = datetime.fromtimestamp(timestamp).time()
            departure_times.append(dep_time)
        return departure_times

    def delay(self, resp, limit):
        delays = []
        for i in range(limit):
            delay = resp.json()["stationboard"][i]["passList"][0]["delay"]
            delays.append(delay)
        return delays




    "Location section"
    def all_locations(self, resp):
        locations = []
        for i in range(len(resp.json()["stations"])):
            location = resp.json()["stations"][i]["name"]
            locations.append(location)
        return locations


    "Connection section"
    def handle_connections(self, resp, limit):
        connections = []
        for i in range(len(resp.json()["connections"])):
            pass





    @app_commands.command(name="location", description="location")
    async def location(self, interaction: discord.Interaction, location: str):
        # shows you all the locations with that name
        resp = self.get_location(location.capitalize())
        embed = discord.Embed(title=f"All locations containing {location}", colour=discord.Colour.random())
        embed.set_thumbnail(
            url="https://www.netcetera.com/de/dam/jcr:e67e6b03-f939-4e6e-86db-666764de4315/wemlin-icon-bodytext.2017-02-15-13-53-49.png")
        for i in self.all_locations(resp):
            embed.add_field(
                name=f"{i}", value="", inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="station", description="All following departs from <station>")
    async def station(self, interaction: discord.Interaction, station: str, limit: int = int(5)):
        # shows you all the following departs from the station
        try:
            if limit <= 15:
                resp = self.get_station(station.capitalize(), limit)
                embed = discord.Embed(title=f"Departures from: {self.depart(resp)}", description=f"The next {limit} departures from now: {datetime.now().time().replace(microsecond=False)}", colour=discord.Colour.random())
                embed.set_thumbnail(url="https://www.netcetera.com/de/dam/jcr:e67e6b03-f939-4e6e-86db-666764de4315/wemlin-icon-bodytext.2017-02-15-13-53-49.png")
                for i in range(0, limit):
                    if self.delay(resp, limit)[i] > 0:
                        embed.add_field(
                            name=f"{self.category_number(resp, limit)[0][i]}{self.category_number(resp, limit)[1][i]} to {self.direction(resp, limit)[i]}",
                            value=f"at {self.depart_time(resp, limit)[i]}\t+{self.delay(resp, limit)[i]} min.", inline=False)
                    else:
                        embed.add_field(
                            name=f"{self.category_number(resp, limit)[0][i]}{self.category_number(resp, limit)[1][i]} to {self.direction(resp, limit)[i]}",
                            value=f"at {self.depart_time(resp, limit)[i]}", inline=False)
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message(f"The max. limit is 15")
        except Exception as e:
            await interaction.response.send_message(f"API not responding, try again")


    @app_commands.command(name="from-to", description="from-to-connection")
    @app_commands.describe(date="enter the date like yyyy-mm-dd", time="enter the time as hh:mm")
    async def connection(self, interaction: discord.Interaction, departure: str, arrival: str, date: str = str(datetime.now().date()), time: str = str(datetime.now().time()), via: str = None, limit: int = 5):
        # shows you all the connections from departure to arrival

        # Still in progress
        try:
            if limit <= 15:
                resp = self.get_connection(departure, arrival, date, time, via, limit)
                print(date)
                print(time)
                embed = discord.Embed(title=f"Connections from: {departure} to {arrival}", description=f"The next {limit} connections from: {date} {time}", colour=discord.Colour.random())
                embed.set_thumbnail(url="https://www.netcetera.com/de/dam/jcr:e67e6b03-f939-4e6e-86db-666764de4315/wemlin-icon-bodytext.2017-02-15-13-53-49.png")
                await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"API not responding, try again.")

    @app_commands.command(name="test-embed", description="sexy-embed")
    async def embed_test(self, interaction: discord.Interaction, member: discord.Member = None):
        if member is None:
            member = interaction.message.author

        embed = discord.Embed(title="this is a embed", description="Embed", colour=discord.Colour.random())
        embed.set_author(name=f"{member.display_name}")
        embed.set_thumbnail(url=f"{member.display_avatar}")
        embed.add_field(name="Test field 1", value="Random value 1")
        embed.add_field(name="Test field 2", value="Random value 2", inline=True)
        embed.add_field(name="Test field 3", value="Random value 3", inline=False)
        embed.set_footer(text=f"{member} made this")

        await interaction.response.send_message(embed=embed)
