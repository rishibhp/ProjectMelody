import discord
from discord.ext import commands

# TODO: Move to a separate file
TOKEN = "OTA1NDk2NzMzMDE3MDU1MzIy.YYK7jA.gMwm60xlrtLscfh77_rPMeMZg0k"
GUILD_NAME = "MelodyTest"

bot = commands.Bot(command_prefix="!")


@bot.command(name="test")
async def test(ctx):
    await ctx.send("it worked!")


bot.run(TOKEN)
