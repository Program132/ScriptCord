import discord

class Data:
    def __init__(self):
        self.global_vars = {}
        self.local_vars  = {}
        self.embeds      = {}
        self.msg_chan    = {}

class Interpreter:
    def __init__(self, client):
        self.client      = client
        self.data        = Data()
        self.script_type = None
        self.ctx         = None

    def load_script(self, nodes):
        if not nodes or nodes[0]["type"] != "config":
            raise ValueError("First instruction must be config")
        self.script_type = nodes[0]["name"]
        for n in nodes:
            if n["type"] == "set" and n["scope"] == "global":
                self.data.global_vars[n["name"]] = n["value"]

    async def execute(self, nodes, context=None):
        self.ctx = context
        self.load_script(nodes)
        if "GUILD" in self.data.global_vars and self.data.global_vars["GUILD"] is not None:
            gid   = int(self._resolve(self.data.global_vars["GUILD"]))
            guild = self.client.get_guild(gid)
        else:
            guild = self.client.guilds[0]
            self.data.global_vars["GUILD"] = {"kind":"number","value":str(guild.id)}
        for n in nodes[1:]:
            if n["type"] == "set":
                if n["scope"] == "local":
                    self.data.local_vars[n["name"]] = n["value"]
            else:
                await getattr(self, f"handle_{n['type']}")(n, guild)

    def _resolve(self, v):
        if isinstance(v, dict):
            if v["kind"] == "var":
                name = v["value"]
                if name in self.data.local_vars:
                    return self.data.local_vars[name]["value"]
                if name in self.data.global_vars:
                    return self.data.global_vars[name]["value"]
                raise ValueError(f"Unknown var {name}")
            return v["value"]
        return v

    async def get_channel(self, cid):
        cid = int(cid)
        for g in self.client.guilds:
            c = g.get_channel(cid)
            if c:
                return c
        raise ValueError(f"Channel {cid} not found")

    async def handle_send(self, n, guild):
        msg = self._resolve(n["message"])
        if n["channel"]:
            cid = self._resolve(n["channel"])
            ch  = await self.get_channel(cid)
        else:
            ch = self.ctx.channel
        m = await ch.send(msg)
        self.data.msg_chan[m.id] = ch.id

    async def handle_react(self, n, guild):
        mid = int(self._resolve(n["message"]))
        cid = self.data.msg_chan.get(mid)
        if cid is None:
            raise ValueError(f"Unknown message {mid}")
        ch = await self.get_channel(cid)
        m = await ch.fetch_message(mid)
        await m.add_reaction(n["emoji"])

    async def handle_role(self, n, guild):
        m = guild.get_member(int(self._resolve(n["member"])))
        r = guild.get_role(int(self._resolve(n["role"])))
        if n["function"] == "add":
            await m.add_roles(r)
        else:
            await m.remove_roles(r)

    async def handle_embed(self, n, guild):
        buf, fn = n["name"], n["function"]
        if fn == "create":
            self.data.embeds[buf] = discord.Embed()
            return
        e = self.data.embeds.get(buf)
        if fn == "conf":
            e.title       = self._resolve(n["title"])
            e.url         = self._resolve(n["url"])
            e.description = self._resolve(n["desc"])
            c = self._resolve(n["color"]).lstrip("#")
            e.color       = discord.Color(int(c,16))
        elif fn == "set_author":
            e.set_author(
                name     = self._resolve(n["author_name"]),
                url      = self._resolve(n["author_url"]),
                icon_url = self._resolve(n["author_icon"])
            )
        elif fn == "set_thumbnails":
            e.set_thumbnail(url=self._resolve(n["thumbnail_url"]))
        elif fn in ("add_l","add_nl"):
            e.add_field(
                name   = self._resolve(n["title"]),
                value  = self._resolve(n["value"]),
                inline = n["inline"]
            )
        elif fn == "set_footer":
            e.set_footer(text=self._resolve(n["footer_text"]))
        elif fn == "send":
            if n.get("channel"):
                cid = self._resolve(n["channel"])
                ch  = await self.get_channel(cid)
            else:
                ch = self.ctx.channel
            await ch.send(embed=e)
            del self.data.embeds[buf]