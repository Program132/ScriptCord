from enum import Enum

class TokenType(Enum):
    WHITESPACE  = "WHITESPACE"
    IDENTIFIANT = "IDENTIFIANT"
    NUMBER      = "NUMBER"
    STRING      = "STRING"
    BOOLEAN     = "BOOLEAN"
    COMMENT     = "COMMENT"
    OPERATOR    = "OPERATOR"

class Token:
    def __init__(self, ttype: TokenType, value: str):
        self.type  = ttype
        self.value = value
    def __repr__(self):
        return f"<{self.type.name}:'{self.value}'>"

class Lexer:
    def __init__(self, content: str):
        self.content = content
        self.tokens  = []
        self._run()

    def _run(self):
        ops       = set("+-*/=%<>!:[]{}()")
        current   = Token(TokenType.WHITESPACE, "")
        in_comment = False
        in_string  = False
        quote_char = None

        for c in self.content:
            # ——— Inside a comment?
            if in_comment:
                if c == "\n":
                    self.tokens.append(current)
                    in_comment = False
                    current    = Token(TokenType.WHITESPACE, "")
                else:
                    current.value += c
                continue

            # ——— Start of comment
            if c == "#" and not in_string:
                current = self._conclude(current)
                current = Token(TokenType.COMMENT, "")
                in_comment = True
                continue

            # ——— String delimiters
            if c in ('"', "'"):
                if not in_string:
                    in_string  = True
                    quote_char = c
                    current     = self._conclude(current)
                    current     = Token(TokenType.STRING, "")
                elif c == quote_char:
                    in_string = False
                    self.tokens.append(current)
                    current = Token(TokenType.WHITESPACE, "")
                else:
                    current.value += c
                continue

            # ——— While in a string, just accumulate
            if in_string:
                current.value += c
                continue

            # ——— Operators
            if c in ops:
                current = self._conclude(current)
                self.tokens.append(Token(TokenType.OPERATOR, c))
                continue

            # ——— Numbers (including large IDs)
            if c.isdigit():
                if current.type != TokenType.NUMBER:
                    current = self._conclude(current)
                    current = Token(TokenType.NUMBER, "")
                current.value += c
                continue

            # ——— Decimal point in number
            if c == "." and current.type == TokenType.NUMBER and "." not in current.value:
                current.value += c
                continue

            # ——— Whitespace ends tokens
            if c.isspace():
                current = self._conclude(current)
                continue

            # ——— Identifiers
            if current.type == TokenType.WHITESPACE:
                current = Token(TokenType.IDENTIFIANT, c)
            else:
                current.value += c

        self._conclude(current)

        # Convert true/false to BOOLEAN
        for t in self.tokens:
            if t.type == TokenType.IDENTIFIANT and t.value.lower() in ("true", "false"):
                t.type = TokenType.BOOLEAN

    def _conclude(self, token: Token) -> Token:
        if token.value != "" and token.type not in (TokenType.WHITESPACE, TokenType.COMMENT):
            self.tokens.append(token)
        return Token(TokenType.WHITESPACE, "")

    def get_tokens(self):
        return self.tokens

    def debug(self):
        for t in self.tokens:
            print(t)