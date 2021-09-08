import math # https://docs.python.org/3/library/math.html

from util import Collider

rationals = {
    1.0: (1,),
    2.0: (2,),
    3.0: (3,),
    5.0: (5,),
}

reals = {
    math.pi: ('pi',),
    math.e: ('e',),
}

primitives = set(rationals.keys()) | set(reals.keys())

def lesser(value1, value2):
    if isinstance(value1, tuple):
        if isinstance(value2, tuple):
            if len(value1) < len(value2):
                return True
            elif len(value2) < len(value1):
                return False
            else:
                for i in range(len(value1)):
                    if lesser(value1[i], value2[i]):
                        return True
                    elif lesser(value2[i], value1[i]):
                        return False
                return False
        else:
            return False
    elif isinstance(value1, str):
        if isinstance(value2, tuple):
            return True
        elif isinstance(value2, str):
            return value1 < value2
        else:
            return False
    else:
        if isinstance(value2, tuple) or isinstance(value2, str):
            return True
        else:
            return value1 < value2

def generate_0(config):
    for res, eq in rationals.items():
        yield (eq, (res,))
    for res, eq in reals.items():
        if eq[0] in config.ops:
            yield (eq, (res,))
    for p in config.primitives:
        yield ((p,), (p,))

def generate_1(eq, sim, config):
    op = eq[0]
    value = sim[0]
    isval = isinstance(value, float)
    if '-' in config.ops and op != '-' and (op != 'log' or eq[1][0] != '/') and (op != '+' or (eq[1][0] != '-' and eq[2][0] != '-')):
        if isval:
            yield (('-', eq), (-value,))
        else:
            yield (('-', eq), ('-', sim))
    if 'log' in config.ops and op != '^' and op != 'root' and (op != '*' or (eq[1][0] != 'e' and eq[2][0] != 'e')) and (op != '/' or eq[1][0] != 1):
        if isval:
            if value > 0.0:
                res = math.log(value)
                if not res.is_integer():
                    yield (('log', eq), (res,))
        else:
            yield (('log', eq), ('log', sim))
    if isval:
        if value > 0.0 and value < math.pi / 2.0:
            if 'sin' in config.ops:
                yield (('sin', eq), (math.sin(value),))
            if 'cos' in config.ops:
                yield (('cos', eq), (math.cos(value),))
            res = math.tan(value)
            if 'tan' in config.ops and not res.is_integer():
                yield (('tan', eq), (res,))
    else:
        if 'sin' in config.ops:
            yield (('sin', eq), ('sin', sim))
        if 'cos' in config.ops:
            yield (('cos', eq), ('cos', sim))
        if 'tan' in config.ops:
            yield (('tan', eq), ('tan', sim))

def generate_2(eq1, sim1, eq2, sim2, config):
    op1 = eq1[0]
    op2 = eq2[0]
    value1 = sim1[0]
    value2 = sim2[0]
    isval1 = isinstance(value1, float)
    isval2 = isinstance(value2, float)
    less = value1 < value2 if isval1 and isval2 else lesser(op1, op2)
    if '+' in config.ops and (op1 != op2 or (op1 != '-' and op1 != 'log')) and less:
        if isval1 and isval2:
            if value1 != -value2:
                res = value1 + value2
                if res not in primitives:
                    yield (('+', eq1, eq2), (res,))
        else:
            yield (('+', eq1, eq2), ('+', sim1, sim2))
    if op1 != '-' and op2 != '-' and op1 != '/' and op2 != '/':
        if op1 != op2 or (op1 != '1/' and op1 != 'sqrt' and op1 != 'sqre'):
            if value2 != 1.0 and value2 != -1.0:
                if '*' in config.ops and (not isval1 or (value1 != 1.0 and value1 != -1.0)) and less:
                    if isval1 and isval2:
                        yield (('*', eq1, eq2), (value1 * value2,))
                    else:
                        yield (('*', eq1, eq2), ('*', sim1, sim2))
                if '/' in config.ops and (not isval1 or not isval2 or value1 != value2):
                    if isval1 and isval2:
                        yield (('/', eq1, eq2), (value1 / value2,))
                    else:
                        yield (('/', eq1, eq2), ('/', sim1, sim2))
    if op1 != '^' and op1 != 'root' and op2 != 'log':
        if value1 != 1.0 and value1 != -1.0 and value2 != 1.0 and value2 != -1.0:
            if (not isval1 or (value1 > 0.001 and value1 < 1000.0)) and (not isval2 or (value2 > 0.0 and value2 < 10.0)):
                if 'root' in config.ops and (not isval2 or value2.is_integer()):
                    if isval1 and isval2:
                        yield (('root', eq1, eq2), (math.pow(value1, 1.0 / value2),))
                    else:
                        yield (('root', eq1, eq2), ('root', sim1, sim2))
                if '^' in config.ops and (not isval2 or not (1.0 / value2).is_integer()):
                    if isval1 and isval2:
                        yield (('^', eq1, eq2), (math.pow(value1, value2),))
                    else:
                        yield (('^', eq1, eq2), ('^', sim1, sim2))

def generate_recurse_b(size, config):
    use_filter = size > 2 and size <= config.filter_size
    for eq, sim in generate_recurse_a(size, config):
        if use_filter and config.collider.add(eq, sim[0]):
            continue
        yield (eq, sim)

def generate_recurse_a(size, config):
    if size == 1:
        yield from generate_0(config)
    elif size > 1:
        for eq, sim in generate_recurse_b(size - 1, config):
            yield from generate_1(eq, sim, config)
        for size1 in range(1, size - 1):
            for eq1, sim1 in generate_recurse_b(size1, config):
                for eq2, sim2 in generate_recurse_b(size - size1 - 1, config):
                    yield from generate_2(eq1, sim1, eq2, sim2, config)

class GenerateConfig:
    def __init__(self, primitives, ops, filter_size):
        self.primitives = primitives
        self.ops = ops if ops else { '+', '-', '*', '/', '^', 'root', 'log', 'sin', 'cos', 'tan', 'pi', 'e' }
        self.filter_size = filter_size
        self.collider = Collider()

def generate(size, primitives = [], operations = None, filter_size = 0):

    config = GenerateConfig(primitives, operations, filter_size)
    yield from generate_recurse_a(size, config)

def evaluate(eq, primitives):
    op = eq[0]
    if len(eq) == 1:
        if op in primitives:
            return float(primitives[op])
        if isinstance(op, float):
            return op
    elif len(eq) == 2:
        value = evaluate(eq[1], primitives)
        if value is None:
            return None
        if op == '-':
            return -value
        elif op == '1/':
            if value == 0.0:
                return None
            return 1.0 / value
        elif op == 'sqre':
            return value * value
        elif op == 'sqrt':
            if value < 0.0:
                return None
            return math.sqrt(value)
        elif op == 'log':
            if value <= 0.0:
                return None
            return math.log(value)
        elif op == 'sin':
            return math.sin(value)
        elif op == 'cos':
            return math.cos(value)
        elif op == 'tan':
            return math.tan(value)
        elif op == '!':
            if value < 0.0 or value > 100 or not value.is_integer():
                return None
            return float(math.factorial(int(value)))
        elif op == 'alt':
            if not value.is_integer():
                return None
            return 1.0 if value % 2 == 0 else -1.0
    else:
        value1 = evaluate(eq[1], primitives)
        if value1 is None:
            return None
        value2 = evaluate(eq[2], primitives)
        if value2 is None:
            return None
        elif op == '+':
            return value1 + value2
        elif op == '*':
            res = value1 * value2
            if math.isnan(res):
                return None
            return res
        elif op == '/':
            if value2 == 0.0:
                return None
            return value1 / value2
        elif op == '^':
            if value1 > 1000 or value1 < -1000 or value2 < -10 or value2 > 10:
                return None
            if value1 == 0.0 and value2 < 0:
                return None
            if value1 < 0.0 and not value2.is_integer():
                return None
            return math.pow(value1, value2)
        elif op == 'root':
            if value1 > 1000 or value1 < 0.0 or value2 < 0.1:
                return None
            return math.pow(value1, 1 / value2)
        elif op == 'comb':
            if value1 < 0 or value2 < 0 or value1 > 100 or value2 > 100 or not value1.is_integer() or not value2.is_integer():
                return None
            return float(math.comb(int(value1), int(value2)))
    raise ValueError(f'unknown eq: {eq}')

def stringify(eq):
    if eq[0] == 'root':
        return f'({stringify(eq[1])}^/{stringify(eq[2])})'
    elif len(eq) == 1:
        return str(eq[0])
    elif len(eq[0]) > 2:
        return f'{eq[0]}({" ".join([stringify(x) for x in eq[1:]])})'
    elif len(eq) == 2:
        return f'({eq[0]}{stringify(eq[1])})'
    else:
        return f'({eq[0].join([stringify(x) for x in eq[1:]])})'

def find_rational(value):
    if value.is_integer():
        return (value, 1)
    frac = value % 1.0
    a = 0
    b = 1
    for i in range(0, 20000):
        e = a / b
        if abs(e - frac) < 1e-12:
            return (a + math.floor(value) * b, b)
        if e > frac:
            b += 1 # TODO
        else:
            a += 1
    return None
