import discord
import wavelink
import typing as t
import re
import datetime
import random
import os
import shutil
import asyncio
import spotipy
import math

from dotenv import load_dotenv
from discord_components import *
from spotipy.oauth2 import SpotifyClientCredentials
from pathlib import Path
from discord.ext import commands
from discord.ext.commands import *
from enum import Enum

URL_REG = r'https?://(?:www\.)?.+'
SPOTIFY_URL_REG = re.compile(r'https?://open.spotify.com/(?P<type>album|playlist|track)/(?P<id>[a-zA-Z0-9]+)')
DIR = os.path.dirname(__file__)
path = Path(__file__)
oneup = path.parent.absolute()
twoup = oneup.parent.absolute()
threeup = twoup.parent.absolute()

load_dotenv(f'{threeup}/.env')
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

class AlreadyConnectedToChannel(commands.CommandError):
    pass

class NoVoiceChannel(commands.CommandError):
    pass

class QueueIsEmpty(commands.CommandError):
    pass

class NoTracksFound(commands.CommandError):
    pass

class PlayerIsAlreadyPaused(commands.CommandError):
    pass

class PlayerIsAlreadyPlaying(commands.CommandError):
    pass

class NoMoreTracks(commands.CommandError):
    pass

class NoPreviousTracks(commands.CommandError):
    pass

class InvalidRepeatMode(commands.CommandError):
    pass

class NoPreviousTracks(commands.CommandError):
    pass

class RepeatMode(Enum):
    NONE = 0
    ONE = 1
    ALL = 2

class Queue:
    def __init__(self):
        self._queue = []
        self.position = 0
        self.repeat_mode = RepeatMode.NONE

    @property
    def is_empty(self):
        return not self._queue

    @property
    def current_track(self):
        if not self._queue:
            raise QueueIsEmpty
        if self.position <= len(self._queue) - 1:
            return self._queue[self.position]

    @property
    def upcoming(self):
        if not self._queue:
            raise QueueIsEmpty
        return self._queue[self.position + 1:]

    @property
    def history(self):
        if not self._queue:
            raise QueueIsEmpty
        return self._queue[:self.position]

    @property
    def length(self):
        return len(self._queue[self.position:])

    @property
    def previouslength(self):
        return len(self._queue[:self.position])

    def move(self, oldpos, newpos):
        if not self._queue:
            raise QueueIsEmpty
        song = self._queue[oldpos]
        self._queue.remove(song)
        self._queue.insert(newpos, song)
        return song

    def remove(self, position):
        if not self._queue:
            raise QueueIsEmpty
        song = self._queue[position]
        self._queue.remove(song)
        return song

    def add(self, *args):
        self._queue.extend(args)

    def add_top(self, *args):
        queue_length = int(self.position) + 1
        self._queue.insert(queue_length,*args)
    
    def get_next_track(self):
        if not self._queue:
            raise QueueIsEmpty
        self.position += 1
        if self.position < 0:
            return None
        elif self.position > len(self._queue) - 1:
            if self.repeat_mode == RepeatMode.ALL:
                self.position = 0
            else:
                return None
        return self._queue[self.position]

    def shuffle(self):
        if not self._queue:
            raise QueueIsEmpty
        upcoming = self.upcoming
        random.shuffle(upcoming)
        self._queue = self._queue[:self.position + 1]
        self._queue.extend(upcoming)

    def set_repeat_mode(self, mode):
        if mode == 'none':
            self.repeat_mode = RepeatMode.NONE
        elif mode == '1':
            self.repeat_mode = RepeatMode.ONE
        elif mode == 'all':
            self.repeat_mode = RepeatMode.ALL

    def empty(self):
        self._queue.clear()
        self.position = 0

class Player(wavelink.Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = Queue()
        self.skip_votes = set()
        self.leave_votes = set()
        self.pause_votes = set()
        self.resume_votes = set()
        self.stop_votes = set()
        self.shuffle_votes = set()
        self.loop_votes = set()
        self.loopqueue_votes = set()
        self.clearqueue_votes = set()
        self.dj = None
        self.djonly = False
    
    async def connect(self, ctx):
        if self.is_connected:
            raise AlreadyConnectedToChannel
        voicestate = ctx.author.voice
        if voicestate is None:
            embed = discord.Embed(
                title='**:x: You must be in a voice channel to execute this command.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        channel = ctx.author.voice.channel
        await super().connect(channel.id)
        return channel
    
    async def teardown(self):
        try:
            self.queue.repeat_mode = RepeatMode.NONE
            await self.destroy()
        except KeyError:
            pass

    async def add_tracks(self, ctx, tracks):
        if not tracks:
            raise NoTracksFound
        if isinstance(tracks, wavelink.TrackPlaylist):
            self.queue.add(*tracks.tracks)
            embed = discord.Embed(
                title=f'**:white_check_mark: Added {len(tracks.tracks)} songs to the queue.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
        else:
            if self.queue.length == 0:
                self.queue.add(tracks[0])
                embed = discord.Embed(
                    title=f'**:white_check_mark: Playing "{tracks[0].title}" now.**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
            else:
                self.queue.add(tracks[0])
                embed = discord.Embed(
                    title=f'**:white_check_mark: Added "{tracks[0].title}" to the queue.**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
        if not self.is_playing and not self.queue.is_empty:
            await self.start_playback()

    async def add_silent_track(self, tracks):
        if not tracks:
            raise NoTracksFound
        self.queue.add(tracks)
        if not self.is_playing and not self.queue.is_empty:
            await self.start_playback()

    async def add_top_track(self, ctx, tracks):
        if not tracks:
            raise NoTracksFound
        if isinstance(tracks, wavelink.TrackPlaylist):
            embed = discord.Embed(
                title=f'**:x: Cannot be a playlist**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
        else:
            self.queue.add_top(tracks[0])
            embed = discord.Embed(
                title=f'**:white_check_mark: Added "{tracks[0].title}" to the top of the queue.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
        if not self.is_playing and not self.queue.is_empty:
            await self.start_playback()

    async def add_now_track(self, ctx, tracks):
        if not tracks:
            raise NoTracksFound
        if isinstance(tracks, wavelink.TrackPlaylist):
            embed = discord.Embed(
                title=f'**:x: Cannot be a playlist**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
        else:
            self.queue.add_top(tracks[0])
            embed = discord.Embed(
                title=f'**:white_check_mark: Playing "{tracks[0].title}" now.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
        if not self.is_playing and not self.queue.is_empty:
            await self.start_playback()

    async def start_playback(self):
        track = self.queue.current_track
        if track.id == 'spotify':
            spotify_track = await self.node.get_tracks(f"ytsearch:{track.title} - {track.author}")
            await self.play(spotify_track[0])
        else:
            await self.play(self.queue.current_track)

    async def advance(self):
        try:
            if (track := self.queue.get_next_track()) is not None:
                self.skip_votes.clear()
                self.leave_votes.clear()
                self.pause_votes.clear()
                self.resume_votes.clear()
                self.stop_votes.clear()
                self.shuffle_votes.clear()
                self.loop_votes.clear()
                self.loopqueue_votes.clear()
                if track.id == 'spotify':
                    spotify_track = await self.node.get_tracks(f"ytsearch:{track.title} - {track.author}")
                    await self.play(spotify_track[0])
                else:
                    await self.play(track)
        except QueueIsEmpty:
            pass

    async def repeat_track(self):
        await self.play(self.queue.current_track)

    async def move_track(self, oldpos, newpos):
        moving = self.queue.move(oldpos, newpos)
        return moving

    async def remove_track(self, position):
        removing = self.queue.remove(position)
        return removing

class Music(commands.Cog, wavelink.WavelinkMixin):
    def __init__(self, client):
        self.client = client
        self.wavelink = wavelink.Client(bot=self.client)
        self.client.loop.create_task(self.start_nodes())

    @wavelink.WavelinkMixin.listener('on_track_stuck')
    @wavelink.WavelinkMixin.listener('on_track_end')
    @wavelink.WavelinkMixin.listener('on_track_exception')
    async def on_player_stop(self, node: wavelink.Node, payload):
        if payload.player.queue.repeat_mode == RepeatMode.ONE:
            await payload.player.repeat_track()
        else:
            await payload.player.advance()

    async def start_nodes(self):
        await self.client.wait_until_ready()
        nodes = {
            'MAIN': {
                'host': '10.0.0.14',
                'port': 2333,
                'rest_uri': 'http://10.0.0.14:2333',
                'password': 'password',
                'identifier': 'MAIN',
                'region': 'europe'
            }
        }
        for node in nodes.values():
            await self.wavelink.initiate_node(**node)

    def get_player(self, obj):
        if isinstance(obj, commands.Context):
            return self.wavelink.get_player(obj.guild.id, cls=Player, context=obj)
        elif isinstance(obj, discord.Guild):
            return self.wavelink.get_player(obj.id, cls=Player)

    def required(self, ctx):
        player = self.get_player(ctx)
        channel = self.client.get_channel(int(player.channel_id))
        count = 0
        for member in channel.members:
            if not member.bot:
                count += 1
        required = math.ceil((count) / 2.5)
        return required

    @commands.command(aliases=['connect', 'j'])
    async def join(self, ctx):
        player = self.get_player(ctx)
        channel = await player.connect(ctx)
        await asyncio.sleep(0.5)
        if self.client.user in channel.members:
            player.dj = ctx.author
            embed = discord.Embed(
                title=f'**:white_check_mark: Joined {channel.name}!**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
        else:
            await player.teardown()
            embed = discord.Embed(
                title=':x: I do not have access to this channel.',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    @join.error
    async def join_error(self, ctx, error):
        if isinstance(error, AlreadyConnectedToChannel):
            embed = discord.Embed(
                title='**:x: I am already connected to a voice channel.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
        if isinstance(error, NoVoiceChannel):
            embed = discord.Embed(
                title='**:x: You must be in a voice channel to execute this command.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    @commands.command(aliases=['disconnect', 'dc'])
    async def leave(self, ctx):
        player = self.get_player(ctx)
        if ctx.message.author.voice is None:
            embed = discord.Embed(
                title='**:x: You must be in the same channel as the bot to execute this command.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        if player.channel_id is None:
            embed = discord.Embed(
                title='**:x: I am not connected to a voice channel.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        if ctx.message.author.voice.channel.id and ctx.message.author.voice.channel.id == player.channel_id:
            channel = self.client.get_channel(int(player.channel_id))
            if self.length(ctx) >= 3:
                if self.is_dj(ctx):
                    embed = discord.Embed(
                        title='**The dj disconnected the bot.**',
                        color=(0xFFFF00),
                        timestamp=datetime.datetime.utcnow()
                    )
                    embed.set_footer(
                        text='\u200b',
                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                    )
                    await ctx.send(embed = embed)
                    player.leave_votes.clear()
                    await player.teardown()
                    return
                elif self.is_admin(ctx):
                    embed = discord.Embed(
                        title='**An admin disconnected the bot.**',
                        color=(0xFFFF00),
                        timestamp=datetime.datetime.utcnow()
                    )
                    embed.set_footer(
                        text='\u200b',
                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                    )
                    await ctx.send(embed = embed)
                    player.leave_votes.clear()
                    await player.teardown()
                    return
                elif player.djonly:
                    embed = discord.Embed(
                        title='**:x: The bot is currently in dj only mode.**',
                        color=(0xFFFF00),
                        timestamp=datetime.datetime.utcnow()
                    )
                    embed.set_footer(
                        text='\u200b',
                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                    )
                    await ctx.send(embed = embed)
                    return
            required = self.required(ctx)
            if ctx.author in player.leave_votes:
                player.leave_votes.remove(ctx.author)
                embed = discord.Embed(
                    title=f'**{ctx.author.name} is no longer voting for the bot to leave. {len(player.leave_votes)}/{required} required votes.**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
                return
            player.leave_votes.add(ctx.author)
            if len(player.leave_votes) >= required:
                channel = self.client.get_channel(int(player.channel_id))
                player.leave_votes.clear()
                await player.teardown()
                embed = discord.Embed(
                    title=f'**:white_check_mark: left {channel.name}.**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
            else:
                embed = discord.Embed(
                    title=f'**{ctx.author.name} voted for the bot to leave. {len(player.leave_votes)}/{required} required votes.**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
        else:
            embed = discord.Embed(
                title='**:x: You must be in the same channel as the bot to execute this command.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    @commands.command(aliases=['p'])
    async def play(self, ctx, *, query: t.Optional[str]):
        supported_files = ['webm', 'mkv', 'ogg', 'mov', 'mp4', 'aac', 'flac', 'mp3', 'wav']
        player = self.get_player(ctx)
        if not player.is_connected:
            channel = await player.connect(ctx)
            await asyncio.sleep(0.5)
            if not self.client.user in channel.members:
                await player.teardown()
                embed = discord.Embed(
                    title=':x: I do not have access to this channel.',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
                return
            else:
                player.dj = ctx.author
        if ctx.message.author.voice is None:
            embed = discord.Embed(
                title='**:x: You must be in the same channel as the bot to execute this command.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        if ctx.message.author.voice.channel.id and ctx.message.author.voice.channel.id == player.channel_id:
            if not self.is_admin(ctx) or not self.is_dj(ctx):
                if player.djonly:
                    embed = discord.Embed(
                        title='**:x: The bot is currently in dj only mode.**',
                        color=(0xFFFF00),
                        timestamp=datetime.datetime.utcnow()
                    )
                    embed.set_footer(
                        text='\u200b',
                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                    )
                    await ctx.send(embed = embed)
                    return
            if query is None:
                if ctx.message.attachments:
                    for attachment in ctx.message.attachments:
                        if any(attachment.filename.lower().endswith(filetype) for filetype in supported_files):
                            await attachment.save(attachment.filename)
                            path = './bin/Songs'
                            while os.path.isfile(attachment.filename) is False:
                                return
                            else:
                                try:
                                    os.remove(f'./bin/Songs/{attachment.filename}')
                                except:
                                    pass
                                shutil.move(attachment.filename, path)
                                pass
                            songpath = f'./bin/Songs/{attachment.filename}'
                            songfile = os.path.basename(songpath)
                            songname = songfile[:-4].replace('_', ' ')
                            if len(songname) >= 200:
                                embed = discord.Embed(
                                    title='**:x: This filename is too long.**',
                                    color=(0xFFFF00),
                                    timestamp=datetime.datetime.utcnow()
                                )
                                embed.set_footer(
                                    text='\u200b',
                                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                                )
                                await ctx.send(embed = embed)
                                return
                            seed = random.randint(1000000000,2000000000)
                            os.system(f'ffmpeg -loglevel quiet -y -i "./bin/Songs/{attachment.filename}" -map 0:a:0 -metadata title="{songname}" "./bin/Songs/{songname}-{seed}.mp3"')
                            os.remove(songpath)
                            await player.add_tracks(ctx, await self.wavelink.get_tracks(f'{twoup}\\Songs\\{songname}-{seed}.mp3'))
                        else:
                            embed = discord.Embed(
                                title='**:x: Unsupported filetype.**',
                                color=(0xFFFF00),
                                timestamp=datetime.datetime.utcnow()
                            )
                            embed.set_footer(
                                text='\u200b',
                                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                            )
                            await ctx.send(embed = embed)
                elif player.is_playing and not player.is_paused:
                    raise PlayerIsAlreadyPlaying
                else:
                    if player.queue.is_empty:
                        raise QueueIsEmpty
                    if self.length(ctx) >= 3:
                        if self.is_dj(ctx):
                            embed = discord.Embed(
                                title='**The dj resumed the bot.**',
                                color=(0xFFFF00),
                                timestamp=datetime.datetime.utcnow()
                            )
                            embed.set_footer(
                                text='\u200b',
                                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                            )
                            await ctx.send(embed = embed)
                            player.resume_votes.clear()
                            await player.set_pause(False)
                            return
                        elif self.is_admin(ctx):
                            embed = discord.Embed(
                                title='**An admin resumed the bot.**',
                                color=(0xFFFF00),
                                timestamp=datetime.datetime.utcnow()
                            )
                            embed.set_footer(
                                text='\u200b',
                                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                            )
                            await ctx.send(embed = embed)
                            player.resume_votes.clear()
                            await player.set_pause(False)
                            return
                        elif player.djonly:
                            embed = discord.Embed(
                                title='**:x: The bot is currently in dj only mode.**',
                                color=(0xFFFF00),
                                timestamp=datetime.datetime.utcnow()
                            )
                            embed.set_footer(
                                text='\u200b',
                                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                            )
                            await ctx.send(embed = embed)
                            return
                    required = self.required(ctx)
                    if ctx.author in player.resume_votes:
                        player.resume_votes.remove(ctx.author)
                        embed = discord.Embed(
                            title=f'**{ctx.author.name} is no longer voting for the music to be resumed. {len(player.resume_votes)}/{required} required votes.**',
                            color=(0xFFFF00),
                            timestamp=datetime.datetime.utcnow()
                        )
                        embed.set_footer(
                            text='\u200b',
                            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                        )
                        await ctx.send(embed = embed)
                        return
                    player.resume_votes.add(ctx.author)
                    if len(player.resume_votes) >= required:
                        player.resume_votes.clear()
                        await player.set_pause(False)
                        embed = discord.Embed(
                            title='**:white_check_mark: Music resumed!**',
                            color=(0xFFFF00),
                            timestamp=datetime.datetime.utcnow()
                        )
                        embed.set_footer(
                            text='\u200b',
                            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                        )
                        await ctx.send(embed = embed)
                    else:
                        embed = discord.Embed(
                            title=f'**{ctx.author.name} voted for the music to be resumed. {len(player.resume_votes)}/{required} required votes.**',
                            color=(0xFFFF00),
                            timestamp=datetime.datetime.utcnow()
                        )
                        embed.set_footer(
                            text='\u200b',
                            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                        )
                        await ctx.send(embed = embed)
            else:
                query = query.strip('<>')
                if SPOTIFY_URL_REG.match(query):
                    spoturl_check = SPOTIFY_URL_REG.match(query)
                    search_type = spoturl_check.group('type')
                    spotify_id = spoturl_check.group('id')
                    if search_type == 'playlist':
                        client_credentials_manager = SpotifyClientCredentials(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
                        spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)    
                        results = spotify.user_playlist_tracks(user="", playlist_id=query)
                        tracks = results['items']
                        while results['next']:
                            results = spotify.next(results)
                            tracks.extend(results['items'])
                        tracks = [
                            wavelink.Track(
                                id_= 'spotify',
                                info={'title': track['track']['name'] or 'Unknown', 'author': track['track']['artists'][0]['name'] or 'Unknown',
                                            'length': 0, 'identifier': 'Unknown', 'uri': 'spotify',
                                            'isStream': False, 'isSeekable': False, 'position': 0, 'thumbnail': None},
                            ) for track in tracks
                        ]
                        if not tracks:
                            raise NoTracksFound
                        if search_type == 'playlist':
                            for track in tracks:
                                await player.add_silent_track(track)
                            embed = discord.Embed(
                                title=f'**:white_check_mark: Added {len(tracks)} songs to the queue.**',
                                color=(0xFFFF00),
                                timestamp=datetime.datetime.utcnow()
                            )
                            embed.set_footer(
                                text='\u200b',
                                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                            )
                            await ctx.send(embed = embed)
                        else:
                            raise NoTracksFound
                    elif search_type == 'track':
                        client_credentials_manager = SpotifyClientCredentials(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
                        spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)    
                        result = spotify.track(track_id=query)
                        name = result['name'] + ' - ' + result['artists'][0]['name']
                        await player.add_tracks(ctx, await self.wavelink.get_tracks(f'ytsearch:{name}'))
                    else:
                        raise NoTracksFound
                elif re.match(URL_REG, query):
                    await player.add_tracks(ctx, await self.wavelink.get_tracks(query))
                else:
                    query = f'ytsearch:{query}'
                    await player.add_tracks(ctx, await self.wavelink.get_tracks(query))
        else:
            embed = discord.Embed(
                title='**:x: You must be in the same channel as the bot to execute this command.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    @play.error
    async def play_error(self, ctx, error):
        if isinstance(error, PlayerIsAlreadyPlaying):
            embed = discord.Embed(
                title='**:x: Music is not paused.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
        if isinstance(error, QueueIsEmpty):
            embed = discord.Embed(
                title='**:x: Nothing to play.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
        if isinstance(error, NoTracksFound):
            embed = discord.Embed(
                title='**:x: No songs found.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    @commands.command()
    async def pause(self, ctx):
        player = self.get_player(ctx)
        if ctx.message.author.voice is None:
            embed = discord.Embed(
                title='**:x: You must be in the same channel as the bot to execute this command.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        if player.channel_id is None:
            embed = discord.Embed(
                title='**:x: I am not connected to a voice channel.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        if ctx.message.author.voice.channel.id and ctx.message.author.voice.channel.id == player.channel_id:
            if player.is_paused:
                raise PlayerIsAlreadyPaused
            if self.length(ctx) >= 3:
                if self.is_dj(ctx):
                    embed = discord.Embed(
                        title='**The dj paused the bot.**',
                        color=(0xFFFF00),
                        timestamp=datetime.datetime.utcnow()
                    )
                    embed.set_footer(
                        text='\u200b',
                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                    )
                    await ctx.send(embed = embed)
                    player.pause_votes.clear()
                    await player.set_pause(True)
                    return
                elif self.is_admin(ctx):
                    embed = discord.Embed(
                        title='**An admin paused the bot.**',
                        color=(0xFFFF00),
                        timestamp=datetime.datetime.utcnow()
                    )
                    embed.set_footer(
                        text='\u200b',
                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                    )
                    await ctx.send(embed = embed)
                    player.pause_votes.clear()
                    await player.set_pause(True)
                    return
                elif player.djonly:
                    embed = discord.Embed(
                        title='**:x: The bot is currently in dj only mode.**',
                        color=(0xFFFF00),
                        timestamp=datetime.datetime.utcnow()
                    )
                    embed.set_footer(
                        text='\u200b',
                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                    )
                    await ctx.send(embed = embed)
                    return
            required = self.required(ctx)
            if ctx.author in player.pause_votes:
                player.pause_votes.remove(ctx.author)
                embed = discord.Embed(
                    title=f'**{ctx.author.name} is no longer voting for the music to be paused. {len(player.pause_votes)}/{required} required votes.**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
                return
            player.pause_votes.add(ctx.author)
            if len(player.pause_votes) >= required:
                player.pause_votes.clear()
                await player.set_pause(True)
                embed = discord.Embed(
                    title='**:white_check_mark: Music paused!**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
            else:
                embed = discord.Embed(
                    title=f'**{ctx.author.name} voted for the music to be paused. {len(player.pause_votes)}/{required} required votes.**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)   
        else:
            embed = discord.Embed(
                title='**:x: You must be in the same channel as the bot to execute this command.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    @pause.error
    async def pause_error(self, ctx, error):
        if isinstance(error, PlayerIsAlreadyPaused):
            embed = discord.Embed(
                title='**:x: Music is already paused.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    @commands.command()
    async def stop(self, ctx):
        player = self.get_player(ctx)
        if ctx.message.author.voice is None:
            embed = discord.Embed(
                title='**:x: You must be in the same channel as the bot to execute this command.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        if player.channel_id is None:
            embed = discord.Embed(
                title='**:x: I am not connected to a voice channel.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        if ctx.message.author.voice.channel.id and ctx.message.author.voice.channel.id == player.channel_id:
            if self.length(ctx) >= 3:
                if self.is_dj(ctx):
                    embed = discord.Embed(
                        title='**The dj stopped the bot.**',
                        color=(0xFFFF00),
                        timestamp=datetime.datetime.utcnow()
                    )
                    embed.set_footer(
                        text='\u200b',
                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                    )
                    await ctx.send(embed = embed)
                    player.stop_votes.clear()
                    player.queue.empty()
                    player.queue.repeat_mode = RepeatMode.NONE
                    await player.stop()
                    return
                elif self.is_admin(ctx):
                    embed = discord.Embed(
                        title='**An admin stopped the bot.**',
                        color=(0xFFFF00),
                        timestamp=datetime.datetime.utcnow()
                    )
                    embed.set_footer(
                        text='\u200b',
                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                    )
                    await ctx.send(embed = embed)
                    player.stop_votes.clear()
                    player.queue.empty()
                    player.queue.repeat_mode = RepeatMode.NONE
                    await player.stop()
                    return
                elif player.djonly:
                    embed = discord.Embed(
                        title='**:x: The bot is currently in dj only mode.**',
                        color=(0xFFFF00),
                        timestamp=datetime.datetime.utcnow()
                    )
                    embed.set_footer(
                        text='\u200b',
                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                    )
                    await ctx.send(embed = embed)
                    return
            required = self.required(ctx)
            if ctx.author in player.stop_votes:
                player.stop_votes.remove(ctx.author)
                embed = discord.Embed(
                    title=f'**{ctx.author.name} is no longer voting for the music to be stopped. {len(player.stop_votes)}/{required} required votes.**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
                return
            player.stop_votes.add(ctx.author)
            if len(player.stop_votes) >= required:
                player.stop_votes.clear()
                player.queue.empty()
                player.queue.repeat_mode = RepeatMode.NONE
                await player.stop()
                embed = discord.Embed(
                    title='**:white_check_mark: Music stopped!**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
            else:
                embed = discord.Embed(
                    title=f'**{ctx.author.name} voted for the music to be stopped. {len(player.stop_votes)}/{required} required votes.**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed) 
        else:
            embed = discord.Embed(
                title='**:x: You must be in the same channel as the bot to execute this command.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    @commands.command(aliases=['next'])
    async def skip(self, ctx):
        player = self.get_player(ctx)
        if ctx.message.author.voice is None:
            embed = discord.Embed(
                title='**:x: You must be in the same channel as the bot to execute this command.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        if player.channel_id is None:
            embed = discord.Embed(
                title='**:x: I am not connected to a voice channel.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        if ctx.message.author.voice.channel.id and ctx.message.author.voice.channel.id == player.channel_id:
            if not player.queue.upcoming:
                raise NoMoreTracks
            if self.length(ctx) >= 3:
                if self.is_dj(ctx):
                    player.skip_votes.clear()
                    await player.stop()
                    await asyncio.sleep(1)
                    embed = discord.Embed(
                        title='**The dj skipped the song.**',
                        description=f'Now playing: {player.queue.current_track}',
                        color=(0xFFFF00),
                        timestamp=datetime.datetime.utcnow()
                    )
                    embed.set_footer(
                        text='\u200b',
                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                    )
                    await ctx.send(embed = embed)
                    return
                elif self.is_admin(ctx):
                    player.skip_votes.clear()
                    await player.stop()
                    await asyncio.sleep(1)
                    embed = discord.Embed(
                        title='**An admin skipped the song.**',
                        description=f'Now playing: {player.queue.current_track}',
                        color=(0xFFFF00),
                        timestamp=datetime.datetime.utcnow()
                    )
                    embed.set_footer(
                        text='\u200b',
                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                    )
                    await ctx.send(embed = embed)
                    return
                elif player.djonly:
                    embed = discord.Embed(
                        title='**:x: The bot is currently in dj only mode.**',
                        color=(0xFFFF00),
                        timestamp=datetime.datetime.utcnow()
                    )
                    embed.set_footer(
                        text='\u200b',
                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                    )
                    await ctx.send(embed = embed)
                    return
            required = self.required(ctx)
            if ctx.author in player.skip_votes:
                player.skip_votes.remove(ctx.author)
                embed = discord.Embed(
                    title=f'**{ctx.author.name} is no longer voting to skip. {len(player.skip_votes)}/{required} required votes.**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
                return
            player.skip_votes.add(ctx.author)
            if len(player.skip_votes) >= required:
                player.skip_votes.clear()
                await player.stop()
                await asyncio.sleep(0.1)
                embed = discord.Embed(
                    title='**:white_check_mark: Skipped song.**',
                    description=f'Now playing: {player.queue.current_track}',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
            else:
                embed = discord.Embed(
                    title=f'**{ctx.author.name} voted to skip. {len(player.skip_votes)}/{required} required votes.**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
        else:
            embed = discord.Embed(
                title='**:x: You must be in the same channel as the bot to execute this command.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    @skip.error
    async def skip_error(self, ctx, error):
        if isinstance(error, QueueIsEmpty):
            embed = discord.Embed(
                title='**:x: There are no songs left in the queue.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
        if isinstance(error, NoMoreTracks):
            embed = discord.Embed(
                title='**:x: There are no songs left in the queue.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    @commands.command()
    async def shuffle(self, ctx):
        player = self.get_player(ctx)
        if ctx.message.author.voice is None:
            embed = discord.Embed(
                title='**:x: You must be in the same channel as the bot to execute this command.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        if player.channel_id is None:
            embed = discord.Embed(
                title='**:x: I am not connected to a voice channel.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        if ctx.message.author.voice.channel.id and ctx.message.author.voice.channel.id == player.channel_id:
            if self.length(ctx) >= 3:
                if self.is_dj(ctx):
                    embed = discord.Embed(
                        title='**The dj shuffled the queue.**',
                        color=(0xFFFF00),
                        timestamp=datetime.datetime.utcnow()
                    )
                    embed.set_footer(
                        text='\u200b',
                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                    )
                    await ctx.send(embed = embed)
                    player.shuffle_votes.clear()
                    player.queue.shuffle()
                    return
                elif self.is_admin(ctx):
                    embed = discord.Embed(
                        title='**An admin shuffled the queue.**',
                        color=(0xFFFF00),
                        timestamp=datetime.datetime.utcnow()
                    )
                    embed.set_footer(
                        text='\u200b',
                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                    )
                    await ctx.send(embed = embed)
                    player.shuffle_votes.clear()
                    player.queue.shuffle()
                    return            
                elif player.djonly:
                    embed = discord.Embed(
                        title='**:x: The bot is currently in dj only mode.**',
                        color=(0xFFFF00),
                        timestamp=datetime.datetime.utcnow()
                    )
                    embed.set_footer(
                        text='\u200b',
                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                    )
                    await ctx.send(embed = embed)
                    return
            required = self.required(ctx)
            if ctx.author in player.shuffle_votes:
                player.shuffle_votes.remove(ctx.author)
                embed = discord.Embed(
                    title=f'**{ctx.author.name} is no longer voting to shuffle. {len(player.shuffle_votes)}/{required} required votes.**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
                return
            player.shuffle_votes.add(ctx.author)
            if len(player.shuffle_votes) >= required:
                player.shuffle_votes.clear()
                player.queue.shuffle()
                embed = discord.Embed(
                    title='**:white_check_mark: Shuffled the queue!**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
            else:
                embed = discord.Embed(
                    title=f'**{ctx.author.name} voted to shuffle. {len(player.shuffle_votes)}/{required} required votes.**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
        else:
            embed = discord.Embed(
                title='**:x: You must be in the same channel as the bot to execute this command.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    @shuffle.error
    async def shuffle_error(self, ctx, error):
        if isinstance(error, QueueIsEmpty):
            embed = discord.Embed(
                title='**:x: The queue is empty.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    @commands.command(aliases=['repeat'])
    async def loop(self, ctx):
        player = self.get_player(ctx)
        mode = '1'
        if ctx.message.author.voice is None:
            embed = discord.Embed(
                title='**:x: You must be in the same channel as the bot to execute this command.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        if player.channel_id is None:
            embed = discord.Embed(
                title='**:x: I am not connected to a voice channel.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        if ctx.message.author.voice.channel.id and ctx.message.author.voice.channel.id == player.channel_id:
            if self.length(ctx) >= 3:
                if self.is_dj(ctx):
                    player.loop_votes.clear()
                    if str(player.queue.repeat_mode) == 'RepeatMode.ONE':
                        mode = 'none'
                        player.queue.set_repeat_mode(mode)
                        embed = discord.Embed(
                            title='**The dj disabled looping.**',
                            color=(0xFFFF00),
                            timestamp=datetime.datetime.utcnow()
                        )
                        embed.set_footer(
                            text='\u200b',
                            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                        )
                        await ctx.send(embed = embed)
                    else:
                        player.queue.set_repeat_mode(mode)
                        embed = discord.Embed(
                            title='**The dj enabled looping.**',
                            color=(0xFFFF00),
                            timestamp=datetime.datetime.utcnow()
                        )
                        embed.set_footer(
                            text='\u200b',
                            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                        )
                        await ctx.send(embed = embed)
                    return
                elif self.is_admin(ctx):
                    player.loop_votes.clear()
                    if str(player.queue.repeat_mode) == 'RepeatMode.ONE':
                        mode = 'none'
                        player.queue.set_repeat_mode(mode)
                        embed = discord.Embed(
                            title='**An admin disabled looping.**',
                            color=(0xFFFF00),
                            timestamp=datetime.datetime.utcnow()
                        )
                        embed.set_footer(
                            text='\u200b',
                            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                        )
                        await ctx.send(embed = embed)
                    else:
                        player.queue.set_repeat_mode(mode)
                        embed = discord.Embed(
                            title='**An admin enabled looping.**',
                            color=(0xFFFF00),
                            timestamp=datetime.datetime.utcnow()
                        )
                        embed.set_footer(
                            text='\u200b',
                            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                        )
                        await ctx.send(embed = embed)
                    return
                elif player.djonly:
                    embed = discord.Embed(
                        title='**:x: The bot is currently in dj only mode.**',
                        color=(0xFFFF00),
                        timestamp=datetime.datetime.utcnow()
                    )
                    embed.set_footer(
                        text='\u200b',
                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                    )
                    await ctx.send(embed = embed)
                    return
            required = self.required(ctx)
            if ctx.author in player.loop_votes:
                player.loop_votes.remove(ctx.author)
                embed = discord.Embed(
                    title=f'**{ctx.author.name} is no longer voting to toggle loop. {len(player.loop_votes)}/{required} required votes.**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
                return
            player.loop_votes.add(ctx.author)
            if len(player.loop_votes) >= required:
                player.loop_votes.clear()
                if str(player.queue.repeat_mode) == 'RepeatMode.ONE':
                    mode = 'none'
                    player.queue.set_repeat_mode(mode)
                    embed = discord.Embed(
                        title=f'**:white_check_mark: Looping disabled.**',
                        color=(0xFFFF00),
                        timestamp=datetime.datetime.utcnow()
                    )
                    embed.set_footer(
                        text='\u200b',
                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                    )
                    await ctx.send(embed = embed)
                    return
                player.queue.set_repeat_mode(mode)
                embed = discord.Embed(
                    title=f'**:white_check_mark: Looping current song.**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
            else:
                embed = discord.Embed(
                    title=f'**{ctx.author.name} voted to toggle loop. {len(player.loop_votes)}/{required} required votes.**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
        else:
            embed = discord.Embed(
                title='**:x: You must be in the same channel as the bot to execute this command.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    @commands.command(aliases=['repeatqueue'])
    async def loopqueue(self, ctx):
        player = self.get_player(ctx)
        mode = 'all'
        if ctx.message.author.voice is None:
            embed = discord.Embed(
                title='**:x: You must be in the same channel as the bot to execute this command.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        if player.channel_id is None:
            embed = discord.Embed(
                title='**:x: I am not connected to a voice channel.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        if ctx.message.author.voice.channel.id and ctx.message.author.voice.channel.id == player.channel_id:
            if self.length(ctx) >= 3:
                if self.is_dj(ctx):
                    player.loopqueue_votes.clear()
                    if str(player.queue.repeat_mode) == 'RepeatMode.ALL':
                        mode = 'none'
                        player.queue.set_repeat_mode(mode)
                        embed = discord.Embed(
                            title='**The dj disabled queue looping.**',
                            color=(0xFFFF00),
                            timestamp=datetime.datetime.utcnow()
                        )
                        embed.set_footer(
                            text='\u200b',
                            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                        )
                        await ctx.send(embed = embed)
                    else:
                        player.queue.set_repeat_mode(mode)
                        embed = discord.Embed(
                            title='**The dj enabled queue looping.**',
                            color=(0xFFFF00),
                            timestamp=datetime.datetime.utcnow()
                        )
                        embed.set_footer(
                            text='\u200b',
                            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                        )
                        await ctx.send(embed = embed)
                    return
                elif self.is_admin(ctx):
                    player.loopqueue_votes.clear()
                    if str(player.queue.repeat_mode) == 'RepeatMode.ALL':
                        mode = 'none'
                        player.queue.set_repeat_mode(mode)
                        embed = discord.Embed(
                            title='**An admin disabled queue looping.**',
                            color=(0xFFFF00),
                            timestamp=datetime.datetime.utcnow()
                        )
                        embed.set_footer(
                            text='\u200b',
                            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                        )
                        await ctx.send(embed = embed)
                    else:
                        player.queue.set_repeat_mode(mode)
                        embed = discord.Embed(
                            title='**An admin enabled queue looping.**',
                            color=(0xFFFF00),
                            timestamp=datetime.datetime.utcnow()
                        )
                        embed.set_footer(
                            text='\u200b',
                            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                        )
                        await ctx.send(embed = embed)
                    return
                elif player.djonly:
                    embed = discord.Embed(
                        title='**:x: The bot is currently in dj only mode.**',
                        color=(0xFFFF00),
                        timestamp=datetime.datetime.utcnow()
                    )
                    embed.set_footer(
                        text='\u200b',
                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                    )
                    await ctx.send(embed = embed)
                    return
            required = self.required(ctx)
            if ctx.author in player.loopqueue_votes:
                player.loopqueue_votes.remove(ctx.author)
                embed = discord.Embed(
                    title=f'**{ctx.author.name} is no longer voting to toggle queue loop. {len(player.loopqueue_votes)}/{required} required votes.**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
                return
            player.loopqueue_votes.add(ctx.author)
            if len(player.loopqueue_votes) >= required:
                player.loopqueue_votes.clear()
                if str(player.queue.repeat_mode) == 'RepeatMode.ALL':
                    mode = 'none'
                    player.queue.set_repeat_mode(mode)
                    embed = discord.Embed(
                        title=f'**:white_check_mark: Looping disabled.**',
                        color=(0xFFFF00),
                        timestamp=datetime.datetime.utcnow()
                    )
                    embed.set_footer(
                        text='\u200b',
                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                    )
                    await ctx.send(embed = embed)
                    return
                player.queue.set_repeat_mode(mode)
                embed = discord.Embed(
                    title=f'**:white_check_mark: Looping the queue.**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
            else:
                embed = discord.Embed(
                    title=f'**{ctx.author.name} voted to toggle queue loop. {len(player.loopqueue_votes)}/{required} required votes.**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
        else:
            embed = discord.Embed(
                title='**:x: You must be in the same channel as the bot to execute this command.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    @commands.command(aliases=['q'])
    async def queue(self, ctx):
        player = self.get_player(ctx)
        count = 10
        seed = random.randint(1000000000,2000000000)
        if player.queue.is_empty:
            raise QueueIsEmpty
        async def callback(interaction):
            nonlocal count
            nonlocal seed
            if interaction.author == ctx.author and interaction.custom_id == f'first{seed}' and interaction.message == message:
                await interaction.respond(type=6)
                count = 10
                embed = discord.Embed(
                    title='Queue',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.add_field(
                    name='Currently playing:',
                    value=getattr(player.queue.current_track, 'title', 'No music playing.'),
                    inline=False
                )
                if upcoming := player.queue.upcoming:
                    upcomingsongs = []
                    for i, name in enumerate(upcoming, 1):
                        upcomingsongs.append(f'{i}. {name}')
                    embed.add_field(
                        name='Upcoming songs:',
                        value='\n'.join(upcomingsongs[:count]),
                        inline=False
                    )
                embed.add_field(
                    name='Songs in queue:',
                    value=player.queue.length,
                    inline=False
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await message.edit(embed = embed)
            elif interaction.author == ctx.author and interaction.custom_id == f'previous{seed}' and interaction.message == message:
                await interaction.respond(type=6)
                if count > 20:
                    oldcount = count - 20
                    count -= 10
                    embed = discord.Embed(
                        title='Queue',
                        color=(0xFFFF00),
                        timestamp=datetime.datetime.utcnow()
                    )
                    embed.add_field(
                        name='Currently playing:',
                        value=getattr(player.queue.current_track, 'title', 'No music playing.'),
                        inline=False
                    )
                    if upcoming := player.queue.upcoming:
                        upcomingsongs = []
                        for i, name in enumerate(upcoming, 1):
                            upcomingsongs.append(f'{i}. {name}')
                        embed.add_field(
                            name='Upcoming songs:',
                            value='\n'.join(upcomingsongs[oldcount:count]),
                            inline=False
                        )
                    embed.add_field(
                        name='Songs in queue:',
                        value=player.queue.length,
                        inline=False
                    )
                    embed.set_footer(
                        text='\u200b',
                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                    )
                    await message.edit(embed=embed)
                else:
                    count = 10
                    embed = discord.Embed(
                        title='Queue',
                        color=(0xFFFF00),
                        timestamp=datetime.datetime.utcnow()
                    )
                    embed.add_field(
                        name='Currently playing:',
                        value=getattr(player.queue.current_track, 'title', 'No music playing.'),
                        inline=False
                    )
                    if upcoming := player.queue.upcoming:
                        upcomingsongs = []
                        for i, name in enumerate(upcoming, 1):
                            upcomingsongs.append(f'{i}. {name}')
                        embed.add_field(
                            name='Upcoming songs:',
                            value='\n'.join(upcomingsongs[:count]),
                            inline=False
                        )
                    embed.add_field(
                        name='Songs in queue:',
                        value=player.queue.length,
                        inline=False
                    )
                    embed.set_footer(
                        text='\u200b',
                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                    )
                    await message.edit(embed = embed)
            elif interaction.author == ctx.author and interaction.custom_id == f'next{seed}' and interaction.message == message:
                await interaction.respond(type=6)
                if count <= player.queue.length - 10:
                    oldcount = count
                    count += 10
                    embed = discord.Embed(
                        title='Queue',
                        color=(0xFFFF00),
                        timestamp=datetime.datetime.utcnow()
                    )
                    embed.add_field(
                        name='Currently playing:',
                        value=getattr(player.queue.current_track, 'title', 'No music playing.'),
                        inline=False
                    )
                    if upcoming := player.queue.upcoming:
                        upcomingsongs = []
                        for i, name in enumerate(upcoming, 1):
                            upcomingsongs.append(f'{i}. {name}')
                        embed.add_field(
                            name='Upcoming songs:',
                            value='\n'.join(upcomingsongs[oldcount:count]),
                            inline=False
                        )
                    embed.add_field(
                        name='Songs in queue:',
                        value=player.queue.length,
                        inline=False
                    )
                    embed.set_footer(
                        text='\u200b',
                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                    )
                    await message.edit(embed=embed)
                else:
                    oldcount = player.queue.length - 10
                    count = player.queue.length
                    embed = discord.Embed(
                        title='Queue',
                        color=(0xFFFF00),
                        timestamp=datetime.datetime.utcnow()
                    )
                    embed.add_field(
                        name='Currently playing:',
                        value=getattr(player.queue.current_track, 'title', 'No music playing.'),
                        inline=False
                    )
                    if upcoming := player.queue.upcoming:
                        upcomingsongs = []
                        for i, name in enumerate(upcoming, 1):
                            upcomingsongs.append(f'{i}. {name}')
                        embed.add_field(
                            name='Upcoming songs:',
                            value='\n'.join(upcomingsongs[oldcount:count]),
                            inline=False
                        )
                    embed.add_field(
                        name='Songs in queue:',
                        value=player.queue.length,
                        inline=False
                    )
                    embed.set_footer(
                        text='\u200b',
                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                    )
                    await message.edit(embed=embed)
            elif interaction.author == ctx.author and interaction.custom_id == f'last{seed}' and interaction.message == message:
                await interaction.respond(type=6)
                oldcount = player.queue.length - 10
                count = player.queue.length
                embed = discord.Embed(
                    title='Queue',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.add_field(
                    name='Currently playing:',
                    value=getattr(player.queue.current_track, 'title', 'No music playing.'),
                    inline=False
                )
                if upcoming := player.queue.upcoming:
                    upcomingsongs = []
                    for i, name in enumerate(upcoming, 1):
                        upcomingsongs.append(f'{i}. {name}')
                    embed.add_field(
                        name='Upcoming songs:',
                        value='\n'.join(upcomingsongs[oldcount:count]),
                        inline=False
                    )
                embed.add_field(
                    name='Songs in queue:',
                    value=player.queue.length,
                    inline=False
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await message.edit(embed=embed)
            else:
                embed = discord.Embed(
                    title='**:x: You are not the invoker of this command.**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await interaction.respond(embed=embed)
        embed = discord.Embed(
            title='Queue',
            color=(0xFFFF00),
            timestamp=datetime.datetime.utcnow()
        )
        embed.add_field(
            name='Currently playing:',
            value=getattr(player.queue.current_track, 'title', 'No music playing.'),
            inline=False
        )
        if upcoming := player.queue.upcoming:
            upcomingsongs = []
            for i, name in enumerate(upcoming, 1):
                upcomingsongs.append(f'{i}. {name}')
            embed.add_field(
                name='Upcoming songs:',
                value='\n'.join(upcomingsongs[:count]),
                inline=False
            )
        embed.add_field(
            name='Songs in queue:',
            value=player.queue.length,
            inline=False
        )
        embed.set_footer(
            text='\u200b',
            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
        )
        message = await ctx.send(embed = embed,
            components=[
                [
                    self.client.components_manager.add_callback(Button(style=ButtonStyle.red, label='First', custom_id=f'first{seed}'), callback),
                    self.client.components_manager.add_callback(Button(style=ButtonStyle.red, label='Previous', custom_id=f'previous{seed}'), callback),
                    self.client.components_manager.add_callback(Button(style=ButtonStyle.red, label='Next', custom_id=f'next{seed}'), callback),
                    self.client.components_manager.add_callback(Button(style=ButtonStyle.red, label='Last', custom_id=f'last{seed}'), callback),
                ]
            ]
        )

    @queue.error
    async def queue_error(self, ctx, error):
        if isinstance(error, QueueIsEmpty):
            embed = discord.Embed(
                title='Queue',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.add_field(
                name='Currently playing:',
                value='No music playing.',
                inline=False
            )
            embed.add_field(
                name='Songs in queue:',
                value=0,
                inline=False
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    @commands.command(aliases=['np'])
    async def nowplaying(self, ctx):
        player = self.get_player(ctx)
        if player.queue.is_empty:
            raise QueueIsEmpty
        embed = discord.Embed(
            title='**Currently playing song:**',
            description=player.queue.current_track.title,
            color=(0xFFFF00),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_footer(
            text='\u200b',
            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
        )
        msg = await ctx.send(embed = embed)

    @nowplaying.error
    async def nowplaying_error(self, ctx, error):
        if isinstance(error, QueueIsEmpty):
            embed = discord.Embed(
                title='**:x: There is nothing playing.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    @commands.command(aliases=['playnext', 'pnext', 'ptop'])
    async def playtop(self, ctx, *, query: t.Optional[str]):
        supported_files = ['webm', 'mkv', 'ogg', 'mov', 'mp4', 'aac', 'flac', 'mp3', 'wav']
        player = self.get_player(ctx)
        if not player.is_connected:
            channel = await player.connect(ctx)
            await asyncio.sleep(0.5)
            if not self.client.user in channel.members:
                await player.teardown()
                embed = discord.Embed(
                    title=':x: I do not have access to this channel.',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
                return
            else:
                player.dj = ctx.author
        if ctx.message.author.voice is None:
            embed = discord.Embed(
                title='**:x: You must be in the same channel as the bot to execute this command.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        if ctx.message.author.voice.channel.id and ctx.message.author.voice.channel.id == player.channel_id:      
            if not self.is_admin(ctx) or not self.is_dj(ctx):
                if self.length(ctx) >= 3:
                    embed = discord.Embed(
                        title='**:x: There are too many people in this channel for this command to be used.**',
                        color=(0xFFFF00),
                        timestamp=datetime.datetime.utcnow()
                    )
                    embed.set_footer(
                        text='\u200b',
                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                    )
                    await ctx.send(embed = embed)
                    return
                elif player.djonly:
                    embed = discord.Embed(
                        title='**:x: The bot is currently in dj only mode.**',
                        color=(0xFFFF00),
                        timestamp=datetime.datetime.utcnow()
                    )
                    embed.set_footer(
                        text='\u200b',
                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                    )
                    await ctx.send(embed = embed)
                    return
            if query is None:
                if ctx.message.attachments:
                        for attachment in ctx.message.attachments:
                            if any(attachment.filename.lower().endswith(filetype) for filetype in supported_files):
                                await attachment.save(attachment.filename)
                                path = './bin/Songs'
                                while os.path.isfile(attachment.filename) is False:
                                    return
                                else:
                                    try:
                                        os.remove(f'./bin/Songs/{attachment.filename}')
                                    except:
                                        pass
                                    shutil.move(attachment.filename, path)
                                    pass
                                songpath = f'./bin/Songs/{attachment.filename}'
                                songfile = os.path.basename(songpath)
                                songname = songfile[:-4].replace('_', ' ')
                                if len(songname) >= 200:
                                    embed = discord.Embed(
                                        title='**:x: This filename is too long.**',
                                        color=(0xFFFF00),
                                        timestamp=datetime.datetime.utcnow()
                                    )
                                    embed.set_footer(
                                        text='\u200b',
                                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                                    )
                                    await ctx.send(embed = embed)
                                    return
                                seed = random.randint(1000000000,2000000000)
                                os.system(f'ffmpeg -loglevel quiet -y -i "./bin/Songs/{attachment.filename}" -map 0:a:0 -metadata title="{songname}" "./bin/Songs/{songname}-{seed}.mp3"')
                                os.remove(songpath)
                                await player.add_top_track(ctx, await self.wavelink.get_tracks(f'{twoup}\\Songs\\{songname}-{seed}.mp3'))
                            else:
                                embed = discord.Embed(
                                    title='**:x: Unsupported filetype.**',
                                    color=(0xFFFF00),
                                    timestamp=datetime.datetime.utcnow()
                                )
                                embed.set_footer(
                                    text='\u200b',
                                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                                )
                                await ctx.send(embed = embed)
                else:
                    embed = discord.Embed(
                        title='**:x: Use: bc!playtop <url/search> or bc!help playtop for more info.**',
                        color=(0xFFFF00),
                        timestamp=datetime.datetime.utcnow()
                    )
                    embed.set_footer(
                        text='\u200b',
                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                    )
                    await ctx.send(embed = embed)
            else:
                query = query.strip('<>')
                if SPOTIFY_URL_REG.match(query):
                    spoturl_check = SPOTIFY_URL_REG.match(query)
                    search_type = spoturl_check.group('type')
                    spotify_id = spoturl_check.group('id')
                    if search_type == 'playlist':
                        embed = discord.Embed(
                            title='**:x: Cannot be a playlist.**',
                            color=(0xFFFF00),
                            timestamp=datetime.datetime.utcnow()
                        )
                        embed.set_footer(
                            text='\u200b',
                            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                        )
                        await ctx.send(embed = embed)
                    elif search_type == 'track':
                        client_credentials_manager = SpotifyClientCredentials(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
                        spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
                        result = spotify.track(track_id=query)
                        name = result['name'] + ' - ' + result['artists'][0]['name']
                        await player.add_top_track(ctx, await self.wavelink.get_tracks(f'ytsearch:{name}'))
                    else:
                        raise NoTracksFound
                elif re.match(URL_REG, query):
                    await player.add_top_track(ctx, await self.wavelink.get_tracks(query))
                else:
                    query = f'ytsearch:{query}'
                    await player.add_top_track(ctx, await self.wavelink.get_tracks(query))
        else:
            embed = discord.Embed(
                title='**:x: You must be in the same channel as the bot to execute this command.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    @playtop.error
    async def playtop_error(self, ctx, error):
        if isinstance(error, QueueIsEmpty):
            embed = discord.Embed(
                title='**:x: Nothing to play.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
        if isinstance(error, NoTracksFound):
            embed = discord.Embed(
                title='**:x: No songs found.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    @commands.command(aliases=['pnow'])
    async def playnow(self, ctx, *, query: t.Optional[str]):
        supported_files = ['webm', 'mkv', 'ogg', 'mov', 'mp4', 'aac', 'flac', 'mp3', 'wav']
        player = self.get_player(ctx)
        if not player.is_connected:
            channel = await player.connect(ctx)
            await asyncio.sleep(0.5)
            if not self.client.user in channel.members:
                await player.teardown()
                embed = discord.Embed(
                    title=':x: I do not have access to this channel.',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
                return
            else:
                player.dj = ctx.author
        if ctx.message.author.voice is None:
            embed = discord.Embed(
                title='**:x: You must be in the same channel as the bot to execute this command.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        if ctx.message.author.voice.channel.id and ctx.message.author.voice.channel.id == player.channel_id:
            if not self.is_admin(ctx) or not self.is_dj(ctx):
                if self.length(ctx) >= 3:
                    embed = discord.Embed(
                        title='**:x: There are too many people in this channel for this command to be used.**',
                        color=(0xFFFF00),
                        timestamp=datetime.datetime.utcnow()
                    )
                    embed.set_footer(
                        text='\u200b',
                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                    )
                    await ctx.send(embed = embed)
                    return
                elif player.djonly:
                    embed = discord.Embed(
                        title='**:x: The bot is currently in dj only mode.**',
                        color=(0xFFFF00),
                        timestamp=datetime.datetime.utcnow()
                    )
                    embed.set_footer(
                        text='\u200b',
                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                    )
                    await ctx.send(embed = embed)
                    return
            if query is None:
                if ctx.message.attachments:
                        for attachment in ctx.message.attachments:
                            if any(attachment.filename.lower().endswith(filetype) for filetype in supported_files):
                                await attachment.save(attachment.filename)
                                path = './bin/Songs'
                                while os.path.isfile(attachment.filename) is False:
                                    return
                                else:
                                    try:
                                        os.remove(f'./bin/Songs/{attachment.filename}')
                                    except:
                                        pass
                                    shutil.move(attachment.filename, path)
                                    pass
                                songpath = f'./bin/Songs/{attachment.filename}'
                                songfile = os.path.basename(songpath)
                                songname = songfile[:-4].replace('_', ' ')
                                if len(songname) >= 200:
                                    embed = discord.Embed(
                                        title='**:x: This filename is too long.**',
                                        color=(0xFFFF00),
                                        timestamp=datetime.datetime.utcnow()
                                    )
                                    embed.set_footer(
                                        text='\u200b',
                                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                                    )
                                    await ctx.send(embed = embed)
                                    return
                                seed = random.randint(1000000000,2000000000)
                                os.system(f'ffmpeg -loglevel quiet -y -i "./bin/Songs/{attachment.filename}" -map 0:a:0 -metadata title="{songname}" "./bin/Songs/{songname}-{seed}.mp3"')
                                os.remove(songpath)
                                await player.add_now_track(ctx, await self.wavelink.get_tracks(f'{twoup}\\Songs\\{songname}-{seed}.mp3'))
                                if player.queue.upcoming:
                                    await player.stop()
                            else:
                                embed = discord.Embed(
                                    title='**:x: Unsupported filetype.**',
                                    color=(0xFFFF00),
                                    timestamp=datetime.datetime.utcnow()
                                )
                                embed.set_footer(
                                    text='\u200b',
                                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                                )
                                await ctx.send(embed = embed)
                else:
                    embed = discord.Embed(
                        title='**:x: Use: bc!playnow <url/search> or bc!help playnow for more info.**',
                        color=(0xFFFF00),
                        timestamp=datetime.datetime.utcnow()
                    )
                    embed.set_footer(
                        text='\u200b',
                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                    )
                    await ctx.send(embed = embed)
            else:
                query = query.strip('<>')
                if SPOTIFY_URL_REG.match(query):
                    spoturl_check = SPOTIFY_URL_REG.match(query)
                    search_type = spoturl_check.group('type')
                    spotify_id = spoturl_check.group('id')
                    if search_type == 'playlist':
                        embed = discord.Embed(
                            title='**:x: Cannot be a playlist.**',
                            color=(0xFFFF00),
                            timestamp=datetime.datetime.utcnow()
                        )
                        embed.set_footer(
                            text='\u200b',
                            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                        )
                        await ctx.send(embed = embed)
                    elif search_type == 'track':
                        client_credentials_manager = SpotifyClientCredentials(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
                        spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
                        result = spotify.track(track_id=query)
                        name = result['name'] + ' - ' + result['artists'][0]['name']
                        await player.add_now_track(ctx, await self.wavelink.get_tracks(f'ytsearch:{name}'))
                        if player.queue.upcoming:
                            await player.stop()
                    else:
                        raise NoTracksFound
                elif re.match(URL_REG, query):
                    await player.add_now_track(ctx, await self.wavelink.get_tracks(query))
                    if player.queue.upcoming:
                        await player.stop()
                else:
                    query = f'ytsearch:{query}'
                    await player.add_now_track(ctx, await self.wavelink.get_tracks(query))
                    if player.queue.upcoming:
                        await player.stop()
        else:
            embed = discord.Embed(
                title='**:x: You must be in the same channel as the bot to execute this command.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    @playnow.error
    async def playnow_error(self, ctx, error):
        if isinstance(error, QueueIsEmpty):
            embed = discord.Embed(
                title='**:x: Nothing to play.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
        if isinstance(error, NoTracksFound):
            embed = discord.Embed(
                title='**:x: No songs found.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    @commands.command()
    async def jump(self, ctx, number : int):
        player = self.get_player(ctx)
        if ctx.message.author.voice is None:
            embed = discord.Embed(
                title='**:x: You must be in the same channel as the bot to execute this command.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        if player.channel_id is None:
            embed = discord.Embed(
                title='**:x: I am not connected to a voice channel.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        if ctx.message.author.voice.channel.id and ctx.message.author.voice.channel.id == player.channel_id:
            if not player.queue.upcoming:
                raise NoMoreTracks
            if self.length(ctx) < 3:
                if number >= player.queue.length:
                    embed = discord.Embed(
                        title='**:x: There aren\'t that many songs in the queue.**',
                        color=(0xFFFF00),
                        timestamp=datetime.datetime.utcnow()
                    )
                    embed.set_footer(
                        text='\u200b',
                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                    )
                    await ctx.send(embed = embed)
                elif number <= 0:
                    embed = discord.Embed(
                        title='**:x: Amount must be higher than 0.**',
                        color=(0xFFFF00),
                        timestamp=datetime.datetime.utcnow()
                    )
                    embed.set_footer(
                        text='\u200b',
                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                    )
                    await ctx.send(embed = embed)
                else:
                    player.queue.position += number - 1
                    await player.stop()
                    embed = discord.Embed(
                        title=f'**:white_check_mark: Jumped to track {number}.**',
                        color=(0xFFFF00),
                        timestamp=datetime.datetime.utcnow()
                    )
                    embed.set_footer(
                        text='\u200b',
                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                    )
                    await ctx.send(embed = embed)
            else:
                if self.is_dj(ctx):
                    if number >= player.queue.length:
                        embed = discord.Embed(
                            title='**:x: There aren\'t that many songs in the queue.**',
                            color=(0xFFFF00),
                            timestamp=datetime.datetime.utcnow()
                        )
                        embed.set_footer(
                            text='\u200b',
                            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                        )
                        await ctx.send(embed = embed)
                    elif number <= 0:
                        embed = discord.Embed(
                            title='**:x: Amount must be higher than 0.**',
                            color=(0xFFFF00),
                            timestamp=datetime.datetime.utcnow()
                        )
                        embed.set_footer(
                            text='\u200b',
                            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                        )
                        await ctx.send(embed = embed)
                    else:
                        player.queue.position += number - 1
                        await player.stop()
                        embed = discord.Embed(
                            title=f'**The dj jumped to track {number}.**',
                            color=(0xFFFF00),
                            timestamp=datetime.datetime.utcnow()
                        )
                        embed.set_footer(
                            text='\u200b',
                            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                        )
                        await ctx.send(embed = embed)
                    return
                elif self.is_admin(ctx):
                    if number >= player.queue.length:
                        embed = discord.Embed(
                            title='**:x: There aren\'t that many songs in the queue.**',
                            color=(0xFFFF00),
                            timestamp=datetime.datetime.utcnow()
                        )
                        embed.set_footer(
                            text='\u200b',
                            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                        )
                        await ctx.send(embed = embed)
                    elif number <= 0:
                        embed = discord.Embed(
                            title='**:x: Amount must be higher than 0.**',
                            color=(0xFFFF00),
                            timestamp=datetime.datetime.utcnow()
                        )
                        embed.set_footer(
                            text='\u200b',
                            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                        )
                        await ctx.send(embed = embed)
                    else:
                        player.queue.position += number - 1
                        await player.stop()
                        embed = discord.Embed(
                            title=f'**An admin jumped to track {number}.**',
                            color=(0xFFFF00),
                            timestamp=datetime.datetime.utcnow()
                        )
                        embed.set_footer(
                            text='\u200b',
                            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                        )
                        await ctx.send(embed = embed)
                    return                
                embed = discord.Embed(
                    title='**:x: There are too many people in this channel for this command to be used.**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
        else:
            embed = discord.Embed(
                title='**:x: You must be in the same channel as the bot to execute this command.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    @jump.error
    async def jump_error(self, ctx, error):
        if isinstance(error, QueueIsEmpty):
            embed = discord.Embed(
                title='**:x: There are no songs left in the queue.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
        if isinstance(error, NoMoreTracks):
            embed = discord.Embed(
                title='**:x: There are no songs left in the queue.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
        if isinstance(error, MissingRequiredArgument):
            embed = discord.Embed(
                title='**:x: Use: bc!jump <number> or bc!help jump for more info.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)  

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        try:
            player = self.get_player(member.guild)
            if member.id == self.client.user.id:
                if before.channel is not None and after.channel is None:                
                    try:
                        player.dj = None
                        player.djonly = False
                        await player.stop()                    
                    except:
                        return
            else:
                channel = self.client.get_channel(int(player.channel_id))
                if member == player.dj and after.channel is None:
                    for m in channel.members:
                        if m.bot:
                            continue
                        else:
                            player.dj = m
                            return
                elif after.channel == channel and player.dj not in channel.members:
                    player.dj = member
        except:
            pass

    @commands.command()
    @commands.is_owner()
    async def move(self, ctx, oldposition : int, newposition : int):
        player = self.get_player(ctx)
        if ctx.message.author.voice is None:
            embed = discord.Embed(
                title='**:x: You must be in the same channel as the bot to execute this command.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        if player.channel_id is None:
            embed = discord.Embed(
                title='**:x: I am not connected to a voice channel.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        if ctx.message.author.voice.channel.id and ctx.message.author.voice.channel.id == player.channel_id:
            if not player.queue.upcoming:
                raise NoMoreTracks
            if self.length(ctx) < 3:
                if oldposition > player.queue.length or oldposition < 1:
                    embed = discord.Embed(
                        title='**:x: Invalid old position.**',
                        color=(0xFFFF00),
                        timestamp=datetime.datetime.utcnow()
                    )
                    embed.set_footer(
                        text='\u200b',
                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                    )
                    await ctx.send(embed = embed)
                    return
                if newposition > player.queue.length or newposition < 1:
                    embed = discord.Embed(
                        title='**:x: Invalid new position.**',
                        color=(0xFFFF00),
                        timestamp=datetime.datetime.utcnow()
                    )
                    embed.set_footer(
                        text='\u200b',
                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                    )
                    await ctx.send(embed = embed)
                    return
                oldsong = await player.move_track(oldposition, newposition)
                embed = discord.Embed(
                    title=f'**:white_check_mark: Moved "{oldsong.title}" to position {newposition}.**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
            else:
                if self.is_dj(ctx):
                    if oldposition > player.queue.length or oldposition < 1:
                        embed = discord.Embed(
                            title='**:x: Invalid old position.**',
                            color=(0xFFFF00),
                            timestamp=datetime.datetime.utcnow()
                        )
                        embed.set_footer(
                            text='\u200b',
                            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                        )
                        await ctx.send(embed = embed)
                        return
                    if newposition > player.queue.length or newposition < 1:
                        embed = discord.Embed(
                            title='**:x: Invalid new position.**',
                            color=(0xFFFF00),
                            timestamp=datetime.datetime.utcnow()
                        )
                        embed.set_footer(
                            text='\u200b',
                            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                        )
                        await ctx.send(embed = embed)
                        return
                    oldsong = await player.move_track(oldposition, newposition)
                    embed = discord.Embed(
                        title=f'**The dj moved "{oldsong.title}" to position {newposition}.**',
                        color=(0xFFFF00),
                        timestamp=datetime.datetime.utcnow()
                    )
                    embed.set_footer(
                        text='\u200b',
                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                    )
                    await ctx.send(embed = embed)
                    return
                elif self.is_admin(ctx):
                    if oldposition > player.queue.length or oldposition < 1:
                        embed = discord.Embed(
                            title='**:x: Invalid old position.**',
                            color=(0xFFFF00),
                            timestamp=datetime.datetime.utcnow()
                        )
                        embed.set_footer(
                            text='\u200b',
                            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                        )
                        await ctx.send(embed = embed)
                        return
                    if newposition > player.queue.length or newposition < 1:
                        embed = discord.Embed(
                            title='**:x: Invalid new position.**',
                            color=(0xFFFF00),
                            timestamp=datetime.datetime.utcnow()
                        )
                        embed.set_footer(
                            text='\u200b',
                            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                        )
                        await ctx.send(embed = embed)
                        return
                    oldsong = await player.move_track(oldposition, newposition)
                    embed = discord.Embed(
                        title=f'**An admin moved "{oldsong.title}" to position {newposition}.**',
                        color=(0xFFFF00),
                        timestamp=datetime.datetime.utcnow()
                    )
                    embed.set_footer(
                        text='\u200b',
                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                    )
                    await ctx.send(embed = embed)
                    return
                embed = discord.Embed(
                    title='**:x: There are too many people in this channel for this command to be used.**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
        else:
            embed = discord.Embed(
                title='**:x: You must be in the same channel as the bot to execute this command.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    @move.error
    async def move_error(self, ctx, error):
        if isinstance(error, NoMoreTracks):
            embed = discord.Embed(
                title='**:x: There are no songs in the queue.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
        if isinstance(error, QueueIsEmpty):
            embed = discord.Embed(
                title='**:x: There are no songs in the queue.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
        if isinstance(error, MissingRequiredArgument):
            embed = discord.Embed(
                title='**:x: Use: bc!move <old-position> <new-position> or bc!help move for more info.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(text='\u200b', icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png')
            await ctx.send(embed = embed)
        if isinstance(error, BadArgument):
            embed = discord.Embed(
                title='**:x: Use: bc!move <old-position> <new-position> or bc!help move for more info.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(text='\u200b', icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png')
            await ctx.send(embed = embed)

    @commands.command()
    @commands.is_owner()
    async def remove(self, ctx, number : int):
        player = self.get_player(ctx)
        if ctx.message.author.voice is None:
            embed = discord.Embed(
                title='**:x: You must be in the same channel as the bot to execute this command.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        if player.channel_id is None:
            embed = discord.Embed(
                title='**:x: I am not connected to a voice channel.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        if ctx.message.author.voice.channel.id and ctx.message.author.voice.channel.id == player.channel_id:
            if not player.queue.upcoming:
                raise NoMoreTracks
            if self.length(ctx) < 3:
                if number > player.queue.length or number < 1:
                    embed = discord.Embed(
                        title='**:x: Invalid position.**',
                        color=(0xFFFF00),
                        timestamp=datetime.datetime.utcnow()
                    )
                    embed.set_footer(
                        text='\u200b',
                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                    )
                    await ctx.send(embed = embed)
                    return
                song = await player.remove_track(number)
                embed = discord.Embed(
                    title=f'**:white_check_mark: Removed "{song.title}" from the queue.**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
            else:
                if self.is_dj(ctx):
                    if number > player.queue.length or number < 1:
                        embed = discord.Embed(
                            title='**:x: Invalid position.**',
                            color=(0xFFFF00),
                            timestamp=datetime.datetime.utcnow()
                        )
                        embed.set_footer(
                            text='\u200b',
                            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                        )
                        await ctx.send(embed = embed)
                        return
                    song = await player.remove_track(number)
                    embed = discord.Embed(
                        title=f'**The dj removed "{song.title}" from the queue.**',
                        color=(0xFFFF00),
                        timestamp=datetime.datetime.utcnow()
                    )
                    embed.set_footer(
                        text='\u200b',
                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                    )
                    await ctx.send(embed = embed)
                    return
                elif self.is_admin(ctx):
                    if number > player.queue.length or number < 1:
                        embed = discord.Embed(
                            title='**:x: Invalid position.**',
                            color=(0xFFFF00),
                            timestamp=datetime.datetime.utcnow()
                        )
                        embed.set_footer(
                            text='\u200b',
                            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                        )
                        await ctx.send(embed = embed)
                        return
                    song = await player.remove_track(number)
                    embed = discord.Embed(
                        title=f'**An admin removed "{song.title}" from the queue.**',
                        color=(0xFFFF00),
                        timestamp=datetime.datetime.utcnow()
                    )
                    embed.set_footer(
                        text='\u200b',
                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                    )
                    await ctx.send(embed = embed)
                    return
                embed = discord.Embed(
                    title='**:x: There are too many people in this channel for this command to be used.**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
        else:
            embed = discord.Embed(
                title='**:x: You must be in the same channel as the bot to execute this command.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    @remove.error
    async def remove_error(self, ctx, error):
        if isinstance(error, NoMoreTracks):
            embed = discord.Embed(
                title='**:x: There are no songs in the queue.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
        if isinstance(error, QueueIsEmpty):
            embed = discord.Embed(
                title='**:x: There are no songs in the queue.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
        if isinstance(error, MissingRequiredArgument):
            embed = discord.Embed(
                title='**:x: Use: bc!remove <position> or bc!help remove for more info.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
        if isinstance(error, BadArgument):
            embed = discord.Embed(
                title='**:x: Use: bc!remove <position> or bc!help remove for more info.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    def is_dj(self, ctx):
        player = self.get_player(ctx)
        return player.dj == ctx.author

    def is_admin(self, ctx):
        return ctx.author.guild_permissions.manage_guild

    def length(self, ctx):
        player = self.get_player(ctx)
        channel = self.client.get_channel(int(player.channel_id))
        count = 0
        for member in channel.members:
            if not member.bot:
                count += 1
        return count

    @commands.command()
    async def dj(self, ctx):
        player = self.get_player(ctx)
        if player.channel_id is None:
            embed = discord.Embed(
                title='**:x: I am not connected to a voice channel.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        else:
            embed = discord.Embed(
                title=f'**{player.dj.name} is currently the dj.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    @commands.command()
    async def makedj(self, ctx, member: discord.Member):
        player = self.get_player(ctx)
        if self.is_dj(ctx):
            channel = self.client.get_channel(int(player.channel_id))
            if member in channel.members:
                player.dj = member
                embed = discord.Embed(
                    title=f'**{member.name} is now the dj.**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
            else:
                embed = discord.Embed(
                    title='**:x: Member is not in this channel.**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
        else:
            embed = discord.Embed(
                title='**:x: You are not the dj.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    @makedj.error
    async def makedj_error(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            embed = discord.Embed(
                title='**:x: Use: bc!makedj <@user/id> or bc!help makedj for more info.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
        if isinstance(error, MemberNotFound):
            embed = discord.Embed(
                title='**:x: User not found!**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    @commands.command()
    async def djonly(self, ctx):
        player = self.get_player(ctx)
        if self.is_dj(ctx):
            if player.djonly:
                player.djonly = False
                embed = discord.Embed(
                    title='**:white_check_mark: Dj only mode disabled.**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
            else:
                player.djonly = True
                embed = discord.Embed(
                    title='**:white_check_mark: Dj only mode enabled.**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
        else:
            embed = discord.Embed(
                title='**:x: You are not the dj.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

def setup(client):
    client.add_cog(Music(client))