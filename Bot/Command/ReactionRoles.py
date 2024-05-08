import discord
from discord.commands import Option, slash_command
from discord.ext import commands
from definition.Classes import Cog_Extension
from definition.JsonProcess import JsonProcess
from definition.Language import Language
from datetime import datetime
import asyncio
import json
import os

class ReactionRoles(Cog_Extension):
    @commands.Cog.listener()
    async def on_ready(self):
        now = datetime.now()
        day=now.strftime("%Y-%m-%d %H:%M:%S")
        print (f'{day}-ReactionRole has loaded')
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self,payload):
        read_json, write_json = await self.json_process()
        data = await read_json()
        if not str(payload.message_id) in data:
            return
        if data[str(payload.message_id)]["emoji"] != str(payload.emoji):
            return
        guild = await self.bot.fetch_guild(payload.guild_id)
        role = guild.get_role(data[str(payload.message_id)]["role"])
        channel = self.bot.get_channel(data[str(payload.message_id)]['channels'])
        language = await Language().language_reactionrole_msg(payload.guild_id)
        try:
            await payload.member.add_roles(role)
            try:
                await payload.member.send(language.get('reactionrole_dict_acquired').format(f"`@{str(role)}`"), delete_after=10)
            except:
                pass
        except:
            await channel.send(language.get('reactionrole_dict_warn').format(role.mention), delete_after=10)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self,payload):
        read_json, write_json = await self.json_process()
        data = await read_json()
        if not str(payload.message_id) in data:
            return
        if data[str(payload.message_id)]["emoji"] != str(payload.emoji):
            return
        guild = await self.bot.fetch_guild(payload.guild_id)
        role = guild.get_role(data[str(payload.message_id)]["role"])
        channel = self.bot.get_channel(data[str(payload.message_id)]['channels'])
        member = await guild.fetch_member(payload.user_id)
        language = await Language().language_reactionrole_msg(payload.guild_id)
        try:
            await member.remove_roles(role)
            try:
                await member.send(language.get('reactionrole_dict_removed').format(f"`@{str(role)}`"), delete_after=10)
            except:
                pass
        except:
            await channel.send(language.get('reactionrole_dict_warn').format(role.mention), delete_after=10)
    
    async def json_process(self):
        reactionrole_file_path = os.path.join("database", "reactionrole.json")
        async def read_json():
            data = await JsonProcess(reactionrole_file_path).read_json()
            return data
        async def write_json(data):
            await JsonProcess(reactionrole_file_path).write_json(data)
            return 
        return read_json, write_json

    @slash_command(name="reactionrole",description="Set reaction roles")
    async def reaction_role(self,ctx,
                            content: Option(str, "Embed message content"),
                            roles: Option(discord.Role, "Roles to claim"),
                            reactions: Option(str, "Reactions to add")):
        language = await Language().language_reactionrole_msg(ctx.guild.id)
        await ctx.defer()
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond(language.get('reactionrole_dict_admin'))
            return
        try:
            embed = discord.Embed(title="", description=content, color=0xfabab8, timestamp=datetime.now())
            embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ",icon_url=self.bot.user.avatar.url)
            embed.set_author(name=language.get('reactionrole_dict_claim'), icon_url=ctx.guild.icon.url)
            message = await ctx.send(embed=embed)
            await message.add_reaction(reactions)
            read_json, write_json = await self.json_process()
            data = await read_json()
            data[str(message.id)] = {"role": roles.id, "emoji": reactions, "channels": ctx.channel.id}
            await write_json(data)
            await ctx.respond(language.get('reactionrole_dict_completed'), delete_after=3)
        except:
            await ctx.respond(language.get('reactionrole_dict_error'), delete_after=3)
def setup(bot):
    bot.add_cog(ReactionRoles(bot))