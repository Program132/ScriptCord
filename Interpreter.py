import discord

class Interpreter:
    def __init__(self, client):
        self.client               = client
        self.embeds               = {}
        self.script_type          = None
        self.global_vars          = {}
        self.message_channel_map  = {}

    def load_script(self, parsed_commands):
        if not parsed_commands or parsed_commands[0]["type"] != "config":
            raise ValueError("First instruction must be 'config'.")
        self.script_type = parsed_commands[0]["name"]
        required = ["GUILD"] if self.script_type=="DEFAULT" else ["COMMAND_NAME","DESCRIPTION","ALIASES","GUILD"]
        for var in required:
            found = next((c for c in parsed_commands if c["type"]=="set" and c["name"]==var), None)
            if found:
                self.global_vars[var] = found["value"]
            elif var=="GUILD":
                self.global_vars["GUILD"] = None

    async def execute(self, parsed_commands):
        self.load_script(parsed_commands)

        # pick or auto-detect guild
        if self.global_vars["GUILD"]:
            gid   = int(self.global_vars["GUILD"])
            guild = self.client.get_guild(gid)
        else:
            guild = self.client.guilds[0]
            self.global_vars["GUILD"] = str(guild.id)

        for cmd in parsed_commands[1:]:
            h = getattr(self, f"handle_{cmd['type']}", None)
            if h:
                await h(cmd, guild)

    async def get_channel(self, channel_id):
        cid = int(channel_id)
        for g in self.client.guilds:
            ch = g.get_channel(cid)
            if ch:
                return ch
        raise ValueError(f"Channel {cid} not found.")

    async def handle_send(self, command, guild):
        ch  = await self.get_channel(command["channel_id"])
        msg = await ch.send(command["message"])
        self.message_channel_map[msg.id] = ch.id

    async def handle_react(self, command, guild):
        mid = int(command["message_id"])
        cid = self.message_channel_map.get(mid)
        if not cid:
            raise ValueError(f"Don’t know channel for message {mid}.")
        ch = await self.get_channel(cid)
        msg = await ch.fetch_message(mid)
        await msg.add_reaction(command["emoji"])

    async def handle_role(self, command, guild):
        m = guild.get_member(int(command["member"]))
        r = guild.get_role(int(command["role"]))
        if command["function"]=="add":
            await m.add_roles(r)
        else:
            await m.remove_roles(r)

    async def handle_embed(self, command, guild):
        name, fn = command["name"], command["function"]
        if fn=="create":
            self.embeds[name] = discord.Embed(); return

        if name not in self.embeds:
            raise ValueError(f"Embed '{name}' not created.")
        e = self.embeds[name]

        if fn=="conf":
            e.title       = command["title"]
            e.url         = command["url"]
            e.description = command["desc"]
            c = command["color"].lstrip("#")
            e.color       = discord.Color(int(c,16))
        elif fn=="set_author":
            e.set_author(name=command["author_name"],
                         url=command["author_url"],
                         icon_url=command["author_icon"])
        elif fn=="set_thumbails":
            e.set_thumbnail(url=command["thumbnail_url"])
        elif fn in ("add_l","add_nl"):
            e.add_field(name=command["title"],
                        value=command["value"],
                        inline=command["inline"])
        elif fn=="set_footer":
            e.set_footer(text=command["footer_text"])
        elif fn=="send":
            ch = await self.get_channel(command["channel_id"])
            sent = await ch.send(embed=e)
            del self.embeds[name]