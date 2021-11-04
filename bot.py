import discord
from discord.ext import commands

# TODO: Move to a separate file
TOKEN = "OTA1NDk2NzMzMDE3MDU1MzIy.YYK7jA.gMwm60xlrtLscfh77_rPMeMZg0k"
GUILD_NAME = "MelodyTest"

bot = commands.Bot(command_prefix="!")


@bot.command(name="test")
async def test(ctx):
    """Test command"""
    await ctx.send("it worked!")


@bot.command()
async def join(ctx):
    """Command to have bot join the voice channel that the user is in"""
    if len(bot.voice_clients) > 0:
        # Indicates bot is already in a voice channel
        await ctx.send("This bot is already in use!")
    elif ctx.author.voice is not None:
        # Making sure that the user themself is in a voice channel
        channel = ctx.author.voice.channel
        await channel.connect()
    else:
        await ctx.send("Please join one of the voice channels first!")


@bot.command()
async def leave(ctx):
    """ Command to have bot leave a voice channel (if is currently in one) """
    if len(bot.voice_clients) == 0:
        await ctx.send("There are no channels for me to leave from!")
    else:
        # Assuming the bot will only every be in one voice channel at mo
        await bot.voice_clients[0].disconnect()


# :)
# @bot.command()
# async def rick(ctx):
#     await ctx.send(
#     "https://tenor.com/view/rickroll-roll-rick-never-gonna-give-you-up-never-gonna-gif-22954713")


bot.run(TOKEN)
