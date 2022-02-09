"""To run this file manually, type
py -3 bot.py
into the terminal.
"""
import discord
from discord.ext import commands
from Music import Music
from dotenv import load_dotenv
import os

load_dotenv("token.env")
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix="?")
bot.add_cog(Music(bot))

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game("currently on beta stage!"))
bot.run(DISCORD_TOKEN)
