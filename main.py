from Lexer import Lexer
from Parser import Parser

with open("script.sc", "r", encoding="utf-8") as f:
    content = f.read()

lexer = Lexer(content)
#lexer.debug()
parser = Parser(lexer)
parser.run()