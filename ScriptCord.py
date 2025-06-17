import discord
from pathlib import Path
from Lexer import Lexer
from Parser import Parser
from Interpreter import Interpreter

class ScriptCord(discord.Client):
    def __init__(self, *, intents: discord.Intents, prefix: str):
        super().__init__(intents=intents)
        self.prefix = prefix
        self.default_scripts = []
        self.commands = {}
        self.tree = discord.app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

    async def on_ready(self):
        print(f"🔌 Logged on as {self.user}!")
        for nodes in self.default_scripts:
            await Interpreter(self).execute(nodes)

    async def on_message(self, message):
        if self.prefix is None or message.author.bot:
            return

        content = message.content.strip()
        if not content:
            return

        for cmd in self.commands.values():
            if cmd["guild"] and message.guild and message.guild.id != cmd["guild"]:
                continue
            triggers = [cmd["name"]] + cmd["aliases"]
            if any(content == f"{self.prefix}{t}" for t in triggers):
                await Interpreter(self).execute(cmd["nodes"], context=message)
                return

    def register(self, script_path: str):
        if self.prefix is None:
            return
        text  = Path(script_path).read_text(encoding="utf-8")
        nodes = Parser(Lexer(text)).getNodes()
        cfg   = nodes[0]
        if cfg["type"] != "config":
            raise ValueError("Script must start with config")

        if cfg["name"] == "DEFAULT":
            self.default_scripts.append(nodes)
            return

        if cfg["name"] == "COMMAND":
            name       = next(n["value"]["value"]
                              for n in nodes
                              if n["type"]=="set" and n["name"]=="COMMAND_NAME")
            desc       = next(n["value"]["value"]
                              for n in nodes
                              if n["type"]=="set" and n["name"]=="DESCRIPTION")
            alias_node = next((n for n in nodes
                               if n["type"]=="set" and n["name"]=="ALIASES"), None)
            aliases    = [a.strip()
                          for a in alias_node["value"]["value"].split(",")] if alias_node else []
            guild_node = next((n for n in nodes
                               if n["type"]=="set" and n["name"]=="GUILD"), None)
            guild      = int(guild_node["value"]["value"]) if guild_node else None

            self.commands[name] = {
                "nodes":       nodes,
                "name":        name,
                "description": desc,
                "aliases":     aliases,
                "guild":       guild
            }
            return

        raise ValueError(f"Unknown config type: {cfg['name']}")
