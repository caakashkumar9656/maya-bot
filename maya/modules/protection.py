from .. import db
from ..registry import command
from ..utils import esc, reply

CAT = "Protection"

# name -> (enabled by default, description)
FEATURES = {
    "welcome": (True, "welcome messages for new members"),
    "goodbye": (False, "goodbye messages when members leave"),
    "antiflood": (False, "flood control (mutes users who spam)"),
    "antibot": (False, "automatic removal of bots added by non-admins"),
    "cleanservice": (False, "deleting join/leave service messages"),
    "cleanwelcome": (False, "deleting the previous welcome message"),
    "antichannel": (False, "deleting messages sent as other channels"),
    "reports": (True, "the /report command"),
}


def feature(chat_id, name):
    v = db.get(chat_id, f"feat:{name}")
    return FEATURES[name][0] if v is None else v == "1"


def _mk(name, on):
    @command(f"{name}{'on' if on else 'off'}", CAT,
             f"{'Enable' if on else 'Disable'} {FEATURES[name][1]}", admin=True, group_only=True)
    async def handler(update, context):
        db.put(update.effective_chat.id, f"feat:{name}", "1" if on else "0")
        await reply(update, f"{'✅ Enabled' if on else '⛔ Disabled'}: {esc(FEATURES[name][1])}")


for _n in FEATURES:
    _mk(_n, True)
    _mk(_n, False)


@command("features", CAT, "Show which protection features are enabled", group_only=True)
async def features(update, context):
    cid = update.effective_chat.id
    await reply(update, "<b>Features</b>\n" + "\n".join(
        f"{'✅' if feature(cid, n) else '⛔'} {n} — {esc(d)}" for n, (_, d) in FEATURES.items()))


@command("setflood", CAT, "Set max messages per 10 seconds (3-50)", admin=True, group_only=True)
async def setflood(update, context):
    if not context.args or not context.args[0].isdigit() or not 3 <= int(context.args[0]) <= 50:
        return await reply(update, "Usage: /setflood &lt;3-50&gt;")
    db.put(update.effective_chat.id, "floodlimit", context.args[0])
    await reply(update, f"✅ Flood limit: {context.args[0]} messages / 10s.")


@command("flood", CAT, "Show flood settings", group_only=True)
async def flood(update, context):
    cid = update.effective_chat.id
    await reply(update, f"Antiflood is {'on' if feature(cid, 'antiflood') else 'off'}: "
                        f"{db.get(cid, 'floodlimit', '6')} msgs/10s → {db.get(cid, 'floodmode', 'mute')}")


@command("setfloodmode", CAT, "Action on flood: mute, kick or ban", admin=True, group_only=True)
async def setfloodmode(update, context):
    if not context.args or context.args[0].lower() not in ("mute", "kick", "ban"):
        return await reply(update, "Usage: /setfloodmode &lt;mute|kick|ban&gt;")
    db.put(update.effective_chat.id, "floodmode", context.args[0].lower())
    await reply(update, f"✅ Flood action: {context.args[0].lower()}.")
