import discord
from discord import message
from discord.commands import slash_command
from discord.ext import commands
from definition.Classes import Cog_Extension
from definition.Language import Language
from datetime import datetime
from discord.ui import Button,View

class Invite(Cog_Extension):
    @commands.Cog.listener()
    async def on_ready(self):
        now = datetime.now()
        day=now.strftime("%Y-%m-%d %H:%M:%S")
        print (f'{day}-Info has loaded')
    @slash_command(name="invite", description="Bot Introduction")
    async def invite(self, ctx):
        now = datetime.now()
        day=now.strftime("%Y-%m-%d %H:%M:%S")
        print(f'{day}-Info')
        language = await Language().language_info_msg(ctx.guild.id)
        button_botlink = Button(label=language.get('info_dict_button_botlink'),style=discord.ButtonStyle.url,url="https://discord.com/api/oauth2/authorize?client_id=1154738787247734784&permissions=8&scope=applications.commands%20bot",emoji="<:bot:1184518149979254795>", row=1)
        button_official = Button(label=language.get('info_dict_button_official'),style=discord.ButtonStyle.url,url="https://www.nightsakuramoon.idv.tw/",emoji="<:night_sakura_logo:1181065765563150376>", row=2)
        button_dc = Button(label=language.get('info_dict_button_dc'),style=discord.ButtonStyle.url,url="https://discord.gg/W9WeC77DPZ",emoji="<:discord:1184518399766827048>", row=1)
        button_pixiv = Button(label=language.get('info_dict_button_pixiv'),style=discord.ButtonStyle.url,url="https://www.pixiv.net/users/59922240",emoji="<:pixiv:1184297633783754783>", row=2)
        button_twitter = Button(label=language.get('info_dict_button_twitter'),style=discord.ButtonStyle.url,url="https://twitter.com/CockatooChino",emoji="<:twitter:1184297615404322887>", row=2)
        view = View()
        view.add_item(button_botlink)
        view.add_item(button_dc)
        view.add_item(button_official)
        view.add_item(button_pixiv)
        view.add_item(button_twitter)
        embed=discord.Embed(title=f"{ctx.guild.name}",color=0xfeadbc,timestamp=datetime.now())
        embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ",icon_url=self.bot.user.avatar.url)
        embed.add_field(name = "", value=language.get('info_dict_msg_value'), inline=False)
        await ctx.response.send_message(embed=embed, view=view)
def setup(bot):
    bot.add_cog(Invite(bot))