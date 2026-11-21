import collections
import re
import time
from datetime import datetime, timedelta, timezone

from .. import db
from ..utils import ANON_ADMIN_ID, esc, is_admin_id
from .locks import LOCKS
from .moderation import apply_action
from .protection import feature
from .welcome import get_template, render

FLOOD = collections.defaultdict(lambda: collections.deque(maxlen=60))
LAST_WELCOME = {}  # chat_id -> message_id (for cleanwelcome)


async def _violation(m, chat, user):
    """Return the name of the rule this message breaks, or None."""
    cid = chat.id
    if (m.sender_chat and m.sender_chat.id != cid and not getattr(m, "is_automatic_forward", False)
            and feature(cid, "antichannel")):
        return "antichannel"
    locked = {k for k, _ in db.items(cid, "lock:")}
    if locked:
        text = m.text or m.caption or ""
        ents = list(m.entities or []) + list(m.caption_entities or [])
        types = {str(getattr(e.type, "value", e.type)) for e in ents}
        for k in locked:
            pred = LOCKS.get(k)
            if pred and pred(m, types, text):
                return k
    words = [k for k, _ in db.items(cid, "bl:")]
    if words:
        low = (m.text or m.caption or "").lower()
        if any(w in low for w in words):
            return "blacklist"
    if feature(cid, "antiflood"):
        now = time.time()
        dq = FLOOD[(cid, user.id)]
        dq.append(now)
        if sum(1 for t in dq if now - t <= 10) > int(db.get(cid, "floodlimit", "6")):
            return "flood"
    return None


async def watcher(update, context):
    m, chat, user = update.effective_message, update.effective_chat, update.effective_user
    if not m or not chat or not user:
        return
    cid = chat.id
    sent_as_self = m.sender_chat is not None and m.sender_chat.id == cid
    violation = await _violation(m, chat, user)
    if violation and (sent_as_self or user.id == ANON_ADMIN_ID or await is_admin_id(context, cid, user.id)):
        violation = None
    if violation:
        try:
            await m.delete()
        except Exception:
            pass
        if violation == "flood":
            FLOOD[(cid, user.id)].clear()
            act = db.get(cid, "floodmode", "mute")
            until = datetime.now(timezone.utc) + timedelta(minutes=5)
            try:
                await apply_action(context, cid, act, user.id, until)
                await context.bot.send_message(cid, f"🌊 {user.mention_html()} was {act}d for flooding.",
                                               parse_mode="HTML")
            except Exception:
                pass
        return

    text = m.text or ""
    # notes: "#name"
    if text.startswith("#") and len(text) > 1:
        note = db.get(cid, f"note:{text[1:].split()[0].lower()}")
        if note is not None:
            await m.reply_text(note)
            return
    # filters
    if text:
        low = text.lower()
        for word, body in db.items(cid, "filter:"):
            if re.search(rf"(?<!\w){re.escape(word)}(?!\w)", low):
                await m.reply_text(body)
                return


async def on_new_members(update, context):
    m, chat = update.effective_message, update.effective_chat
    cid = chat.id
    if feature(cid, "cleanservice"):
        try:
            await m.delete()
        except Exception:
            pass
    adder_is_admin = m.from_user is not None and await is_admin_id(context, cid, m.from_user.id)
    humans = []
    for u in m.new_chat_members or []:
        if u.id == context.bot.id:
            await context.bot.send_message(
                cid, "👋 Hi, I'm <b>Maya</b>! Make me an admin so I can manage this group. Try /help",
                parse_mode="HTML")
        elif u.is_bot:
            if not adder_is_admin and (feature(cid, "antibot") or db.get(cid, "lock:bots")):
                try:
                    await apply_action(context, cid, "kick", u.id)
                except Exception:
                    pass
        else:
            humans.append(u)
    if humans and feature(cid, "welcome"):
        try:
            count = await context.bot.get_chat_member_count(cid)
        except Exception:
            count = 0
        if feature(cid, "cleanwelcome") and cid in LAST_WELCOME:
            try:
                await context.bot.delete_message(cid, LAST_WELCOME.pop(cid))
            except Exception:
                pass
        sent = await context.bot.send_message(
            cid, render(get_template(cid, "welcome"), humans, chat, count), parse_mode="HTML")
        LAST_WELCOME[cid] = sent.message_id


async def on_left_member(update, context):
    m, chat = update.effective_message, update.effective_chat
    cid = chat.id
    if feature(cid, "cleanservice"):
        try:
            await m.delete()
        except Exception:
            pass
    u = m.left_chat_member
    if u and not u.is_bot and feature(cid, "goodbye"):
        await context.bot.send_message(cid, render(get_template(cid, "goodbye"), [u], chat, 0),
                                       parse_mode="HTML")
