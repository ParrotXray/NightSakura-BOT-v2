import os
from typing import Any
import discord
from definition.JsonProcess import JsonProcess
from definition.Language import Language
import asyncio
from datetime import datetime
from discord.ui import Select, View, Button, InputText, Modal

class ConfigMenu():
    def __init__(self, bot, guild):
        self.bot = bot
        self.guild = guild

    async def config_menu(self):
        setting = ConfigSetting(self.bot, self.guild)
                    
        embed=discord.Embed(title="Welcome to me.", description="please set the following functions first.", color=0xfeadbc,timestamp=datetime.now())
        embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ",icon_url=self.bot.user.avatar.url)
        embed.add_field(name="", value=f"- Language setting: `{await setting.get_setting_language()}`", inline=False)
        embed.add_field(name="", value=f"- Volume setting: `{await setting.get_setting_volume()}%`", inline=False)
        embed.add_field(name="", value=f"- AutoRole setting: {('`No Setting`' if await setting.get_auto_role() is None else await setting.get_auto_role())}", inline=False)
        embed.add_field(name="", value=f"- Welcome setting: {('`No Setting`' if await setting.get_welcome_channel() is None else await setting.get_welcome_channel())}", inline=False)
        embed.add_field(name="", value=f"- Leave setting: {('`No Setting`' if await setting.get_leave_channel() is None else await setting.get_leave_channel())}", inline=False)
        embed.add_field(name="", value=f"- Notification setting: {('`No Setting`' if await setting.get_notification_channel() is None else await setting.get_notification_channel())}", inline=False)
        return embed

class MusicVolumeModal(Modal):
    def __init__(self, bot, guild) -> None:
        super().__init__(title="Please setting the music volume")
        self.bot = bot
        self.guild = guild
        self.volume_item = os.path.join("database", "volume.json")
        self.add_item(InputText(label="music volume", placeholder="Please enter a value between 1 and 100"))   

    async def callback(self, interaction):
        if not 0 < float(self.children[0].value) < 101:
            embed = discord.Embed(title="", description="Please enter a value between 1 and 100", color=0xfeadbc)
            await interaction.response.send_message(embed = embed, delete_after=5)
        else:
            data = await JsonProcess(self.volume_item).read_json()
            data[str(self.guild.id)] = round(float(self.children[0].value), 2)
            await JsonProcess(self.volume_item).write_json(data)
            embed = await ConfigMenu(self.bot, self.guild).config_menu()
            await interaction.response.edit_message(embed = embed, view=SetButton(self.bot, self.guild))

class ConfigSetting():
    def __init__(self, bot, guild) -> None:
        self.bot = bot
        self.guild = guild
        self.language_item = os.path.join("database", "language.json")
        self.volume_item = os.path.join("database", "volume.json")
        self.auto_role = os.path.join("database", "autorole.json")
        self.welcome_channel = os.path.join("database", "welcome.json")
        self.leave_channel = os.path.join("database", "leave.json")
        self.notification_channel = os.path.join("database", "notificationguilds.json")

    async def get_setting_language(self):
        data = await JsonProcess(self.language_item).read_json()
        if str(self.guild.id) in data:
            language_data = data[str(self.guild.id)]
            
            option_language = {
                "US": "English",
                "JP": "日本語",
                "TW": "繁體中文",
                "CN": "简体中文"
            }
            
            return option_language.get(language_data, 'Invalid Option')
        
    async def get_setting_volume(self):
        data = await JsonProcess(self.volume_item).read_json()
        if str(self.guild.id) in data:
            volume_data = data[str(self.guild.id)]
            return volume_data
        
    async def get_auto_role(self):
        data = await JsonProcess(self.auto_role).read_json()
        if str(self.guild.id) in data:
            role = self.guild.get_role(data[str(self.guild.id)]['role'])
            return role.mention
        
    async def get_welcome_channel(self):
        data = await JsonProcess(self.welcome_channel).read_json()
        if str(self.guild.id) in data:
            channel = self.bot.get_channel(data[str(self.guild.id)]["channel"])
            return channel.mention
        
    async def get_leave_channel(self):
        data = await JsonProcess(self.leave_channel).read_json()
        if str(self.guild.id) in data:
            channel = self.bot.get_channel(data[str(self.guild.id)])
            return channel.mention
        
    async def get_notification_channel(self):
        data = await JsonProcess(self.notification_channel).read_json()
        if str(self.guild.id) in data:
            channel = self.bot.get_channel(data[str(self.guild.id)])
            return channel.mention

class SetLanguage(View):
    def __init__(self, bot, guild):
        super().__init__(timeout=None)
        self.bot = bot
        self.guild = guild
        self.language_item = os.path.join("database", "language.json")

    @discord.ui.select(
        placeholder="Please choose a language.",
        options=[
            discord.SelectOption(
                label="English",
                description = "default",
                # emoji= ""

            ),
            discord.SelectOption(
                label="日本語",
                description = "日本",
                # emoji= ""

            ),
            discord.SelectOption(
                label="繁體中文",
                description = "台灣/香港",
                # emoji= ""
            ),
            discord.SelectOption(
                label="简体中文",
                description = "中国大陆",
                # emoji= ""
            ),
        ]
    )
    async def select_callback(self, select, interaction):
        data = await JsonProcess(self.language_item).read_json()

        option_language = {
                "English": "US",
                "日本語": "JP",
                "繁體中文": "TW",
                "简体中文": "CN"
        }

        data[str(self.guild.id)] = option_language.get(select.values[0])
        await JsonProcess(self.language_item).write_json(data)

        if str(self.guild.id) in data:
            embed = await ConfigMenu(self.bot, self.guild).config_menu()
        await interaction.response.edit_message(embed = embed, view=SetButton(self.bot, self.guild))

class SetButton(View):
    def __init__(self, bot, guild):
        super().__init__(timeout=None)
        self.bot = bot
        self.guild = guild

    @discord.ui.button(label='Language',style=discord.ButtonStyle.blurple, row=1)
    async def set_language(self, button, interaction):
        await interaction.response.edit_message(view=SetLanguage(self.bot, self.guild))

    @discord.ui.button(label='Volume',style=discord.ButtonStyle.blurple, row=1)
    async def set_volume(self, button, interaction):
        modal = MusicVolumeModal(self.bot, self.guild)
        await interaction.response.send_modal(modal)