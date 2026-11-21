import calendar
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

from ..registry import command
from ..utils import reply

CAT = "Time"

ZONES = {
    "utc": "UTC", "gmt": "Etc/GMT", "ist": "Asia/Kolkata", "est": "America/New_York", "cst": "America/Chicago",
    "mst": "America/Denver", "pst": "America/Los_Angeles", "cet": "Europe/Paris", "eet": "Europe/Athens",
    "msk": "Europe/Moscow", "jst": "Asia/Tokyo", "kst": "Asia/Seoul", "sgt": "Asia/Singapore",
    "hkt": "Asia/Hong_Kong", "gst": "Asia/Dubai", "pkt": "Asia/Karachi", "aest": "Australia/Sydney",
    "nzst": "Pacific/Auckland", "brt": "America/Sao_Paulo", "wat": "Africa/Lagos", "eat": "Africa/Nairobi",
    "sast": "Africa/Johannesburg", "art": "America/Argentina/Buenos_Aires", "npt": "Asia/Kathmandu",
    "bdt": "Asia/Dhaka", "ict": "Asia/Bangkok", "wib": "Asia/Jakarta", "pht": "Asia/Manila",
    "irst": "Asia/Tehran", "gmtlondon": "Europe/London",
}
FMT = "%A, %d %B %Y — %H:%M:%S %Z (UTC%z)"


def _now(tz):
    return datetime.now(ZoneInfo(tz)).strftime(FMT)


def _mk_zone(name, tz):
    @command(name, CAT)
    async def handler(update, context):
        await reply(update, f"🕒 {tz}\n{_now(tz)}", parse_mode=None)


for _n, _tz in ZONES.items():
    _mk_zone(_n, _tz)


def _parse_date(s):
    return datetime.strptime(s, "%Y-%m-%d").date()


@command("time", CAT, "Current time: /time [Area/City], e.g. /time Asia/Tokyo", aliases=["now"])
async def time_(update, context):
    tz = context.args[0] if context.args else "UTC"
    try:
        out = _now(tz)
    except Exception:
        return await reply(update, "Unknown timezone. Use names like Asia/Kolkata, or a shortcut from /zones.")
    await reply(update, f"🕒 {tz}\n{out}", parse_mode=None)


@command("zones", CAT, "List timezone shortcut commands")
async def zones(update, context):
    await reply(update, " ".join(f"/{z}" for z in ZONES), parse_mode=None)


@command("date", CAT, "Today's date (UTC)", aliases=["today"])
async def date_(update, context):
    await reply(update, datetime.now(timezone.utc).strftime("📅 %A, %d %B %Y (UTC)"), parse_mode=None)


@command("unix", CAT, "Current unix time, or convert: /unix 1700000000")
async def unix(update, context):
    if context.args:
        ts = datetime.fromtimestamp(int(context.args[0]), timezone.utc)
        return await reply(update, ts.strftime("%Y-%m-%d %H:%M:%S UTC"), parse_mode=None)
    await reply(update, str(int(datetime.now(timezone.utc).timestamp())), parse_mode=None)


@command("daysuntil", CAT, "Days until a date: /daysuntil 2027-01-01")
async def daysuntil(update, context):
    if not context.args:
        return await reply(update, "Usage: /daysuntil YYYY-MM-DD")
    d = (_parse_date(context.args[0]) - datetime.now(timezone.utc).date()).days
    await reply(update, f"📆 {d} day(s) {'from now' if d >= 0 else 'ago'}.", parse_mode=None)


@command("age", CAT, "Age from a birth date: /age 2000-05-17")
async def age(update, context):
    if not context.args:
        return await reply(update, "Usage: /age YYYY-MM-DD")
    b, t = _parse_date(context.args[0]), datetime.now(timezone.utc).date()
    y, m, d = t.year - b.year, t.month - b.month, t.day - b.day
    if d < 0:
        pm = t.month - 1 or 12
        d += calendar.monthrange(t.year if t.month > 1 else t.year - 1, pm)[1]
        m -= 1
    if m < 0:
        y -= 1
        m += 12
    await reply(update, f"🎂 {y} years, {m} months, {d} days", parse_mode=None)


@command("weekday", CAT, "Weekday of a date: /weekday 2026-12-25")
async def weekday(update, context):
    if not context.args:
        return await reply(update, "Usage: /weekday YYYY-MM-DD")
    await reply(update, _parse_date(context.args[0]).strftime("%A"), parse_mode=None)


@command("calendar", CAT, "Show a month: /calendar [YYYY MM]", aliases=["cal"])
async def calendar_(update, context):
    t = date.today()
    y, m = (int(context.args[0]), int(context.args[1])) if len(context.args) >= 2 else (t.year, t.month)
    await reply(update, f"<pre>{calendar.month(y, m)}</pre>")
