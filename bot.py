import discord
from discord.ext import commands
from ytGateway import yt_search

# TODO: Move to a separate file
TOKEN = "OTA1NDk2NzMzMDE3MDU1MzIy.YYK7jA.gMwm60xlrtLscfh77_rPMeMZg0k"
GUILD_NAME = "MelodyTest"
FFMPEG_OPTIONS = {'before_options':
                  '-reconnect 1 '
                  '-reconnect_streamed 1 '
                  '-reconnect_delay_max 5',
                  'options': '-vn'}

bot = commands.Bot(command_prefix="!")


# @bot.command(name="test")
# async def test(ctx):
#     """Test command"""
#     await ctx.send("it worked!")


@bot.command(help="Have Melody join a voice channel")
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


@bot.command(aliases=["disconnect"], help="Have Melody leave a voice channel")
async def leave(ctx):
    """ Command to have bot leave a voice channel (if is currently in one) """
    if len(bot.voice_clients) == 0:
        await ctx.send("There are no channels for me to leave from!")
    else:
        # Assuming the bot will only every be in one voice channel at mo
        await bot.voice_clients[0].disconnect()


# TODO: Allowing play to play from urls
# TODO: Add error handling, e.g. checking if bot in a voice channel
@bot.command(aliases=["p"], help="Get Melody to play something")
async def play(ctx, *args):
    query = " ".join(args)
    channel = bot.voice_clients[0]
    query_results = yt_search(query)
    url = query_results["source"]
    channel.play(discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS))

    # TODO: Send something that looks less silly
    await ctx.send(f"Playing {query_results['title']} from "
                   f"https://www.youtube.com/watch?v={query_results['id']}")


bot.run(TOKEN)
