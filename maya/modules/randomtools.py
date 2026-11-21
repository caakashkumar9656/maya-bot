import random
import re
import secrets
import string
import uuid

from ..registry import command
from ..utils import raw_args, reply

CAT = "Random"


@command("coin", CAT, "Flip a coin", aliases=["flip"])
async def coin(update, context):
    await reply(update, random.choice(["🪙 Heads", "🪙 Tails"]), parse_mode=None)


def _mk_die(sides):
    @command(f"d{sides}", CAT)
    async def handler(update, context):
        await reply(update, f"🎲 d{sides}: {random.randint(1, sides)}", parse_mode=None)


for _s in (4, 6, 8, 10, 12, 20, 100):
    _mk_die(_s)


@command("roll", CAT, "Roll dice: /roll 3d6 (max 50 dice)")
async def roll(update, context):
    m = re.fullmatch(r"(\d{1,2})d(\d{1,4})", (context.args[0] if context.args else "1d6").lower())
    if not m or not 1 <= int(m[1]) <= 50 or int(m[2]) < 2:
        return await reply(update, "Usage: /roll &lt;N&gt;d&lt;sides&gt; e.g. /roll 2d20")
    rolls = [random.randint(1, int(m[2])) for _ in range(int(m[1]))]
    await reply(update, f"🎲 {rolls} = {sum(rolls)}", parse_mode=None)


@command("rand", CAT, "Random number: /rand [min] max", aliases=["randint"])
async def rand(update, context):
    try:
        nums = [int(a) for a in context.args]
    except ValueError:
        nums = []
    if len(nums) == 1:
        lo, hi = 1, nums[0]
    elif len(nums) == 2:
        lo, hi = nums
    else:
        return await reply(update, "Usage: /rand &lt;max&gt; or /rand &lt;min&gt; &lt;max&gt;")
    if lo > hi:
        lo, hi = hi, lo
    await reply(update, f"🎯 {random.randint(lo, hi)}", parse_mode=None)


@command("choose", CAT, "Pick one: /choose pizza | sushi | tacos", aliases=["pick"])
async def choose(update, context):
    text = raw_args(update)
    opts = [o.strip() for o in (text.split("|") if "|" in text else text.split()) if o.strip()]
    if len(opts) < 2:
        return await reply(update, "Usage: /choose a | b | c")
    await reply(update, f"👉 {random.choice(opts)}", parse_mode=None)


@command("shuffle", CAT, "Shuffle the words you give")
async def shuffle(update, context):
    words = list(context.args)
    if not words:
        return await reply(update, "Usage: /shuffle &lt;words&gt;")
    random.shuffle(words)
    await reply(update, " ".join(words), parse_mode=None)


@command("uuid", CAT, "Generate a UUID4")
async def uuid_(update, context):
    await reply(update, str(uuid.uuid4()), parse_mode=None)


@command("password", CAT, "Generate a strong password: /password [length 8-64]", aliases=["genpass"])
async def password(update, context):
    n = int(context.args[0]) if context.args and context.args[0].isdigit() else 16
    n = max(8, min(n, 64))
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*-_=+"
    await reply(update, "".join(secrets.choice(alphabet) for _ in range(n)), parse_mode=None)


@command("pincode", CAT, "Random 4-digit PIN (use a real secret for anything important)", aliases=["randompin"])
async def pin(update, context):
    await reply(update, "".join(secrets.choice(string.digits) for _ in range(4)), parse_mode=None)


@command("token", CAT, "Random hex token")
async def token(update, context):
    await reply(update, secrets.token_hex(16), parse_mode=None)


@command("randomcolor", CAT, "Random hex colour")
async def randomcolor(update, context):
    await reply(update, f"🎨 #{random.randint(0, 0xFFFFFF):06X}", parse_mode=None)


@command("yesno", CAT, "Yes or no?")
async def yesno(update, context):
    await reply(update, random.choice(["✅ Yes", "❌ No"]), parse_mode=None)


@command("lottery", CAT, "Six random numbers from 1-49")
async def lottery(update, context):
    await reply(update, "🎟️ " + " ".join(f"{n:02d}" for n in sorted(random.sample(range(1, 50), 6))), parse_mode=None)
