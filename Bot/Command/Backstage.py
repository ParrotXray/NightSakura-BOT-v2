import discord
from discord import message
from discord.commands import slash_command
from discord import option
from discord.ext import commands
from definition.Classes import Cog_Extension
from datetime import datetime
from definition.JsonProcess import JsonProcess
import os

class Backstage(Cog_Extension):
    @commands.Cog.listener()
    async def on_ready(self):
        now = datetime.now()
        day=now.strftime("%Y-%m-%d %H:%M:%S")
        print (f'{day}-Backstage has loaded')

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        backstage_file_path = os.path.join("database", "backstage.json")
        data = await JsonProcess(backstage_file_path).read_json()
        if str(member.guild.id) in data:
            try:
                embed=discord.Embed(title="", color=0xfeadbc, timestamp=datetime.now())
                embed.set_author(name=f"{member.name}({member.id})", icon_url=(member.avatar.url if member.avatar.url else 'https://discordapp.com/assets/322c936a8c8be1b803cd94861bdfa868.png'))
                embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ",icon_url=self.bot.user.avatar.url)
                channels = self.bot.get_channel(data[str(member.guild.id)])
                if before.channel != after.channel:
                    if before.channel is None:
                        embed.add_field(name = "成員加入語音頻道", value=f"{member} 加入了語音頻道 **#{after.channel.name}**", inline=False)
                    elif after.channel is None:
                        embed.add_field(name = "成員離開了語音頻道", value=f"{member} 離開了語音頻道 **#{before.channel.name}**", inline=False)
                    else:
                        embed.add_field(name = "成員切換語音頻道", value=f"{member} 從 **#{before.channel}** 切換到了 **#{after.channel.name}**", inline=False)
                    await channels.send(embed=embed)
            except:
                return

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        backstage_file_path = os.path.join("database", "backstage.json")
        data = await JsonProcess(backstage_file_path).read_json()
        if str(after.guild.id) in data:
            try:
                embed=discord.Embed(title="", color=0xfeadbc, timestamp=datetime.now())
                embed.set_author(name=f"{after.name}({after.id})", icon_url=(after.avatar.url if after.avatar.url else 'https://discordapp.com/assets/322c936a8c8be1b803cd94861bdfa868.png'))
                embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ",icon_url=self.bot.user.avatar.url)
                channels = self.bot.get_channel(data[str(after.guild.id)])
                if before.nick != after.nick:
                    embed.add_field(name = "成員暱稱更改", value=f"{before} 的暱稱已從 **{before.nick}** 更改為 **{after.nick}**", inline=False)
                    await channels.send(embed=embed)
                if before.roles != after.roles:
                    added_roles = [role for role in after.roles if role not in before.roles]
                    if added_roles:
                        for role in added_roles:
                            embed.add_field(name = "成員已獲得身分組", value=f"{after} 已獲得 **@{role.name} 身分組**", inline=False)
                    removed_roles = [role for role in before.roles if role not in after.roles]
                    if removed_roles:
                        for role in removed_roles:
                            embed.add_field(name = "成員已失去身分組", value=f"{after} 已失去 **@{role.name}** 身分組", inline=False)
                    await channels.send(embed=embed)
            except:
                return
        
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        backstage_file_path = os.path.join("database", "backstage.json")
        data = await JsonProcess(backstage_file_path).read_json()
        if str(channel.guild.id) in data:
            try:
                embed=discord.Embed(title="", color=0xfeadbc, timestamp=datetime.now())
                embed.set_author(name=f"{channel.guild.name}", icon_url=(channel.guild.icon.url if channel.guild.icon.url else 'https://discordapp.com/assets/322c936a8c8be1b803cd94861bdfa868.png'))
                embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ",icon_url=self.bot.user.avatar.url)
                channels = self.bot.get_channel(data[str(channel.guild.id)])
                if isinstance(channel, discord.TextChannel):
                    embed.add_field(name = "文字頻道創建", value=f"**#{channel.name}** 創建於 {channel.guild.name}", inline=False)
                elif isinstance(channel, discord.VoiceChannel):
                    embed.add_field(name = "語音頻道創建", value=f"**#{channel.name}** 創建於 {channel.guild.name}", inline=False)
                elif isinstance(channel, discord.CategoryChannel):
                    embed.add_field(name = "類別創建", value=f"**{channel.name}** 創建於 {channel.guild.name}", inline=False)
                await channels.send(embed=embed)
            except:
                return
            
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        backstage_file_path = os.path.join("database", "backstage.json")
        data = await JsonProcess(backstage_file_path).read_json()
        if str(channel.guild.id) in data:
            try:
                embed=discord.Embed(title="", color=0xfeadbc, timestamp=datetime.now())
                embed.set_author(name=f"{channel.guild.name}", icon_url=(channel.guild.icon.url if channel.guild.icon.url else 'https://discordapp.com/assets/322c936a8c8be1b803cd94861bdfa868.png'))
                embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ",icon_url=self.bot.user.avatar.url)
                channels = self.bot.get_channel(data[str(channel.guild.id)])
                if isinstance(channel, discord.TextChannel):
                    embed.add_field(name = "文字頻道刪除", value=f"**#{channel.name}** 在 {channel.guild.name} 中被刪除", inline=False)
                elif isinstance(channel, discord.VoiceChannel):
                    embed.add_field(name = "語音頻道刪除", value=f"**#{channel.name}** 在 {channel.guild.name} 中被刪除", inline=False)
                elif isinstance(channel, discord.CategoryChannel):
                    embed.add_field(name = "分類刪除", value=f"**{channel.name}** 在 {channel.guild.name} 中被刪除", inline=False)
                await channels.send(embed=embed)

            except:
                return
        
    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        backstage_file_path = os.path.join("database", "backstage.json")
        data = await JsonProcess(backstage_file_path).read_json()
        if str(after.guild.id) in data:
            try:
                embed=discord.Embed(title="", color=0xfeadbc, timestamp=datetime.now())
                embed.set_author(name=f"{after.guild.name}", icon_url=(after.guild.icon.url if after.guild.icon.url else 'https://discordapp.com/assets/322c936a8c8be1b803cd94861bdfa868.png'))
                embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ",icon_url=self.bot.user.avatar.url)
                channels = self.bot.get_channel(data[str(after.guild.id)])
                if before.name != after.name:
                    embed.add_field(name = "身分組的名稱更新", value=f"身分組 **@{before.name}** 的名稱已更新為 **@{after.name}**", inline=False)
                    await channels.send(embed=embed)
            except:
                return

    @commands.Cog.listener()
    async def on_member_join(self,member):
        backstage_file_path = os.path.join("database", "backstage.json")
        data = await JsonProcess(backstage_file_path).read_json()
        if str(member.guild.id) in data:
            try:
                channels = self.bot.get_channel(data[str(member.guild.id)])
                embed=discord.Embed(title="", color=0xfeadbc, timestamp=datetime.now())
                embed.set_author(name=f"{member.name}({member.id})", icon_url=(member.avatar.url if member.avatar.url else 'https://discordapp.com/assets/322c936a8c8be1b803cd94861bdfa868.png'))
                embed.set_thumbnail(url=(member.avatar.url if member.avatar.url else 'https://discordapp.com/assets/322c936a8c8be1b803cd94861bdfa868.png'))
                embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ",icon_url=self.bot.user.avatar.url)
                embed.add_field(name = "", value=f"{member} 加入了", inline=False)
                await channels.send(embed=embed)
            except:
                return

    @commands.Cog.listener()
    async def on_member_remove(self,member):
        backstage_file_path = os.path.join("database", "backstage.json")
        data = await JsonProcess(backstage_file_path).read_json()
        if str(member.guild.id) in data:
            try:
                channels = self.bot.get_channel(data[str(member.guild.id)])
                embed=discord.Embed(title="", color=0xfeadbc, timestamp=datetime.now())
                embed.set_author(name=f"{member.name}({member.id})", icon_url=(member.avatar.url if member.avatar.url else 'https://discordapp.com/assets/322c936a8c8be1b803cd94861bdfa868.png'))
                embed.set_thumbnail(url=(member.avatar.url if member.avatar.url else 'https://discordapp.com/assets/322c936a8c8be1b803cd94861bdfa868.png'))
                embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ",icon_url=self.bot.user.avatar.url)
                embed.add_field(name = "", value=f"{member} 離開了", inline=False)
                await channels.send(embed=embed)
            except:
                return

    @commands.Cog.listener()
    async def on_guild_emojis_update(self, guild, before, after):
        backstage_file_path = os.path.join("database", "backstage.json")
        data = await JsonProcess(backstage_file_path).read_json()
        if str(guild.id) in data:
            try:
                channels = self.bot.get_channel(data[str(guild.id)])
                embed = discord.Embed(title="", color=0xfeadbc, timestamp=datetime.now())
                embed.set_author(name=f"{guild.name}", icon_url=(guild.icon.url if guild.icon.url else 'https://discordapp.com/assets/322c936a8c8be1b803cd94861bdfa868.png'))
                embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ", icon_url=self.bot.user.avatar.url)
                if len(before) < len(after):
                    # Emoji added
                    for emoji in after:
                        if emoji not in before:
                            emoji_obj = discord.utils.get(guild.emojis, id=emoji.id)
                            embed.add_field(name="新增表情", value=f"`{emoji.name}`")
                            embed.set_thumbnail(url=emoji_obj.url)
                            await channels.send(embed=embed)
                elif len(before) > len(after):
                    # Emoji removed
                    for emoji in before:
                        if emoji not in after:
                            embed.add_field(name="移除表情", value=f"`{emoji.name}`")
                            embed.set_thumbnail(url=emoji.url)
                            await channels.send(embed=embed)
                else:
                    # Emoji updated
                    for emoji in after:
                        if emoji in before and emoji.url != before[before.index(emoji)].url:
                            emoji_obj = discord.utils.get(guild.emojis, id=emoji.id)
                            embed.add_field(name="更新表情", value=f"`{emoji.name}`")
                            embed.set_thumbnail(url=emoji_obj.url)
                            await channels.send(embed=embed)
            except:
                return

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        backstage_file_path = os.path.join("database", "backstage.json")
        data = await JsonProcess(backstage_file_path).read_json()
        if str(after.guild.id) in data:
            try:
                embed=discord.Embed(title="", color=0xfeadbc, timestamp=datetime.now())
                embed.set_author(name=f"{after.guild.name}", icon_url=(after.guild.icon.url if after.guild.icon.url else 'https://discordapp.com/assets/322c936a8c8be1b803cd94861bdfa868.png'))
                embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ", icon_url=self.bot.user.avatar.url)
                channels = self.bot.get_channel(data[str(after.guild.id)])
                if isinstance(after, discord.TextChannel):
                    if before.name != after.name: 
                        embed.add_field(name="頻道的名稱更改", value=f"頻道 **#{before.name}** 的名稱已更改為 **#{after.name}**")
                        await channels.send(embed=embed)
                elif isinstance(after, discord.VoiceChannel):
                    if before.name != after.name: 
                        embed.add_field(name="頻道的名稱更改", value=f"頻道 **#{before.name}** 的名稱已更改為 **#{after.name}**")
                        await channels.send(embed=embed)
            except:
                return

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        backstage_file_path = os.path.join("database", "backstage.json")
        data = await JsonProcess(backstage_file_path).read_json()
        if str(role.guild.id) in data:
            try:
                embed = discord.Embed(title="", color=0xfeadbc, timestamp=datetime.now())
                embed.set_author(name=f"{role.guild.name}", icon_url=(role.guild.icon.url if role.guild.icon.url else 'https://discordapp.com/assets/322c936a8c8be1b803cd94861bdfa868.png'))
                embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ", icon_url=self.bot.user.avatar.url)
                channels = self.bot.get_channel(data[str(role.guild.id)])
                embed.add_field(name="身分組創建", value=f"新的身分組 **@{role.name}** 已經被創建")
                await channels.send(embed=embed)
            except:
                return

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        backstage_file_path = os.path.join("database", "backstage.json")
        data = await JsonProcess(backstage_file_path).read_json()
        if str(role.guild.id) in data:
            try:
                embed = discord.Embed(title="", color=0xfeadbc, timestamp=datetime.now())
                embed.set_author(name=f"{role.guild.name}", icon_url=(role.guild.icon.url if role.guild.icon.url else 'https://discordapp.com/assets/322c936a8c8be1b803cd94861bdfa868.png'))
                embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ", icon_url=self.bot.user.avatar.url)
                channels = self.bot.get_channel(data[str(role.guild.id)])
                embed.add_field(name="身分組刪除", value=f"身分組 **@{role.name}** 已經被刪除")
                await channels.send(embed=embed)
            except:
                return

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        backstage_file_path = os.path.join("database", "backstage.json")
        data = await JsonProcess(backstage_file_path).read_json()
        if str(invite.guild.id) in data:
            try:
                channels = self.bot.get_channel(data[str(invite.guild.id)])
                embed = discord.Embed(title="", color=0xfeadbc, timestamp=datetime.now())
                embed.set_author(name=f"{invite.guild.name}", icon_url=(invite.guild.icon.url if invite.guild.icon.url else 'https://discordapp.com/assets/322c936a8c8be1b803cd94861bdfa868.png'))
                embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ", icon_url=self.bot.user.avatar.url)
                embed.add_field(name="邀請連結創建", value=f"邀請連結 `{invite.code}` 已經創建。")
                await channels.send(embed=embed)
            except:
                return

    @commands.Cog.listener()
    async def on_guild_update(self, before, after):
        backstage_file_path = os.path.join("database", "backstage.json")
        data = await JsonProcess(backstage_file_path).read_json()
        if str(after.id) in data:
            try:
                embed = discord.Embed(title="", color=0xfeadbc, timestamp=datetime.now())
                embed.set_author(name=f"{after.name}", icon_url=(after.icon.url if after.icon.url else 'https://discordapp.com/assets/322c936a8c8be1b803cd94861bdfa868.png'))
                embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ", icon_url=self.bot.user.avatar.url)
                channels = self.bot.get_channel(data[str(after.id)])
                if before.name != after.name:
                    embed.add_field(name="伺服器名稱更改", value=f"伺服器名稱已更改為 **{after.name}**")
                    await channels.send(embed=embed)
                if before.icon != after.icon:
                    embed.set_thumbnail(url=after.icon.url)
                    embed.add_field(name="伺服器圖片更改", value=f"**{after.name}** 圖片已更改")
                    await channels.send(embed=embed)
            except:
                return

    @slash_command(name="backstage", description="Server Activity Log Messages")
    async def backstage(self, ctx, channel:discord.TextChannel):
        backstage_file_path = os.path.join("database", "backstage.json")
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond("只有管理員能使用此指令")
            return
        data = await  JsonProcess(backstage_file_path).read_json()
        data[str(ctx.guild.id)] = channel.id
        data = await JsonProcess(backstage_file_path).write_json(data)
        embed=discord.Embed(title=f"{ctx.guild.name}", color=0xfeadbc, timestamp=datetime.now())
        embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ",icon_url=self.bot.user.avatar.url)
        embed.add_field(name = "資料更新成功", value=f"頻道為<#{channel.id}>", inline=False)
        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(Backstage(bot))