from datetime import datetime, timedelta, timezone

from .. import db
from ..registry import command
from ..utils import esc, get_target, reply
from .moderation import apply_action, prep

CAT = "Warnings"
MODES = ("ban", "kick", "mute")


def limit(chat_id):
    return int(db.get(chat_id, "warnlimit", "3"))


def mode(chat_id):
    return db.get(chat_id, "warnmode", "ban")


def _make(cmd, delete=False, silent=False):
    desc = "Warn a user" + (" and delete the replied message" if delete else "") + (" silently" if silent else "")

    @command(cmd, CAT, desc, admin=True, group_only=True)
    async def handler(update, context):
        r = await prep(update, context)
        if not r:
            return
        uid, who, rest = r
        chat, msg = update.effective_chat, update.effective_message
        if delete and msg.reply_to_message:
            try:
                await msg.reply_to_message.delete()
            except Exception:
                pass
        key = f"warn:{uid}"
        n = int(db.get(chat.id, key, "0")) + 1
        lim, act = limit(chat.id), mode(chat.id)
        reason = " ".join(rest)
        if n >= lim:
            db.delete(chat.id, key)
            until = datetime.now(timezone.utc) + timedelta(hours=1) if act == "mute" else None
            await apply_action(context, chat.id, act, uid, until)
            text = f"🚨 {who} reached {lim}/{lim} warnings and was {act}{'ned' if act == 'ban' else 'ed'}."
        else:
            db.put(chat.id, key, n)
            text = f"⚠️ {who} has been warned ({n}/{lim})."
        if reason:
            text += f"\nReason: {esc(reason)}"
        if silent:
            try:
                await msg.delete()
            except Exception:
                pass
            return
        await reply(update, text)


_make("warn")
_make("dwarn", delete=True)
_make("swarn", silent=True)


@command("unwarn", CAT, "Remove one warning from a user", admin=True, group_only=True)
async def unwarn(update, context):
    uid, who, _ = await get_target(update, context)
    if not uid:
        return await reply(update, "Reply to a user or give a numeric id.")
    cid = update.effective_chat.id
    n = int(db.get(cid, f"warn:{uid}", "0"))
    if n <= 1:
        db.delete(cid, f"warn:{uid}")
        n = 0
    else:
        db.put(cid, f"warn:{uid}", n - 1)
        n -= 1
    await reply(update, f"✅ {who} now has {n}/{limit(cid)} warnings.")


@command("warns", CAT, "Show a user's warnings (defaults to you)", group_only=True)
async def warns(update, context):
    uid, who, _ = await get_target(update, context)
    if not uid:
        uid, who = update.effective_user.id, update.effective_user.mention_html()
    cid = update.effective_chat.id
    await reply(update, f"{who} has {db.get(cid, f'warn:{uid}', '0')}/{limit(cid)} warnings.")


@command("resetwarns", CAT, "Clear a user's warnings", admin=True, group_only=True, aliases=["clearwarns"])
async def resetwarns(update, context):
    uid, who, _ = await get_target(update, context)
    if not uid:
        return await reply(update, "Reply to a user or give a numeric id.")
    db.delete(update.effective_chat.id, f"warn:{uid}")
    await reply(update, f"✅ Warnings cleared for {who}.")


@command("resetallwarns", CAT, "Clear all warnings in this chat", admin=True, group_only=True)
async def resetallwarns(update, context):
    n = db.clear(update.effective_chat.id, "warn:")
    await reply(update, f"✅ Cleared warnings for {n} user(s).")


@command("warnlist", CAT, "List users who currently have warnings", admin=True, group_only=True)
async def warnlist(update, context):
    rows = db.items(update.effective_chat.id, "warn:")
    if not rows:
        return await reply(update, "Nobody has warnings.")
    await reply(update, "⚠️ <b>Warned users</b>\n" + "\n".join(
        f'• <a href="tg://user?id={u}">{u}</a>: {n}' for u, n in rows))


@command("setwarnlimit", CAT, "Set warnings before action (2-20)", admin=True, group_only=True)
async def setwarnlimit(update, context):
    if not context.args or not context.args[0].isdigit() or not 2 <= int(context.args[0]) <= 20:
        return await reply(update, "Usage: /setwarnlimit &lt;2-20&gt;")
    db.put(update.effective_chat.id, "warnlimit", context.args[0])
    await reply(update, f"✅ Warn limit set to {context.args[0]}.")


@command("warnlimit", CAT, "Show the warn limit", group_only=True)
async def warnlimit(update, context):
    await reply(update, f"Warn limit: {limit(update.effective_chat.id)}")


@command("setwarnmode", CAT, "Set action at the limit: ban, kick or mute", admin=True, group_only=True)
async def setwarnmode(update, context):
    if not context.args or context.args[0].lower() not in MODES:
        return await reply(update, "Usage: /setwarnmode &lt;ban|kick|mute&gt;")
    db.put(update.effective_chat.id, "warnmode", context.args[0].lower())
    await reply(update, f"✅ Warn action set to {context.args[0].lower()}.")


@command("warnmode", CAT, "Show the warn action", group_only=True)
async def warnmode(update, context):
    await reply(update, f"Warn action: {mode(update.effective_chat.id)}")
