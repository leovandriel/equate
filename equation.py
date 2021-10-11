import math # https://docs.python.org/3/library/math.html

from util import lookup_add, lesser
import number

default_ops = { '+', '-', '*', '/', '^', '^/', 'log', 'sin', 'cos', 'pi', 'e' }
reals = { 'pi': number.pi(), 'e': number.e() }
primitives = set(reals.values())
one = number.create(1)
two = number.create(2)
min_one = number.create(-1)

def generate_0(ops, vars):
    for value in range(1, 6):
        yield ((value,), (number.create(value),))
    for prim, res in reals.items():
        if prim in ops:
            yield ((prim,), (res,))
    for p in vars:
        yield ((p,), (p,))

def generate_1(eq, sim, ops):
    op = eq[0]
    value = sim[0]
    isval = not isinstance(value, str)
    if op != '-' and (op != 'log' or eq[1][0] != '/') and (op != '+' or (eq[1][0] != '-' and eq[2][0] != '-')) and '-' in ops:
        if isval:
            yield (('-', eq), (-value,))
        else:
            yield (('-', eq), ('-', sim))
    if op != '^' and op != '^/' and (op != '*' or (eq[1][0] != 'e' and eq[2][0] != 'e')) and (op != '/' or eq[1][0] != 1) and 'log' in ops:
        if isval:
            if not number.is_signed(value):
                res = number.log(value)
                if not number.is_integer(res):
                    yield (('log', eq), (res,))
        else:
            yield (('log', eq), ('log', sim))
    if isval:
        if not number.is_signed(value) and value < reals['pi'] / two:
            if 'sin' in ops:
                yield (('sin', eq), (number.sin(value),))
            if 'cos' in ops:
                yield (('cos', eq), (number.cos(value),))
    else:
        if 'sin' in ops:
            yield (('sin', eq), ('sin', sim))
        if 'cos' in ops:
            yield (('cos', eq), ('cos', sim))

def generate_2(eq1, sim1, eq2, sim2, ops):
    op1 = eq1[0]
    op2 = eq2[0]
    value1 = sim1[0]
    value2 = sim2[0]
    isval1 = not isinstance(value1, str)
    isval2 = not isinstance(value2, str)
    less = lesser(eq1, eq2)
    if (less
        and (op1 != op2 or (op1 != '-' and op1 != 'log' and op1 != '+'))
        and (op2 != '+' or lesser(eq1, eq2[1]))
        and (op2 != '*' or (eq1 != eq2[1] and eq1 != eq2[2]))
        and '+' in ops):
        if isval1 and isval2:
            if value1 != -value2:
                res = value1 + value2
                if not number.is_integer(res) and res not in primitives:
                    yield (('+', eq1, eq2), (res,))
        else:
            yield (('+', eq1, eq2), ('+', sim1, sim2))
    if (op1 != '-' and op2 != '-' and op1 != '/' and op2 != '/'
        and (op1 != op2 or (op1 != '1/' and op1 != '*'))
        and (op2 != '*' or (op1 != eq2[1][0] and op1 != eq2[2][0]))
        and ((op2 != '^' and op2 != '^/') or (op1 != eq2[1][0]))
        and value2 != one and value2 != min_one):
        if (less
            and (not isval1 or (value1 != one and value1 != min_one))
            and (op2 != '*' or lesser(eq1, eq2[1]))
            and '*' in ops):
            if isval1 and isval2:
                res = value1 * value2
                if not number.is_integer(res) and res not in primitives:
                    yield (('*', eq1, eq2), (res,))
            else:
                yield (('*', eq1, eq2), ('*', sim1, sim2))
        if ((not isval1 or not isval2 or value1 != value2)
            and '/' in ops):
            if isval1 and isval2:
                res = value1 / value2
                if not number.is_integer(res) and res not in primitives:
                    yield (('/', eq1, eq2), (res,))
            else:
                yield (('/', eq1, eq2), ('/', sim1, sim2))
    if (op1 != '^' and op1 != '^/'
        and value1 != one and value1 != min_one and value2 != one and value2 != min_one
        and (not isval1 or (value1 > 1e-3 and value1 < 1e3))
        and (not isval2 or (not number.is_signed(value2) and value2 <= 3e1))):
        if ((not isval2 or number.is_integer(value2))
            and '^/' in ops):
            if isval1 and isval2:
                yield (('^/', eq1, eq2), (value1 ** (one / value2),))
            else:
                yield (('^/', eq1, eq2), ('^/', sim1, sim2))
        if ((not isval2 or not number.is_integer(one / value2))
            and '^' in ops):
            if isval1 and isval2:
                yield (('^', eq1, eq2), (value1 ** value2,))
            else:
                yield (('^', eq1, eq2), ('^', sim1, sim2))

def generate(size, ops = default_ops, vars = []):
    if size == 1:
        yield from generate_0(ops, vars)
    else:
        for eq, sim in generate(size - 1, ops, vars):
            yield from generate_1(eq, sim, ops)
        for size1 in range(1, size - 1):
            for eq1, sim1 in generate(size1, ops, vars):
                for eq2, sim2 in generate(size - size1 - 1, ops, vars):
                    yield from generate_2(eq1, sim1, eq2, sim2, ops)

def evaluate_0(op, vars):
    if op in vars:
        return vars[op]
    elif not isinstance(op, str):
        return op

def evaluate_1(op, value, vars):
    if op == '-':
        return -value
    elif op == '1/':
        if number.is_zero(value):
            return None
        return one / value
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

def evaluate_2(op, value1, value2, vars):
    if op == '+':
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
    elif op == '^/':
        if value1 > 1000 or number.is_signed(value1) or value2 < 0.1:
            return None
        return value1 ** (1 / value2)
    elif op == 'comb':
        if value1 < 0 or value2 < 0 or value1 > 100 or value2 > 100 or not number.is_integer(value1) or not number.is_integer(value2):
            return None
        return number.create(math.comb(int(value1), int(value2)))

def evaluate(eq, vars):
    if len(eq) == 1:
        return evaluate_0(eq[0], vars)
    elif len(eq) == 2:
        value = evaluate(eq[1], vars)
        if value is None:
            return None
        return evaluate_1(eq[0], value, vars)
    else:
        value1 = evaluate(eq[1], vars)
        if value1 is None:
            return None
        value2 = evaluate(eq[2], vars)
        if value2 is None:
            return None
        return evaluate_2(eq[0], value1, value2, vars)
    raise ValueError(f'unknown eq: {eq}')

def stringify(eq):
    if eq[0] == '^/':
        return f'({stringify(eq[1])}^/{stringify(eq[2])})'
    elif len(eq) == 1:
        return str(eq[0])
    elif len(eq[0]) > 2:
        return f'{eq[0]}({" ".join([stringify(x) for x in eq[1:]])})'
    elif len(eq) == 2:
        return f'({eq[0]}{stringify(eq[1])})'
    else:
        return f'({eq[0].join([stringify(x) for x in eq[1:]])})'
