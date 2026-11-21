from ..registry import command
from ..utils import reply

CAT = "Converters"

# unit -> size in the group's base unit
GROUPS = {
    "length": {"m": 1, "km": 1000, "cm": 0.01, "mm": 0.001, "mi": 1609.344, "yd": 0.9144, "ft": 0.3048, "inch": 0.0254},
    "mass": {"kg": 1, "g": 0.001, "mg": 1e-6, "lb": 0.45359237, "oz": 0.028349523125, "ton": 1000},
    "volume": {"l": 1, "ml": 0.001, "gal": 3.785411784, "qt": 0.946352946, "pt": 0.473176473, "cup": 0.2365882365},
    "speed": {"kmh": 1, "mph": 1.609344, "mps": 3.6, "kn": 1.852},
    "data": {"b": 1, "kb": 1024, "mb": 1024 ** 2, "gb": 1024 ** 3, "tb": 1024 ** 4},
    "time": {"sec": 1, "min": 60, "hr": 3600, "day": 86400, "wk": 604800},
    "area": {"sqm": 1, "sqkm": 1e6, "sqft": 0.09290304, "sqmi": 2589988.110336, "acre": 4046.8564224, "ha": 10000},
}
TEMPS = {
    "c2f": lambda c: c * 9 / 5 + 32, "f2c": lambda f: (f - 32) * 5 / 9,
    "c2k": lambda c: c + 273.15, "k2c": lambda k: k - 273.15,
    "f2k": lambda f: (f - 32) * 5 / 9 + 273.15, "k2f": lambda k: (k - 273.15) * 9 / 5 + 32,
}
UNIT_GROUP = {u: g for g, units in GROUPS.items() for u in units}


def convert(value, a, b):
    g = UNIT_GROUP[a]
    if UNIT_GROUP.get(b) != g:
        raise ValueError(f"cannot convert {a} to {b}")
    return value * GROUPS[g][a] / GROUPS[g][b]


def _f(v):
    return f"{v:.8g}"


def _mk_conv(a, b):
    @command(f"{a}2{b}", CAT)
    async def handler(update, context):
        if not context.args:
            return await reply(update, f"Usage: /{a}2{b} &lt;number&gt; [more numbers]")
        out = [f"{_f(float(x))} {a} = {_f(convert(float(x), a, b))} {b}" for x in context.args[:20]]
        await reply(update, "\n".join(out), parse_mode=None)


def _mk_temp(name, fn):
    @command(name, CAT)
    async def handler(update, context):
        if not context.args:
            return await reply(update, f"Usage: /{name} &lt;number&gt;")
        a, b = name.split("2")
        out = [f"{_f(float(x))}°{a.upper()} = {_f(fn(float(x)))}°{b.upper()}" for x in context.args[:20]]
        await reply(update, "\n".join(out), parse_mode=None)


for _g, _units in GROUPS.items():
    for _a in _units:
        for _b in _units:
            if _a != _b:
                _mk_conv(_a, _b)
for _n, _fn in TEMPS.items():
    _mk_temp(_n, _fn)


@command("convert", CAT, "Convert units: /convert 10 km mi")
async def convert_cmd(update, context):
    if len(context.args) != 3:
        return await reply(update, "Usage: /convert &lt;value&gt; &lt;from&gt; &lt;to&gt; (see /units)")
    v, a, b = float(context.args[0]), context.args[1].lower(), context.args[2].lower()
    if a not in UNIT_GROUP or b not in UNIT_GROUP:
        return await reply(update, "Unknown unit. See /units.")
    await reply(update, f"{_f(v)} {a} = {_f(convert(v, a, b))} {b}", parse_mode=None)


@command("units", CAT, "List supported units")
async def units(update, context):
    lines = [f"{g}: {', '.join(u)}" for g, u in GROUPS.items()]
    lines.append("temperature: use /c2f /f2c /c2k /k2c /f2k /k2f")
    lines.append("Every pair works as /<from>2<to>, e.g. /km2mi 42")
    await reply(update, "\n".join(lines), parse_mode=None)
