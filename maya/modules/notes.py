from .. import db
from ..registry import command
from ..utils import esc, raw_args, reply

CAT = "Notes"


def _split(update, context):
    """(name, body) from '/cmd name body...' or a replied message."""
    parts = raw_args(update).split(None, 1)
    if not parts:
        return None, ""
    body = parts[1] if len(parts) > 1 else ""
    r = update.effective_message.reply_to_message
    if not body and r:
        body = r.text or r.caption or ""
    return parts[0].lower(), body


# ---------------------------------------------------------------- notes
@command("save", CAT, "Save a note: /save name text (or reply). Get it with #name or /get",
         admin=True, group_only=True, aliases=["addnote"])
async def save(update, context):
    name, body = _split(update, context)
    if not name or not body:
        return await reply(update, "Usage: /save &lt;name&gt; &lt;text&gt; (or reply to a message)")
    db.put(update.effective_chat.id, f"note:{name}", body)
    await reply(update, f"✅ Saved note <code>{esc(name)}</code>. Use #{esc(name)} or /get {esc(name)}.")


@command("get", CAT, "Show a saved note", group_only=True)
async def get(update, context):
    if not context.args:
        return await reply(update, "Usage: /get &lt;name&gt;")
    note = db.get(update.effective_chat.id, f"note:{context.args[0].lower()}")
    await reply(update, note if note is not None else "No such note.", parse_mode=None)


@command("notes", CAT, "List saved notes", group_only=True, aliases=["saved"])
async def notes(update, context):
    rows = db.items(update.effective_chat.id, "note:")
    await reply(update, ("<b>Notes</b>\n" + "\n".join(f"• #{esc(k)}" for k, _ in rows)) if rows else "No notes saved.")


@command("clear", CAT, "Delete a note", admin=True, group_only=True, aliases=["delnote"])
async def clear(update, context):
    if not context.args:
        return await reply(update, "Usage: /clear &lt;name&gt;")
    ok = db.delete(update.effective_chat.id, f"note:{context.args[0].lower()}")
    await reply(update, "🗑️ Note deleted." if ok else "No such note.")


@command("clearall", CAT, "Delete every note", admin=True, group_only=True)
async def clearall(update, context):
    await reply(update, f"🗑️ Deleted {db.clear(update.effective_chat.id, 'note:')} note(s).")


# -------------------------------------------------------------- filters
@command("filter", CAT, "Auto-reply when a word is said: /filter word reply", admin=True, group_only=True)
async def filter_(update, context):
    word, body = _split(update, context)
    if not word or not body:
        return await reply(update, "Usage: /filter &lt;word&gt; &lt;reply&gt; (or reply to a message)")
    db.put(update.effective_chat.id, f"filter:{word}", body)
    await reply(update, f"✅ Filter added for <code>{esc(word)}</code>.")


@command("stop", CAT, "Remove a filter", admin=True, group_only=True, aliases=["unfilter"])
async def stop(update, context):
    if not context.args:
        return await reply(update, "Usage: /stop &lt;word&gt;")
    ok = db.delete(update.effective_chat.id, f"filter:{context.args[0].lower()}")
    await reply(update, "🗑️ Filter removed." if ok else "No such filter.")


@command("filters", CAT, "List filters", group_only=True)
async def filters_(update, context):
    rows = db.items(update.effective_chat.id, "filter:")
    await reply(update, ("<b>Filters</b>\n" + "\n".join(f"• {esc(k)}" for k, _ in rows)) if rows else "No filters.")


@command("stopall", CAT, "Remove every filter", admin=True, group_only=True)
async def stopall(update, context):
    await reply(update, f"🗑️ Removed {db.clear(update.effective_chat.id, 'filter:')} filter(s).")


# ------------------------------------------------------------ blacklist
@command("addblacklist", CAT, "Delete messages containing a word", admin=True, group_only=True)
async def addblacklist(update, context):
    if not context.args:
        return await reply(update, "Usage: /addblacklist &lt;word&gt;")
    for w in context.args:
        db.put(update.effective_chat.id, f"bl:{w.lower()}", "1")
    await reply(update, f"🚫 Blacklisted {len(context.args)} word(s).")


@command("unblacklist", CAT, "Remove a word from the blacklist", admin=True, group_only=True)
async def unblacklist(update, context):
    if not context.args:
        return await reply(update, "Usage: /unblacklist &lt;word&gt;")
    ok = db.delete(update.effective_chat.id, f"bl:{context.args[0].lower()}")
    await reply(update, "✅ Removed." if ok else "Not blacklisted.")


@command("blacklist", CAT, "Show blacklisted words", admin=True, group_only=True)
async def blacklist(update, context):
    rows = db.items(update.effective_chat.id, "bl:")
    await reply(update, ("<b>Blacklist</b>\n" + ", ".join(esc(k) for k, _ in rows)) if rows else "Blacklist is empty.")


@command("clearblacklist", CAT, "Empty the blacklist", admin=True, group_only=True)
async def clearblacklist(update, context):
    await reply(update, f"🗑️ Removed {db.clear(update.effective_chat.id, 'bl:')} word(s).")
