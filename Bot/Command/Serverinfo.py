import discord
from discord import message
from discord.commands import slash_command
from discord import option
from discord.ext import commands
from definition.Classes import Cog_Extension
from definition.Language import Language
from datetime import datetime

class Serverinfo(Cog_Extension):
    @commands.Cog.listener()
    async def on_ready(self):
        now = datetime.now()
        day=now.strftime("%Y-%m-%d %H:%M:%S")
        print (f'{day}-Serverinfo has loaded')

    @slash_command(name="serverinfo", description="View server information")
    async def serverinfo(self, ctx):
        language = await Language().language_serverinfo_msg(ctx.guild.id)
        guild = ctx.guild
        # statuses = [len(list(filter(lambda m: str(m.status) == "online", guild.members))),
        #             len(list(filter(lambda m: str(m.status) == "idle", guild.members))),
        #             len(list(filter(lambda m: str(m.status) == "dnd", guild.members))),
        #             len(list(filter(lambda m: str(m.status) == "offline", guild.members)))]

        embed = discord.Embed(title=f"{guild.name} ({guild.id})", description=f"{str(guild.member_count)} {language.get('serverinfo_dict_description')}", color=0xfeadbc, timestamp=datetime.now())
        embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ",icon_url=self.bot.user.avatar.url)

        embed.set_thumbnail(url=(guild.icon.url if guild.icon.url else 'https://discordapp.com/assets/322c936a8c8be1b803cd94861bdfa868.png'))
        fields = [(f"🪪{language.get('serverinfo_dict_id')}", f'`{guild.id}`', True),
                (f"👑 {language.get('serverinfo_dict_owner')}", guild.owner, True),
                (f"⏰ {language.get('serverinfo_dict_creation')}", guild.created_at.strftime("%Y/%m/%d %H:%M:%S"), True),
                (f"👤 {language.get('serverinfo_dict_total')}", len(guild.members), True),
                (f"👥 {language.get('serverinfo_dict_members')}", len(list(filter(lambda m: not m.bot, guild.members))), True),
                (f"🤖 {language.get('serverinfo_dict_bots')}", len(list(filter(lambda m: m.bot, guild.members))), True),
                # (f"💥 {language.get('serverinfo_dict_status')}", f"🟢 {statuses[0]} 🟠 {statuses[1]} 🔴 {statuses[2]} ⚪ {statuses[3]}", True),
                (f"💬 {language.get('serverinfo_dict_text')}", len(guild.text_channels), True),
                (f"📣 {language.get('serverinfo_dict_voice')}", len(guild.voice_channels), True),
                (f"💎 {language.get('serverinfo_dict_categories')}", len(guild.categories), True),
                (f"💠 {language.get('serverinfo_dict_roles')}", len(guild.roles), True),
                (f"🏵️ {language.get('serverinfo_dict_invites')}", len(await guild.invites()), True),
                ("\u200b", "\u200b", True)]

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        await ctx.respond(embed=embed)
def setup(bot):
    bot.add_cog(Serverinfo(bot))