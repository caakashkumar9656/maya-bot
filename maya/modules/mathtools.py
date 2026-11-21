import ast
import math
import operator
import statistics

from ..registry import command
from ..utils import raw_args, reply

CAT = "Math"

OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv,
       ast.FloorDiv: operator.floordiv, ast.Mod: operator.mod, ast.Pow: operator.pow}
CONST = {"pi": math.pi, "e": math.e, "tau": math.tau}
FUNCS = {"sqrt": math.sqrt, "sin": math.sin, "cos": math.cos, "tan": math.tan, "log": math.log,
         "log10": math.log10, "ln": math.log, "abs": abs, "floor": math.floor, "ceil": math.ceil,
         "round": round, "exp": math.exp, "factorial": lambda x: math.factorial(int(x)) if x <= 800 else (_ for _ in ()).throw(ValueError("too large"))}


def _eval(n):
    if isinstance(n, ast.Expression):
        return _eval(n.body)
    if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)) and not isinstance(n.value, bool):
        return n.value
    if isinstance(n, ast.BinOp) and type(n.op) in OPS:
        a, b = _eval(n.left), _eval(n.right)
        if isinstance(n.op, ast.Pow):
            if abs(b) > 1000 or (isinstance(a, int) and isinstance(b, int) and abs(a).bit_length() * abs(b) > 20000):
                raise ValueError("exponent too large")
        return OPS[type(n.op)](a, b)
    if isinstance(n, ast.UnaryOp) and isinstance(n.op, (ast.UAdd, ast.USub)):
        v = _eval(n.operand)
        return v if isinstance(n.op, ast.UAdd) else -v
    if isinstance(n, ast.Name) and n.id in CONST:
        return CONST[n.id]
    if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in FUNCS and not n.keywords:
        return FUNCS[n.func.id](*[_eval(a) for a in n.args])
    raise ValueError("unsupported expression")


def safe_eval(expr):
    return _eval(ast.parse(expr.replace("^", "**").replace(",", "").strip(), mode="eval"))


def fmt(x):
    if isinstance(x, float):
        return str(int(x)) if x.is_integer() and abs(x) < 1e15 else f"{x:.10g}"
    return str(x)


def num(s):
    try:
        return int(s)
    except ValueError:
        return float(s)


def to_roman(n):
    if not 1 <= n <= 3999:
        raise ValueError("roman numerals support 1-3999")
    out = ""
    for v, s in ((1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"), (50, "L"),
                 (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")):
        while n >= v:
            out += s
            n -= v
    return out


def from_roman(s):
    vals = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    total = 0
    s = s.upper()
    for i, c in enumerate(s):
        v = vals[c]
        total += -v if i + 1 < len(s) and vals[s[i + 1]] > v else v
    return total


def is_prime(n):
    n = int(n)
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0:
        return False
    if n > 10 ** 12:
        raise ValueError("too large (max 10^12)")
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True


def _next_prime(n):
    n = int(n) + 1
    while not is_prime(n):
        n += 1
    return n


def _fib(n):
    n = int(n)
    if not 0 <= n <= 5000:
        raise ValueError("n must be 0-5000")
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def _divisors(n):
    n = int(n)
    if not 1 <= n <= 10 ** 7:
        raise ValueError("n must be 1-10,000,000")
    return [d for d in range(1, n + 1) if n % d == 0]


def _collatz(n):
    n, steps = int(n), 0
    if n < 1:
        raise ValueError("n must be positive")
    while n != 1 and steps < 100000:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        steps += 1
    return f"{steps} steps"


def _perfect(n):
    n = int(n)
    return f"{n} is {'' if n > 1 and sum(_divisors(n)[:-1]) == n else 'not '}a perfect number"


def _checked_factorial(x):
    if not 0 <= x <= 800:
        raise ValueError("n must be 0-800")
    return math.factorial(int(x))


MATH1 = {
    "sqrt": math.sqrt, "cbrt": lambda x: math.copysign(abs(x) ** (1 / 3), x), "square": lambda x: x * x,
    "cube": lambda x: x ** 3, "abs": abs, "factorial": _checked_factorial, "fib": _fib,
    "isprime": lambda x: f"{fmt(x)} is {'' if is_prime(x) else 'not '}prime",
    "nextprime": _next_prime, "log10": math.log10, "ln": math.log, "log2": math.log2, "exp": math.exp,
    "sin": math.sin, "cos": math.cos, "tan": math.tan, "asin": math.asin, "acos": math.acos,
    "atan": math.atan, "sinh": math.sinh, "cosh": math.cosh, "tanh": math.tanh,
    "deg2rad": math.radians, "rad2deg": math.degrees, "floor": math.floor, "ceil": math.ceil,
    "trunc": math.trunc, "inverse": lambda x: 1 / x, "half": lambda x: x / 2, "double": lambda x: x * 2,
    "triple": lambda x: x * 3, "negate": lambda x: -x, "divisors": lambda x: ", ".join(map(str, _divisors(x))),
    "collatz": _collatz, "digitsum": lambda x: sum(int(c) for c in str(abs(int(x)))),
    "parity": lambda x: "even" if int(x) % 2 == 0 else "odd", "isperfect": _perfect,
}


def _pow(a, b):
    if abs(b) > 1000:
        raise ValueError("exponent too large")
    return a ** b


def _emi(p, annual, years):
    r, n = annual / 12 / 100, years * 12
    if r == 0:
        return f"EMI: {fmt(round(p / n, 2))} per month"
    emi = p * r * (1 + r) ** n / ((1 + r) ** n - 1)
    return f"EMI: {emi:.2f} per month (total {emi * n:.2f})"


# name -> (min args, function)
MATHN = {
    "sum": (1, lambda *a: sum(a)), "product": (1, lambda *a: math.prod(a)),
    "avg": (1, lambda *a: sum(a) / len(a)), "median": (1, lambda *a: statistics.median(a)),
    "max": (1, lambda *a: max(a)), "min": (1, lambda *a: min(a)), "range": (1, lambda *a: max(a) - min(a)),
    "gcd": (2, lambda *a: math.gcd(*map(int, a))), "lcm": (2, lambda *a: math.lcm(*map(int, a))),
    "pow": (2, _pow), "percent": (2, lambda p, x: p * x / 100),
    "pctchange": (2, lambda old, new: f"{(new - old) / old * 100:.2f}%"), "mod": (2, lambda a, b: a % b),
    "hypot": (2, math.hypot), "stdev": (2, lambda *a: statistics.stdev(a)),
    "variance": (2, lambda *a: statistics.variance(a)),
    "discount": (2, lambda price, pct: f"Pay {price * (1 - pct / 100):.2f} (save {price * pct / 100:.2f})"),
    "taxadd": (2, lambda price, pct: f"Total {price * (1 + pct / 100):.2f} (tax {price * pct / 100:.2f})"),
    "tip": (2, lambda bill, pct: f"Tip {bill * pct / 100:.2f}, total {bill * (1 + pct / 100):.2f}"),
    "si": (3, lambda p, r, t: f"Simple interest: {p * r * t / 100:.2f}"),
    "ci": (3, lambda p, r, t: f"Amount after {fmt(t)} yrs: {p * (1 + r / 100) ** t:.2f}"),
    "emi": (3, _emi), "bmi": (2, lambda kg, cm: f"BMI: {kg / (cm / 100) ** 2:.1f}"),
    "cagr": (3, lambda start, end, yrs: f"CAGR: {((end / start) ** (1 / yrs) - 1) * 100:.2f}%"),
}

BASES = {
    "bin2dec": lambda s: int(s, 2), "dec2bin": lambda s: bin(int(s))[2:], "dec2hex": lambda s: hex(int(s))[2:],
    "hex2dec": lambda s: int(s, 16), "dec2oct": lambda s: oct(int(s))[2:], "oct2dec": lambda s: int(s, 8),
    "bin2hex": lambda s: hex(int(s, 2))[2:], "hex2bin": lambda s: bin(int(s, 16))[2:],
    "roman": lambda s: to_roman(int(s)), "unroman": from_roman,
}


@command("calc", CAT, "Calculate: /calc 2*(3+4)^2 — supports sqrt, sin, cos, log, pi, e…", aliases=["math"])
async def calc(update, context):
    expr = raw_args(update)
    if not expr:
        return await reply(update, "Usage: /calc &lt;expression&gt;")
    await reply(update, f"= {fmt(safe_eval(expr))}", parse_mode=None)


def _mk1(name, fn):
    @command(name, CAT)
    async def handler(update, context):
        if not context.args:
            return await reply(update, f"Usage: /{name} &lt;number&gt;")
        await reply(update, fmt(fn(num(context.args[0]))), parse_mode=None)


def _mkn(name, need, fn):
    @command(name, CAT)
    async def handler(update, context):
        if len(context.args) < need:
            return await reply(update, f"Usage: /{name} &lt;at least {need} numbers&gt;")
        await reply(update, fmt(fn(*[num(a) for a in context.args])), parse_mode=None)


def _mkb(name, fn):
    @command(name, CAT)
    async def handler(update, context):
        if not context.args:
            return await reply(update, f"Usage: /{name} &lt;value&gt;")
        await reply(update, fmt(fn(context.args[0])), parse_mode=None)


for _n, _f in MATH1.items():
    _mk1(_n, _f)
for _n, (_need, _f) in MATHN.items():
    _mkn(_n, _need, _f)
for _n, _f in BASES.items():
    _mkb(_n, _f)
