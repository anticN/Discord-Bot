import discord
from discord.ext import commands


class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # sends the help message
        self.help_message = """
```
General commands:
§help - displays all the available commands for users
$admin - displays all the admin and dev only commands
§p - Play the selected song from youtube
§q - Displays all the songs currently in the queue
§skip - Skips the currently played song
§clear - Stops the current song and clears the queue
§leave - Kick the bot from the voice channel
§pause - pauses the current song being played
§resume - Resumes playing the current song
§roll <amount of dice> <sides per dice> - Roll a dice
§spam <amount> <spam message> - spams a message 
§newSeries [§ns] <name of series (if more than 1 word use "")> <episode> - adds a new series to the user 
§mySeries [§myS, §mys] - shows all the series from a user
§updateSeries [§us] <name of series (use the same spelling you used for §ns)> <new episode> - updates a series to the users current episode
§deleteSeries [§ds] <name of series> - deletes a series from a user

Slash commands:
/dm <user> <message> - The bot sends a message to a user
/move <@user> <voice channel> - moves the pinged user to another voice channel
/create-vc <name> - creates a new voice channel
/create-txtc <name> - creates a new text channel
/delete-vc <name> - deletes a voice channel
/delete-txtc <name> - deletes a text channel
/ns - still in development
/current-weather-in <city> - shows the current weather from a city
/weekly-predict-for <city> - shows the weekly weather predict for a city
/cities - shows the list of cities you can use for the weather
/my-reports - returns the amount of reports an user has
/russian-roulette <number between 1-10> - bot generates a random number and if users and bots number are the same, the user will be kicked
/my-score - shows the users current score in /russian-roulette
/my-highscore - shows the users current highscore in /russian-roulette
/all-scores - shows all scores from the server
/all-highscores - shows all highscores from the server
/invite-link - sends the invite link for the bot
```                
"""
        self.text_channel_text = []
        self.admin_help = """
```
Admin (permissions: administrator) & {Dev} -only Commands:
§ping - pings all members from the server

Slash Commands:
{/servers} - shows all the servers the bot is in

/report <user> <amount> - reports a user, amount 1-4, when user has 4 reports, he will be kicked and if he was already
kicked he will be banned

/delete-report <user> <amount> - deletes an amount of reports from a user

/all-server-reports - returns all users who have reports

```
"""

    @commands.Cog.listener()
    async def on_read(self):
        for guild in self.bot.guilds:
            for channel in guild.text_channels:
                self.text_channel_text.append(channel)

        await self.send_to_all(self.help_message)

    async def send_to_all(self, msg):
        for text_channel in self.text_channel_text:
            await text_channel.send(msg)

    @commands.command(name='help', help='Displays all the available commands')
    async def help(self, ctx):
        await ctx.send(self.help_message)

    @commands.command(name="admin", help="Displays all the admin and dev only commands")
    @commands.has_permissions(administrator=True)
    async def admin(self, ctx):
        await ctx.send(self.admin_help)
