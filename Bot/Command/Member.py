import discord
from discord import message
from discord.commands import slash_command
from discord import option
from discord.ext import commands
from definition.Classes import Cog_Extension
from definition.JsonProcess import JsonProcess
from definition.Language import Language
from datetime import datetime
import json
import os

class Member(Cog_Extension):
    @commands.Cog.listener()
    async def on_ready(self):
        now = datetime.now()
        day=now.strftime("%Y-%m-%d %H:%M:%S")
        print (f'{day}-Member has loaded')

    @commands.Cog.listener()
    async def on_member_join(self,member):
        welcome_file_path = os.path.join("database", "welcome.json")
        read_json, write_json = await self.json_process(welcome_file_path)
        data = await read_json()
        if str(member.guild.id) in data:
            language = await Language().language_member_msg(member.guild.id)
            try:
                channel = self.bot.get_channel(data[str(member.guild.id)]["channel"])
                message = data[str(member.guild.id)]["message"]
                user = self.bot.get_user(member.id)
                embed=discord.Embed(title=member.guild, color=0xfabab8, timestamp=datetime.now())
                embed.set_thumbnail(url=member.avatar.url if member.avatar.url else 'https://discordapp.com/assets/322c936a8c8be1b803cd94861bdfa868.png')
                embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ",icon_url=self.bot.user.avatar.url)
                embed.add_field(name="", value=f"🎉{member} {language.get('member_dict_joined')}", inline=False)
                await channel.send(embed=embed)
                if not member.bot:
                    if message is None:
                        return
                    else:
                        embed=discord.Embed(title=member.guild, color=0xfabab8, timestamp=datetime.now())
                        embed.set_thumbnail(url=member.avatar.url if member.avatar.url else 'https://discordapp.com/assets/322c936a8c8be1b803cd94861bdfa868.png')
                        embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ",icon_url=self.bot.user.avatar.url)
                        embed.add_field(name="", value=f"🎉{member} {language.get('member_dict_joined')}", inline=False)
                        embed.add_field(name=f"{language.get('member_dict_message')}-{message}", value="", inline=False)
                        await user.send(embed=embed)
                else:
                    return
            except:
                return

    @commands.Cog.listener()
    async def on_member_remove(self,member):
        leave_file_path = os.path.join("database", "leave.json")
        read_json, write_json = await self.json_process(leave_file_path)
        data = await read_json()
        if str(member.guild.id) in data:
            language = await Language().language_member_msg(member.guild.id)
            try:
                channel = self.bot.get_channel(data[str(member.guild.id)])
                embed=discord.Embed(title=member.guild, color=0xfabab8, timestamp=datetime.now())
                embed.set_thumbnail(url=member.avatar.url if member.avatar.url else 'https://discordapp.com/assets/322c936a8c8be1b803cd94861bdfa868.png')
                embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ",icon_url=self.bot.user.avatar.url)
                embed.add_field(name="", value=f"👋{member} {language.get('member_dict_left')}", inline=False)
                await channel.send(embed=embed)
            except:
                return
            
    async def json_process(self, json_file):
        async def read_json():
            data = await JsonProcess(json_file).read_json()
            return data
        async def write_json(data):
            await JsonProcess(json_file).write_json(data)
            return 
        return read_json, write_json

    @slash_command(name="welcome-add", description="Add join message channel")
    @option("channel", description="Please enter a valid channel")
    @option("message", description="Please enter the welcome message to send to users")
    async def set_welcome(self, ctx, channel:discord.TextChannel, message = None):
        welcome_file_path = os.path.join("database", "welcome.json")
        language = await Language().language_member_msg(ctx.guild.id)
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond(language.get('member_dict_admin'))
            return
        read_json, write_json = await self.json_process(welcome_file_path)
        data = await read_json()
        data[str(ctx.guild.id)] = {"channel": channel.id, "message": message}
        await write_json(data)
        embed=discord.Embed(title=f"{ctx.guild.name}", color=0xfabab8, timestamp=datetime.now())
        embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ",icon_url=self.bot.user.avatar.url)
        embed.add_field(name=language.get('member_dict_updated'), value=language.get('member_dict_channel').format(channel.mention), inline=False)
        embed.add_field(name=f"{language.get('member_dict_welcome')}-{(None if message is None else message)}", value="", inline=False)
        await ctx.respond(embed=embed)

    @slash_command(name="leave-add", description="Add leave message channel")
    @option("channel", description="Please enter a valid channel")
    async def set_leave(self, ctx, channel:discord.TextChannel):
        leave_file_path = os.path.join("database", "leave.json")
        language = await Language().language_member_msg(ctx.guild.id)
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond(language.get('member_dict_admin'))
            return
        read_json, write_json = await self.json_process(leave_file_path)
        data = await read_json()
        data[str(ctx.guild.id)] = channel.id
        await write_json(data)
        embed=discord.Embed(title=f"{ctx.guild.name}", color=0xfabab8, timestamp=datetime.now())
        embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ",icon_url=self.bot.user.avatar.url)
        embed.add_field(name=language.get('member_dict_updated'), value=language.get('member_dict_channel').format(channel.mention), inline=False)
        await ctx.respond(embed=embed)

    @slash_command(name="leave-remove", description="Remove leave message channel")
    async def set_leave_remove(self, ctx):
        leave_file_path = os.path.join("database", "leave.json")
        language = await Language().language_member_msg(ctx.guild.id)
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond(language.get('member_dict_admin'))
            return
        read_json, write_json = await self.json_process(leave_file_path)
        data = await read_json()
        if str(ctx.guild.id) in data:
            Channel = self.bot.get_channel(data[str(ctx.guild.id)])
            del data[str(ctx.guild.id)]
            await write_json(data)
            embed=discord.Embed(title=f"{ctx.guild.name}", color=0xfabab8, timestamp=datetime.now())
            embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ",icon_url=self.bot.user.avatar.url)
            embed.add_field(name=language.get('member_dict_updated'), value=language.get('member_dict_removed').format(Channel.mention), inline=False)
            await ctx.respond(embed=embed)
        else:
            embed=discord.Embed(title=f"{ctx.guild.name}", color=0xfabab8, timestamp=datetime.now())
            embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ",icon_url=self.bot.user.avatar.url)
            embed.add_field(name=language.get('member_dict_failed'), value=language.get('member_dict_not_found'), inline=False)
            await ctx.respond(embed=embed)

    @slash_command(name="welcome-remove", description="Remove join message channel")
    async def set_welcome_remove(self, ctx):
        welcome_file_path = os.path.join("database", "welcome.json")
        language = await Language().language_member_msg(ctx.guild.id)
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond(language.get('member_dict_admin'))
            return
        read_json, write_json = await self.json_process(welcome_file_path)
        data = await read_json()
        if str(ctx.guild.id) in data:
            Channel = self.bot.get_channel(data[str(ctx.guild.id)]['channel'])
            del data[str(ctx.guild.id)]
            await write_json(data)
            embed=discord.Embed(title=f"{ctx.guild.name}", color=0xfabab8, timestamp=datetime.now())
            embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ",icon_url=self.bot.user.avatar.url)
            embed.add_field(name=language.get('member_dict_updated'), value=language.get('member_dict_removed').format(Channel.mention), inline=False)
            await ctx.respond(embed=embed)
        else:
            embed=discord.Embed(title=f"{ctx.guild.name}", color=0xfabab8, timestamp=datetime.now())
            embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ",icon_url=self.bot.user.avatar.url)
            embed.add_field(name=language.get('member_dict_failed'), value=language.get('member_dict_not_found'), inline=False)
            await ctx.respond(embed=embed)
            
def setup(bot):
    bot.add_cog(Member(bot))