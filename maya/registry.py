"""Command registry. Every Maya command registers itself here."""
import re
from dataclasses import dataclass, field
from typing import Callable, Dict, List

NAME_RE = re.compile(r"^[a-z0-9_]{1,32}$")


@dataclass
class Command:
    name: str
    func: Callable
    category: str
    help: str = ""
    admin: bool = False
    group_only: bool = False
    sudo: bool = False
    aliases: List[str] = field(default_factory=list)


COMMANDS: Dict[str, Command] = {}  # primary name -> Command
LOOKUP: Dict[str, Command] = {}    # primary name or alias -> Command


def register(name, func, category, help="", admin=False, group_only=False,
             sudo=False, aliases=()):
    for n in (name, *aliases):
        if not NAME_RE.match(n):
            raise ValueError(f"invalid command name: {n!r}")
        if n in LOOKUP:
            raise ValueError(f"duplicate command name: {n!r}")
    cmd = Command(name, func, category, help, admin, group_only, sudo, list(aliases))
    COMMANDS[name] = cmd
    LOOKUP[name] = cmd
    for a in aliases:
        LOOKUP[a] = cmd
    return cmd


def command(name, category, help="", **kw):
    """Decorator: @command("ban", "Moderation", "Ban a user", admin=True)."""
    def deco(func):
        register(name, func, category, help, **kw)
        return func
    return deco
