"""Import every module and report how many commands Maya registers.

Works without python-telegram-bot installed (telegram is stubbed) so CI and
quick checks stay fast. Exits non-zero if fewer than 500 commands exist.
"""
import os
import sys
from collections import Counter
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.setdefault("DB_PATH", ":memory:")

try:
    import telegram  # noqa: F401
except ImportError:
    for _name in ("telegram", "telegram.constants", "telegram.ext", "telegram.error"):
        sys.modules[_name] = mock.MagicMock()

from maya import modules  # noqa: E402,F401
from maya.registry import COMMANDS, LOOKUP  # noqa: E402

if __name__ == "__main__":
    by_cat = Counter(c.category for c in COMMANDS.values())
    for cat, n in sorted(by_cat.items(), key=lambda kv: -kv[1]):
        print(f"{cat:<12} {n}")
    print(f"\nPrimary commands : {len(COMMANDS)}")
    print(f"Names incl. aliases: {len(LOOKUP)}")
    sys.exit(0 if len(COMMANDS) >= 500 else 1)
