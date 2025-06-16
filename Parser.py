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

    def set_INSTRUCTION(self):
        var = self.expect(TokenType.IDENTIFIANT, "Variable globale attendue après `set`")

        if self.current.type == TokenType.STRING:
            val = self.expect(TokenType.STRING, "Chaîne attendue après nom de variable")
        elif self.current.type == TokenType.NUMBER:
            val = self.expect(TokenType.NUMBER, "Nombre attendu après nom de variable")
        else:
            raise ParseError(f"Unexpected value type for variable `{var.value}`, got {self.current}")

        return {
            "type": "set",
            "name": var.value,
            "value": val.value
        }

    def setl_INSTRUCTION(self):
        var = self.expect(TokenType.IDENTIFIANT, "Variable local attendue après `set`")
        val = self.expect(TokenType.STRING, "Chaîne attendue après nom de variable")
        return {
            "type": "set",
            "name": var.value,
            "value": val.value
        }

    def send_INSTRUCTION(self):
        msg = self.expect(TokenType.STRING, "Message attendu après `send`")
        ch  = self.expect(TokenType.NUMBER, "ID de channel attendu après le message")
        return {
            "type": "send",
            "message": msg.value,
            "channel_id": ch.value
        }

    def react_INSTRUCTION(self):
        emoji = self.expect(TokenType.STRING, "Emoji attendu après `react`")
        mid   = self.expect(TokenType.NUMBER, "ID de message attendu après l'emoji")
        return {
            "type": "react",
            "emoji": emoji.value,
            "message_id": mid.value
        }

    def role_INSTRUCTION(self):
        op   = self.expect(TokenType.OPERATOR,   "Opérateur `:` attendu")
        fn   = self.expect(TokenType.IDENTIFIANT, "Fonction attendue : `add` ou `remove`")
        mem  = self.expect(TokenType.NUMBER,     "ID de membre attendu")
        rid  = self.expect(TokenType.NUMBER,     "ID de rôle attendu")
        return {
            "type":     "role",
            "function": fn.value,
            "member":   mem.value,
            "role":     rid.value
        }

    def embed_INSTRUCTION(self):
        op = self.expect(TokenType.OPERATOR, "Expected `:` operator")
        fn = self.expect(TokenType.IDENTIFIANT,
                         "Expected function name: `create`, `conf`, `set_author`, `set_thumbails`, `add_l`, `add_nl`, `set_footer`, `send`")

        embed_name = self.expect(TokenType.IDENTIFIANT, "Expected embed name as first argument")

        if fn.value == "create":
            return {
                "type": "embed",
                "function": "create",
                "name": embed_name.value
            }

        elif fn.value == "conf":
            title = self.expect(TokenType.STRING, "Expected title")
            url = self.expect(TokenType.STRING, "Expected URL")
            desc = self.expect(TokenType.STRING, "Expected description")
            color = self.expect(TokenType.STRING, "Expected color hex code")
            return {
                "type": "embed",
                "function": "conf",
                "name": embed_name.value,
                "title": title.value,
                "url": url.value,
                "desc": desc.value,
                "color": color.value
            }

        elif fn.value == "set_author":
            name = self.expect(TokenType.STRING, "Expected author name")
            url = self.expect(TokenType.STRING, "Expected author URL")
            icon = self.expect(TokenType.STRING, "Expected icon URL")
            return {
                "type": "embed",
                "function": "set_author",
                "name": embed_name.value,
                "author_name": name.value,
                "author_url": url.value,
                "author_icon": icon.value
            }

        elif fn.value == "set_thumbails":
            url = self.expect(TokenType.STRING, "Expected thumbnail URL")
            return {
                "type": "embed",
                "function": "set_thumbails",
                "name": embed_name.value,
                "thumbnail_url": url.value
            }

        elif fn.value == "add_l":
            title = self.expect(TokenType.STRING, "Expected field title")
            value = self.expect(TokenType.STRING, "Expected field value")
            return {
                "type": "embed",
                "function": "add_l",
                "name": embed_name.value,
                "title": title.value,
                "value": value.value,
                "inline": True
            }

        elif fn.value == "add_nl":
            title = self.expect(TokenType.STRING, "Expected field title")
            value = self.expect(TokenType.STRING, "Expected field value")
            return {
                "type": "embed",
                "function": "add_nl",
                "name": embed_name.value,
                "title": title.value,
                "value": value.value,
                "inline": False
            }

        elif fn.value == "set_footer":
            text = self.expect(TokenType.STRING, "Expected footer text")
            return {
                "type": "embed",
                "function": "set_footer",
                "name": embed_name.value,
                "footer_text": text.value
            }

        elif fn.value == "send":
            channel_id = self.expect(TokenType.NUMBER, "Expected channel ID")
            return {
                "type": "embed",
                "function": "send",
                "name": embed_name.value,
                "channel_id": channel_id.value
            }

        else:
            raise ParseError(f"Unknown embed function: {fn.value}")