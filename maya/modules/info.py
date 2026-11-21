import time

from ..config import BOT_NAME, REPO_URL
from ..registry import COMMANDS, LOOKUP, command
from ..utils import esc, get_target, is_admin_id, reply

CAT = "Info"
START = time.time()
ORDER = ["Moderation", "Warnings", "Locks", "Protection", "Admin", "Notes", "Welcome", "Info",
         "Fun", "Text", "Math", "Converters", "Random", "Time", "Games"]


def _by_cat():
    d = {}
    for c in COMMANDS.values():
        d.setdefault(c.category, []).append(c)
    return d


@command("start", CAT, "Say hello to Maya")
async def start(update, context):
    await reply(update,
                f"👋 Hi {update.effective_user.mention_html()}, I'm <b>{BOT_NAME}</b>, a group management bot "
                f"with <b>{len(COMMANDS)}</b> commands.\n\nAdd me to a group, make me admin, then try /help.")


@command("maya", CAT, "Greet Maya")
async def maya(update, context):
    await reply(update, f"💜 {BOT_NAME} here — {len(COMMANDS)} commands at your service. /help")


@command("help", CAT, "Show commands: /help, /help <category>, /help <command>", aliases=["h"])
async def help_(update, context):
    cats = _by_cat()
    names = ORDER + [c for c in cats if c not in ORDER]
    if not context.args:
        lines = [f"📖 <b>{BOT_NAME}</b> — {len(COMMANDS)} commands in {len(cats)} categories", ""]
        lines += [f"• <b>{c}</b> ({len(cats[c])}) — /help {c.lower()}" for c in names if c in cats]
        lines += ["", "Tip: /help &lt;command&gt; for usage, /search &lt;word&gt; to find a command."]
        return await reply(update, "\n".join(lines))
    q = context.args[0].lower().lstrip("/")
    cat = next((c for c in cats if c.lower() == q), None)
    if cat:
        cmds = sorted(cats[cat], key=lambda c: c.name)
        described = [c for c in cmds if c.help]
        plain = [c for c in cmds if not c.help]
        lines = [f"<b>{cat}</b> ({len(cmds)})"] + [f"/{c.name} — {esc(c.help)}" for c in described]
        if plain:
            lines += ["", " ".join(f"/{c.name}" for c in plain)]
        return await reply(update, "\n".join(lines))
    cmd = LOOKUP.get(q)
    if not cmd:
        return await reply(update, "No such category or command. Try /search &lt;word&gt;.")
    extra = f"\nAliases: {', '.join('/' + a for a in cmd.aliases)}" if cmd.aliases else ""
    flags = " (admins only)" if cmd.admin else ""
    await reply(update, f"/{cmd.name}{flags} — {esc(cmd.help or 'no description')}\nCategory: {cmd.category}{extra}")


@command("commands", CAT, "Show command counts per category")
async def commands(update, context):
    cats = _by_cat()
    await reply(update, "\n".join(f"{c}: {len(cats[c])}" for c in ORDER if c in cats) + f"\n<b>Total: {len(COMMANDS)}</b>")


@command("cmdcount", CAT, "Show the total number of commands")
async def cmdcount(update, context):
    await reply(update, f"{BOT_NAME} has <b>{len(COMMANDS)}</b> commands ({len(LOOKUP)} names including aliases).")


@command("search", CAT, "Search commands by name or description")
async def search(update, context):
    if not context.args:
        return await reply(update, "Usage: /search &lt;word&gt;")
    q = context.args[0].lower()
    hits = [c for c in COMMANDS.values() if q in c.name or q in c.help.lower()][:60]
    await reply(update, "\n".join(f"/{c.name} — {esc(c.help or c.category)}" for c in hits) if hits else "Nothing found.")


@command("ping", CAT, "Check that Maya is alive")
async def ping(update, context):
    t0 = time.perf_counter()
    msg = await reply(update, "🏓 Pong!")
    await msg.edit_text(f"🏓 Pong! {(time.perf_counter() - t0) * 1000:.0f} ms")


@command("uptime", CAT, "How long Maya has been running")
async def uptime(update, context):
    s = int(time.time() - START)
    await reply(update, f"⏱️ Uptime: {s // 86400}d {s % 86400 // 3600}h {s % 3600 // 60}m {s % 60}s")


@command("id", CAT, "Show your id, the chat id and the replied user's id", aliases=["myid", "chatid"])
async def id_(update, context):
    u, c, r = update.effective_user, update.effective_chat, update.effective_message.reply_to_message
    lines = [f"👤 You: <code>{u.id}</code>", f"💬 Chat: <code>{c.id}</code>"]
    if r and r.from_user:
        lines.append(f"↩️ Replied user: <code>{r.from_user.id}</code>")
    await reply(update, "\n".join(lines))


@command("info", CAT, "Show info about a user (reply, id, or yourself)", aliases=["whois"])
async def info(update, context):
    uid, who, _ = await get_target(update, context)
    user = update.effective_message.reply_to_message.from_user if (
        update.effective_message.reply_to_message and update.effective_message.reply_to_message.from_user
    ) else update.effective_user
    if uid and uid != user.id:
        return await reply(update, f"User id: <code>{uid}</code>")
    lines = [f"👤 <b>{esc(user.full_name)}</b>", f"ID: <code>{user.id}</code>"]
    if user.username:
        lines.append(f"Username: @{esc(user.username)}")
    if update.effective_chat.type != "private":
        lines.append(f"Admin: {'yes' if await is_admin_id(context, update.effective_chat.id, user.id) else 'no'}")
    await reply(update, "\n".join(lines))


@command("chatinfo", CAT, "Show info about this chat", aliases=["groupinfo"])
async def chatinfo(update, context):
    c = update.effective_chat
    lines = [f"💬 <b>{esc(c.title or c.full_name)}</b>", f"ID: <code>{c.id}</code>", f"Type: {c.type}"]
    if c.type != "private":
        lines.append(f"Members: {await context.bot.get_chat_member_count(c.id)}")
    await reply(update, "\n".join(lines))


@command("botinfo", CAT, "Show bot details")
async def botinfo(update, context):
    me = context.bot
    await reply(update, f"🤖 <b>{BOT_NAME}</b> (@{esc(me.username)})\nCommands: {len(COMMANDS)}")


@command("about", CAT, "About Maya")
async def about(update, context):
    await reply(update, f"💜 <b>{BOT_NAME}</b> — an open-source Telegram group management bot.\nSource: {esc(REPO_URL)}")


@command("source", CAT, "Link to the source code")
async def source(update, context):
    await reply(update, esc(REPO_URL))


@command("privacy", CAT, "What data Maya stores")
async def privacy(update, context):
    await reply(update, "Maya stores only per-chat settings (notes, filters, warns, locks, rules) in its own database. "
                        "It does not log your messages.")
