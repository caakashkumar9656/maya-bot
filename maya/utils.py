import html
import re

from telegram.constants import ChatMemberStatus, ParseMode

from .config import SUDO_USERS

ANON_ADMIN_ID = 1087968824  # Telegram's "GroupAnonymousBot" (anonymous admins)


def esc(s):
    return html.escape(str(s), quote=False)


def chunks(text, size=3900):
    out, cur = [], ""
    for line in str(text).split("\n"):
        while len(line) > size:
            if cur:
                out.append(cur)
                cur = ""
            out.append(line[:size])
            line = line[size:]
        if len(cur) + len(line) + 1 > size and cur:
            out.append(cur)
            cur = ""
        cur += line + "\n"
    if cur.strip():
        out.append(cur)
    return out or ["…"]


async def reply(update, text, **kw):
    """Reply to the current message. HTML by default; pass parse_mode=None for plain text."""
    kw.setdefault("parse_mode", ParseMode.HTML)
    sent = None
    for part in chunks(text):
        sent = await update.effective_message.reply_text(part.rstrip() or "…", **kw)
    return sent


def raw_args(update):
    """Text after the command, with newlines preserved."""
    parts = (update.effective_message.text or "").split(None, 1)
    return parts[1] if len(parts) > 1 else ""


def is_sudo(uid):
    return uid in SUDO_USERS


async def is_admin_id(context, chat_id, uid):
    if uid in SUDO_USERS or uid == ANON_ADMIN_ID:
        return True
    try:
        member = await context.bot.get_chat_member(chat_id, uid)
    except Exception:
        return False
    return member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)


async def is_admin(update, context):
    user = update.effective_user
    return bool(user) and await is_admin_id(context, update.effective_chat.id, user.id)


async def get_target(update, context):
    """Resolve (user_id, mention_html, remaining_args) from a reply or a numeric id."""
    msg = update.effective_message
    args = list(context.args or [])
    if msg.reply_to_message and msg.reply_to_message.from_user:
        u = msg.reply_to_message.from_user
        return u.id, u.mention_html(), args
    if args and args[0].lstrip("-").isdigit():
        uid = int(args[0])
        return uid, f'<a href="tg://user?id={uid}">{uid}</a>', args[1:]
    return None, None, args


def parse_duration(s):
    m = re.fullmatch(r"(\d+)([smhdw])", (s or "").lower())
    if not m:
        return None
    return int(m[1]) * {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}[m[2]]


def get_text(update, context):
    """Text from args, or from the replied-to message."""
    if context.args:
        return raw_args(update)
    r = update.effective_message.reply_to_message
    return (r.text or r.caption or "") if r else ""
