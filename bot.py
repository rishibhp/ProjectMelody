from discord.ext import commands
from Music import Music
from dotenv import load_dotenv
import os

load_dotenv("token.env")
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix="!")

bot.add_cog(Music(bot))

bot.run(DISCORD_TOKEN)
