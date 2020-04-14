import operator

from lang.scope import Scope


class Node:
    def id(self):
        return str(hash(self))


class Program(Node):
    def __init__(self, block):
        self.block = block

    def eval(self, scope):
        return self.block.eval(scope)

    def draw(self, g):
        g.node(self.id(), "Program")
        g.edge(self.id(), self.block.draw(g))
        return self.id()


class BlockScoped(Node):
    def __init__(self, block):
        self.block = block

    def eval(self, scope, args={}):
        scope.push()
        for name, value in args.items():
            scope.add(name, value)
        value = self.block.eval(scope)
        scope.pop()
        return value

    def draw(self, g):
        g.node(self.id(), "BlockScoped")
        g.edge(self.id(), self.block.draw(g))
        return self.id()


class Block(Node):
    def __init__(self, block):
        self.block = block

    def eval(self, scope):
        value = None
        for stmt in self.block:
            value = stmt.eval(scope)
        return value

    def draw(self, g):
        g.node(self.id(), "Block")
        for stmt in self.block:
            g.edge(self.id(), stmt.draw(g))
        return self.id()


class Statement(Node):
    def __init__(self, stmt):
        self.stmt = stmt

    def eval(self, scope):
        return self.stmt.eval(scope)

    def draw(self, g):
        g.node(self.id(), "Statement")
        g.edge(self.id(), self.stmt.draw(g))
        return self.id()


class Fn(Node):
    def __init__(self, symbol, args, block):
        self.symbol = symbol
        self.args = args
        self.block = block

    def eval(self, scope):
        scope.add(self.symbol, (self.args, self.block))

    def draw(self, g):
        g.node(self.id(), "Define Fn: " + self.symbol)
        g.edge(self.id(), self.args.draw(g), "Args")
        g.edge(self.id(), self.block.draw(g), "Block")
        return self.id()


class FnArg(Node):
    def __init__(self, symbol, type):
        self.symbol = symbol
        self.type = type

    def eval(self, scope):
        return self.symbol, self.type

    def draw(self, g):
        g.node(self.id(), "Arg: " + self.symbol)
        g.edge(self.id(), self.type.draw(g), "Type")
        return self.id()


class FnArgs(Node):
    def __init__(self, args):
        self.args = args

    def eval(self, scope):
        args = []
        for a in self.args:
            args.append(a.eval(scope))
        return args

    def draw(self, g):
        g.node(self.id(), "FnArgs")
        for a in self.args:
            g.edge(self.id(), a.draw(g))
        return self.id()


class Define(Node):
    def __init__(self, symbol, value):
        self.symbol = symbol
        self.value = value

    def eval(self, scope):
        scope.add(self.symbol, self.value.eval(scope))
        return None

    def draw(self, g):
        g.node(self.id(), "Define: " + self.symbol)
        g.edge(self.id(), self.value.draw(g))
        return self.id()


class Assign(Node):
    def __init__(self, symbol, value):
        self.symbol = symbol
        self.value = value

    def eval(self, scope):
        scope.set(self.symbol, self.value.eval(scope))
        return None

    def draw(self, g):
        g.node(self.id(), "Assign: " + self.symbol)
        g.edge(self.id(), self.value.draw(g))
        return self.id()


class Print(Node):
    def __init__(self, value, newline):
        self.value = value
        self.newline = newline

    def eval(self, scope):
        if self.newline:
            print(self.value.eval(scope))
        else:
            print(self.value.eval(scope), end="")
        return None

    def draw(self, g):
        newline = "ln" if self.newline else ""
        g.node(self.id(), "Print" + newline)
        g.edge(self.id(), self.value.draw(g))
        return self.id()


class ValueInt(Node):
    def __init__(self, value):
        self.value = value

    def eval(self, scope):
        return self.value

    def draw(self, g):
        g.node(self.id(), "ValueInt: " + str(self.value))
        return self.id()


class ValueFloat(Node):
    def __init__(self, value):
        self.value = value

    def eval(self, scope):
        return self.value

    def draw(self, g):
        g.node(self.id(), "ValueFloat: " + str(self.value))
        return self.id()


class ValueStr(Node):
    def __init__(self, value):
        self.value = value[1:-1]

    def eval(self, scope):
        return self.value

    def draw(self, g):
        g.node(self.id(), "ValueStr: " + self.value)
        return self.id()


class ValueTrue(Node):
    def eval(self, scope):
        return True

    def draw(self, g):
        g.node(self.id(), "ValueTrue")
        return self.id()


class ValueFalse(Node):
    def eval(self, scope):
        return False

    def draw(self, g):
        g.node(self.id(), "ValueFalse")
        return self.id()


class ValueSymbol(Node):
    def __init__(self, symbol):
        self.symbol = symbol

    def eval(self, scope):
        return scope.get(self.symbol)

    def draw(self, g):
        g.node(self.id(), "ValueSymbol: " + self.symbol)
        return self.id()


class Type(Node):
    def __init__(self, type):
        types = {
            "INT": int,
            "FLOAT": float,
            "STR": str,
            "BOOL": bool,
        }

        self.type = types[type]

    def eval(self, scope):
        return self.type

    def draw(self, g):
        g.node(self.id(), "Type: " + self.type.__name__)
        return self.id()


class BinaryOp(Node):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def eval(self, scope):
        left = self.left.eval(scope)
        right = self.right.eval(scope)

        if not isinstance(left, type(right)):
            ltype = self.left.__class__.__name__
            rtype = self.right.__class__.__name__
            raise ValueError(f"Type mismatch between {ltype} and {rtype}")
        elif isinstance(left, ValueStr) and self.op is not operator.add:
            raise ValueError("Invalid string operation")
        else:
            return self.op(left, right)

    def draw(self, g):
        g.node(self.id(), "BinaryOp: " + self.op.__name__)
        g.edge(self.id(), self.left.draw(g), "Left")
        g.edge(self.id(), self.right.draw(g), "Right")
        return self.id()


class If(Node):
    def __init__(self, cond, block):
        self.cond = cond
        self.block = block

    def eval(self, scope):
        if self.cond.eval(scope):
            return self.block.eval(scope)

    def draw(self, g):
        g.node(self.id(), "If")
        g.edge(self.id(), self.cond.draw(g), "Condition")
        g.edge(self.id(), self.block.draw(g), "Consequence")
        return self.id()


class IfElse(Node):
    def __init__(self, cond, true_block, false_block):
        self.cond = cond
        self.true_block = true_block
        self.false_block = false_block

    def eval(self, scope):
        if self.cond.eval(scope):
            return self.true_block.eval(scope)
        else:
            return self.false_block.eval(scope)

    def draw(self, g):
        g.node(self.id(), "IfElse")
        g.edge(self.id(), self.cond.draw(g), "Condition")
        g.edge(self.id(), self.true_block.draw(g), "Consequence")
        g.edge(self.id(), self.false_block.draw(g), "Alternative")
        return self.id()


class While(Node):
    def __init__(self, cond, block):
        self.cond = cond
        self.block = block

    def eval(self, scope):
        value = None
        while self.cond.eval(scope):
            value = self.block.eval(scope)
        return value

    def draw(self, g):
        g.node(self.id(), "While")
        g.edge(self.id(), self.cond.draw(g), "Condition")
        g.edge(self.id(), self.block.draw(g), "Consequence")
        return self.id()


class For(Node):
    def __init__(self, begin, cond, step, block):
        self.begin = begin
        self.cond = cond
        self.step = step
        self.block = block

    def eval(self, scope):
        self.begin.eval(scope)
        value = None
        while self.cond.eval(scope):
            value = self.block.eval(scope)
            self.step.eval(scope)
        return value

    def draw(self, g):
        g.node(self.id(), "For")
        g.edge(self.id(), self.begin.draw(g), "Begin")
        g.edge(self.id(), self.cond.draw(g), "Condition")
        g.edge(self.id(), self.step.draw(g), "Step")
        g.edge(self.id(), self.block.draw(g), "Consequnce")
        return self.id()


class Minus(Node):
    def __init__(self, value):
        self.value = value

    def eval(self, scope):
        value = self.value.eval(scope)
        if not isinstance(value, int) and not isinstance(value, float):
            type = value.__class__.__name__
            raise ValueError(f"Cannot negate {type}")
        return value * -1

    def draw(self, g):
        g.node(self.id(), "Unary minus")
        g.edge(self.id(), self.value.draw(g))
        return self.id()


class Not(Node):
    def __init__(self, value):
        self.value = value

    def eval(self, scope):
        value = self.value.eval(scope)
        if not isinstance(value, bool):
            type = value.__class__.__name__
            raise ValueError(f"Cannot negate {type}")
        return not value

    def draw(self, g):
        g.node(self.id(), "Negate")
        g.edge(self.id(), self.value.draw(g))
        return self.id()


class Cast(Node):
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def eval(self, scope):
        cast = self.type.eval(scope)
        return cast(self.value.eval(scope))

    def draw(self, g):
        g.node(self.id(), "Cast")
        g.edge(self.id(), self.type.draw(g), "Type")
        g.edge(self.id(), self.value.draw(g), "Value")
        return self.id()


class Args(Node):
    def __init__(self, args):
        self.args = args

    def eval(self, scope):
        args = []
        for a in self.args:
            args.append(a.eval(scope))
        return args

    def draw(self, g):
        g.node(self.id(), "Args")
        for a in self.args:
            g.edge(self.id(), a.draw(g))
        return self.id()


class Call(Node):
    def __init__(self, symbol, args):
        self.symbol = symbol
        self.args = args

    def eval(self, scope):
        evaled = self.args.eval(scope)
        types, fn = scope.get(self.symbol)
        types = types.eval(scope)
        if len(evaled) != len(types):
            raise ValueError(f"Invalid number of arguments passed to '{self.symbol}'")

        args = {}
        for i in range(len(types)):
            value = evaled[i]
            name, type = types[i]
            type = type.eval(scope)
            if not isinstance(value, type):
                ltype = value.__class__.__name__
                rtype = type.__name__
                raise ValueError(f"Argument type mismatch between {ltype} and {rtype}")
            args[name] = value

        scope = Scope()
        return fn.eval(scope, args)

    def draw(self, g):
        g.node(self.id(), "Call: " + self.symbol)
        g.edge(self.id(), self.args.draw(g), "Args")
        return self.id()
