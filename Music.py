from typing import List, Tuple

import discord
from discord.ext import commands
from ytGateway import yt_search

import asyncio
import random

REPLY_COLOR = discord.Color.dark_blue()
LEAVE_MESSAGES = ["Adios amigos :wave:",
                  "Hasta la vista :spy:",
                  "Bye :wave:",
                  "See you later!"]


def playing_message(vid_title: str, vid_url: str, requester_name: str) \
        -> discord.Embed:
    """
    This method returns the message to be sent when a track is being played
    :param vid_title: (YouTube) title of track
    :param vid_url: Url of track
    :param requester_name: Discord (nick)name of requester
    :return: discord.Embed object representing the return message
    """
    message = f"**Now Playing**\n {vid_url} [{requester_name}]"
    embed = discord.Embed(url=vid_url,
                          description=message,
                          title=vid_title,
                          color=REPLY_COLOR)
    return embed


def queue_message(vid_title: str, vid_url: str, requester_name: str) \
        -> discord.Embed:
    """
    This method returns the message to be sent when a track is queued
    :param vid_title: (YouTube) title of track
    :param vid_url: Url of track
    :param requester_name: Discord (nick)name of requester
    :return: discord.Embed object representing the return message
    """
    message = f"**Added to queue**\n {vid_url} [{requester_name}]"
    embed = discord.Embed(url=vid_url,
                          description=message,
                          title=vid_title,
                          color=REPLY_COLOR)
    return embed


class Music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.FFMPEG_OPTIONS = {'before_options':
                               '-reconnect 1 '
                               '-reconnect_streamed 1 '
                               '-reconnect_delay_max 5',
                               'options': '-vn'}

        # Each element in self.playing_queue is a tuple of 4 objects:
        # 0. discord.FFmpegPCMAudio object for the audio itself
        # 1. String object for the video title
        # 2. String object for the video url
        # 3. String object for the requester's nickname
        self.playing_queue = []

    def bot_in_vc(self):
        return len(self.bot.voice_clients) > 0

    @commands.command(help="Have Melody join a voice channel")
    async def join(self, ctx: commands.Context) -> None:
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
    async def leave(self, ctx: commands.Context) -> None:
        """ Command to have bot leave a voice channel"""
        if not self.bot_in_vc():
            await ctx.send("There are no channels for me to leave from!")
        else:
            # Assuming the bot will only every be in one voice channel at most
            await ctx.send(random.choice(LEAVE_MESSAGES))
            await self.bot.voice_clients[0].disconnect()

    @commands.command(aliases=["q"], help="Add a track to the queue")
    async def queue(self, ctx: commands.Context, *args: str) -> None:
        """ Command to add items to the queue """
        # TODO: Add functionality to view the queue
        # Currently we instantly download that is added to queue.
        # Can likely be made more efficient
        self.download_audio(args, ctx.author.display_name)
        await ctx.send(embed=queue_message(*self.playing_queue[-1][-3:]))

    @commands.command(aliases=["p"], help="Get Melody to play something")
    async def play(self, ctx: commands.Context, *args: str) -> None:
        """Command to play something in a voice client"""

        if not self.bot_in_vc():
            # If the bot is not in any voice channels,
            # it joins the appropriate one
            await self.join(ctx)

        client = self.bot.voice_clients[0]

        if client.is_paused():
            await self.resume(ctx)
            return

        if client.is_playing():
            # If bot is already playing, we simply add to queue
            await self.queue(ctx, *args)
            return

        if len(self.playing_queue) == 0:
            # Ensure that there is something in the queue
            await self.queue(ctx, *args)

        audio_data = self.playing_queue.pop()
        self.play_song(ctx, client, audio_data)

    def play_song(self, ctx: commands.Context,
                  client: discord.VoiceClient,
                  audio_data: List):
        """
        Plays the song in audio_data in client and sends a message to the
        channel relaying this information
        :param ctx:
        :param client:
        :param audio_data:
        :return:
        """

        def after_playing(error):
            if len(self.playing_queue) > 0:
                # Play next song if available
                self.play_song(ctx, client, self.playing_queue.pop())

        asyncio.run_coroutine_threadsafe(
            ctx.send(embed=playing_message(*audio_data[1:])),
            self.bot.loop
        )

        client.play(audio_data[0], after=after_playing)

    def download_audio(self, search_args: Tuple[str], requester: str) -> None:
        """This function downloads the result from search_args
        :param search_args: the arguments for the search, as provided by user
        :param requester: String representing the nickname of the requester
        """
        query_results = yt_search(" ".join(search_args))

        if query_results is None:
            # Make sure search actually returned something
            return

        url = query_results["source"]
        self.playing_queue.append(
            (
                discord.FFmpegPCMAudio(url, **self.FFMPEG_OPTIONS),
                query_results["title"],
                "https://www.youtube.com/watch?v=" + query_results["id"],
                requester
            )
        )

    @commands.command(help="Pause whatever Melody is playing")
    async def pause(self, ctx):
        """Command to pause what is playing"""
        if not self.bot_in_vc():
            await ctx.send("I don't think I was playing anything, "
                           "but I'll stop anyway :persevere:")
            return

        channel = self.bot.voice_clients[0]
        channel.pause()
        await ctx.send("**Playing paused** :pause_button:")

    @commands.command(help="Have Melody resume playing")
    async def resume(self, ctx):
        """Command to resume playing"""
        if not self.bot_in_vc():
            await ctx.send("Um I don't think I am in a vc? "
                           "But um I guess I will continue playing silence")
            return

        channel = self.bot.voice_clients[0]

        channel.resume()
        await ctx.send("**Playing resumed** :arrow_forward:")
