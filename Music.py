import discord
from discord.ext import commands
from ytGateway import yt_search


class Music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.FFMPEG_OPTIONS = {'before_options':
                               '-reconnect 1 '
                               '-reconnect_streamed 1 '
                               '-reconnect_delay_max 5',
                               'options': '-vn'}
        self.queue = []

    def bot_in_vc(self):
        return len(self.bot.voice_clients) > 0

    @commands.command(help="Have Melody join a voice channel")
    async def join(self, ctx):
        """Command to have bot join the voice channel that the user is in"""
        if self.bot_in_vc():
            # Indicates bot is already in a voice channel
            await ctx.send("This bot is already in use!")
        elif ctx.author.voice is not None:
            # Making sure that the user themself is in a voice channel
            channel = ctx.author.voice.channel
            await channel.connect()
        else:
            await ctx.send("Please join one of the voice channels first!")

    @commands.command(aliases=["disconnect"],
                      help="Have Melody leave a voice channel")
    async def leave(self, ctx):
        """ Command to have bot leave a voice channel"""
        if not self.bot_in_vc():
            await ctx.send("There are no channels for me to leave from!")
        else:
            # Assuming the bot will only every be in one voice channel at mo
            await self.bot.voice_clients[0].disconnect()

    @commands.command(aliases=["p"], help="Get Melody to play something")
    async def play(self, ctx, *args):
        """Command to play something in a voice channel"""

        if not self.bot_in_vc():
            # If the bot is not in any voice channels,
            # it joins the appropriate one
            await self.join(ctx)

        channel = self.bot.voice_clients[0]

        if channel.is_paused():
            await self.resume(ctx)
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
        channel.play(discord.FFmpegPCMAudio(url, **self.FFMPEG_OPTIONS))

        # TODO: Have a better message
        # url above is a bit funky so we manually create the youtube link
        await ctx.send(f"Playing {query_results['title']}: "
                       f"https://www.youtube.com/watch?v={query_results['id']}")

    @commands.command(help="Pause whatever Melody is playing")
    async def pause(self, ctx):
        """Command to pause what is playing"""
        if not self.bot_in_vc():
            await ctx.send("I don't think I was playing anything, "
                           "but I'll stop anyway :persevere:")
            return

        channel = self.bot.voice_clients[0]
        channel.pause()
        # TODO: Have a better message?
        await ctx.send("Playing paused")

    @commands.command(help="Have Melody resume playing")
    async def resume(self, ctx):
        """Command to resume playing"""
        if not self.bot_in_vc():
            await ctx.send("Um I don't think I am in a vc? "
                           "But um I guess I will continue playing silence")
            return

        channel = self.bot.voice_clients[0]

        channel.resume()
        await ctx.send("Playing resumed")
