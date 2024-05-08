import os
from typing import Any
import discord
from definition.JsonProcess import JsonProcess
from definition.Language import Language
import asyncio
from datetime import datetime
from discord.ui import Select, View, Button, InputText, Modal

class BotMenu(View):
    def __init__(self, bot, ctx):
        super().__init__(timeout=None)
        self.bot = bot
        self.ctx = ctx

    @discord.ui.button(label='Music', style=discord.ButtonStyle.green, row=1)
    async def music_command(self, button, interaction):
        await interaction.response.edit_message(view=MusicMenu(self.bot, self.ctx))

    @discord.ui.button(label='Manager', style=discord.ButtonStyle.green, row=1)
    async def manager_command(self, button, interaction):
        await interaction.response.edit_message(view=ManagerMenu(self.bot, self.ctx))

    @discord.ui.button(label='back', style=discord.ButtonStyle.red, row=1)
    async def back(self, button, interaction):
        language = await Language().language_core_msg(self.ctx.guild.id)
        embed=discord.Embed(title=f"", color=0xfeadbc, timestamp=datetime.now())
        embed.set_author(name=language.get('help_dict_select_msg'))
        embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ",icon_url=self.bot.user.avatar.url)
        embed.add_field(name = "", value=language.get('help_dict_select_title').format(self.ctx.author.mention), inline=False)
        await interaction.response.edit_message(embed=embed, view=HelpButton(self.bot, self.ctx))

    @discord.ui.select(
        placeholder="Bot command",
        options=[
            discord.SelectOption(label="/help"),
            discord.SelectOption(label="/invite"),
            discord.SelectOption(label="/reload"),
            discord.SelectOption(label="/delay"),
            discord.SelectOption(label="/update"),
            discord.SelectOption(label="/notification"),
            discord.SelectOption(label="/config"),
        ]
    )
    async def select_callback(self, select, interaction):
        language = await Language().language_core_msg(self.ctx.guild.id)
        
        option_explanations = {
            '/help': language.get('help_dict_help'),
            '/invite': language.get('help_dict_Info'),
            '/reload': language.get('help_dict_reload'),
            '/delay': language.get('help_dict_Delay'),
            '/update': language.get('help_dict_Update'),
            '/notification': language.get('help_dict_Subscription'),
            '/config': language.get('help_dict_Config'),
        }

        explanation = option_explanations.get(select.values[0], 'Invalid Option')

        embed=discord.Embed(title="",description="", color=0xfeadbc, timestamp=datetime.now())
        embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ",icon_url=self.bot.user.avatar.url)
        embed.add_field(name="Command", value=f"```{select.values[0]}```", inline=False)
        embed.add_field(name="Command explanation", value=f"```{explanation}```", inline=False)

        await interaction.response.edit_message(embed=embed)

class ManagerMenu(View):
    def __init__(self, bot, ctx):
        super().__init__(timeout=None)
        self.bot = bot
        self.ctx = ctx

    @discord.ui.button(label='Bot', style=discord.ButtonStyle.green, row=1)
    async def bot_command(self, button, interaction):
        await interaction.response.edit_message(view=BotMenu(self.bot, self.ctx))

    @discord.ui.button(label='Music', style=discord.ButtonStyle.green, row=1)
    async def music_command(self, button, interaction):
        await interaction.response.edit_message(view=MusicMenu(self.bot, self.ctx))

    @discord.ui.button(label='back', style=discord.ButtonStyle.red, row=1)
    async def back(self, button, interaction):
        language = await Language().language_core_msg(self.ctx.guild.id)
        embed=discord.Embed(title=f"", color=0xfeadbc, timestamp=datetime.now())
        embed.set_author(name=language.get('help_dict_select_msg'))
        embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ",icon_url=self.bot.user.avatar.url)
        embed.add_field(name = "", value=language.get('help_dict_select_title').format(self.ctx.author.mention), inline=False)
        await interaction.response.edit_message(embed=embed, view=HelpButton(self.bot, self.ctx))

    @discord.ui.select(
        placeholder="Manager command",
        options=[
            discord.SelectOption(label="/autorole-add"),
            discord.SelectOption(label="/autorole-remove"),
            discord.SelectOption(label="/welcome-add"),
            discord.SelectOption(label="/leave-add"),
            discord.SelectOption(label="/leave-remove"),
            discord.SelectOption(label="/welcome-remove"),
            discord.SelectOption(label="/reactionrole"),
            discord.SelectOption(label="/serverinfo"),
            discord.SelectOption(label="/userinfo"),
        ]
    )
    async def select_callback(self, select, interaction):
        language = await Language().language_core_msg(self.ctx.guild.id)
        
        option_explanations = {
            '/autorole-add': language.get('help_dict_autorole_set'),
            '/autorole-remove': language.get('help_dict_autorole_remove'),
            '/welcome-add': language.get('help_dict_welcome_set'),
            '/leave-add': language.get('help_dict_leave_set'),
            '/leave-remove': language.get('help_dict_leave_remove'),
            '/welcome-remove': language.get('help_dict_welcome_remove'),
            '/reactionrole': language.get('help_dict_reaction_set'),
            '/serverinfo': language.get('help_dict_serverinfo'),
            '/userinfo': language.get('help_dict_userinfo'),
        }

        explanation = option_explanations.get(select.values[0], 'Invalid Option')

        embed=discord.Embed(title="",description="", color=0xfeadbc, timestamp=datetime.now())
        embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ",icon_url=self.bot.user.avatar.url)
        embed.add_field(name="Command", value=f"```{select.values[0]}```", inline=False)
        embed.add_field(name="Command explanation", value=f"```{explanation}```", inline=False)

        await interaction.response.edit_message(embed=embed)

class MusicMenu(View):
    def __init__(self, bot, ctx):
        super().__init__(timeout=None)
        self.bot = bot
        self.ctx = ctx

    @discord.ui.button(label='Bot', style=discord.ButtonStyle.green, row=1)
    async def bot_command(self, button, interaction):
        await interaction.response.edit_message(view=BotMenu(self.bot, self.ctx))

    @discord.ui.button(label='Manager', style=discord.ButtonStyle.green, row=1)
    async def manager_command(self, button, interaction):
        await interaction.response.edit_message(view=ManagerMenu(self.bot, self.ctx))

    @discord.ui.button(label='back', style=discord.ButtonStyle.red, row=1)
    async def back(self, button, interaction):
        language = await Language().language_core_msg(self.ctx.guild.id)
        embed=discord.Embed(title=f"", color=0xfeadbc, timestamp=datetime.now())
        embed.set_author(name=language.get('help_dict_select_msg'))
        embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ",icon_url=self.bot.user.avatar.url)
        embed.add_field(name = "", value=language.get('help_dict_select_title').format(self.ctx.author.mention), inline=False)
        await interaction.response.edit_message(embed=embed, view=HelpButton(self.bot, self.ctx))

    @discord.ui.select(
        placeholder="Music command",
        options=[
            discord.SelectOption(label="/play"),
            discord.SelectOption(label="/join"),
            discord.SelectOption(label="/pasue"),
            discord.SelectOption(label="/resume"),
            discord.SelectOption(label="/skip"),
            discord.SelectOption(label="/queue"),
            discord.SelectOption(label="/remove"),
            discord.SelectOption(label="/clear"),
            discord.SelectOption(label="/volume"),
            discord.SelectOption(label="/leave"),
            discord.SelectOption(label="/loop"),
            discord.SelectOption(label="/pl-add"),
            discord.SelectOption(label="/pl-show"),
            discord.SelectOption(label="/pl-play"),
            discord.SelectOption(label="/pl-del"),
            discord.SelectOption(label="/shuffle"),
            discord.SelectOption(label="/insert"),
        ]
    )
    async def select_callback(self, select, interaction):
        language = await Language().language_core_msg(self.ctx.guild.id)
        
        option_explanations = {
            '/play': language.get('help_dict_music_play'),
            '/join': language.get('help_dict_music_join'),
            '/pasue': language.get('help_dict_music_pasue'),
            '/resume': language.get('help_dict_music_resume'),
            '/skip': language.get('help_dict_music_skip'),
            '/queue': language.get('help_dict_music_queue'),
            '/remove': language.get('help_dict_music_remove'),
            '/clear': language.get('help_dict_music_clear'),
            '/volume': language.get('help_dict_music_volume'),
            '/leave': language.get('help_dict_music_leave'),
            '/loop': language.get('help_dict_music_loop'),
            '/pl-add': language.get('help_dict_music_pladd'),
            '/pl-show': language.get('help_dict_music_plshow'),
            '/pl-play': language.get('help_dict_music_plplay'),
            '/pl-del': language.get('help_dict_music_pldel'),
            '/shuffle': language.get('help_dict_music_shuffle'),
            '/insert': language.get('help_dict_music_insert'),
        }

        explanation = option_explanations.get(select.values[0], 'Invalid Option')

        embed=discord.Embed(title="",description="", color=0xfeadbc, timestamp=datetime.now())
        embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ",icon_url=self.bot.user.avatar.url)
        embed.add_field(name="Command", value=f"```{select.values[0]}```", inline=False)
        embed.add_field(name="Command explanation", value=f"```{explanation}```", inline=False)

        await interaction.response.edit_message(embed=embed)



class HelpButton(View):
    def __init__(self, bot, ctx):
        super().__init__(timeout=None)
        self.bot = bot
        self.ctx = ctx

    @discord.ui.button(label='Bot', style=discord.ButtonStyle.blurple, row=1)
    async def bot_command(self, button, interaction):
        await interaction.response.edit_message(view=BotMenu(self.bot, self.ctx))

    @discord.ui.button(label='Music', style=discord.ButtonStyle.blurple, row=1)
    async def music_command(self, button, interaction):
        await interaction.response.edit_message(view=MusicMenu(self.bot, self.ctx))

    @discord.ui.button(label='Manager', style=discord.ButtonStyle.blurple, row=1)
    async def manager_command(self, button, interaction):
        await interaction.response.edit_message(view=ManagerMenu(self.bot, self.ctx))
