import discord
from discord import message
from discord.commands import slash_command
from discord import option
from discord.ext import commands, tasks
from definition.Classes import Cog_Extension
from definition.JsonProcess import JsonProcess
from definition.Language import Language
import json
from discord.ui import Select,View
from datetime import datetime
import os

class Notification(Cog_Extension):
    @commands.Cog.listener()
    async def on_ready(self):
        now = datetime.now()
        day=now.strftime("%Y-%m-%d %H:%M:%S")
        print (f'{day}-Notification has loaded')
        await self.check_notification.start()

    @tasks.loop(minutes = 60)
    async def check_notification(self):
        notification_data_file_path = os.path.join("announcement.json")
        notification_file_path = os.path.join("database", "notificationguilds.json")
        data = await JsonProcess(notification_data_file_path).read_json()
        data_guild = await JsonProcess(notification_file_path).read_json()
        if data['description'] == "" and data['title'] == "" and data['content'] == "":
            return
        else:
            description = data['description']
            title = data['title']
            content = data['content']
            for guild_id, channel_id in data_guild.items():
                try:
                    guild = self.bot.get_guild(int(guild_id))
                    channel = guild.get_channel(channel_id)
                    embed=discord.Embed(title=f"{guild.name}",description=description,color=0xfeadbc,timestamp=datetime.now())
                    embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ",icon_url=self.bot.user.avatar.url)
                    embed.add_field(name = title, value=content, inline=False)
                    await channel.send(embed=embed)
                    data['description'] = ""
                    data['title'] = ""
                    data['content'] = ""
                    await JsonProcess(notification_file_path).write_json(data)
                except:
                    now = datetime.now()
                    day=now.strftime("%Y-%m-%d %H:%M:%S")
                    print(f'{day}-Unrecognized channel')

    @slash_command(name="notification", description="Subscribe to BOT information")
    @option("channel", description="Please enter a valid channel")
    async def subscription(self, ctx, channel:discord.TextChannel):
        now = datetime.now()
        day=now.strftime("%Y-%m-%d %H:%M:%S")
        print(f'{day}-{ctx.guild.name}')
        language = await Language().language_subscription_msg(ctx.guild.id)
        notification_file_path = os.path.join("database", "notificationguilds.json")
        data = await JsonProcess(notification_file_path).read_json()
        data[str(ctx.guild.id)] = channel.id
        await JsonProcess(notification_file_path).write_json(data)
        embed=discord.Embed(title=f"{ctx.guild.name}", color=0xfeadbc, timestamp=datetime.now())
        embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ",icon_url=self.bot.user.avatar.url)
        embed.add_field(name = language.get('subscription_dict_update'), value=f"{language.get('subscription_dict_channel')}[{channel.mention}]", inline=False)
        await ctx.respond(embed=embed)
def setup(bot):
    bot.add_cog(Notification(bot))