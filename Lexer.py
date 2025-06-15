from enum import Enum


class TokenType(Enum):
    WHITESPACE       = "WHITESPACE"
    IDENTIFIANT      = "IDENTIFIANT"
    NUMBER           = "NUMBER"
    STRING           = "STRING"
    BOOLEAN          = "BOOLEAN"
    POSSIBLE_STRING  = "POSSIBLE_STRING"
    POSSIBLE_STRING2 = "POSSIBLE_STRING2"
    COMMENT          = "COMMENT"
    OPERATOR         = "OPERATOR"


class Token:
    def __init__(self, tokenType: TokenType, tokenValue: str):
        self.type  = tokenType
        self.value = tokenValue

    def __repr__(self):
        return f"<{self.type.name}:'{self.value}'>"


class Lexer:
    def __init__(self, content: str):
        self.content     = content
        self.tokens      = []
        self.run()

    def run(self):
        current     = Token(TokenType.WHITESPACE, "")
        in_comment  = False
        ops         = set("+-*/=%<>!:[]{}()")

        for c in self.content:
            # ——— Mode commentaire ———
            if in_comment:
                if c == "\n":
                    self.tokens.append(current)
                    in_comment = False
                    current    = Token(TokenType.WHITESPACE, "")
                else:
                    current.value += c
                continue

            # ——— Début de commentaire ———
            if c == "#":
                current    = self.concludeToken(current)
                current    = Token(TokenType.COMMENT, "")
                in_comment = True
                continue

            # ——— Opérateurs ———
            if c in ops and current.type not in (
                TokenType.POSSIBLE_STRING,
                TokenType.POSSIBLE_STRING2,
                TokenType.STRING
            ):
                current = self.concludeToken(current)
                self.tokens.append(Token(TokenType.OPERATOR, c))
                current = Token(TokenType.WHITESPACE, "")
                continue

            # ——— Nombres ———
            if c.isdigit():
                if current.type in (TokenType.IDENTIFIANT, TokenType.NUMBER):
                    current.type = TokenType.NUMBER
                else:
                    current = self.concludeToken(current)
                    current = Token(TokenType.NUMBER, "")
                current.value += c
                continue

            if c == "." and current.type == TokenType.NUMBER and "." not in current.value:
                current.value += c
                continue

            # ——— Strings ———
            if c == '"' or c == "'":
                start_type = TokenType.POSSIBLE_STRING  if c == '"' else TokenType.POSSIBLE_STRING2
                end_type   = TokenType.STRING           if c == '"' else TokenType.STRING

                if current.type == TokenType.WHITESPACE:
                    current = self.concludeToken(current)
                    current = Token(start_type, "")
                elif current.type == start_type:
                    current.type = end_type
                    self.tokens.append(current)
                    current = Token(TokenType.WHITESPACE, "")
                continue

            # ——— Séparateurs (espace / saut de ligne) ———
            if c.isspace():
                if current.type != TokenType.POSSIBLE_STRING and current.type != TokenType.POSSIBLE_STRING2:
                    current = self.concludeToken(current)
                else:
                    current.value += " "
                continue

            # ——— Identifiants et suite de chaînes ———
            if current.type == TokenType.WHITESPACE:
                current = Token(TokenType.IDENTIFIANT, c)
            else:
                current.value += c

        self.concludeToken(current)

        for t in self.tokens:
            if t.type == TokenType.IDENTIFIANT and t.value in ["true", "false"]:
                t.type = TokenType.BOOLEAN

    def concludeToken(self, current: Token) -> Token:
        if current and current.type != TokenType.WHITESPACE and current.type != TokenType.COMMENT and current.value != "":
            self.tokens.append(current)
        return Token(TokenType.WHITESPACE, "")

    def get_tokens(self):
        return self.tokens

    def debug(self):
        for t in self.tokens:
            print(t)