import re

from .. import db
from ..registry import command
from ..utils import reply

CAT = "Locks"

INVITE = re.compile(r"(t\.me/\+|t\.me/joinchat|telegram\.me/joinchat)", re.I)


def _has(*names):
    wanted = set(names)
    return lambda m, t, x: bool(t & wanted)


def _rx(pattern):
    rx = re.compile(pattern)
    return lambda m, t, x: bool(rx.search(x))


# Each predicate gets (message, entity-type-set, text-or-caption).
LOCKS = {
    "text": lambda m, t, x: bool(m.text) and not m.text.startswith("/"),
    "photo": lambda m, t, x: bool(m.photo),
    "video": lambda m, t, x: bool(m.video),
    "audio": lambda m, t, x: bool(m.audio),
    "voice": lambda m, t, x: bool(m.voice),
    "document": lambda m, t, x: bool(m.document),
    "sticker": lambda m, t, x: bool(m.sticker),
    "gif": lambda m, t, x: bool(m.animation),
    "videonote": lambda m, t, x: bool(m.video_note),
    "contact": lambda m, t, x: bool(m.contact),
    "location": lambda m, t, x: bool(m.location),
    "venue": lambda m, t, x: bool(m.venue),
    "poll": lambda m, t, x: bool(m.poll),
    "dice": lambda m, t, x: bool(m.dice),
    "game": lambda m, t, x: bool(m.game),
    "forward": lambda m, t, x: getattr(m, "forward_origin", None) is not None,
    "inline": lambda m, t, x: m.via_bot is not None,
    "story": lambda m, t, x: getattr(m, "story", None) is not None,
    "media": lambda m, t, x: any([m.photo, m.video, m.audio, m.voice, m.document,
                                  m.animation, m.video_note, m.sticker]),
    "url": _has("url", "text_link"),
    "email": _has("email"),
    "mention": _has("mention", "text_mention"),
    "hashtag": _has("hashtag", "cashtag"),
    "command": _has("bot_command"),
    "phone": _has("phone_number"),
    "spoiler": _has("spoiler"),
    "code": _has("code", "pre"),
    "customemoji": _has("custom_emoji"),
    "invitelink": lambda m, t, x: bool(INVITE.search(x)),
    "arabic": _rx(r"[؀-ۿ]"),
    "cyrillic": _rx(r"[Ѐ-ӿ]"),
    "cjk": _rx(r"[一-鿿぀-ヿ가-힯]"),
}
# "bots" is enforced when members join (see watcher.on_new_members)
LOCK_TYPES = list(LOCKS) + ["bots"]


def _set(chat_id, t, on):
    if on:
        db.put(chat_id, f"lock:{t}", "1")
    else:
        db.delete(chat_id, f"lock:{t}")


def _mk(t, on):
    verb = "lock" if on else "unlock"

    @command(f"{verb}{t}", CAT, "", admin=True, group_only=True)
    async def handler(update, context):
        _set(update.effective_chat.id, t, on)
        await reply(update, f"{'🔒 Locked' if on else '🔓 Unlocked'}: <b>{t}</b>")


for _t in LOCK_TYPES:
    _mk(_t, True)
    _mk(_t, False)


async def _generic(update, context, on):
    if not context.args or context.args[0].lower() not in LOCK_TYPES:
        return await reply(update, f"Usage: /{'lock' if on else 'unlock'} &lt;type&gt;\nTypes: " + ", ".join(LOCK_TYPES))
    t = context.args[0].lower()
    _set(update.effective_chat.id, t, on)
    await reply(update, f"{'🔒 Locked' if on else '🔓 Unlocked'}: <b>{t}</b>")


@command("lock", CAT, "Lock a message type (non-admins' messages of that type are deleted)",
         admin=True, group_only=True)
async def lock(update, context):
    await _generic(update, context, True)


@command("unlock", CAT, "Unlock a message type", admin=True, group_only=True)
async def unlock(update, context):
    await _generic(update, context, False)


@command("lockall", CAT, "Lock every message type", admin=True, group_only=True)
async def lockall(update, context):
    for t in LOCK_TYPES:
        _set(update.effective_chat.id, t, True)
    await reply(update, "🔒 Everything locked (admins are exempt).")


@command("unlockall", CAT, "Remove all locks", admin=True, group_only=True)
async def unlockall(update, context):
    db.clear(update.effective_chat.id, "lock:")
    await reply(update, "🔓 All locks removed.")


@command("locks", CAT, "Show current locks", group_only=True)
async def locks(update, context):
    on = {k for k, _ in db.items(update.effective_chat.id, "lock:")}
    lines = [f"{'🔒' if t in on else '🔓'} {t}" for t in LOCK_TYPES]
    await reply(update, "<b>Locks</b>\n" + "\n".join(lines))


@command("locktypes", CAT, "List lockable types", aliases=["lockables"])
async def locktypes(update, context):
    await reply(update, "Lockable types:\n" + ", ".join(LOCK_TYPES))
