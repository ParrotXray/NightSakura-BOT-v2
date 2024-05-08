import discord
from discord import message
from discord.commands import slash_command
from discord import option
from discord.ext import commands, tasks
from definition.Classes import Cog_Extension
from definition.JsonProcess import JsonProcess
from definition.Language import Language
import json
from discord.ui import Select, View, InputText, Modal, Button, Item
from datetime import datetime
import os

class SupportModal(Modal):
    def __init__(self, bot, ctx, language) -> None:
        super().__init__(title=language.get('support_dict_title'))
        self.language = language
        self.bot = bot
        self.ctx = ctx
        self.file = os.path.join("database", "support.json")
        self.add_item(InputText(label=self.language.get('support_dict_label'), placeholder=self.language.get('support_dict_placeholder'))) 
        self.add_item(
            InputText(
                label= self.language.get('support_dict_InputText_label'), 
                placeholder=self.language.get('support_dict_InputText_placeholder'),
                style=discord.InputTextStyle.long,
            )
        )

    async def callback(self, interaction):
        support_data = await JsonProcess(self.file).read_json()
        support_data[str(self.ctx.author.id)] = {"name": str(self.ctx.author), "id": self.ctx.author.id}
        await JsonProcess(self.file).write_json(support_data)

        admin = self.bot.get_user(449906584647237633)
        table = []
        for title, values in support_data.items():
            name = values.get("name")
            table.append(discord.SelectOption(label = title, description = name))
        embed=discord.Embed(title="",color=0xfeadbc,timestamp=datetime.now())
        embed.set_author(name=self.language.get('support_dict_submit').format(str(interaction.user)), icon_url=interaction.user.avatar.url)
        embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ",icon_url=self.bot.user.avatar.url)
        embed.add_field(name=self.children[0].value, value=self.children[1].value, inline=False)
        await admin.send(embed=embed, view=SupportProcess(self.bot, self.ctx, table, self.language, self.file))

        author = self.bot.get_user(self.ctx.author.id)
        embed=discord.Embed(title="",color=0xfeadbc,timestamp=datetime.now())
        embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ",icon_url=self.bot.user.avatar.url)
        embed.add_field(name=self.language.get('support_dict_Reply_title_msg'), value=self.language.get('support_dict_Reply_msg'), inline=False)
        await author.send(embed=embed, view=SupportUser(self.bot, self.ctx, self.language, self.file))

        embed=discord.Embed(title="",color=0xfeadbc,timestamp=datetime.now())
        embed.set_author(name=f"{interaction.user.name}{self.language.get('support_dict_provided')}", icon_url=interaction.user.avatar.url)
        embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ",icon_url=self.bot.user.avatar.url)
        embed.add_field(name=self.children[0].value, value=self.children[1].value, inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

class SupportProcessModal(Modal):
    def __init__(self, bot, ctx, language, user, file) -> None:
        super().__init__(title=language.get('support_dict_Reply_title'))
        self.language = language
        self.bot = bot
        self.ctx = ctx
        self.user = user
        self.file = file
        self.add_item(
            InputText(
                label= self.language.get('support_dict_InputText_label'), 
                placeholder=self.language.get('support_dict_Reply_InputText_placeholder'),
                style=discord.InputTextStyle.long,
            )
        )

    async def callback(self, interaction):
        support_data = await JsonProcess(self.file).read_json()
        if not len(support_data) or str(self.ctx.author.id) not in support_data:
            await interaction.response.send_message(self.language.get('support_dict_Reply_error'))
        else:
            table = []
            for title, values in support_data.items():
                name = values.get("name")
                table.append(discord.SelectOption(label = title, description = name))
            author = self.bot.get_user(int(self.user))
            embed=discord.Embed(title="",color=0xfeadbc,timestamp=datetime.now())
            embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ",icon_url=self.bot.user.avatar.url)
            embed.add_field(name=self.language.get('support_dict_Reply_admin'), value=self.children[0].value, inline=False)
            await author.send(embed=embed, view=SupportUser(self.bot, self.ctx, self.language, self.file))

            await interaction.response.edit_message(view=SupportProcess(self.bot, self.ctx, table, self.language, self.file))

class SupportUserModal(Modal):
    def __init__(self, bot, ctx, language, file) -> None:
        super().__init__(title=language.get('support_dict_Reply_title'))
        self.language = language
        self.bot = bot
        self.ctx = ctx
        self.file = file
        self.add_item(
            InputText(
                label= self.language.get('support_dict_InputText_label'), 
                placeholder=self.language.get('support_dict_Reply_InputText_placeholder'),
                style=discord.InputTextStyle.long,
            )
        )  

    async def callback(self, interaction):
        admin = self.bot.get_user(449906584647237633)
        support_data = await JsonProcess(self.file).read_json()
        if not len(support_data) or str(self.ctx.author.id) not in support_data:
            await interaction.response.send_message(self.language.get('support_dict_Reply_error'))
        else:
            table = []
            for title, values in support_data.items():
                name = values.get("name")
                table.append(discord.SelectOption(label = title, description = name))

            embed=discord.Embed(title="",color=0xfeadbc,timestamp=datetime.now())
            embed.set_author(name=self.language.get('support_dict_Reply_user').format(str(interaction.user)), icon_url=interaction.user.avatar.url)
            embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ",icon_url=self.bot.user.avatar.url)
            embed.add_field(name="", value=self.children[0].value, inline=False)
            await admin.send(embed=embed, view=SupportProcess(self.bot, self.ctx, table, self.language, self.file))

            await interaction.response.edit_message(view=SupportUser(self.bot, self.ctx, self.language, self.file))

class SupportProcess(View):
    def __init__(self, bot, ctx, table, language, file) -> None:
        super().__init__(timeout=None)
        self.language = language
        self.bot = bot
        self.ctx = ctx
        self.table = table
        self.file = file

        self.support_item = Select(placeholder=self.language.get('support_dict_Reply'), options=self.table)
        self.close_item = Select(placeholder=self.language.get('support_dict_Close'), options=self.table)
        self.add(self.support_item, self.support_select_callback)
        self.add(self.close_item, self.close_select_callback)

    def add(self, item:Item, callback):
        self.add_item(item)
        item.callback = callback

    async def support_select_callback(self, interaction):
        await interaction.response.send_modal(SupportProcessModal(self.bot, self.ctx, self.language, self.support_item.values[0], self.file))

    async def close_select_callback(self, interaction):
        author = self.bot.get_user(int(self.close_item.values[0]))
        data = await JsonProcess(self.file).read_json()
        if str(self.close_item.values[0]) in data:
            del data[str(self.close_item.values[0])]
            await JsonProcess(self.file).write_json(data)
            await author.send(self.language.get('support_dict_Reply_admin_close'))
            await interaction.response.send_message(self.language.get('support_dict_Reply_close_msg'))
        else:
            await interaction.response.send_message(self.language.get('support_dict_Reply_error'))

class SupportUser(View):
    def __init__(self, bot, ctx, language, file) -> None:
        super().__init__(timeout=None)
        self.language = language
        self.bot = bot
        self.ctx = ctx
        self.file = file

    @discord.ui.button(label='Reply',style=discord.ButtonStyle.green, row=1)
    async def set_language(self, button, interaction):
        modal = SupportUserModal(self.bot, self.ctx, self.language, self.file)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label='Close',style=discord.ButtonStyle.red, row=1)
    async def set_volume(self, button, interaction):
        admin = self.bot.get_user(449906584647237633)
        data = await JsonProcess(self.file).read_json()
        if str(self.ctx.author.id) in data:
            del data[str(self.ctx.author.id)]
            await JsonProcess(self.file).write_json(data)
            await admin.send(self.language.get('support_dict_Reply_user_close').format(str(self.ctx.author)))
            await interaction.response.send_message(self.language.get('support_dict_Reply_close_msg'))
        else:
            await interaction.response.send_message(self.language.get('support_dict_Reply_error'))

class Support(Cog_Extension):
    @commands.Cog.listener()
    async def on_ready(self):
        now = datetime.now()
        day=now.strftime("%Y-%m-%d %H:%M:%S")
        print (f'{day}-Support has loaded')
    @slash_command(name="support", description="Ask questions to the developers")
    async def support(self, ctx):
        language = await Language().language_support_msg(ctx.guild.id)
        modal = SupportModal(self.bot, ctx, language)
        await ctx.interaction.response.send_modal(modal)

def setup(bot):
    bot.add_cog(Support(bot))