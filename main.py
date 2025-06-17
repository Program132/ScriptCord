import json
import discord
from ScriptCord import ScriptCord

with open("config.json", "r") as f:
    cfg = json.load(f)

# 1) Définition des intents
intents = discord.Intents(
    guilds=True,
    messages=True,
    message_content=True
)
intents.reactions = True

# 2) Instanciation du bot
bot = ScriptCord(intents=intents, prefix=";")

# 3) Enregistrement des scripts
bot.register("default.sc")       # scripts DEFAULT
bot.register("cmd_ping.sc")      # !ping

# 4) Démarrage
bot.run(cfg["token"])