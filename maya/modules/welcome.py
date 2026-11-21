import re

from .. import db
from ..registry import command
from ..utils import esc, raw_args, reply
from .protection import feature

CAT = "Welcome"

DEFAULTS = {
    "welcome": "👋 Welcome {mention} to {chatname}! You are member #{count}. Please read the /rules.",
    "goodbye": "👋 {first} left the group. Goodbye!",
}


def get_template(chat_id, kind):
    return db.get(chat_id, f"tpl:{kind}", DEFAULTS[kind])


def render(tpl, users, chat, count):
    """Fill {placeholders}. The template is HTML-escaped first, so admins can't break formatting."""
    u = users[0]
    values = {
        "first": ", ".join(esc(x.first_name) for x in users),
        "last": esc(u.last_name or ""),
        "fullname": esc(u.full_name),
        "username": "@" + u.username if u.username else esc(u.first_name),
        "mention": ", ".join(x.mention_html() for x in users),
        "id": str(u.id),
        "chatname": esc(chat.title or ""),
        "count": str(count),
    }
    return re.sub(r"\{(\w+)\}", lambda m: values.get(m[1], m[0]), esc(tpl))


def _body(update):
    text = raw_args(update)
    r = update.effective_message.reply_to_message
    return text or ((r.text or r.caption or "") if r else "")


def _mk(kind):
    @command(f"set{kind}", CAT, f"Set the {kind} message (placeholders: see /welcomehelp)",
             admin=True, group_only=True)
    async def set_(update, context):
        body = _body(update)
        if not body:
            return await reply(update, f"Usage: /set{kind} &lt;text&gt; (or reply to a message)")
        db.put(update.effective_chat.id, f"tpl:{kind}", body)
        await reply(update, f"✅ {kind.title()} message updated.")

    @command(f"reset{kind}", CAT, f"Restore the default {kind} message", admin=True, group_only=True)
    async def reset(update, context):
        db.delete(update.effective_chat.id, f"tpl:{kind}")
        await reply(update, f"✅ {kind.title()} message reset.")

    @command(kind, CAT, f"Preview the {kind} message and status", group_only=True)
    async def show(update, context):
        chat, user = update.effective_chat, update.effective_user
        on = feature(chat.id, kind)
        await reply(update, f"{kind.title()} is <b>{'on' if on else 'off'}</b>. Preview:\n\n"
                            + render(get_template(chat.id, kind), [user], chat, 0))


_mk("welcome")
_mk("goodbye")


@command("welcomehelp", CAT, "Show welcome/goodbye placeholders")
async def welcomehelp(update, context):
    await reply(update, "Placeholders: {first} {last} {fullname} {username} {mention} {id} {chatname} {count}",
                parse_mode=None)


@command("setrules", CAT, "Set the group rules", admin=True, group_only=True)
async def setrules(update, context):
    body = _body(update)
    if not body:
        return await reply(update, "Usage: /setrules &lt;text&gt; (or reply to a message)")
    db.put(update.effective_chat.id, "rules", body)
    await reply(update, "✅ Rules saved.")


@command("rules", CAT, "Show the group rules", group_only=True)
async def rules(update, context):
    text = db.get(update.effective_chat.id, "rules")
    await reply(update, f"📜 <b>Rules</b>\n{esc(text)}" if text else "No rules have been set yet.")


@command("clearrules", CAT, "Delete the group rules", admin=True, group_only=True)
async def clearrules(update, context):
    db.delete(update.effective_chat.id, "rules")
    await reply(update, "🗑️ Rules cleared.")
