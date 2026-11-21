import base64
import codecs
import hashlib
import html
import random
import re
import urllib.parse
import zlib

from ..registry import command
from ..utils import get_text, reply

CAT = "Text"

MORSE = {"a": ".-", "b": "-...", "c": "-.-.", "d": "-..", "e": ".", "f": "..-.", "g": "--.", "h": "....",
         "i": "..", "j": ".---", "k": "-.-", "l": ".-..", "m": "--", "n": "-.", "o": "---", "p": ".--.",
         "q": "--.-", "r": ".-.", "s": "...", "t": "-", "u": "..-", "v": "...-", "w": ".--", "x": "-..-",
         "y": "-.--", "z": "--..", "0": "-----", "1": ".----", "2": "..---", "3": "...--", "4": "....-",
         "5": ".....", "6": "-....", "7": "--...", "8": "---..", "9": "----."}
MORSE_INV = {v: k for k, v in MORSE.items()}
FLIP = dict(zip("abcdefghijklmnopqrstuvwxyz", "ɐqɔpǝɟƃɥᴉɾʞlɯuodbɹsʇnʌʍxʎz"))


def _style(up, lo, dig=None, exc=None):
    exc = exc or {}

    def f(s):
        out = []
        for c in s:
            if c in exc:
                out.append(exc[c])
            elif "A" <= c <= "Z":
                out.append(chr(up + ord(c) - 65))
            elif "a" <= c <= "z":
                out.append(chr(lo + ord(c) - 97))
            elif dig and "0" <= c <= "9":
                out.append(chr(dig + ord(c) - 48))
            else:
                out.append(c)
        return "".join(out)
    return f


def _words(s):
    return [w.lower() for w in re.findall(r"[A-Za-z0-9]+", re.sub(r"([a-z])([A-Z])", r"\1 \2", s))]


def _hash(algo):
    return lambda s: hashlib.new(algo, s.encode()).hexdigest()


def _owo(s):
    s = re.sub(r"[rl]", "w", s)
    s = re.sub(r"[RL]", "W", s)
    s = re.sub(r"n([aeiou])", r"ny\1", s)
    return s + " owo"


def _rot47(s):
    return "".join(chr(33 + (ord(c) - 33 + 47) % 94) if 33 <= ord(c) <= 126 else c for c in s)


def _vapor(s):
    return "".join("　" if c == " " else chr(ord(c) + 0xFEE0) if 33 <= ord(c) <= 126 else c for c in s)


def _zalgo(s):
    return "".join(c + "".join(chr(random.randint(0x300, 0x36F)) for _ in range(random.randint(1, 4))) for c in s)


def _bubble(s):
    return "".join(chr(0x24B6 + ord(c) - 65) if "A" <= c <= "Z" else chr(0x24D0 + ord(c) - 97) if "a" <= c <= "z" else c
                   for c in s)


TEXT = {
    "upper": str.upper,
    "lower": str.lower,
    "titlecase": str.title,
    "capitalize": str.capitalize,
    "swapcase": str.swapcase,
    "reverse": lambda s: s[::-1],
    "reversewords": lambda s: " ".join(s.split()[::-1]),
    "mock": lambda s: "".join(c.upper() if i % 2 else c.lower() for i, c in enumerate(s)),
    "vaporwave": _vapor,
    "spaced": lambda s: " ".join(s),
    "clapify": lambda s: "👏".join(s.split()),
    "stutter": lambda s: " ".join(f"{w[0]}-{w}" if w else w for w in s.split()),
    "owo": _owo,
    "leet": lambda s: s.translate(str.maketrans("aeiostlAEIOSTL", "43105714310571")),
    "rot13": lambda s: codecs.encode(s, "rot_13"),
    "rot47": _rot47,
    "morse": lambda s: " / ".join(" ".join(MORSE.get(c, "?") for c in w) for w in s.lower().split()),
    "unmorse": lambda s: " ".join("".join(MORSE_INV.get(x, "?") for x in w.split()) for w in s.split("/")),
    "binary": lambda s: " ".join(format(b, "08b") for b in s.encode()),
    "unbinary": lambda s: bytes(int(x, 2) for x in s.split()).decode(),
    "hex": lambda s: s.encode().hex(),
    "unhex": lambda s: bytes.fromhex(s.replace(" ", "")).decode(),
    "b64": lambda s: base64.b64encode(s.encode()).decode(),
    "unb64": lambda s: base64.b64decode(s).decode(),
    "urlenc": urllib.parse.quote,
    "urldec": urllib.parse.unquote,
    "htmlesc": html.escape,
    "htmlunesc": html.unescape,
    "md5": _hash("md5"),
    "sha1": _hash("sha1"),
    "sha224": _hash("sha224"),
    "sha256": _hash("sha256"),
    "sha384": _hash("sha384"),
    "sha512": _hash("sha512"),
    "blake2b": _hash("blake2b"),
    "crc32": lambda s: format(zlib.crc32(s.encode()) & 0xFFFFFFFF, "08x"),
    "charcount": lambda s: f"{len(s)} characters",
    "wordcount": lambda s: f"{len(s.split())} words",
    "linecount": lambda s: f"{len(s.splitlines())} lines",
    "vowels": lambda s: f"{sum(c in 'aeiouAEIOU' for c in s)} vowels",
    "sortwords": lambda s: " ".join(sorted(s.split(), key=str.lower)),
    "sortlines": lambda s: "\n".join(sorted(s.splitlines(), key=str.lower)),
    "unique": lambda s: " ".join(dict.fromkeys(s.split())),
    "nospace": lambda s: "".join(s.split()),
    "snake": lambda s: "_".join(_words(s)),
    "kebab": lambda s: "-".join(_words(s)),
    "camel": lambda s: "".join(w if i == 0 else w.title() for i, w in enumerate(_words(s))),
    "pascal": lambda s: "".join(w.title() for w in _words(s)),
    "constcase": lambda s: "_".join(_words(s)).upper(),
    "slug": lambda s: "-".join(_words(s)),
    "palindrome": lambda s: "✅ Palindrome" if (c := re.sub(r"\W", "", s.lower())) == c[::-1] else "❌ Not a palindrome",
    "zalgo": _zalgo,
    "strike": lambda s: "".join(c + "̶" for c in s),
    "underline": lambda s: "".join(c + "̲" for c in s),
    "ascii": lambda s: " ".join(str(ord(c)) for c in s),
    "unascii": lambda s: "".join(chr(int(x)) for x in s.split()),
    "fliptext": lambda s: "".join(FLIP.get(c, c) for c in s.lower()[::-1]),
    "bubble": _bubble,
    "shout": lambda s: s.upper() + "!!!",
    "whisper": lambda s: s.lower() + "...",
    "trim": lambda s: " ".join(s.split()),
    "acronym": lambda s: "".join(w[0].upper() for w in s.split()),
    "bold": _style(0x1D400, 0x1D41A, 0x1D7CE),
    "italic": _style(0x1D434, 0x1D44E, None, {"h": "ℎ"}),
    "bolditalic": _style(0x1D468, 0x1D482),
    "mono": _style(0x1D670, 0x1D68A, 0x1D7F6),
    "sans": _style(0x1D5A0, 0x1D5BA, 0x1D7E2),
    "sansbold": _style(0x1D5D4, 0x1D5EE, 0x1D7EC),
    "sansitalic": _style(0x1D608, 0x1D622),
}


def _mk(name, fn):
    @command(name, CAT)
    async def handler(update, context):
        text = get_text(update, context)
        if not text:
            return await reply(update, f"Usage: /{name} &lt;text&gt; (or reply to a message)")
        await reply(update, str(fn(text)) or "(empty)", parse_mode=None)


for _n, _f in TEXT.items():
    _mk(_n, _f)
