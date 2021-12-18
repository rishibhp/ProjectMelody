from typing import Tuple

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
MAX_TITLE_LENGTH = 40  # max num characters in track title when displaying queue


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
        self.loop_track = False
        self.loop = False

        # Each element in self.playing_queue is a tuple of 4 objects:
        # 0. discord.FFmpegPCMAudio object for the audio itself
        # 1. String object for the video title
        # 2. String object for the video url
        # 3. String object for the requester's nickname
        # 4. Integer representing length of track in seconds
        self.playing_queue = []

    def bot_in_vc(self):
        return len(self.bot.voice_clients) > 0

    def format_queue(self) -> str:
        if len(self.playing_queue) == 0:
            return "Empty queue!"

        return_message = "```md"
        for i in range(len(self.playing_queue)):
            track_title = self.trim_title(self.playing_queue[i][1])
            track_len = self.format_seconds(self.playing_queue[i][4])
            return_message += f"\n{i + 1:>2}) {track_title:<40} {track_len:>10}"
        footer = f"\nLoop queue: {self.bool_to_emoji(self.loop)} | " \
                 f"Loop track: {self.bool_to_emoji(self.loop_track)}"
        return return_message + footer + "```"

    @staticmethod
    def trim_title(title: str) -> str:
        if len(title) < MAX_TITLE_LENGTH:
            return title
        return title[:MAX_TITLE_LENGTH - 3] + "..."

    @staticmethod
    def format_seconds(seconds: int) -> str:
        m, s = divmod(seconds, 60)
        return f"{m}:{str(s).zfill(2)}"

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
            self.bot.voice_clients[0].stop()
            self.playing_queue = []
            await ctx.send(random.choice(LEAVE_MESSAGES))
            await self.bot.voice_clients[0].disconnect()

    @staticmethod
    def bool_to_emoji(bool_val: bool) -> str:
        """ Converts a boolean value into an emoji """
        if bool_val:
            return "✅"
        else:
            return "❌"

    @commands.command(aliases=["lt"], help="Loop the current track")
    async def looptrack(self, ctx: commands.Context) -> None:
        """ Command to loop the current track (or the first one in queue) """
        self.loop_track = not self.loop_track
        await ctx.send("Looping track: " + self.bool_to_emoji(self.loop_track))

    @commands.command(aliases=["loop", "l", "loopqueue", "lq"],
                      help="Loop the queue")
    async def loop_command(self, ctx: commands.Context) -> None:
        """ Command to loop the queue in order """
        self.loop = not self.loop
        await ctx.send("Queue loop: " + self.bool_to_emoji(self.loop))

    @commands.command(help="Pause whatever Melody is playing")
    async def pause(self, ctx: commands.Context) -> None:
        """Command to pause what is playing"""
        if not self.bot_in_vc():
            await ctx.send("I don't think I was playing anything, "
                           "but I'll stop anyway :persevere:")
            return

        channel = self.bot.voice_clients[0]
        channel.pause()
        await ctx.send("**Playing paused** :pause_button:")

    @commands.command(help="Have Melody resume playing")
    async def resume(self, ctx: commands.Context) -> None:
        """Command to resume playing"""
        if not self.bot_in_vc():
            await ctx.send("Um I don't think I am in a vc? "
                           "But um I guess I will continue playing silence")
            return

        channel = self.bot.voice_clients[0]

        channel.resume()
        await ctx.send("**Playing resumed** :arrow_forward:")

    @commands.command(aliases=["clearqueue", "cq"], help="Clear queue")
    async def clear_queue(self, ctx: commands.Context):
        """ Commands to clear the queue """
        self.bot.voice_clients[0].stop()
        self.playing_queue = []
        await ctx.send("Queue cleared")

    @commands.command(aliases=["q"], help="Add a track to the queue")
    async def queue(self, ctx: commands.Context, *args: str) -> None:
        """ Command to add items to the queue """
        # Currently we instantly download anything that is added to queue.
        # Can likely be made more efficient
        if len(args) == 0:
            # queue_embed = discord.Embed(description=self.format_queue())
            await ctx.send(self.format_queue())
            return
        self.download_audio(args, ctx.author.display_name)
        await ctx.send(embed=queue_message(*self.playing_queue[-1][1:4]))

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

        self.play_song(ctx, client, self.playing_queue[0])

    def play_song(self, ctx: commands.Context,
                  client: discord.VoiceClient,
                  audio_data: Tuple) -> None:
        """
        Plays the song in audio_data in client and sends a message to the
        channel relaying this information
        :param ctx: context of request
        :param client: VoiceClient where track is to be played
        :param audio_data: Tuple containing information about the track
        (see self.playing_queue for details)
        :return: None
        """

        def after_playing(error):
            if not self.loop_track:
                track_data = self.playing_queue.pop(0)
                if self.loop:
                    self.playing_queue.append(track_data)

            if len(self.playing_queue) > 0:
                # Play next song if available
                self.play_song(ctx, client, self.playing_queue[0])

        asyncio.run_coroutine_threadsafe(
            ctx.send(embed=playing_message(*audio_data[1:4])),
            self.bot.loop
        )
        source = discord.FFmpegPCMAudio(audio_data[0], **self.FFMPEG_OPTIONS)
        client.play(source, after=after_playing)

    def download_audio(self, search_args: Tuple[str], requester: str) -> None:
        """
        This method downloads the result from search_args and saves it and
        its information to self.playing_queue
        :param search_args: Search arguments as provided by user
        :param requester: Discord (nick)name of requester
        :return: None
        """
        query_results = yt_search(" ".join(search_args))

        if query_results is None:
            # Make sure search actually returned something
            return

        # download audio and save it and its information in self.playing_queue
        self.playing_queue.append(
            (
                query_results["source"],
                query_results["title"],
                query_results["url"],
                requester,
                query_results["duration"]
            )
        )
