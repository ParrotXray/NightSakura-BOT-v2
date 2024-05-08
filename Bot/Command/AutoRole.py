import os
import json
import discord
from discord import option
from discord import message
from datetime import datetime
from discord.ext import commands
from definition.Language import Language
from discord.commands import slash_command
from definition.Classes import Cog_Extension
from definition.JsonProcess import JsonProcess

class Autorole(Cog_Extension):
    @commands.Cog.listener()
    async def on_ready(self):
        now = datetime.now()
        day=now.strftime("%Y-%m-%d %H:%M:%S")
        print (f'{day}-Autorole has loaded')

    @commands.Cog.listener()
    async def on_member_join(self,member):
        read_json, write_json = await self.json_process()
        data = await read_json()
        if str(member.guild.id) in data:
            language = await Language().language_autorole_msg(member.guild.id)
            try:
                role = member.guild.get_role(data[str(member.guild.id)]['role'])
                channel = self.bot.get_channel(data[str(member.guild.id)]['channels'])
                await member.add_roles(role)
            except:
                await channel.send(language.get('autorole_dict_warn').format(role.mention), delete_after=10)

    async def json_process(self):
        autorole_file_path = os.path.join("database", "autorole.json")
        async def read_json():
            data = await JsonProcess(autorole_file_path).read_json()
            return data
        async def write_json(data):
            await JsonProcess(autorole_file_path).write_json(data)
            return 
        return read_json, write_json

    @slash_command(name="autorole-add", description="Set up automatic roles")
    @option("roles", description="Please enter a roles")
    async def auto_role_add(self, ctx, role:discord.Role):
        language = await Language().language_autorole_msg(ctx.guild.id)
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond(language.get('autorole_dict_admin'))
            return
        read_json, write_json = await self.json_process()
        data = await read_json()
        data[str(ctx.guild.id)] = {"role": role.id, "channels": ctx.channel.id}
        await write_json(data)
        embed=discord.Embed(title=f"", description=language.get('autorole_dict_notice'),color=role.color, timestamp=datetime.now())
        embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ",icon_url=self.bot.user.avatar.url)
        embed.set_author(name=f"{ctx.guild.name}", icon_url=ctx.guild.icon.url)
        embed.add_field(name=language.get('autorole_dict_updated'), value=language.get('autorole_dict_role').format(role.mention), inline=False)
        await ctx.respond(embed=embed)

    @slash_command(name="autorole-remove", description="Remove automatic roles")
    async def auto_role_remove(self, ctx):
        language = await Language().language_autorole_msg(ctx.guild.id)
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond(language.get('autorole_dict_admin'))
            return
        read_json, write_json = await self.json_process()
        data = await read_json()
        if str(ctx.guild.id) in data:
            role = ctx.guild.get_role(data[str(ctx.guild.id)]['role'])
            del data[str(ctx.guild.id)]
            await write_json(data)
            embed=discord.Embed(title=f"", color=role.color, timestamp=datetime.now())
            embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ",icon_url=self.bot.user.avatar.url)
            embed.set_author(name=f"{ctx.guild.name}", icon_url=ctx.guild.icon.url)
            embed.add_field(name=language.get('autorole_dict_updated'), value=language.get('autorole_dict_removed').format(role.mention), inline=False)
            await ctx.respond(embed=embed)
        else:
            embed=discord.Embed(title=f"{ctx.guild.name}", color=role.color, timestamp=datetime.now())
            embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ",icon_url=self.bot.user.avatar.url)
            embed.add_field(name=language.get('autorole_dict_failed'), value=language.get('autorole_dict_not_found'), inline=False)
            await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(Autorole(bot))