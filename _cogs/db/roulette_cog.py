import discord
import pymongo
import random
import time
from discord.ext import commands
from discord import app_commands


# Connect to the MongoDB, change the connection string per your MongoDB environment
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["discBot"]
roulette = db["roulette"]


class RouletteCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.char = None

    def first_insert(self, user_id, username, server_id, server):
        insert = {
            "user_id": user_id,
            "user": username,
            "server_id": server_id,
            "server": server,
            "wins": 1,
            "highscore": 1
            }
        roulette.insert_one(insert)

    def update_roulette(self, user_id, server_id):
        update = {"user_id": user_id, "server_id": server_id}
        updated_wins = self.current_wins(user_id, server_id)
        wins_query = {"$set": {"wins": updated_wins + 1}}
        roulette.update_one(update, wins_query)
        if updated_wins >= self.current_highscore(user_id, server_id):
            updated_highscore = self.current_highscore(user_id, server_id)
            highscore_query = {"$set": {"highscore": updated_highscore + 1}}
            roulette.update_one(update, highscore_query)

    def current_wins(self, user_id, server_id):
        query = {"user_id": user_id, "server_id": server_id}
        if roulette.count_documents(query) > 0:
            current_wins = roulette.find_one(query).get("wins")
            return current_wins
        else:
            return 0

    def current_highscore(self, user_id, server_id):
        query = {"user_id": user_id, "server_id": server_id}
        if roulette.count_documents(query) is None:
            return 0
        else:
            current_highscore = roulette.find_one(query).get("highscore")
            return current_highscore

    def reset_wins(self, user_id, server_id):
        query = {"user_id": user_id, "server_id": server_id}
        reset = {"$set": {"wins": 0}}
        roulette.update_one(query, reset)

    def insert_or_update(self, user_id, username, server_id, server):
        search = {"user_id": user_id, "server_id": server_id}
        if roulette.count_documents(search) > 0:
            self.update_roulette(user_id, server_id)
        else:
            self.first_insert(user_id, username, server_id, server)

    def get_server_scores(self, server_id):
        result = []
        self.char = "s"
        for x in roulette.find({"server_id": server_id}, {"_id": 0, "highscore": 0, "server_id": 0, "user_id": 0, "server": 0}).sort("wins", -1):
            result.append(x)
        return self.list_to_str_formater(result, self.char)

    def get_server_highscores(self, server_id):
        result = []
        self.char = "h"
        for x in roulette.find({"server_id": server_id}, {"_id": 0, "wins": 0, "server_id": 0, "user_id": 0, "server": 0}).sort("highscore", -1):
            result.append(x)
        return self.list_to_str_formater(result, self.char)

    def list_to_str_formater(self, array, checker):
        result_str = str(array)
        test = result_str.replace(":", "")
        test2 = test.replace("user", "")
        if checker == "s":
            test3 = test2.replace("wins", "")
        else:
            test3 = test2.replace("highscore", "")
        test4 = test3.replace("'", "")
        test5 = test4.replace("[", "")
        test6 = test5.replace("]", "")
        test7 = test6.replace("{", "")
        test8 = test7.replace("}", "\n")
        test9 = test8.replace(",", "")
        return test9

    @app_commands.command(name="russian-roulette", description="The user has a 6% chance of being kicked")
    async def russian_roulette(self, interaction: discord.Interaction, number: int):
        # Russian roulette, the bot generates a random number and if the user and the bot have the same number, the user will be kicked.
        # The scores and highscores are saved in a database.
        if 0 < number <= 10:
            user_id = interaction.user.id
            username = interaction.user.name
            server_id = interaction.guild.id
            server = interaction.guild.name
            random_number = random.choice(range(1, 11))
            if random_number == number:
                await interaction.response.send_message(
                    f"My number was **{random_number}** and your number was **{number}**"
                    f"\nYou lost, Bye Bye.😘")
                self.reset_wins(user_id, server_id)
                time.sleep(2.5)
                await interaction.guild.kick(interaction.user)
                link = await interaction.channel.create_invite(max_age=300)
                try:
                    #  need to check if he can send another message (except)
                    await interaction.user.send(f"You lost in Russian Roulette but here is the link to come back."
                                                f"\n{link}")
                except Exception as e:
                    await interaction.response.send_message(e)
            else:
                self.insert_or_update(user_id, username, server_id, server)
                await interaction.response.send_message(
                    f"My number was **{random_number}** and your number was **{number}** \nYou were lucky this time.")
        else:
            await interaction.response.send_message(f"You can only type entire numbers between 1-10")

    @app_commands.command(name="my-score", description="shows the current wins from the user in russian-roulette")
    async def my_score(self, interaction: discord.Interaction):
        # shows the current wins from the user in russian-roulette
        user_id = interaction.user.id
        server_id = interaction.guild.id
        await interaction.response.send_message(f"Your current score in russian roulette is: {self.current_wins(user_id, server_id)}")

    @app_commands.command(name="my-highscore", description="shows the users current highscore in russian-roulette")
    async def my_highscore(self, interaction: discord.Interaction):
        # shows the users current highscore in russian-roulette
        user_id = interaction.user.id
        server_id = interaction.guild.id
        await interaction.response.send_message(f"Your current highscore in russian roulette is: {self.current_highscore(user_id, server_id)}")

    @app_commands.command(name="all-scores", description="shows the current scores of all users in russian-roulette")
    async def all_scores(self, interaction: discord.Interaction):
        # shows the current scores of all users in russian-roulette
        server_id = interaction.guild.id
        if roulette.count_documents({"server_id": server_id}) != 0:
            await interaction.response.send_message(f"Current scores in russian roulette:\n {self.get_server_scores(server_id)}")
        else:
            await interaction.response.send_message(f"There are no scores in this server")

    @app_commands.command(name="all-highscores", description="shows the current highscores of all users in russian-roulette")
    async def all_highscores(self, interaction: discord.Interaction):
        # shows the current highscores of all users in russian-roulette
        server_id = interaction.guild.id
        if roulette.count_documents({"server_id": server_id}) != 0:
            await interaction.response.send_message(f"Current highscores in russian roulette:\n {self.get_server_highscores(server_id)}")
        else:
            await interaction.response.send_message(f"There are no highscores in this server")
