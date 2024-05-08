import sys
import os
import json
import re
import discord
import random
import asyncio
import itertools
import traceback
import yt_dlp as youtube_dl
from discord import option
from datetime import datetime
from functools import partial
from discord.ext import commands
from async_timeout import timeout
from fake_useragent import UserAgent
from definition.Language import Language
from modules.Spotify import SpotifyAddons
from discord.commands import slash_command
from discord.ui import Button, View, Select
from definition.Classes import Cog_Extension
from definition.JsonProcess import JsonProcess
from modules.SpotifyToYTMusic import ToYTMusicAddons
from youtubesearchpython.__future__ import VideosSearch

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

ytdlopts = {
    'format': 'bestaudio/best',
    'extractaudio': True,
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'dump_single_json': True,
    'default_search': 'auto',
    'add_header': f'User-Agent: {UserAgent().random}',
    'postprocessors': [{"key" : "FFmpegExtractAudio", "preferredcodec" : "mp3", "preferredquality" : "256"}],
    'source_address': '0.0.0.0'  # ipv6 addresses cause issues sometimes
}

ffmpegopts = {
    'before_options': '-nostdin -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn -af loudnorm=I=-16:TP=-1.5:LRA=11,equalizer=f=1000:t=h:width_type=h:width=200:g=-3,compand=attacks=0.4:decays=0.8:points=-80/-900|-45/-15|-15/-15|0/-12'
}

ytdl = youtube_dl.YoutubeDL(ytdlopts)


class VoiceConnectionError(commands.CommandError):
    pass


class InvalidVoiceChannel(VoiceConnectionError):
    pass


class ExtractorError(VoiceConnectionError):
    pass


class ClientException(VoiceConnectionError):
    pass


class YTDLSource(discord.PCMVolumeTransformer):

    def __init__(self, source, *, data, requester):
        super().__init__(source)
        self.requester = requester

        self.title = data.get('title')
        self.web_url = data.get('webpage_url')
        self.thumbnail = data.get('thumbnail')
        self.duration = data.get('duration')

        # YTDL info dicts (data) have other useful information you might want
        # https://github.com/rg3/youtube-dl/blob/master/README.md

    def __getitem__(self, item: str):
        """Allows us to access attributes similar to a dict.
        This is only useful when you are NOT downloading.
        """
        return self.__getattribute__(item)

    @classmethod
    async def create_source(cls, ctx, search: str, language, *, loop, download=False, bot):
        try:
            loop = loop or asyncio.get_event_loop()

            to_run = partial(ytdl.extract_info, url=search, download=download)
            data = await loop.run_in_executor(None, to_run)

            if 'entries' in data:
                # take first item from a playlist
                data = data['entries'][0]

            if 'duration' in data:
                duration_seconds = int(data['duration'])
                hours, remainder = divmod(duration_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                if hours > 0:
                    duration = f"{hours}:{minutes:02d}:{seconds:02d}"
                else:
                    duration = f"{minutes:02d}:{seconds:02d}"
            else:
                duration = None

            if 'thumbnail' in data:
                # 取得影片封面的網址
                thumbnail_url = data['thumbnail']
            else:
                thumbnail_url = None

            embed = discord.Embed(title="", description=f"**{language.get('music_dict_add_queue')}** [{data['title']}]({data['webpage_url']}) [{ctx.author.mention}]", color=0xfeadbc, timestamp=datetime.now())
            embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar.url)
            embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ",icon_url=bot.user.avatar.url)
            if thumbnail_url:
                embed.set_thumbnail(url=thumbnail_url)
            if duration:
                embed.add_field(name=f"{language.get('music_dict_add_duration')}-{duration}", value="", inline=True)  # 在 Embed 中添加時長欄位
            await ctx.edit(embed=embed)

            if download:
                source = ytdl.prepare_filename(data)
            else:
                return {'webpage_url': data['webpage_url'], 'requester': ctx.author, 'title': data['title']}

            return cls(discord.FFmpegPCMAudio(source, **ffmpegopts), data=data, requester=ctx.author)
        except Exception:
            embed = discord.Embed(title=f"**{language.get('music_dict_err_source')}**", description="", color=0xfeadbc)
            await ctx.edit(embed=embed)
            raise ExtractorError("URL analysis error")

    @classmethod
    async def regather_stream(cls, data, *, loop):
        """Used for preparing a stream, instead of downloading.
        Since Youtube Streaming links expire."""
        loop = loop or asyncio.get_event_loop()
        requester = data['requester']

        to_run = partial(ytdl.extract_info, url=data['webpage_url'], download=False)
        data = await loop.run_in_executor(None, to_run)

        return cls(discord.FFmpegPCMAudio(data['url'], **ffmpegopts), data=data, requester=requester)

class task(View):
    def __init__(self, bot, ctx, language):
        super().__init__(timeout=None)
        self.bot = bot
        self.ctx = ctx
        self.language = language
    @discord.ui.button(label='',style=discord.ButtonStyle.blurple, emoji='<:stop_icon:1154418421807718420>', row=1)
    async def button_control(self, button, interaction):
        """Pause the currently playing song."""
        vc = self.ctx.voice_client

        if not vc or not vc.is_connected():
            embed = discord.Embed(title="", description=f"{self.language.get('music_dict_noconnect')}", color=0xfeadbc)
            return await interaction.response.send_message(embed=embed, delete_after=5)
        elif not self.ctx.author.voice:  # 檢查使用者是否在語音頻道中
            embed = discord.Embed(title="", description=f"{self.language.get('music_dict_nojoin')}", color=0xfeadbc)
            return await interaction.response.send_message(embed=embed, delete_after=5)
        elif not vc.is_playing() and not vc.is_paused():
            embed = discord.Embed(title="", description=f"{self.language.get('music_dict_noplay')}", color=0xfeadbc)
            return await interaction.response.send_message(embed=embed, delete_after=5)
        
        player = await Music.get_player(self, self.ctx)

        if not vc.is_playing():
            vc.resume()
            button.emoji='<:stop_icon:1154418421807718420>'
            await interaction.response.edit_message(view = self)
            await interaction.followup.send(f"**<:resume_icon:1154418430691258549> {self.language.get('music_dict_resume')} `{player.current.title}`**")
        elif vc.is_playing():
            vc.pause()
            button.emoji='<:resume_icon:1154418430691258549>'
            await interaction.response.edit_message(view = self)
            await interaction.followup.send(f"**<:stop_icon:1154418421807718420> {self.language.get('music_dict_stop')} `{player.current.title}`**")
        elif vc.is_paused():
            return

    # @discord.ui.button(label='',style=discord.ButtonStyle.blurple, emoji='<:stop_icon:1154418421807718420>')
    # async def Bpause(self, button, interaction):
    #         """Pause the currently playing song."""
    #         vc = self.ctx.voice_client

    #         if not vc or not vc.is_connected():
    #             embed = discord.Embed(title="", description=f"{language.get('music_dict_noconnect')}", color=0xfeadbc)
    #             return await interaction.response.send_message(embed=embed, delete_after=5)
    #         elif not vc.is_playing():
    #             embed = discord.Embed(title="", description=f"{language.get('music_dict_noplay')}", color=0xfeadbc)
    #             return await interaction.response.send_message(embed=embed, delete_after=5)
    #         elif vc.is_paused():
    #             return

    #         vc.pause()
    #         await interaction.response.send_message("**<:stop_icon:1154418421807718420> 暫停**")

    # @discord.ui.button(label='',style=discord.ButtonStyle.blurple, emoji='<:resume_icon:1154418430691258549>')
    # async def Bresume(self, button, interaction):
    #     vc = self.ctx.voice_client

    #     if not vc or not vc.is_connected():
    #         embed = discord.Embed(title="", description=f"{language.get('music_dict_noconnect')}", color=0xfeadbc)
    #         return await interaction.response.send_message(embed=embed, delete_after=5)
    #     elif vc.is_playing():
    #         embed = discord.Embed(title="", description=f"{language.get('music_dict_playing')}", color=0xfeadbc)
    #         return await interaction.response.send_message(embed=embed, delete_after=5)
    #     elif not vc.is_paused():
    #         embed = discord.Embed(title="", description=f"{language.get('music_dict_noplay')}", color=0xfeadbc)
    #         return await interaction.response.send_message(embed=embed, delete_after=5)

    #     vc.resume()
    #     await interaction.response.send_message("**<:resume_icon:1154418430691258549> 繼續**")

    @discord.ui.button(label='',style=discord.ButtonStyle.blurple, emoji='<:skip_icon:1154418419538612444>', row=1)
    async def button_skip(self, button, interaction):
        vc = self.ctx.voice_client
        """Skip the song."""

        if not vc or not vc.is_connected():
            embed = discord.Embed(title="", description=f"{self.language.get('music_dict_noconnect')}", color=0xfeadbc)
            return await interaction.response.send_message(embed=embed, delete_after=5)
        elif not self.ctx.author.voice:  # 檢查使用者是否在語音頻道中
            embed = discord.Embed(title="", description=f"{self.language.get('music_dict_nojoin')}", color=0xfeadbc)
            return await interaction.response.send_message(embed=embed, delete_after=5)

        if vc.is_paused():
            pass
        elif not vc.is_playing():
            embed = discord.Embed(title="", description=f"{self.language.get('music_dict_noplay')}", color=0xfeadbc)
            return await interaction.response.send_message(embed=embed, delete_after=5)
        
        player = await Music.get_player(self, self.ctx)

        vc.stop()
        await interaction.response.send_message(f"**<:skip_icon:1154418419538612444> {self.language.get('music_dict_skip')} `{player.current.title}`**")
        

    @discord.ui.button(label='',style=discord.ButtonStyle.blurple, emoji='<:shuffle_icon:1155177170784755732>', row=1)
    async def button_shuffle(self, button, interaction):
        """打亂目前的播放列表"""

        vc = self.ctx.voice_client

        if not vc or not vc.is_connected():
            embed = discord.Embed(title="", description=f"{self.language.get('music_dict_noconnect')}", color=0xfeadbc)
            return await interaction.response.send_message(embed=embed, delete_after=5)
        elif not self.ctx.author.voice:  # 檢查使用者是否在語音頻道中
            embed = discord.Embed(title="", description=f"{self.language.get('music_dict_nojoin')}", color=0xfeadbc)
            return await interaction.response.send_message(embed=embed, delete_after=5)

        player = await Music.get_player(self, self.ctx)

        if player.queue.empty():
            embed = discord.Embed(title="", description=f"{self.language.get('music_dict_shuffle_empty_msg')}", color=0xfeadbc)
            return await interaction.response.send_message(embed=embed)

        # 從原佇列中取出元素，並放入一個臨時的 list 中
        queue_list = []
        while not player.queue.empty():
            item = await player.queue.get()
            queue_list.append(item)

        # 打亂 list 中的項目
        random.shuffle(queue_list)

        # 將打亂後的項目重新放回佇列中
        for item in queue_list:
            await player.queue.put(item)

        await interaction.response.send_message(f"**<:shuffle_icon:1155177170784755732> {self.language.get('music_dict_shuffle_queue_msg')}**")

    @discord.ui.button(label='',style=discord.ButtonStyle.grey, emoji='<:add_icon:1154418424634675201>', row=2)
    async def button_add_volume(self, button, interaction):
        vc = self.ctx.voice_client

        if not vc or not vc.is_connected():
            embed = discord.Embed(title="", description=f"{self.language.get('music_dict_noconnect')}", color=0xfeadbc)
            return await interaction.response.send_message(embed=embed, delete_after=5)
        elif not self.ctx.author.voice:  # 檢查使用者是否在語音頻道中
            embed = discord.Embed(title="", description=f"{self.language.get('music_dict_nojoin')}", color=0xfeadbc)
            return await interaction.response.send_message(embed=embed, delete_after=5)
        elif not vc.is_playing():
            embed = discord.Embed(title="", description=f"{self.language.get('music_dict_noplay')}", color=0xfeadbc)
            return await interaction.response.send_message(embed=embed, delete_after=5)

        current_volume = vc.source.volume * 100
        if current_volume == 100:
            embed = discord.Embed(title="", description=f"**<:add_icon:1154418424634675201> {self.language.get('music_dict_add')}**", color=0xfeadbc)
        else:
            new_volume = round(current_volume + 10, 2)
            if new_volume > 100:
                new_volume = 100
            vc.source.volume = new_volume / 100
            embed = discord.Embed(title="", description=f"**`{interaction.user}`** **{self.language.get('music_dict_volume_setting')} {new_volume}%**", color=0xfeadbc)

            player = await Music.get_player(self, self.ctx)

            player.volume = new_volume / 100

        await interaction.response.send_message(embed=embed, delete_after=5)

    @discord.ui.button(label='',style=discord.ButtonStyle.grey, emoji='<:reduce_icon:1154418428308893849>', row=2)
    async def button_reduce_volume(self, button, interaction):
        vc = self.ctx.voice_client

        if not vc or not vc.is_connected():
            embed = discord.Embed(title="", description=f"{self.language.get('music_dict_noconnect')}", color=0xfeadbc)
            return await interaction.response.send_message(embed=embed, delete_after=5)
        elif not self.ctx.author.voice:  # 檢查使用者是否在語音頻道中
            embed = discord.Embed(title="", description=f"{self.language.get('music_dict_nojoin')}", color=0xfeadbc)
            return await interaction.response.send_message(embed=embed, delete_after=5)
        elif not vc.is_playing():
            embed = discord.Embed(title="", description=f"{self.language.get('music_dict_noplay')}", color=0xfeadbc)
            return await interaction.response.send_message(embed=embed, delete_after=5)

        current_volume = vc.source.volume * 100
        if current_volume == 0:
            embed = discord.Embed(title="", description=f"**<:reduce_icon:1154418428308893849> {self.language.get('music_dict_reduce')}**", color=0xfeadbc)
        else:
            new_volume = round(current_volume - 10, 2)
            if new_volume < 0:
                new_volume = 0
            vc.source.volume = new_volume / 100
            embed = discord.Embed(title="", description=f"**`{interaction.user}`** **{self.language.get('music_dict_volume_setting')} {new_volume}%**", color=0xfeadbc)

            player = await Music.get_player(self, self.ctx)

            player.volume = new_volume / 100
        
        await interaction.response.send_message(embed=embed, delete_after=5)

    @discord.ui.button(label='',style=discord.ButtonStyle.red, emoji='<:bye_icon:1163025984187019294>', row=2)
    async def button_stop(self, button, interaction):
        vc = self.ctx.voice_client

        if not vc or not vc.is_connected():
            embed = discord.Embed(title="", description=f"{self.language.get('music_dict_noconnect')}", color=0xfeadbc)
            return await interaction.response.send_message(embed=embed, delete_after=5)
        elif not self.ctx.author.voice:  # 檢查使用者是否在語音頻道中
            embed = discord.Embed(title="", description=f"{self.language.get('music_dict_nojoin')}", color=0xfeadbc)
            return await interaction.response.send_message(embed=embed, delete_after=5)
        else:
            guild = self.ctx.guild
            await interaction.response.send_message(f"**<:bye_icon:1163025984187019294> {self.language.get('music_dict_disconnect')}**")
            await Music.cleanup(self, guild)

class MusicPlayer:
    """A class which is assigned to each guild using the bot for Music.
    This class implements a queue and loop, which allows for different guilds to listen to different playlists
    simultaneously.
    When the bot disconnects from the Voice it's instance will be destroyed.
    """

    __slots__ = ('bot', '_guild', '_channel', '_cog', '_loop', 'queue', 'next', 'language', 'current', 'np', 'volume')

    def __init__(self, ctx):
        self.bot = ctx.bot
        self._guild = ctx.guild
        self._channel = ctx.channel
        self._cog = ctx.cog
        self._loop = False

        self.queue = asyncio.Queue()
        self.next = asyncio.Event()
        self.language = Language()

        self.np = None  # Now playing message
        self.volume = None
        self.current = None

        ctx.bot.loop.create_task(self.player_loop(ctx))

    async def set_volume(self, ctx):
        volume_file_path = os.path.join("database", "volume.json")
        data = await JsonProcess(volume_file_path).read_json()
        if str(ctx.guild.id) in data:
            self.volume = data[str(ctx.guild.id)] / 100
        else:
            data[str(ctx.guild.id)] = 100.0
            await JsonProcess(self.file).write_json(self.data)
            self.volume = data[str(ctx.guild.id)] / 100

    async def player_loop(self, ctx):
        """Our main player loop."""
        await self.bot.wait_until_ready()

        await self.set_volume(ctx)

        language = await self.language.language_music_msg(ctx.guild.id)

        while not self.bot.is_closed():
            self.next.clear()

            try:
                # Wait for the next song. If we timeout cancel the player and disconnect...
                async with timeout(300):  # 5 minutes...
                    source = await self.queue.get()
            except asyncio.TimeoutError:
                return self.destroy(self._guild)

            if not isinstance(source, YTDLSource):
                # Source was probably a stream (not downloaded)
                # So we should regather to prevent stream expiration
                try:
                    source = await YTDLSource.regather_stream(source, loop=self.bot.loop)
                except Exception as e:
                    await self._channel.send(f"{language.get('music_dict_process_err_msg')}\n"
                                             f"```css\n[{e}]\n```")
                    continue

            source.volume = self.volume
            self.current = source

            try:
                self._guild.voice_client.play(source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))
            except Exception:
                await Music.cleanup(self, self._guild)
                source.cleanup()
                self._loop = False
                self.current = None
                raise ClientException("Accidental operation")

            embed = discord.Embed(title=f"{language.get('music_dict_playing')}", description=f"[{source.title}]({source.web_url}) [{source.requester.mention}]", color=0xfeadbc, timestamp=datetime.now())
            embed.set_author(name=f"{ctx.author.name}", icon_url=source.requester.avatar.url)
            embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ",icon_url=self.bot.user.avatar.url)
            if source.thumbnail:
                embed.set_thumbnail(url=source.thumbnail)
            if source.duration:
                duration_seconds = int(source.duration)
                hours, remainder = divmod(duration_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                if hours > 0:
                    duration = f"{hours}:{minutes:02d}:{seconds:02d}"
                else:
                    duration = f"{minutes:02d}:{seconds:02d}"
                embed.add_field(name='', value=f"00:00 <:start_icon:1155132881845366795><:pink_icon:1155393951331790900><:pink_icon:1155393951331790900><:fill_icon:1162999844877631569><:black_icon:1155132884798160998><:black_icon:1155132884798160998><:black_icon:1155132884798160998><:black_icon:1155132884798160998><:black_icon:1155132884798160998><:black_icon:1155132884798160998><:black_icon:1155132884798160998><:black_icon:1155132884798160998><:black_icon:1155132884798160998><:end_icon:1155132886563946516> {duration}", inline=True)  # 在 Embed 中添加時長欄位
            self.np = await self._channel.send(embed=embed,view=task(self.bot, ctx, language))
            await self.next.wait()

            # Make sure the FFmpeg process is cleaned up.
            source.cleanup()
            self.current = None

    def destroy(self, guild):
        """Disconnect and cleanup the player."""
        return self.bot.loop.create_task(self._cog.cleanup(guild))


class Music(Cog_Extension):
    @commands.Cog.listener()
    async def on_ready(self):
        now = datetime.now()
        day=now.strftime("%Y-%m-%d %H:%M:%S")
        print (f'{day}-Music has loaded')

    """Music related commands."""

    global players
    players = {}

    async def cleanup(self, guild):
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass

        try:
            del players[guild.id]
        except KeyError:
            pass

    async def join_channel(self, ctx, language, channel=None):
        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                embed = discord.Embed(title="", description=f"{language.get('music_dict_nomember_join_msg')}", color=0xfeadbc)
                await ctx.respond(embed=embed)
                raise InvalidVoiceChannel(f"{language.get('music_dict_nojoin_msg')}")

        vc = ctx.voice_client

        if vc:
            if vc.channel.id == channel.id:
                embed = discord.Embed(title="", description=f"{language.get('music_dict_already')}", color=0xfeadbc)
                return await ctx.respond(embed=embed)
            try:
                await vc.move_to(channel)
            except asyncio.TimeoutError:
                raise VoiceConnectionError(f'Move to channel: <{channel}> timed out.')
        else:
            try:
                await channel.connect()
            except asyncio.TimeoutError:
                raise VoiceConnectionError(f'Connecting to channel: <{channel}> timed out.')
            
        await ctx.guild.change_voice_state(channel=channel, self_deaf=True)

        return channel
    
    async def song_list_from_db(self, ctx):
        """Returns list of items from db, sorted in such a way that Pycord can autocomplete"""
        song_file_path = os.path.join("database", "song.json")
        with open(song_file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        options = []
        if str(ctx.interaction.user.id) in data:
            user_data = data[str(ctx.interaction.user.id)]
            videos = user_data["video"]

            for video_opt in videos:
                options.append(video_opt["name"])

        return options

    async def song_search(self, ctx):
        """Returns list of items from video title, sorted in such a way that Pycord can autocomplete"""

        options = []
        if ctx.value:
            if re.compile(r'https?://\S+').match(ctx.value):
                pass
            else:
                videos_result = await VideosSearch(ctx.value, limit = 10).next()
                if 'result' in videos_result:
                    result = videos_result['result']
                    for entry in result:
                        if 'title' in entry:
                            options.append(entry['title'])
        return options
    
    async def load_source_defer(self, ctx, language):
        embed = discord.Embed(title=f"**<:load:1140493383828262983> {language.get('music_dict_loading_source')}**", description="", color=0xfeadbc)
        await ctx.respond(embed=embed)

    async def get_music_source(self, ctx, url):
        language = await Language().language_music_msg(ctx.guild.id)
        if re.compile(r'https://open.spotify.com/(track|album|playlist)/[a-zA-Z0-9]+').match(url):
            item_type, item_id = await SpotifyAddons().parse_spotify_url(url)
            songs = await SpotifyAddons().fetch_tracks(item_type, item_id)

            url = await ToYTMusicAddons().to_ytmusic(songs)
        
        source = await YTDLSource.create_source(ctx, url, language, loop=self.bot.loop, download=False, bot=self.bot)
        return source

    async def loop_source(self, ctx, player):
        while player._loop:
            try:
                if player.queue.empty():
                    url = player.current.web_url
                    await asyncio.wait_for(player.next.wait(), timeout=None)
                    if ctx.voice_client or ctx.voice_client.is_connected():
                        source = await self.get_music_source(ctx, url)
                        await player.queue.put(source)

                else:
                    upcoming = list(itertools.islice(player.queue._queue, 0, int(len(player.queue._queue))))
                    # Keep track of unique titles
                    unique_titles = []
                    for _ in upcoming:
                        webpage_url = _['webpage_url']
                        if webpage_url in unique_titles:
                            # If title is not unique, add a suffix to the number
                            unique_titles.append(webpage_url)
                        else:
                            # If title is unique, add it to the list of unique titles
                            unique_titles.append(webpage_url)
                                
                    for i in range(len(unique_titles)):
                        await asyncio.wait_for(player.next.wait(), timeout=None)
                        source = await self.get_music_source(ctx, unique_titles[i])
                        await player.queue.put(source)    
                    
            except:
                embed = discord.Embed(title="Unable to retrieve the song you are playing", description="", color=0xfeadbc)
                player._loop = False
                return await ctx.edit(embed=embed)
            
        unique_titles.clear()
        player.queue._queue.clear()

    async def json_process(self):
        song_file_path = os.path.join("database", "song.json")
        async def read_json():
            data = await JsonProcess(song_file_path).read_json()
            return data
        async def write_json(data):
            await JsonProcess(song_file_path).write_json(data)
            return 
        return read_json, write_json

    async def __local_check(self, ctx):
        """A local check which applies to all commands in this cog."""
        if not ctx.guild:
            raise commands.NoPrivateMessage
        return True

    async def __error(self, ctx, error):
        """A local error handler for all errors arising from commands in this cog."""
        language = await Language().language_music_msg(ctx.guild.id)
        if isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.send(f"{language.get('music_dict_private_command_msg')}")
            except discord.HTTPException:
                pass
        elif isinstance(error, InvalidVoiceChannel):
            await ctx.send(f"{language.get('music_dict_private_command_msg')}")

        print('Ignore exceptions in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    async def get_player(self, ctx):
        """Retrieve the guild player, or generate one."""
        try:
            player = players[ctx.guild.id]
        except KeyError:
            player = MusicPlayer(ctx)
            players[ctx.guild.id] = player

        return player

    @slash_command(name="join", description="connects to voice")
    @option("channel", description="Please select a voice channel")
    #@commands.command(name='join', aliases=['connect', 'j'], description="connects to voice")
    async def connect_(self, ctx, channel: discord.VoiceChannel=None):
        """Connect to voice.
        Parameters
        ------------
        channel: discord.VoiceChannel [Optional]
            The channel to connect to. If a channel is not specified, an attempt to join the voice channel you are in
            will be made.
        This command also handles moving the bot to different channels.
        """

        await ctx.trigger_typing()

        language = await Language().language_music_msg(ctx.guild.id)

        channel = await self.join_channel(ctx, language, channel)

        await ctx.respond(f'**<:night_sakura_logo:1179751919347060787> join the {channel.mention}**')

    @slash_command(name="play", description="play music")
    @option("search",description="Please enter a valid link or keyword", autocomplete=song_search)
    #@commands.command(name='play', aliases=['sing','p'], description="streams music")
    async def play_(self, ctx, *, search: str):
        """Request a song and add it to the queue.
        This command attempts to join a valid voice channel if the bot is not already in one.
        Uses YTDL to automatically search and retrieve a song.
        Parameters
        ------------
        search: str [Required]
            The song to search and retrieve using YTDL. This could be a simple search, an ID or URL.
        """
        await ctx.trigger_typing()

        vc = ctx.voice_client

        language = await Language().language_music_msg(ctx.guild.id)

        if not vc:
            await self.join_channel(ctx, language)

        await self.load_source_defer(ctx, language)

        player = await self.get_player(ctx)

        if player._loop is True:
            return await ctx.respond(f"Loop mode is already active, and I can't add music")

        # If download is False, source will be a dict which will be used later to regather the stream.
        # If download is True, source will be a discord.FFmpegPCMAudio with a VolumeTransformer.
        source = await self.get_music_source(ctx, search)

        await player.queue.put(source)

    @slash_command(name="loop", description="loop mode(beta release)")
    async def loop_(self, ctx):
        await ctx.trigger_typing()

        vc = ctx.voice_client

        language = await Language().language_music_msg(ctx.guild.id)

        if not vc or not vc.is_connected():
            embed = discord.Embed(title="", description=f"{language.get('music_dict_noconnect')}", color=0xfeadbc)
            return await ctx.respond(embed=embed)
        elif not ctx.author.voice:
            embed = discord.Embed(title="", description=f"{language.get('music_dict_nojoin')}", color=0xfeadbc)
            return await ctx.respond(embed=embed)

        player = await self.get_player(ctx)

        player._loop = not player._loop  # Toggle the loop value
        embed_title = "loop is on" if player._loop else "loop is off"
        embed = discord.Embed(title=embed_title, description="", color=0xfeadbc)
        await ctx.respond(embed=embed)

        await self.loop_source(ctx, player)

    @slash_command(name="pl-add", description="Add music playlist", autocomplete=song_search)
    @option("search", description="Please enter a valid link or keyword")
    async def songadd_(self, ctx, *, search: str):
        language = await Language().language_music_msg(ctx.guild.id)
        await ctx.defer(ephemeral = True)
        try:
            if re.compile(r'https://open.spotify.com/(track|album|playlist)/[a-zA-Z0-9]+').match(search):
                item_type, item_id = await SpotifyAddons().parse_spotify_url(search)
                songs = await SpotifyAddons().fetch_tracks(item_type, item_id)
                search = await ToYTMusicAddons().to_ytmusic(songs)

            to_run = partial(ytdl.extract_info, url=search, download=False)
            info_dict = await asyncio.get_event_loop().run_in_executor(None, to_run)

            if 'entries' in info_dict:
                # take first item from a playlist
                info_dict = info_dict['entries'][0]
            
            video_title = info_dict['title']
            video_url = info_dict['webpage_url']

            read_json, write_json = await self.json_process()
            data = await read_json()

            if str(ctx.author.id) in data:
                user_data = data[str(ctx.author.id)]
                if user_data["index"] >= 25:
                    embed = discord.Embed(title=f"{ctx.author.name}", description=f"{language.get('music_dict_songlist_over_msg')}", color=0xfeadbc, timestamp=datetime.now())
                    embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ", icon_url=self.bot.user.avatar.url)
                    return await ctx.respond(embed=embed)
                else:
                    existing_songs = [
                        song["name"]
                        for song in user_data["video"]
                    ]
                    if video_title in existing_songs:
                        embed = discord.Embed(title=f"{ctx.author.name}",description=f"{language.get('music_dict_songlist_exist_msg')}",color=0xfeadbc,timestamp=datetime.now())
                        embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ", icon_url=self.bot.user.avatar.url)
                        return await ctx.respond(embed=embed)
                    else:
                        user_data["index"] += 1  # 自增index值
                        user_data["video"].append({"name": video_title, "url": video_url})
            else:
                data[str(ctx.author.id)] = {"index": 1, "video": [{"name": video_title, "url": video_url}]}
            
            await write_json(data)

            embed = discord.Embed(title=f"{ctx.author.name}", color=0xfeadbc, timestamp=datetime.now())
            embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ", icon_url=self.bot.user.avatar.url)
            embed.add_field(name=f"{language.get('music_dict_add_songlist_msg')}", value=f"[{video_title}]({video_url})", inline=False)
            await ctx.respond(embed=embed)

        except:
            embed = discord.Embed(title=f"{ctx.author.name}", description=f"{language.get('music_dict_err_loading_msg')}", color=0xfeadbc, timestamp=datetime.now())
            embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ",icon_url=self.bot.user.avatar.url)
            await ctx.respond(embed=embed)

    @slash_command(name="pl-show", description="Show songs in the playlist")
    async def songlist_(self, ctx):
        language = await Language().language_music_msg(ctx.guild.id)
        await ctx.defer(ephemeral = True)
        read_json, write_json = await self.json_process()
        data = await read_json()

        if str(ctx.author.id) in data:
            user_data = data[str(ctx.author.id)]
            videos = user_data["video"]

            options = []
            for video_opt in videos:
                option = discord.SelectOption(
                    label=video_opt["name"],
                    description=video_opt["url"],
                )
                options.append(option)

            song = Select(
                placeholder=language.get('music_dict_songlist_select_placeholder'),
                options=options
            )

            async def song_menu(interaction):
                selected_value = song.values[0]

                # 根据选择的值查找匹配的视频信息
                video = next((video for video in videos if video["name"] == selected_value and video["url"]), None)
                if video:
                    video_url = video["url"]
                    embed = discord.Embed(title=selected_value, description=video_url, color=0xfeadbc, timestamp=datetime.now())
                    embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ", icon_url=self.bot.user.avatar.url)
                    await interaction.response.send_message(embed=embed, ephemeral = True)

                else:
                    return await interaction.response.send_message(f"{language.get('music_dict_nofound_songlist_url')}")
                
                await ctx.edit(content=f"{ctx.author.name}{language.get('music_dict_show_songlist_msg')}", view=view)

            song.callback = song_menu
            view = View(timeout=None)
            view.add_item(song)
            await ctx.respond(f"{ctx.author.name}{language.get('music_dict_show_songlist_msg')}", view=view)
        else:
            embed = discord.Embed(title=f"{ctx.author.name}", description=f"{language.get('music_dict_nofound_songlist_data')}", color=0xfeadbc, timestamp=datetime.now())
            embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ", icon_url=self.bot.user.avatar.url)
            await ctx.respond(embed=embed)

    @slash_command(name="pl-play", description="Play songs from the playlist")
    @option("songs", description="Please select music from the playlist", autocomplete = song_list_from_db)
    async def songplay_(self, ctx, songs: str):
        await ctx.trigger_typing()
        language = await Language().language_music_msg(ctx.guild.id)
        
        vc = ctx.voice_client

        if not vc:
            await self.join_channel(ctx, language)
        
        read_json, write_json = await self.json_process()
        data = await read_json()

        if str(ctx.author.id) in data:
            user_data = data[str(ctx.author.id)]
            videos = user_data["video"]
        else:
            embed = discord.Embed(title=f"{ctx.author.name}", description=f"{language.get('music_dict_nofound_songlist_data')}", color=0xfeadbc, timestamp=datetime.now())
            embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ", icon_url=self.bot.user.avatar.url)
            return await ctx.respond(embed=embed)

        video = next((video for video in videos if video["name"] == songs), None)
        if video:
            video_url = video["url"]

        else:
            return await ctx.respond(f"{language.get('music_dict_nofound_songlist_url')}")

        await self.load_source_defer(ctx, language)

        player = await self.get_player(ctx)

        if player._loop is True:
            return await ctx.respond(f"Loop mode is already active, and I can't add music")

        # If download is False, source will be a dict which will be used later to regather the stream.
        # If download is True, source will be a discord.FFmpegPCMAudio with a VolumeTransformer.
        source = await self.get_music_source(ctx, video_url)

        await player.queue.put(source)

    @slash_command(name="pl-del", description="Remove songs from the playlist")
    @option("songs", description="Please select music from the playlist", autocomplete = song_list_from_db)
    async def songdel_(self, ctx, songs: str):
        language = await Language().language_music_msg(ctx.guild.id)
        await ctx.defer()

        read_json, write_json = await self.json_process()
        data = await read_json()

        if str(ctx.author.id) in data:
            user_data = data[str(ctx.author.id)]
            videos = user_data["video"]

            # 根据选择的值查找匹配的视频信息
            video = next((video for video in videos if video["name"] == songs), None)

            if video:
                # 从列表中删除对应的视频信息
                if user_data["index"] == 1:
                    video_url = video["url"]
                    del data[str(ctx.author.id)]
                else:
                    video_url = video["url"]
                    videos.remove(video)
                    user_data["index"] -= 1

                await write_json(data)
                    
                embed = discord.Embed(title=f"{ctx.author.name}", color=0xfeadbc, timestamp=datetime.now())
                embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ", icon_url=self.bot.user.avatar.url)
                embed.add_field(name=f"{language.get('music_dict_show_songlist_del')}", value=f"[{songs}]({video_url})", inline=False)
                await ctx.respond(embed=embed, ephemeral = True)
            else:
                return await ctx.respond(f"{language.get('music_dict_nofound_songlist_song')}")
                
        else:
            embed = discord.Embed(title=f"{ctx.author.name}", description=f"{language.get('music_dict_nofound_songlist_data')}", color=0xfeadbc, timestamp=datetime.now())
            embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ", icon_url=self.bot.user.avatar.url)
            await ctx.respond(embed=embed)

    @slash_command(name="shuffle", description="Shuffle the current playlist")
    async def shuffle_(self, ctx):
        """打亂目前的播放列表"""

        await ctx.trigger_typing()

        await ctx.defer()

        vc = ctx.voice_client
        
        language = await Language().language_music_msg(ctx.guild.id)

        if not vc or not vc.is_connected():
            embed = discord.Embed(title="", description=f"{language.get('music_dict_noconnect')}", color=0xfeadbc)
            return await ctx.respond(embed=embed)
        elif not ctx.author.voice:  # 檢查使用者是否在語音頻道中
            embed = discord.Embed(title="", description=f"{language.get('music_dict_nojoin')}", color=0xfeadbc)
            return await ctx.respond(embed=embed)

        player = await self.get_player(ctx)

        if player.queue.empty():
            embed = discord.Embed(title="", description=f"{language.get('music_dict_shuffle_empty_msg')}", color=0xfeadbc)
            return await ctx.respond(embed=embed)

        # 從原佇列中取出元素，並放入一個臨時的 list 中
        queue_list = []
        while not player.queue.empty():
            item = await player.queue.get()
            queue_list.append(item)

        # 打亂 list 中的項目
        random.shuffle(queue_list)

        # 將打亂後的項目重新放回佇列中
        for item in queue_list:
            await player.queue.put(item)

        embed = discord.Embed(title="", description=f"{language.get('music_dict_shuffle_queue_msg')}", color=0xfeadbc)
        await ctx.respond(embed=embed)

    @slash_command(name="insert", description="Insert a song at the beginning of the current playlist")
    @option("search", description="Please enter a valid link or keyword", autocomplete=song_search)
    async def insert_(self, ctx, *, search: str):
        """在目前播放的歌曲後插入一首歌曲"""

        await ctx.trigger_typing()

        vc = ctx.voice_client

        language = await Language().language_music_msg(ctx.guild.id)

        if not vc or not vc.is_connected():
            embed = discord.Embed(title="", description=f"{language.get('music_dict_noconnect')}", color=0xfeadbc)
            return await ctx.respond(embed=embed)
        elif not ctx.author.voice:  # 檢查使用者是否在語音頻道中
            embed = discord.Embed(title="", description=f"{language.get('music_dict_nojoin')}", color=0xfeadbc)
            return await ctx.respond(embed=embed)
        
        await self.load_source_defer(ctx, language)

        player = await self.get_player(ctx)

        if player._loop is True:
            return await ctx.respond(f"Loop mode is already active, and I can't add music")

        # 創建 YTDLSource 物件並加入佇列中，指定插入到最上面
        source = await self.get_music_source(ctx, search)

        player.queue._queue.appendleft(source)
        
    @slash_command(name="pause", description="pauses music")
    #@commands.command(name='pause', description="pauses music")
    async def pause_(self, ctx):
        """Pause the currently playing song."""
        vc = ctx.voice_client

        language = await Language().language_music_msg(ctx.guild.id)

        if not vc or not vc.is_connected():
            embed = discord.Embed(title="", description=f"{language.get('music_dict_noconnect')}", color=0xfeadbc)
            return await ctx.respond(embed=embed)
        elif not ctx.author.voice:  # 檢查使用者是否在語音頻道中
            embed = discord.Embed(title="", description=f"{language.get('music_dict_nojoin')}", color=0xfeadbc)
            return await ctx.respond(embed=embed)
        elif not vc.is_playing():
            embed = discord.Embed(title="", description=f"{language.get('music_dict_noplay')}", color=0xfeadbc)
            return await ctx.respond(embed=embed)
        elif vc.is_paused():
            return

        player = await self.get_player(ctx)

        vc.pause()
        await ctx.respond(f"**<:stop_icon:1154418421807718420> {language.get('music_dict_stop')} `{player.current.title}`**")

    @slash_command(name="resume", description="resumes music")
    #@commands.command(name='resume', description="resumes music")
    async def resume_(self, ctx):
        """Resume the currently paused song."""
        vc = ctx.voice_client

        language = await Language().language_music_msg(ctx.guild.id)

        if not vc or not vc.is_connected():
            embed = discord.Embed(title="", description=f"{language.get('music_dict_noconnect')}", color=0xfeadbc)
            return await ctx.respond(embed=embed)
        elif not ctx.author.voice:  # 檢查使用者是否在語音頻道中
            embed = discord.Embed(title="", description=f"{language.get('music_dict_nojoin')}", color=0xfeadbc)
            return await ctx.respond(embed=embed)
        elif vc.is_playing():
            embed = discord.Embed(title="", description=f"{language.get('music_dict_playing')}", color=0xfeadbc)
            return await ctx.respond(embed=embed)
        elif not vc.is_paused():
            embed = discord.Embed(title="", description=f"{language.get('music_dict_noplay')}", color=0xfeadbc)
            return await ctx.respond(embed=embed)

        player = await self.get_player(ctx)

        vc.resume()
        await ctx.respond(f"**<:resume_icon:1154418430691258549> {language.get('music_dict_resume')} `{player.current.title}`**")

    @slash_command(name="skip", description="skips to next song in queue")
    #@commands.command(name='skip', description="skips to next song in queue")
    async def skip_(self, ctx):
        """Skip the song."""
        vc = ctx.voice_client

        language = await Language().language_music_msg(ctx.guild.id)

        if not vc or not vc.is_connected():
            embed = discord.Embed(title="", description=f"{language.get('music_dict_noconnect')}", color=0xfeadbc)
            return await ctx.respond(embed=embed)
        elif not ctx.author.voice:  # 檢查使用者是否在語音頻道中
            embed = discord.Embed(title="", description=f"{language.get('music_dict_nojoin')}", color=0xfeadbc)
            return await ctx.respond(embed=embed)

        if vc.is_paused():
            pass
        elif not vc.is_playing():
            embed = discord.Embed(title="", description=f"{language.get('music_dict_noplay')}", color=0xfeadbc)
            return await ctx.respond(embed=embed)
        
        player = await self.get_player(ctx)

        vc.stop()
        await ctx.respond(f"**<:skip_icon:1154418419538612444> {language.get('music_dict_skip')} `{player.current.title}`**")

    @slash_command(name="remove", description="removes specified song from queue")
    @option("number",description="Please enter the queue number")
    #@commands.command(name='remove', aliases=['rm', 'rem'], description="removes specified song from queue")
    async def remove_(self, ctx, number: int):
        """Removes specified song from queue"""
        vc = ctx.voice_client

        language = await Language().language_music_msg(ctx.guild.id)

        if not vc or not vc.is_connected():
            embed = discord.Embed(title="", description=f"{language.get('music_dict_noconnect')}", color=0xfeadbc)
            return await ctx.respond(embed=embed)
        elif not ctx.author.voice:  # 檢查使用者是否在語音頻道中
            embed = discord.Embed(title="", description=f"{language.get('music_dict_nojoin')}", color=0xfeadbc)
            return await ctx.respond(embed=embed)

        player = await self.get_player(ctx)
        
        try:
            s = player.queue._queue[number-1]
            del player.queue._queue[number-1]
            embed = discord.Embed(title="", description=f"{language.get('music_dict_queue_number_msg')} [{s['title']}]({s['webpage_url']}) [{s['requester'].mention}]", color=0xfeadbc)
            await ctx.respond(embed=embed)
        except:
            embed = discord.Embed(title="", description=f"'{language.get('music_dict_queue_nofound_msg')} '{number}'", color=0xfeadbc)
            await ctx.respond(embed=embed)

    @slash_command(name="clear", description="clears entire queue")    
    #@commands.command(name='clear', aliases=['clr', 'cl', 'cr'], description="clears entire queue")
    async def clear_(self, ctx):
        """Deletes entire queue of upcoming songs."""
        vc = ctx.voice_client

        language = await Language().language_music_msg(ctx.guild.id)

        if not vc or not vc.is_connected():
            embed = discord.Embed(title="", description=f"{language.get('music_dict_noconnect')}", color=0xfeadbc)
            return await ctx.respond(embed=embed)
        elif not ctx.author.voice:  # 檢查使用者是否在語音頻道中
            embed = discord.Embed(title="", description=f"{language.get('music_dict_nojoin')}", color=0xfeadbc)
            return await ctx.respond(embed=embed)

        player = await self.get_player(ctx)
        player.queue._queue.clear()
        await ctx.respond(f"**<:night_sakura_logo:1179751919347060787> {language.get('music_dict_queue_clear_msg')}**")

    @slash_command(name="queue", description="shows the queue")
    #@commands.command(name='queue', aliases=['q', 'playlist', 'que'], description="shows the queue")
    async def queue_info(self, ctx):
        """Retrieve a basic queue of upcoming songs."""
        vc = ctx.voice_client

        language = await Language().language_music_msg(ctx.guild.id)

        if not vc or not vc.is_connected():
            embed = discord.Embed(title="", description=f"{language.get('music_dict_noconnect')}", color=0xfeadbc)
            return await ctx.respond(embed=embed)
        elif not ctx.author.voice:  # 檢查使用者是否在語音頻道中
            embed = discord.Embed(title="", description=f"{language.get('music_dict_nojoin')}", color=0xfeadbc)
            return await ctx.respond(embed=embed)

        player = await self.get_player(ctx)
        if player.queue.empty():
            embed = discord.Embed(title="", description=f"{language.get('music_dict_shuffle_empty_msg')}", color=0xfeadbc)
            return await ctx.respond(embed=embed)
        
        seconds = vc.source.duration % (24 * 3600) 
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        if hour > 0:
            duration = "%dh %02dm %02ds" % (hour, minutes, seconds)
        else:
            duration = "%02dm %02ds" % (minutes, seconds)

        # Grabs the songs in the queue...
        upcoming = list(itertools.islice(player.queue._queue, 0, int(len(player.queue._queue))))

        # Keep track of unique titles
        unique_titles = []

        fmt = ''
        index = 1
        for _ in upcoming:
            title = _['title']
            if title in unique_titles:
                # If title is not unique, add a suffix to the number
                unique_titles.append(title)
            else:
                # If title is unique, add it to the list of unique titles
                unique_titles.append(title)
            fmt += f"`{index}.` [{title}]({_['webpage_url']})\n"
            index += 1

        fmt = f"\n__{language.get('music_dict_playing')}__:\n[{vc.source.title}]({vc.source.web_url}) | `{duration}`\n\n__{language.get('music_dict_next_song_msg')}__\n" + fmt + f"\n**{len(upcoming)} {language.get('music_dict_in_queue_msg')}**"
        embed = discord.Embed(title=f"", description=fmt, color=0xfeadbc)
        embed.set_author(name=f"{ctx.guild.name}{language.get('music_dict_playlist_msg')}", icon_url=ctx.guild.icon.url)
        #embed.set_footer(text=f"{ctx.author.display_name}")

        await ctx.respond(embed=embed)

    @slash_command(name="current", description="shows the current")  
    #@commands.command(name='np', aliases=['song', 'current', 'currentsong', 'playing'], description="shows the current playing song")
    async def now_playing_(self, ctx):
        """Display information about the currently playing song."""
        vc = ctx.voice_client

        language = await Language().language_music_msg(ctx.guild.id)

        if not vc or not vc.is_connected():
            embed = discord.Embed(title="", description=f"{language.get('music_dict_noconnect')}", color=0xfeadbc)
            return await ctx.respond(embed=embed)
        elif not ctx.author.voice:  # 檢查使用者是否在語音頻道中
            embed = discord.Embed(title="", description=f"{language.get('music_dict_nojoin')}", color=0xfeadbc)
            return await ctx.respond(embed=embed)

        player = await self.get_player(ctx)
        if not player.current:
            embed = discord.Embed(title="", description=f"{language.get('music_dict_noplay')}", color=0xfeadbc)
            return await ctx.respond(embed=embed)
        
        seconds = vc.source.duration % (24 * 3600) 
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        if hour > 0:
            duration = "%dh %02dm %02ds" % (hour, minutes, seconds)
        else:
            duration = "%02dm %02ds" % (minutes, seconds)

        embed = discord.Embed(title="", description=f"[{vc.source.title}]({vc.source.web_url}) [{vc.source.requester.mention}] | `{duration}`", color=0xfeadbc)
        embed.add_field(name = "", value=f"<:night_sakura_logo:1179751919347060787> {language.get('music_dict_playing')}", inline=False)
        #embed.set_author(icon_url=self.bot.user.avatar_url, name=f"Now Playing 🎶")
        await ctx.respond(embed=embed)

    @slash_command(name="volume", description="Show current playback volume and modify volume settings")
    @option("number",description="Please enter a number between 1 and 100")
    #@commands.command(name='volume', aliases=['vol', 'v'], description="changes Kermit's volume")
    async def change_volume(self, ctx, *, number: float=None):
        """Change the player volume.
        Parameters
        ------------
        volume: float or int [Required]
            The volume to set the player to in percentage. This must be between 1 and 100.
        """
        vc = ctx.voice_client

        language = await Language().language_music_msg(ctx.guild.id)

        if not vc or not vc.is_connected():
            embed = discord.Embed(title="", description=f"{language.get('music_dict_noconnect')}", color=0xfeadbc)
            return await ctx.respond(embed=embed)
        elif not ctx.author.voice:  # 檢查使用者是否在語音頻道中
            embed = discord.Embed(title="", description=f"{language.get('music_dict_nojoin')}", color=0xfeadbc)
            return await ctx.respond(embed=embed)
        elif not vc.is_playing():
            embed = discord.Embed(title="", description=f"{language.get('music_dict_noplay')}", color=0xfeadbc)
            return await ctx.respond(embed=embed)
        
        if not number:
            embed = discord.Embed(title="", description=f"**<:add_icon:1154418424634675201> {(vc.source.volume)*100}%**", color=0xfeadbc)
            return await ctx.respond(embed=embed)

        if not 0 < number < 101:
            embed = discord.Embed(title="", description=f"{language.get('music_dict_volume_value_msg')}", color=0xfeadbc)
            return await ctx.respond(embed=embed)

        player = await self.get_player(ctx)
        number = round(number, 2)

        if vc.source:
            vc.source.volume = number / 100

        player.volume = number / 100
        embed = discord.Embed(title="", description=f"**`{ctx.author}`** {language.get('music_dict_volume_setting')} **{number}%**", color=0xfeadbc)
        await ctx.respond(embed=embed)

    @slash_command(name="leave", description="stops music and disconnects from voice")
    #@commands.command(name='leave', aliases=["stop", "dc", "disconnect", "bye"], description="stops music and disconnects from voice")
    async def leave_(self, ctx):
        """Stop the currently playing song and destroy the player.
        !Warning!
            This will destroy the player assigned to your guild, also deleting any queued songs and settings.
        """
        vc = ctx.voice_client

        language = await Language().language_music_msg(ctx.guild.id)

        if not vc or not vc.is_connected():
            embed = discord.Embed(title="", description=f"{language.get('music_dict_noconnect')}", color=0xfeadbc)
            return await ctx.respond(embed=embed)
        elif not ctx.author.voice:  # 檢查使用者是否在語音頻道中
            embed = discord.Embed(title="", description=f"{language.get('music_dict_nojoin')}", color=0xfeadbc)
            return await ctx.respond(embed=embed)

        #if (random.randint(0, 1) == 0):
            #await ctx.message.add_reaction('👋')
        await ctx.respond(f"**<:bye_icon:1163025984187019294> {language.get('music_dict_disconnect')}**")

        await self.cleanup(ctx.guild)

def setup(bot):
    bot.add_cog(Music(bot))