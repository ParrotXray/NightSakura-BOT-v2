import os
import json
import asyncio
import discord
import aiofiles
from pycord.ext import ipc
from pycord.i18n import I18n
from datetime import datetime
from discord.ext import commands, tasks
from modules.GitControl import GitControl
from definition.Language import CommandLanguage

with open("config.json" , "r" ,encoding="utf8") as configFiles:  
    config = json.load(configFiles)

intents = discord.Intents.default()
intents.members = True
bot = discord.Bot(intents=intents, proxy=config["ProxyIP"])
command_language = CommandLanguage()
ipc_server = ipc.Server(bot, secret_key=config["IPCSecret"], host=config["IPCHost"], port=63719)
i18n = I18n(bot, consider_user_locale=True, ja=command_language.command_jp_msg(), zh_TW=command_language.command_tw_msg(), zh_CN=command_language.command_cn_msg())

print("Bot starting...")

@bot.event
async def on_ready():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("*"*20)
    print(f"🌸 {bot.user}({bot.user.id}) \N{COPYRIGHT SIGN} 夜桜の月スタジオ")
    print("💠 BOT Launcher ver - v1.0.5")
    print("💠 BOT ver - v1.0.6")
    print("*"*20)
    print("💮 Number of joined server: " + str(len(bot.guilds)))
    for i in range(len(bot.guilds)):
        print(f'⭐Name:{bot.guilds[i].name},ID:{bot.guilds[i].id}')
    print("*"*20)
    print("Debug Log:\n")
    await asyncio.gather(backup_database.start(), act_status.start())

@bot.event
async def on_ipc_error(endpoint, error):
    """Called upon an error being raised within an IPC route"""
    print(endpoint, "raised", error)
     
@ipc_server.route()
async def get_guild_count(data):
    return len(bot.guilds) # returns the len of the guilds to the client

@ipc_server.route()
async def get_channel_count(data):
    total_channels = sum(len(guild.channels) for guild in bot.guilds)
    return total_channels

@ipc_server.route()
async def get_member_count(data):
    total_members = sum(len(guild.members) for guild in bot.guilds)
    return total_members

@ipc_server.route()
async def get_guild_ids(data):
    final = []
    for guild in bot.guilds:
        final.append(guild.id)
    return final # returns the guild ids to the client

@ipc_server.route()
async def get_guild(data):
    guild = bot.get_guild(data.guild_id)
    if guild is None: return None

    guild_data = {
		"name": guild.name,
		"id": guild.id,
        "member_count": guild.member_count,
		"premium_tier" : guild.premium_tier,
        "icon" : guild._icon
	}

    return guild_data

@tasks.loop(seconds=20)
async def act_status():
    Activity = discord.Activity(type=discord.ActivityType.watching,name="/help")
    await bot.change_presence(activity=Activity)
    await asyncio.sleep(20)
    Activity = discord.Activity(type=discord.ActivityType.watching,name=f"{len(bot.guilds)} server")
    await bot.change_presence(activity=Activity)
    await asyncio.sleep(20)
    Activity = discord.Activity(type=discord.ActivityType.watching,name=f"{sum(len(guild.members) for guild in bot.guilds)} members")
    await bot.change_presence(activity=Activity)
    await asyncio.sleep(20)
    guilds_file_path = os.path.join("database", "guilds.json")
    async with aiofiles.open(guilds_file_path, 'w', encoding='utf-8') as file:
        await file.write(json.dumps("{}", indent=4, ensure_ascii=False))
    async with aiofiles.open(guilds_file_path, 'r', encoding='utf-8') as file:
        json.loads(await file.read())
    data = {'ServerCount': len(bot.guilds), 'ServerList': {}}
    for i in range(len(bot.guilds)):
        data['ServerList'][str(bot.guilds[i].name)] = bot.guilds[i].id
    async with aiofiles.open(guilds_file_path,  'w', encoding='utf-8') as file:
        await file.write(json.dumps(data, indent=4, ensure_ascii=False))

@tasks.loop(hours=12)
async def backup_database():
    await GitControl.git_push('database', '')

def load():
    # still doesn't need to be async
    for filename in os.listdir('./Command'):
        if filename.endswith('.py'):
            try:
                bot.load_extension(f'Command.{filename[:-3]}')
                print(f'✅   loading {filename}')
            except Exception as error:
                print(f'❎   {filename} error {error}')

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

load()
ipc_server.start()
i18n.localize_commands()
bot.run(config["Token"])