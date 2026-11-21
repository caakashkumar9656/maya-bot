"""Checks for the pure (no-Telegram) logic. Run: python tests/test_pure.py"""
import os
import sys
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DB_PATH", ":memory:")
try:
    import telegram  # noqa: F401
except ImportError:
    for n in ("telegram", "telegram.constants", "telegram.ext", "telegram.error"):
        sys.modules[n] = mock.MagicMock()

from maya.modules.converters import convert  # noqa: E402
from maya.modules.mathtools import MATH1, MATHN, from_roman, is_prime, safe_eval, to_roman  # noqa: E402
from maya.modules.texttools import TEXT  # noqa: E402
from maya.utils import chunks, parse_duration  # noqa: E402
from maya.registry import COMMANDS  # noqa: E402

assert safe_eval("2+3*4") == 14
assert safe_eval("2^10") == 1024
assert abs(safe_eval("sqrt(16)+pi") - (4 + 3.141592653589793)) < 1e-9
for bad in ("__import__('os')", "9**9**9", "open('x')"):
    try:
        safe_eval(bad)
        raise SystemExit(f"unsafe expression accepted: {bad}")
    except (ValueError, SyntaxError, TypeError):
        pass

assert abs(convert(10, "km", "mi") - 6.2137119) < 1e-5
assert convert(1, "gb", "mb") == 1024
assert to_roman(1994) == "MCMXCIV" and from_roman("MCMXCIV") == 1994
assert is_prime(97) and not is_prime(100)
assert MATH1["factorial"](5) == 120 and MATH1["fib"](10) == 55
assert MATHN["gcd"][1](12, 18) == 6 and MATHN["lcm"][1](4, 6) == 12

assert TEXT["md5"]("abc") == "900150983cd24fb0d6963f7d28e17f72"
assert TEXT["unmorse"](TEXT["morse"]("sos maya")) == "sos maya"
assert TEXT["unb64"](TEXT["b64"]("Maya")) == "Maya"
assert TEXT["unbinary"](TEXT["binary"]("hi")) == "hi"
assert TEXT["snake"]("helloWorld Maya") == "hello_world_maya"
assert TEXT["palindrome"]("A man, a plan, a canal: Panama").startswith("✅")

assert parse_duration("10m") == 600 and parse_duration("2h") == 7200 and parse_duration("x") is None
assert all(len(c) <= 4096 for c in chunks("line\n" * 5000))
assert len(COMMANDS) >= 500
print("all checks passed;", len(COMMANDS), "commands")
