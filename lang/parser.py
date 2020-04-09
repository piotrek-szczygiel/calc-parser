import operator

from rply import ParserGenerator

from lang import ast


class Parser:
    def __init__(self, tokens):
        self.parser = Parser.create_parser(tokens)

    def parse(self, input):
        return self.parser.parse(input)

    @staticmethod
    def create_parser(tokens):
        pg = ParserGenerator(
            tokens,
            precedence=[
                ("left", ["OR"]),
                ("left", ["AND"]),
                ("right", ["NOT"]),
                ("left", ["EQ", "NE", "LE", "GE", "LT", "GT"]),
                ("left", ["ADD", "SUB"]),
                ("left", ["MUL", "DIV", "MOD"]),
                ("right", ["POW"]),
            ],
            cache_id="lang",
        )

        @pg.production("program : block")
        def program(p):
            return ast.Program(p[0])

        @pg.production("block : block SC stmt")
        def block(p):
            return ast.Block(p[0].block + [p[2]])

        @pg.production("block : stmt")
        def block_stmt(p):
            return ast.Block([p[0]])

        @pg.production("stmt : SYMBOL DEFINE expr")
        def stmt_define(p):
            return ast.Define(p[0].getstr(), p[2])

        @pg.production("stmt : SYMBOL ASSIGN expr")
        def stmt_assign(p):
            return ast.Assign(p[0].getstr(), p[2])

        @pg.production("stmt : PRINT LPAREN expr RPAREN")
        def stmt_print(p):
            return ast.Print(p[2])

        @pg.production("stmt : expr")
        def stmt_expr(p):
            return ast.Statement(p[0])

        @pg.production("expr : IF expr LBRACE block RBRACE ELSE LBRACE block RBRACE")
        def expr_if_else(p):
            return ast.IfElse(p[1], p[3], p[7])

        @pg.production("expr : IF expr LBRACE block RBRACE")
        def expr_if(p):
            return ast.If(p[1], p[3])

        @pg.production("expr : WHILE expr LBRACE block RBRACE")
        def expr_while(p):
            return ast.While(p[1], p[3])

        @pg.production("expr : FOR stmt SC expr SC stmt LBRACE block RBRACE")
        def expr_for(p):
            return ast.For(p[1], p[3], p[5], p[7])

        @pg.production("expr : SYMBOL")
        def expr_symbol(p):
            return ast.ValueSymbol(p[0].getstr())

        @pg.production("expr : CAST LPAREN INT COMMA expr RPAREN")
        @pg.production("expr : CAST LPAREN FLOAT COMMA expr RPAREN")
        @pg.production("expr : CAST LPAREN STRING COMMA expr RPAREN")
        def expr_cast(p):
            return ast.Cast(p[2], p[4])

        @pg.production("expr : VALUE_INT")
        def expr_number_int(p):
            return ast.ValueInt(int(p[0].getstr()))

        @pg.production("expr : VALUE_FLOAT")
        def expr_number_float(p):
            return ast.ValueFloat(float(p[0].getstr()))

        @pg.production("expr : VALUE_STRING")
        def expr_string(p):
            return ast.ValueString(p[0].getstr())

        @pg.production("expr : TRUE")
        def expr_true(p):
            return ast.ValueTrue()

        @pg.production("expr : FALSE")
        def expr_false(p):
            return ast.ValueFalse()

        @pg.production("expr : LPAREN expr RPAREN")
        def expr_parens(p):
            return p[1]

        @pg.production("expr : expr ADD expr")
        @pg.production("expr : expr SUB expr")
        @pg.production("expr : expr MUL expr")
        @pg.production("expr : expr DIV expr")
        @pg.production("expr : expr POW expr")
        @pg.production("expr : expr MOD expr")
        @pg.production("expr : expr EQ expr")
        @pg.production("expr : expr NE expr")
        @pg.production("expr : expr LE expr")
        @pg.production("expr : expr GE expr")
        @pg.production("expr : expr LT expr")
        @pg.production("expr : expr GT expr")
        @pg.production("expr : expr AND expr")
        @pg.production("expr : expr OR expr")
        def expr_binop(p):
            left = p[0]
            right = p[2]

            methods = {
                "ADD": operator.add,
                "SUB": operator.sub,
                "MUL": operator.mul,
                "DIV": operator.truediv,
                "POW": operator.pow,
                "MOD": operator.mod,
                "EQ": operator.eq,
                "NE": operator.ne,
                "LE": operator.le,
                "GE": operator.ge,
                "LT": operator.lt,
                "GT": operator.gt,
                "AND": operator.and_,
                "OR": operator.or_,
            }

            op = p[1].gettokentype()
            assert op in methods
            return ast.BinaryOp(methods[op], left, right)

        return pg.build()
