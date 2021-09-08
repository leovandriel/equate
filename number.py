from decimal import Decimal, getcontext
import math

precision = None # None is regular float

if precision:
    getcontext().prec = precision

    def create(value):
        return Decimal(value)

    def pi():
        return approx_pi()

    def e():
        return approx_e()

    def sin(value):
        return approx_sin(value)

    def log(value):
        return value.ln()

    def cos(value):
        return approx_cos(value)

    def floor(value):
        return value.quantize(Decimal(1), rounding=ROUND_DOWN)

    def remainder(value):
        value.copy_abs() % 1

    def is_integer(value):
        return value.to_integral_value() == value

    def is_signed(value):
        return value.is_signed()

    def is_zero(value):
        return value.is_zero()

    def is_nan(value):
        return value.is_nan()

    def approx_pi():
        getcontext().prec += 2
        s, last, n, na, d, da, t = 3, 0, 1, 0, 0, 24, Decimal(3)
        while s != last:
            last = s
            n, na = n + na, na + 8
            d, da = d + da, da + 32
            t = (t * n) / d
            s += t
        getcontext().prec -= 2
        return +s

    def approx_e():
        getcontext().prec += 2
        s, last, i, fact, num = 1, 0, 0, 1, Decimal(1)
        while s != last:
            last = s
            i += 1
            fact *= i
            s += num / fact
        getcontext().prec -= 2
        return +s

    def approx_sin(value):
        sq = value * value
        getcontext().prec += 2
        s, last, i, fact, num, sign = value, 0, 1, 1, value, 1
        while s != last:
            last = s
            i += 2
            fact *= i * (i - 1)
            num *= sq
            sign *= -1
            s += num / fact * sign
        getcontext().prec -= 2
        return +s

    def approx_cos(value):
        sq = value * value
        getcontext().prec += 2
        s, last, i, fact, num, sign = 1, 0, 0, 1, 1, 1
        while s != last:
            last = s
            i += 2
            fact *= i * (i - 1)
            num *= sq
            sign *= -1
            s += num / fact * sign
        getcontext().prec -= 2
        return +s

else:

    def create(value):
        return float(value)

    def pi():
        return math.pi

    def e():
        return math.e

    def sin(value):
        return math.sin(value)

    def log(value):
        return math.log(value)

    def cos(value):
        return math.cos(value)

    def floor(value):
        return math.floor(value)

    def remainder(value):
        abs(value) % 1.0

    def is_integer(value):
        return value.is_integer()

    def is_signed(value):
        return value < 0.0

    def is_zero(value):
        return value == 0.0

    def is_nan(value):
        return math.isnan(value)

    def approx_pi():
        getcontext().prec += 2
        s, last, n, na, d, da, t = 3, 0, 1, 0, 0, 24, Decimal(3)
        while s != last:
            last = s
            n, na = n + na, na + 8
            d, da = d + da, da + 32
            t = (t * n) / d
            s += t
        getcontext().prec -= 2
        return +s

    def approx_e():
        getcontext().prec += 2
        s, last, i, fact, num = 1, 0, 0, 1, Decimal(1)
        while s != last:
            last = s
            i += 1
            fact *= i
            s += num / fact
        getcontext().prec -= 2
        return +s

    def approx_sin(value):
        sq = value * value
        getcontext().prec += 2
        s, last, i, fact, num, sign = value, 0, 1, 1, value, 1
        while s != last:
            last = s
            i += 2
            fact *= i * (i - 1)
            num *= sq
            sign *= -1
            s += num / fact * sign
        getcontext().prec -= 2
        return +s

    def approx_cos(value):
        sq = value * value
        getcontext().prec += 2
        s, last, i, fact, num, sign = 1, 0, 0, 1, 1, 1
        while s != last:
            last = s
            i += 2
            fact *= i * (i - 1)
            num *= sq
            sign *= -1
            s += num / fact * sign
        getcontext().prec -= 2
        return +s
