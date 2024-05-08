import os
import json
import discord
from pythonping import ping
from datetime import datetime
from discord.ext import commands
from definition.Language import Language
from discord.commands import slash_command
from definition.Classes import Cog_Extension

class Delay(Cog_Extension):
    # DELAY
    @commands.Cog.listener()
    async def on_ready(self):
        now = datetime.now()
        day=now.strftime("%Y-%m-%d %H:%M:%S")
        print (f'{day}-Delay has loaded')
    @slash_command(name="delay", description="Check bot latency")
    async def delay(self, ctx):
        now = datetime.now()
        day=now.strftime("%Y-%m-%d %H:%M:%S")
        print(f'{day}-Connecting Server...')
        language = await Language().language_delay_msg(ctx.guild.id)
        await ctx.defer()
        embed=discord.Embed(title="",timestamp=datetime.now())
        embed.set_footer(text="桜の夜 \N{COPYRIGHT SIGN} 夜桜の月スタジオ",icon_url=self.bot.user.avatar.url)
        if self.bot.latency * 1000 <= 1000:
            embed.color = 0x28FF28
        else:
            embed.color = 0xAE0000
        embed.add_field(name=language.get('delay_dict_bot'), value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        if self.bot.latency * 1000 <= 1000:
            embed.add_field(name=language.get('delay_dict_current'), value=f":green_circle:-{language.get('delay_dict_normal')}", inline=False)
        else:
            embed.add_field(name=language.get('delay_dict_current'), value=f":red_circle:-{language.get('delay_dict_timeout')}", inline=False)
        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(Delay(bot))