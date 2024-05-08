from quart import Quart, render_template, request, session, redirect, url_for
from quart_discord import DiscordOAuth2Session
from pycord.ext import ipc
import os
import json

with open("config.json" , "r" ,encoding="utf8") as configFiles:  
    config = json.load(configFiles)

app = Quart(__name__)
ipc_client = ipc.Client(secret_key=config["IPCSecret"], host=config["IPCHost"], port=63719)

app.config["SECRET_KEY"] = config["SecretKey"]
app.config["DISCORD_CLIENT_ID"] = config["DiscordClientID"]   # Discord client ID.
app.config["DISCORD_CLIENT_SECRET"] = config["DiscordClientSecret"]   # Discord client secret.
app.config["DISCORD_REDIRECT_URI"] = config["DiscordRedirectURI"]   
app.config["EXPLAIN_TEMPLATE_LOADING"] = False

discord = DiscordOAuth2Session(app)

@app.route("/")
async def home():
	guild_count = await ipc_client.request("get_guild_count")
	channel_count = await ipc_client.request("get_channel_count")
	member_count = await ipc_client.request("get_member_count")
	return await render_template("index.html", authorized = await discord.authorized, guild_count = guild_count, channel_count = channel_count, member_count = member_count)

@app.route("/login")
async def login():
	return await discord.create_session()

@app.route("/callback")
async def callback():
	try:
		await discord.callback()
	except Exception:
		pass

	return redirect(url_for("dashboard"))

@app.route("/dashboard")
async def dashboard():
	if not await discord.authorized:
		return redirect(url_for("login")) 

	guild_count = await ipc_client.request("get_guild_count")
	guild_ids = await ipc_client.request("get_guild_ids")

	user_guilds = await discord.fetch_guilds()

	guilds = []

	for guild in user_guilds:
		if guild.permissions.administrator:			
			guild.class_color = "green-border" if guild.id in guild_ids else "red-border"
			guilds.append(guild)

	guilds.sort(key = lambda x: x.class_color == "red-border")
	name = (await discord.fetch_user()).name
	return await render_template("dashboard.html", guild_count = guild_count, guilds = guilds, username=name)

@app.route("/privacy")
async def privacy():
	guild_count = await ipc_client.request("get_guild_count")
	channel_count = await ipc_client.request("get_channel_count")
	member_count = await ipc_client.request("get_member_count")
	return await render_template("privacy.html", authorized = await discord.authorized, guild_count = guild_count, channel_count = channel_count, member_count = member_count)

@app.route("/service")
async def service():
	guild_count = await ipc_client.request("get_guild_count")
	channel_count = await ipc_client.request("get_channel_count")
	member_count = await ipc_client.request("get_member_count")
	return await render_template("service.html", authorized = await discord.authorized, guild_count = guild_count, channel_count = channel_count, member_count = member_count)

@app.route("/dashboard/<int:guild_id>")
async def dashboard_server(guild_id):
	if not await discord.authorized:
		return redirect(url_for("login")) 

	guild = await ipc_client.request("get_guild", guild_id = guild_id)
	if guild is None:
		return redirect(f'https://discord.com/oauth2/authorize?&client_id={app.config["DISCORD_CLIENT_ID"]}&scope=bot&permissions=8&guild_id={guild_id}&response_type=code&redirect_uri={app.config["DISCORD_REDIRECT_URI"]}')
	return await render_template("guild.html", guild=guild)
	# return guild["name"]

os.system('cls' if os.name == 'nt' else 'clear')
app.run(host="0.0.0.0", port=30487, debug=True, ca_certs="", certfile="", keyfile="")