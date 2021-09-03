#!/usr/bin/env python3 #-m cProfile -s tottime

import math # https://docs.python.org/3/library/math.html
import sys

target = (1 + math.sqrt(5)) / 2 # golden ratio

def recurse(size):
    if size == 1:
        for i in [1, 2, 3, 5]:
            yield (i, (i,))
        yield (math.pi, ('pi',))
        yield (math.e, ('e',))
    else:
        for value, eq in recurse(size - 1):
            op = eq[0]
            if op != '-':
                yield (-value, ('-', eq))
            if op != '1/' and op != '-':
                res = 1.0 / value
                if not res.is_integer():
                    yield (res, ('1/', eq))
            if value > 0.0:
                if op != '^' and op != '1/':
                    res = math.sqrt(value)
                    if not res.is_integer():
                        yield (res, ('sqrt', eq))
                    if op != 'sqrt':
                        res = math.log(value)
                        if not res.is_integer():
                            yield (res, ('log', eq))
                if not (value * 2.0 / math.pi).is_integer():
                    yield (math.sin(value), ('sin', eq))
                    yield (math.cos(value), ('cos', eq))
        for size1 in range(1, size - 1):
            for value1, eq1 in recurse(size1):
                for value2, eq2 in recurse(size - size1 - 1):
                    op1 = eq1[0]
                    op2 = eq2[0]
                    if value1 != -value2 and value1 < value2:
                        if op1 != op2 or (op1 != '-' and op1 != 'log'):
                            yield (value1 + value2, ('+', eq1, eq2))
                    if value1 != 1.0 and value2 != 1.0 and value1 != -1.0 and value2 != -1.0:
                        if value1 < value2:
                            if op1 != op2 or (op1 != '-' and op1 != '1/' and op1 != 'sqrt'):
                                yield (value1 * value2, ('*', eq1, eq2))
                        if value1 > 0.001 and value1 < 1000.0 and value2 > -10.0 and value2 < 10.0:
                            if op1 != '1/' and op1 != '^' and op1 != 'sqrt':
                                yield (math.pow(value1, value2), ('^', eq1, eq2))

def equations(target, max_size = 7, min_compression = 1):
    total_count = 0
    last_count = 1
    growth = 10
    min_diff = 1.0 / math.pow(growth, min_compression + 1)
    for size in range(1, max_size + 1):
        current_count = 0
        for value, eq in recurse(size):
            total_count += 1
            current_count += 1
            if abs(value - target) < min_diff:
                yield (value, eq)
            if total_count % 1000000 == 0:
                print(f'\riterations: {round(total_count / 1e6)}M ({round(100 * current_count / (last_count * growth), 2)}% of size {size}) ', end='', file=sys.stderr)
        growth = current_count / last_count
        min_diff = 1.0 / (current_count * math.pow(growth, min_compression + 1))
        last_count = current_count

def stringify(eq):
    if len(eq) == 1:
        return str(eq[0])
    elif len(eq[0]) > 2:
        return f'{eq[0]}({" ".join([stringify(x) for x in eq[1:]])})'
    elif len(eq) == 2:
        return f'({eq[0]}{stringify(eq[1])})'
    else:
        return f'({eq[0].join([stringify(x) for x in eq[1:]])})'

if __name__ == '__main__':
    for value, eq in equations(target):
        accuracy = round(-math.log10(abs(value - target)), 1) if value != target else len(str(value % 1)) - 2
        print(f'\r{stringify(eq)} = {value} (accuracy: {accuracy})')
