import hashlib
import json
import math
import os.path
import urllib.request

def trim(value, digits):
    if value == 0.0:
        return value
    precision = digits - math.ceil(math.log10(abs(value)))
    if precision < 0:
        return value
    return float(f'{{:.{precision}f}}'.format(value))

class Collider:
    def __init__(self, precision = 13):
        self.precision = precision
        self.lookup = {}

    def add(self, eq, value):
        key = trim(value, self.precision)
        if key in self.lookup:
            if self.lookup[key] != eq:
                return self.lookup[key]
        else:
            self.lookup[key] = eq
        return None

def cache(op, input, name):
    key = hashlib.md5(str(input).encode('utf-8')).hexdigest()
    path = f'cache/{name}/{key}.json'
    if os.path.exists(path):
        with open(path, 'r') as file:
            data = json.loads(file.read())
            return data['output']
    else:
        output = op(input)
        with open(path, 'w') as file:
            data = { 'input': input, 'output': output }
            file.write(json.dumps(data))
        return output

def fetch_json(url):
    with urllib.request.urlopen(url) as response:
        return json.loads(response.read())
