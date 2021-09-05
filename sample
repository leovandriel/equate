#!/usr/bin/env python3 #-m cProfile -s tottime

import math # https://docs.python.org/3/library/math.html
import random

target = (1 + math.sqrt(5)) / 2 # golden ratio

def nullary():
    rand = random.random()
    if rand < 0.5:
        return (1.0, '1', 1.01)
    if rand < 1.0:
        return (math.pi, 'pi', 1.02)
    # if rand < 1.0:
    #     return (math.e, 'e', 1.02)

def unary(depth):
    rand = random.random()
    (value, form, length) = sample(depth + 1)
    if rand < 1.0:
        return (-value, ('-', form), length + 1.01)
    # if rand < 1.0:
    #     if value == 0.0:
    #         return unary(depth)
    #     return (1 / value, ('1/', form), length + 1.01)
    # if rand < 0.7:
    #     if value > 100:
    #         return unary(depth)
    #     return (math.exp(value), ('exp', form), length + 1.02)
    # if rand < 1.0:
    #     return (math.cos(value), ('cos', form), length + 1.03)

def binary(depth):
    rand = random.random()
    (value1, form1, length1) = sample(depth + 1)
    (value2, form2, length2) = sample(depth + 1)
    if rand < 0.4:
        return (value1 + value2, (form1, '+', form2), length1 + length2 + 1.01)
    if rand < 0.8:
        if value1 == 1.0 or value2 == 1.0 or value1 == -1.0 or value2 == -1.0:
            return binary(depth)
        return (value1 * value2, (form1, '*', form2), length1 + length2 + 1.01)
    if rand < 1.0:
        if value1 <= 0.0 or value1 == 1.0 or value2 == 1.0:
            return binary(depth)
        if abs(value1) > 10 or abs(value1) < 0.01 or value2 > 10 or value2 < -10:
            return binary(depth)
        try:
            return (math.pow(value1, value2), (form1, '^', form2), length1 + length2 + 1.02)
        except:
            print(value1, value2)
            return (math.pow(value1, value2), (form1, '^', form2), length1 + length2 + 1.02)

def sample(depth):
    rand = random.random()
    value = -1
    if rand < 0.5 or depth == 5:
        (value, form, length) = nullary()
    elif rand < 0.6:
        (value, form, length) = unary(depth)
    elif rand < 1.0:
        (value, form, length) = binary(depth)
    if value == 0.0:
        return sample(depth)
    return (value, form, length)

if __name__ == '__main__':
    max_loops = 1e9
    error = 1e-10

    min_diff = 0.01
    min_length = 0
    for loop in range(int(max_loops)):
        (value, form, length) = sample(0)
        diff = abs(value - target)
        if min_diff > diff + error or (abs(min_diff - diff) < error and min_length > length):
            min_diff = diff
            min_length = length
            if diff == 0.0:
                print(f'{form} found! {value}')
            else:
                accuracy = round(-math.log10(diff), 1)
                print(f'{form} ({round(length)}) at {accuracy} digits: {value}')
