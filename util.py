import decimal
import hashlib
import json
import math
import os.path
import urllib.request

def lookup_add(lookup, eq, value, digits):
    key = round(value, digits - math.ceil(math.log10(abs(value)))) if value != 0 else value
    if key in lookup:
        if lookup[key] != eq:
            return lookup[key]
    else:
        lookup[key] = eq
    return None

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return str(o)
        return super(DecimalEncoder, self).default(o)

def cache(op, input, name):
    key = hashlib.md5(str(input).encode('utf-8')).hexdigest()
    path = f'cache/{name}/{key}.json'
    if os.path.exists(path):
        with open(path, 'r') as file:
            data = json.loads(file.read())
            return data['output']
    else:
        output = op(*input)
        with open(path, 'w') as file:
            data = { 'input': input, 'output': output }
            file.write(json.dumps(data, cls=DecimalEncoder))
        return output

def fetch_json(url):
    with urllib.request.urlopen(url) as response:
        return json.loads(response.read())

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

def find_rational(value):
    frac = value
    coef = []
    prod = 1
    while prod < 1e10:
        integer = int(frac)
        coef.append(integer)
        if abs(frac - integer) <1e-5:
            a = 1
            b = 0
            for x in reversed(coef):
                v = a
                a = a * x + b
                b = v
            return (a, b)
        frac = 1 / (frac - integer)
        if integer != 0:
            prod *= abs(integer)
    return None
