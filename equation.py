import math # https://docs.python.org/3/library/math.html

from util import Collider, lesser
import number

rationals = { p: number.create(p) for p in [1, 2, 3, 5] }
reals = {
    'pi': number.pi(),
    'e': number.e(),
}

primitives = set(rationals.values()) | set(reals.values())
one = number.create(1)
two = number.create(2)
min_one = number.create(-1)

def generate_0(config):
    for prim, res in rationals.items():
        yield ((prim,), (res,))
    for prim, res in reals.items():
        if prim in config.ops:
            yield ((prim,), (res,))
    for p in config.variables:
        yield ((p,), (p,))

def generate_1(eq, sim, config):
    op = eq[0]
    value = sim[0]
    isval = not isinstance(value, str)
    if '-' in config.ops and op != '-' and (op != 'log' or eq[1][0] != '/') and (op != '+' or (eq[1][0] != '-' and eq[2][0] != '-')):
        if isval:
            yield (('-', eq), (-value,))
        else:
            yield (('-', eq), ('-', sim))
    if 'log' in config.ops and op != '^' and op != 'root' and (op != '*' or (eq[1][0] != 'e' and eq[2][0] != 'e')) and (op != '/' or eq[1][0] != 1):
        if isval:
            if not number.is_signed(value):
                res = number.log(value)
                if not number.is_integer(res):
                    yield (('log', eq), (res,))
        else:
            yield (('log', eq), ('log', sim))
    if isval:
        if not number.is_signed(value) and value < reals['pi'] / two:
            if 'sin' in config.ops:
                yield (('sin', eq), (number.sin(value),))
            if 'cos' in config.ops:
                yield (('cos', eq), (number.cos(value),))
    else:
        if 'sin' in config.ops:
            yield (('sin', eq), ('sin', sim))
        if 'cos' in config.ops:
            yield (('cos', eq), ('cos', sim))

def generate_2(eq1, sim1, eq2, sim2, config):
    op1 = eq1[0]
    op2 = eq2[0]
    value1 = sim1[0]
    value2 = sim2[0]
    isval1 = not isinstance(value1, str)
    isval2 = not isinstance(value2, str)
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
            if value2 != one and value2 != min_one:
                if '*' in config.ops and (not isval1 or (value1 != one and value1 != min_one)) and less:
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
        if value1 != one and value1 != min_one and value2 != one and value2 != min_one:
            if (not isval1 or (value1 > 0.001 and value1 < 1000)) and (not isval2 or (not number.is_signed(value2) and value2 < 10)):
                if 'root' in config.ops and (not isval2 or number.is_integer(value2)):
                    if isval1 and isval2:
                        yield (('root', eq1, eq2), (value1 ** (one / value2),))
                    else:
                        yield (('root', eq1, eq2), ('root', sim1, sim2))
                if '^' in config.ops and (not isval2 or not number.is_integer(one / value2)):
                    if isval1 and isval2:
                        yield (('^', eq1, eq2), (value1 ** value2,))
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
    def __init__(self, variables, ops, filter_size):
        self.variables = variables
        self.ops = ops if ops else { '+', '-', '*', '/', '^', 'root', 'log', 'sin', 'cos', 'pi', 'e' }
        self.filter_size = filter_size
        self.collider = Collider()

def generate(size, variables = [], operations = None, filter_size = 0):
    config = GenerateConfig(variables, operations, filter_size)
    yield from generate_recurse_a(size, config)

def evaluate(eq, variables):
    op = eq[0]
    if len(eq) == 1:
        if op in variables:
            return variables[op]
        if not isinstance(op, str):
            return op
    elif len(eq) == 2:
        value = evaluate(eq[1], variables)
        if value is None:
            return None
        if op == '-':
            return -value
        elif op == '1/':
            if number.is_zero(value):
                return None
            return one / value
        elif op == 'sqre':
            return value * value
        elif op == 'sqrt':
            if number.is_signed(value):
                return None
            return value.sqrt()
        elif op == 'log':
            if value <= zero:
                return None
            return number.log(value)
        elif op == 'sin':
            return number.sin(value)
        elif op == 'cos':
            return number.cos(value)
        elif op == '!':
            if number.is_signed(value) or value > 100 or not number.is_integer(value):
                return None
            return number.create(math.factorial(int(value)))
        elif op == 'alt':
            if not number.is_integer(value):
                return None
            return one if value % 2 == 0 else min_one
    else:
        value1 = evaluate(eq[1], variables)
        if value1 is None:
            return None
        value2 = evaluate(eq[2], variables)
        if value2 is None:
            return None
        elif op == '+':
            return value1 + value2
        elif op == '*':
            res = value1 * value2
            if number.is_nan(res):
                return None
            return res
        elif op == '/':
            if number.is_zero(value2):
                return None
            return value1 / value2
        elif op == '^':
            if value1 > 1000 or value1 < -1000 or value2 < -10 or value2 > 10:
                return None
            if number.is_zero(value1) and value2 < 0:
                return None
            if number.is_signed(value1) and not number.is_integer(value2):
                return None
            return value1 ** value2
        elif op == 'root':
            if value1 > 1000 or number.is_signed(value1) or value2 < 0.1:
                return None
            return value1 ** (1 / value2)
        elif op == 'comb':
            if value1 < 0 or value2 < 0 or value1 > 100 or value2 > 100 or not number.is_integer(value1) or not number.is_integer(value2):
                return None
            return number.create(math.comb(int(value1), int(value2)))
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
    if number.is_integer(value):
        return (int(value), 1)
    frac = float(value % one)
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
