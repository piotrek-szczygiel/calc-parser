import argparse
import sys
import copy

from graphviz import Digraph
from rply import LexingError, ParsingError

from lang.lexer import Lexer
from lang.parser import Parser
from lang.scope import Scope

lexer = Lexer()
parser = Parser(lexer.tokens)
scope = Scope()


def execute(scope, source, draw=False, lexer_output=False, opt=False):
    try:
        tokens = lexer.lex(source)

        if lexer_output:
            print("LEXER OUTPUT")
            for token in copy.copy(tokens):
                print(token)
            print()
            print("PROGRAM OUTPUT")

        ast = parser.parse(tokens)

        # Optimize
        if opt:
            ast.eval(True, scope)

        result = ast.eval(False, scope)

        # Draw AST graph
        if draw:
            g = Digraph()
            ast.draw(g)
            g.render("ast", format="png", view=True, cleanup=True)

        return result
    except ValueError as err:
        print(err)
    except LexingError:
        print("Lexing error")
    except ParsingError:
        print("Parsing error")


def run_repl():
    while True:
        try:
            source = input("> ")
            result = execute(scope, source)
            if result is not None:
                print(result)
        except KeyboardInterrupt:
            break


def run_file(path, draw=False, verbose=False):
    with open(path, "r") as f:
        source = f.read()
        execute(scope, source, draw=draw, verbose=verbose)


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("file", nargs="?", help="path to script")
    arg_parser.add_argument(
        "-a", "--ast", help="draw abstract syntax tree", action="store_true"
    )
    arg_parser.add_argument(
        "-l", "--lexer", help="print lexer output", action="store_true"
    )
    args = arg_parser.parse_args()

    if args.file:
        run_file(args.file, draw=args.ast, verbose=args.lexer)
    else:
        run_repl()
