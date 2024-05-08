import discord
from discord import message
from discord.commands import slash_command
from discord import option
from discord.ext import commands
from definition.Classes import Cog_Extension
from definition.Language import Language
from datetime import datetime
import socket
import asyncio
import json
from discord.ui import Select,View

class Update(Cog_Extension):
    @commands.Cog.listener()
    async def on_ready(self):
        now = datetime.now()
        day=now.strftime("%Y-%m-%d %H:%M:%S")
        print (f'{day}-Update has loaded')
    @slash_command(name="update", description="View today's update log")
    async def update(self, ctx):
        now = datetime.now()
        day=now.strftime("%Y-%m-%d %H:%M:%S")
        print(f'{day}-update log')
        language = await Language().language_update_msg(ctx.guild.id)
        select = Select(
            placeholder=language.get('update_dict_placeholder_month'),
            options=[
                discord.SelectOption(
                    label=language.get('update_dict_label_ten'),
                    description=language.get('update_dict_description_ten'),
                    emoji="🔟"
                ),
                discord.SelectOption(
                    label=language.get('update_dict_label_eleven'),
                    description=language.get('update_dict_description_eleven'),
                    emoji="1️⃣"
                ),
                discord.SelectOption(
                    label=language.get('update_dict_label_twelve'),
                    description=language.get('update_dict_description_twelve'),
                    emoji="2️⃣"
                ),
            ]
        )

        async def update_main(interaction):
            if select.values[0] == language.get('update_dict_label_ten'):
                select_month = Select(
                placeholder=language.get('update_dict_placeholder_date'),
                options=[
                    discord.SelectOption(label="2023-10-06", description=f"2023-10-06 {language.get('update_dict_description_date')}", emoji= "🔟"),
                    discord.SelectOption(label="2023-10-22", description=f"2023-10-22 {language.get('update_dict_description_date')}", emoji= "🔟"),
                ]
            )
            elif select.values[0] == language.get('update_dict_label_eleven'):
                select_month = Select(
                placeholder=language.get('update_dict_placeholder_date'),
                options=[
                    discord.SelectOption(label="2023-11-23", description=f"2023-11-23 {language.get('update_dict_description_date')}", emoji= "1️⃣"),
                    discord.SelectOption(label="2023-11-26", description=f"2023-11-26 {language.get('update_dict_description_date')}", emoji= "1️⃣"),
                ]
            )
            elif select.values[0] == language.get('update_dict_label_twelve'):
                select_month = Select(
                placeholder=language.get('update_dict_placeholder_date'),
                options=[
                    discord.SelectOption(label="2023-12-02", description=f"2023-12-02 {language.get('update_dict_description_date')}", emoji= "2️⃣"),
                ]
            )
            async def update_menu(interaction):
                match select_month.values[0]:
                    case '2023-10-06':
                        embed=discord.Embed(title=f"",description=language.get('update_dict_description_231006'), color=0xfeadbc, timestamp=datetime.now())
                        embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ",icon_url=self.bot.user.avatar.url)
                        embed.add_field(name=language.get('update_dict_name_update'), value=language.get('update_dict_value_231006'), inline=False)
                        embed.add_field(name="", value=language.get('update_dict_msg_231006'), inline=False)
                    case '2023-10-22':
                        embed=discord.Embed(title=f"",description=language.get('update_dict_description_231022'), color=0xfeadbc, timestamp=datetime.now())
                        embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ",icon_url=self.bot.user.avatar.url)
                        embed.add_field(name=language.get('update_dict_name_update'), value=language.get('update_dict_value_231022'), inline=False)
                        embed.add_field(name="", value=language.get('update_dict_msg_231022'), inline=False)
                    case '2023-11-23':
                        embed=discord.Embed(title=f"",description=language.get('update_dict_description_231123'), color=0xfeadbc, timestamp=datetime.now())
                        embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ",icon_url=self.bot.user.avatar.url)
                        embed.add_field(name=language.get('update_dict_name_update'), value=language.get('update_dict_value_231123'), inline=False)
                        embed.add_field(name="", value=language.get('update_dict_msg_231123'), inline=False)
                    case '2023-11-26':
                        embed=discord.Embed(title=f"",description=language.get('update_dict_description_231126'), color=0xfeadbc, timestamp=datetime.now())
                        embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ",icon_url=self.bot.user.avatar.url)
                        embed.add_field(name=language.get('update_dict_name_update'), value=language.get('update_dict_value_231126'), inline=False)
                        embed.add_field(name="", value=language.get('update_dict_msg_231126'), inline=False)

                    case '2023-12-02':
                        embed=discord.Embed(title=f"",description=language.get('update_dict_description_231202'), color=0xfeadbc, timestamp=datetime.now())
                        embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ",icon_url=self.bot.user.avatar.url)
                        embed.add_field(name=language.get('update_dict_name_update'), value=language.get('update_dict_value_231202'), inline=False)
                        embed.add_field(name="", value=language.get('update_dict_msg_231202'), inline=False)
                    
                view = View(timeout=None)
                view.add_item(select)
                await interaction.response.edit_message(embed=embed, view = view)

            select_month.callback = update_menu
            view = View(timeout=None)
            view.add_item(select_month)
            await interaction.response.edit_message(content=f"🗓️{language.get('update_dict_opt_date')}", view = view)
            
        select.callback = update_main
        view = View(timeout=None)
        view.add_item(select)
        await ctx.respond(f"📅{language.get('update_dict_opt_month')}", view = view, ephemeral = True)
            
def setup(bot):
    bot.add_cog(Update(bot))