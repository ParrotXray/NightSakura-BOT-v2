import os
import discord
import asyncio
from typing import Any
from discord import option
from datetime import datetime
from discord.ext import commands
from definition.Language import Language
from discord.commands import slash_command
from definition.Classes import Cog_Extension
from definition.CommandCore import HelpButton
from definition.JsonProcess import JsonProcess
from definition.ConfigCore import ConfigMenu, SetButton
from discord.ui import Select, View, Button, InputText, Modal

class Core(Cog_Extension):
    # LOAD
    @commands.Cog.listener()
    async def on_ready(self):
        now = datetime.now()
        day=now.strftime("%Y-%m-%d %H:%M:%S")
        print (f'{day}-Core has loaded')

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        welcome_channel = guild.system_channel
        language_file_path = os.path.join("database", "language.json")
        volume_file_path = os.path.join("database", "volume.json")
        data_language = await JsonProcess(language_file_path).read_json()
        data_volume = await JsonProcess(volume_file_path).read_json()
        data_language[str(guild.id)] = "US"
        data_volume[str(guild.id)] = 100.0
        await JsonProcess(language_file_path).write_json(data_language)
        await JsonProcess(volume_file_path).write_json(data_volume)
        if welcome_channel:
            embed = await ConfigMenu(self.bot, guild).config_menu()
            await welcome_channel.send(embed=embed, view=SetButton(self.bot, guild))

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        language_file_path = os.path.join("database", "language.json")
        volume_file_path = os.path.join("database", "volume.json")
        data_language = await JsonProcess(language_file_path).read_json()
        data_volume = await JsonProcess(volume_file_path).read_json()
        if str(guild.id) in data_language or str(guild.id) in data_volume:
            del data_language[str(guild.id)]
            del data_volume[str(guild.id)]
            await JsonProcess(language_file_path).write_json(data_language)
            await JsonProcess(volume_file_path).write_json(data_volume)
            
    @slash_command(name="config", description="show configuration")
    async def config(self,ctx):
        if not ctx.author.guild_permissions.administrator:
            return
        embed = await ConfigMenu(self.bot, ctx.guild).config_menu()
        await ctx.respond(embed=embed, view=SetButton(self.bot, ctx.guild))
    
    # RELOAD
    @slash_command(name="reload", description="Reload module (usable in case of command abnormality)")
    @option("module", description="module", 
    choices=["All", "Other",])
    async def reload(self,ctx,module:str):
        now = datetime.now()
        day=now.strftime("%Y-%m-%d %H:%M:%S")
        print (f'{day}-Reload module')
        language = await Language().language_core_msg(ctx.guild.id)
        if module == "All":
            for Filename in os.listdir("./Command"):
                if Filename.endswith(".py"):
                    self.bot.reload_extension(f"Command.{Filename[:-3]}")
            embed=discord.Embed(title="Discord Bot Status", color=0xfeadbc)
            embed.add_field(name="Reload", value=language.get('reload_dict_All'), inline=False)
            await ctx.respond(embed = embed)
            await asyncio.sleep(3)
            os.system('cls' if os.name == 'nt' else 'clear')
            print ('💠Reloaded.')
        elif module == "Other":
            reload_cmd = Select(
            placeholder=language.get('reload_dict_select_opt'),
            options=[
                discord.SelectOption(label="Delay",description = language.get('reload_dict_Delay')),
                discord.SelectOption(label="Update",description = language.get('reload_dict_Update')),
                # discord.SelectOption(label="BotStatus",description = "主機狀態指令"),
                discord.SelectOption(label="Notification",description = language.get('reload_dict_Subscription')),
                discord.SelectOption(label="Invite",description = language.get('reload_dict_Info')),
                discord.SelectOption(label="Music",description = language.get('reload_dict_Music')),
            ]
        )
            async def reload_menu(interaction):
                if os.path.isfile(f"./Command/{reload_cmd.values[0]}.py")!=True:
                    embed=discord.Embed(title="Discord Bot Status", color=0xfeadbc)
                    embed.add_field(name="Reload", value=language.get('reload_dict_Err'), inline=False)
                    await interaction.response.send_message(embed=embed)  
                else:
                    self.bot.reload_extension(f"Command.{reload_cmd.values[0]}")
                    embed=discord.Embed(title="Discord Bot Status", color=0xfeadbc)
                    embed.add_field(name=reload_cmd.values[0], value=language.get('reload_dict_Success'), inline=False)
                    await interaction.response.send_message(embed=embed)  
                    await asyncio.sleep(3)
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print ('💠Reloaded successfully.')

            reload_cmd.callback = reload_menu
            view = View(timeout=None)
            view.add_item(reload_cmd)
            await ctx.respond(language.get('reload_dict_select_msg'),view = view)
    # HELP
    @slash_command(name="help", description="View command list")
    async def help(self,ctx):
        now = datetime.now()
        day=now.strftime("%Y-%m-%d %H:%M:%S")
        print (f'{day}-Help Used')
        language = await Language().language_core_msg(ctx.guild.id)
        embed=discord.Embed(title=f"", color=0xfeadbc, timestamp=datetime.now())
        embed.set_author(name=language.get('help_dict_select_msg'))
        embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ",icon_url=self.bot.user.avatar.url)
        embed.add_field(name = "", value=language.get('help_dict_select_title').format(ctx.author.mention), inline=False)
        await ctx.respond(embed=embed, view = HelpButton(self.bot, ctx))

def setup(bot):
    bot.add_cog(Core(bot))