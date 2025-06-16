import discord
from pathlib import Path
from Lexer import Lexer
from Parser import Parser
from Interpreter import Interpreter

class ScriptCord:
    def __init__(self, client: discord.Client, script_path: str):
        self.client      = client
        self.script_path = script_path

    async def run(self):
        content = Path(self.script_path).read_text(encoding="utf-8")
        lexer    = Lexer(content)
        parser   = Parser(lexer)
        nodes    = parser.run()
        interpreter = Interpreter(self.client)
        await interpreter.execute(nodes)