from src.myLexer import Lexer
from src.myParser import Parser
from config import *

if __name__ == "__main__":
    lex = Lexer()
    content = open(ERR_PATH).read()
    if content != '' and content != '\n' and content != '':
        print('There are some lexical errors.')
    else: par = Parser()