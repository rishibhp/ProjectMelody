import discord
from discord.ext import commands

# TODO: Move to a separate file
TOKEN = "OTA1NDk2NzMzMDE3MDU1MzIy.YYK7jA.gMwm60xlrtLscfh77_rPMeMZg0k"
GUILD_NAME = "MelodyTest"

bot = commands.Bot(command_prefix="!")

@bot.command(name="test")
async def test(ctx):
    await ctx.send("it worked!")

# TODO: py -3 -m pip install -U discord.py[voice]
@bot.command()
async def join(ctx):
    # TODO: handle cases where the bot is already connected to another voice channel and other user attempts to 
    # make the bot join (should send a message saying "This bot is already in use!")
    try:
        channel = ctx.author.voice.channel
        await channel.connect()
    except Exception:
        await ctx.send("Please join one of the voice channels first!")

# :)
# @bot.command()
# async def rick(ctx):
#     await ctx.send("https://tenor.com/view/rickroll-roll-rick-never-gonna-give-you-up-never-gonna-gif-22954713")

bot.run(TOKEN)
