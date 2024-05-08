import discord
from discord import message
from discord.commands import slash_command
from discord import option
from discord.ext import commands
from definition.Classes import Cog_Extension
from definition.Language import Language
from datetime import datetime
import asyncio

class Userinfo(Cog_Extension):
    @commands.Cog.listener()
    async def on_ready(self):
        now = datetime.now()
        day=now.strftime("%Y-%m-%d %H:%M:%S")
        print (f'{day}-Userinfo has loaded')

    @slash_command(name="userinfo", description="View user information")
    @option('user', discord.Member, description='Please select a user')
    async def userinfo(self, ctx, user=None):
            language = await Language().language_userinfo_msg(ctx.guild.id)
            author = user or ctx.author
            
            embed = discord.Embed(title=f"{author} {language.get('userinfo_dict_information')}",
                        colour=author.colour,
                        timestamp=datetime.now())
            embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ",icon_url=self.bot.user.avatar.url)
            
            # match str(author.status).title():
            #     case 'Offline':
            #         author_status = '⚪'
            #     case 'Idle':
            #         author_status = '🟠'
            #     case 'Dnd':
            #         author_status = '🔴'
            #     case 'Online':
            #         author_status = '🟢'
            #     case None:
            #         author_status = ''

            # if author.activity:
            #     match str(author.activity.type).split('.')[-1].title():
            #         case 'Playing':
            #             activity_type = language.get('userinfo_dict_playing')
            #         case 'Streaming':
            #             activity_type = language.get('userinfo_dict_streaming')
            #         case 'Listening':
            #             activity_type = language.get('userinfo_dict_listening')
            #         case 'Watching':
            #             activity_type = language.get('userinfo_dict_watching')
            #         case 'Competing':
            #             activity_type = language.get('userinfo_dict_competing')
            #         case 'Custom':
            #             activity_type = ""
            # else:
            #     activity_type = ""

            embed.set_thumbnail(url=(author.avatar.url if author.avatar.url else 'https://discordapp.com/assets/322c936a8c8be1b803cd94861bdfa868.png'))
            fields = [(f"👤 {language.get('userinfo_dict_name')}", str(author.name), True),
                    (f"🪪 {language.get('userinfo_dict_id')}", f'`{author.id}`', True),
                    (f"⚙️ {language.get('userinfo_dict_bot')}", (language.get('userinfo_dict_ture') if author.bot is True else language.get('userinfo_dict_false')), True),
                    (f"👥 {language.get('userinfo_dict_role')}", author.top_role.mention, True),
                    # (f"💥 {language.get('userinfo_dict_status')}", author_status, True),
                    # (f"🚨 {language.get('userinfo_dict_activity')}", f"{activity_type if author.activity else language.get('userinfo_dict_none')} {author.activity.name if author.activity else ''}", True),
                    (f"⏰ {language.get('userinfo_dict_time')}", author.created_at.strftime("%Y/%m/%d %H:%M:%S"), True),
                    (f"⏱️ {language.get('userinfo_dict_join')}", author.joined_at.strftime("%Y/%m/%d %H:%M:%S"), True),
                    (f"🚀 {language.get('userinfo_dict_boost')}", (language.get('userinfo_dict_ture') if bool(author.premium_since) is True else language.get('userinfo_dict_false')), True)]
            
            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)
            await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(Userinfo(bot))