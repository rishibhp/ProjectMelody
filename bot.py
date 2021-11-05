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
    if bot_in_vc():
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
    if not bot_in_vc():
        await ctx.send("There are no channels for me to leave from!")
    else:
        # Assuming the bot will only every be in one voice channel at mo
        await bot.voice_clients[0].disconnect()


def bot_in_vc():
    return len(bot.voice_clients) > 0


@bot.command(aliases=["p"], help="Get Melody to play something")
async def play(ctx, *args):
    """Command to play something in a voice channel"""

    if not bot_in_vc():
        # If the bot is not in any voice channels, it joins the appropriate one
        await join(ctx)

    channel = bot.voice_clients[0]

    if channel.is_paused():
        await resume(ctx)
        return

    if len(args) == 0:
        # If no arguments provided, we don't know what to play
        await ctx.send("I don't know what to play :confounded:")
        return

    query = " ".join(args)
    query_results = yt_search(query)

    if query_results is None:
        # Make sure search actually returned something
        await ctx.send("Sorry, I couldn't find anything >_<")
        return

    url = query_results["source"]
    channel.play(discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS))

    # TODO: Have a better message
    # url above is a bit funky so we manually create the youtube link
    await ctx.send(f"Playing {query_results['title']}: "
                   f"https://www.youtube.com/watch?v={query_results['id']}")


@bot.command(help="Pause whatever Melody is playing")
async def pause(ctx):
    """Command to pause what is playing"""
    if not bot_in_vc():
        await ctx.send("I don't think I was playing anything, "
                       "but I'll stop anyway :persevere:")
        return

    channel = bot.voice_clients[0]
    channel.pause()
    # TODO: Have a better message?
    await ctx.send("Playing paused")


@bot.command(help="Have Melody resume playing")
async def resume(ctx):
    """Command to resume playing"""
    if not bot_in_vc():
        await ctx.send("Um I don't think I am in a vc? "
                       "But um I guess I will continue playing silence")
        return

    channel = bot.voice_clients[0]

    channel.resume()
    await ctx.send("Playing resumed")

bot.run(TOKEN)
