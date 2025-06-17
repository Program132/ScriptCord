from Lexer import TokenType, Lexer

INSTRUCTION_HANDLERS = {
    "config": "config_INSTRUCTION",
    "set":    "set_INSTRUCTION",
    "setl": "setl_INSTRUCTION",
    "send":   "send_INSTRUCTION",
    "react":  "react_INSTRUCTION",
    "role":   "role_INSTRUCTION",
    "embed": "embed_INSTRUCTION",
}

class ParseError(Exception):
    pass

class Parser:
    def __init__(self, lexer: Lexer):
        self.tokens = lexer.tokens
        self.id     = 0
        self.nodes  = []
        self.run()

    @property
    def current(self):
        return self.tokens[self.id] if self.id < len(self.tokens) else None

    def advance(self):
        self.id += 1

    def skip_ignorable(self):
        while self.current and self.current.type == TokenType.COMMENT:
            self.advance()

    def getNodes(self):
        return self.nodes

    def expect(self, ttype, msg):
        if not self.current or self.current.type != ttype:
            raise ParseError(f"{msg}, got {self.current}")
        tok = self.current
        self.advance()
        return tok

    def run(self):
        while self.current:
            self.skip_ignorable()

            if not self.current:
                break

            if not self.manage_instruction():
                raise ParseError(f"Instruction non reconnue : {self.current}")

        return self.nodes

    def manage_instruction(self):
        if not self.current or self.current.type != TokenType.IDENTIFIANT:
            return False

        name = self.current.value
        self.advance()

        handler_name = INSTRUCTION_HANDLERS.get(name)
        if not handler_name:
            return False

        handler = getattr(self, handler_name)
        node    = handler()
        self.nodes.append(node)
        return True

    def config_INSTRUCTION(self):
        conf = self.expect( TokenType.IDENTIFIANT,"Nom de configuration attendu après `config` (ex: COMMAND, BOT ou EVENT)")
        return {
            "type": "config",
            "name": conf.value
        }

    def _parse_value(self, what):
        t = self.current
        if t.type == TokenType.STRING:
            tok = self.expect(TokenType.STRING, f"{what} (string) expected")
            return {"kind": "string", "value": tok.value}

        if t.type == TokenType.NUMBER:
            tok = self.expect(TokenType.NUMBER, f"{what} (number) expected")
            return {"kind": "number", "value": tok.value}

        if t.type == TokenType.IDENTIFIANT:
            tok = self.expect(TokenType.IDENTIFIANT, f"{what} (var name) expected")
            return {"kind": "var", "value": tok.value}

        raise ParseError(f"{what} not recognized, got {t}")

    def set_INSTRUCTION(self):
        var = self.expect(TokenType.IDENTIFIANT, "Expected global var name after `set`")
        val = self._parse_value("global variable")
        return { "type":"set", "scope":"global", "name":var.value, "value":val }

    def setl_INSTRUCTION(self):
        var = self.expect(TokenType.IDENTIFIANT, "Expected local var name after `setl`")
        val = self._parse_value("local variable")
        return { "type":"set", "scope":"local", "name":var.value, "value":val }

    def send_INSTRUCTION(self):
        msg = self._parse_value("message or variable")
        if self.current and self.current.type in (
                TokenType.STRING,
                TokenType.NUMBER,
                TokenType.IDENTIFIANT
        ):
            ch = self._parse_value("channel ID or variable")
        else:
            ch = None
        return {
            "type": "send",
            "message": msg,
            "channel": ch
        }

    def react_INSTRUCTION(self):
        emoji = self.expect(TokenType.STRING, "Emoji expected")
        mid   = self._parse_value("message ID or var")
        return { "type":"react", "emoji":emoji.value, "message":mid }

    def role_INSTRUCTION(self):
        op   = self.expect(TokenType.OPERATOR,   "Opérateur `:` attendu")
        fn   = self.expect(TokenType.IDENTIFIANT, "Fonction attendue : `add` ou `remove`")
        mem  = self._parse_value("ID de membre attendu")
        rid  = self._parse_value("ID de rôle attendu")
        return {
            "type":     "role",
            "function": fn.value,
            "member":   mem,
            "role":     rid
        }

    def embed_INSTRUCTION(self):
        self.expect(TokenType.OPERATOR, "Expected ':' after embed")
        fn_tok = self.expect(TokenType.IDENTIFIANT,
                             "Embed function expected (create, conf, …)")
        fn = fn_tok.value
        name_tok = self.expect(TokenType.IDENTIFIANT, "Embed name expected")
        buf = name_tok.value

        base = {
            "type": "embed",
            "function": fn,
            "name": buf
        }
        if fn == "create":
            return base
        if fn == "conf":
            return {
                **base,
                "title": self._parse_value("embed title"),
                "url": self._parse_value("embed URL"),
                "desc": self._parse_value("embed description"),
                "color": self._parse_value("embed color")
            }
        if fn == "set_author":
            return {
                **base,
                "author_name": self._parse_value("author name"),
                "author_url": self._parse_value("author URL"),
                "author_icon": self._parse_value("author icon URL")
            }
        if fn == "set_thumbnails":
            return {
                **base,
                "thumbnail_url": self._parse_value("thumbnail URL")
            }
        if fn in ("add_l", "add_nl"):
            return {
                **base,
                "title": self._parse_value("field title"),
                "value": self._parse_value("field value"),
                "inline": (fn == "add_l")
            }
        if fn == "set_footer":
            return {
                **base,
                "footer_text": self._parse_value("footer text")
            }
        if fn == "send":
            return {
                **base,
                "channel": self._parse_value("channel ID")
            }
        raise ParseError(f"Unknown embed function: {fn}")