import json
import discord
from ScriptCord import ScriptCord

with open("config.json", "r") as f:
    cfg = json.load(f)

intents = discord.Intents.default()
client  = discord.Client(intents=intents)

runner = ScriptCord(client, "command_ex.sc")

@client.event
async def on_ready():
    print(f"Bot is ready as {client.user}")
    await runner.run()

client.run(cfg["token"])