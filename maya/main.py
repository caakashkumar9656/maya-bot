import logging
import time

from telegram import BotCommand, Update
from telegram.ext import Application, MessageHandler, filters

from .config import BOT_TOKEN
from .registry import LOOKUP
from . import modules  # noqa: F401  (importing registers every command)
from .modules.watcher import on_left_member, on_new_members, watcher
from .utils import esc, is_admin, is_sudo, reply

logging.basicConfig(format="%(asctime)s %(levelname)s %(name)s: %(message)s", level=logging.INFO)
log = logging.getLogger("maya")

START_TIME = time.time()

MENU = ["start", "help", "rules", "ban", "unban", "kick", "mute", "unmute", "tmute", "warn",
        "warns", "lock", "unlock", "locks", "purge", "pin", "admins", "info", "id", "save",
        "get", "notes", "filter", "filters", "welcomeon", "welcomeoff", "setwelcome",
        "setrules", "report", "calc", "time", "search", "commands", "ping"]


async def dispatch(update, context):
    """Single entry point for all commands (fast dict lookup instead of 500+ handlers)."""
    m = update.message  # ignore edited messages
    if not m or not m.text or not m.text.startswith("/"):
        return
    first, *args = m.text.split()
    name, _, target = first[1:].partition("@")
    if target and target.lower() != (context.bot.username or "").lower():
        return
    cmd = LOOKUP.get(name.lower())
    if not cmd:
        return
    user, chat = update.effective_user, update.effective_chat
    if cmd.group_only and chat.type == "private":
        return await reply(update, "This command only works in groups.")
    if cmd.sudo and not (user and is_sudo(user.id)):
        return await reply(update, "🚫 Only the bot owner can use this.")
    if cmd.admin and not await is_admin(update, context):
        return await reply(update, "🚫 Admins only.")
    context.args = args
    try:
        await cmd.func(update, context)
    except Exception as e:  # report Telegram/permission errors to the chat
        log.warning("/%s failed: %s", cmd.name, e)
        await reply(update, f"⚠️ {esc(e)}")


async def post_init(app):
    cmds = [BotCommand(n, (LOOKUP[n].help or f"{n} command")[:200].ljust(3))
            for n in MENU if n in LOOKUP]
    try:
        await app.bot.set_my_commands(cmds)
    except Exception as e:
        log.warning("could not set command menu: %s", e)


def main():
    if not BOT_TOKEN:
        raise SystemExit("BOT_TOKEN is missing. Copy .env.example to .env and fill it in.")
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    app.add_handler(MessageHandler(filters.COMMAND, dispatch), group=0)
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, on_new_members), group=1)
    app.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, on_left_member), group=1)
    app.add_handler(MessageHandler(filters.ChatType.GROUPS & ~filters.StatusUpdate.ALL, watcher), group=2)
    log.info("Maya started with %d commands", len({c.name for c in LOOKUP.values()}))
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
