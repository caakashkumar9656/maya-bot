from datetime import datetime, timedelta, timezone

from telegram import ChatPermissions

from ..registry import command
from ..utils import esc, get_target, is_admin_id, parse_duration, reply

CAT = "Moderation"
MUTED = ChatPermissions(can_send_messages=False)
FULL = ChatPermissions(
    can_send_messages=True, can_send_audios=True, can_send_documents=True,
    can_send_photos=True, can_send_videos=True, can_send_video_notes=True,
    can_send_voice_notes=True, can_send_polls=True, can_send_other_messages=True,
    can_add_web_page_previews=True, can_invite_users=True,
)


async def apply_action(context, chat_id, kind, uid, until=None):
    bot = context.bot
    if kind == "ban":
        await bot.ban_chat_member(chat_id, uid, until_date=until)
    elif kind == "kick":
        await bot.ban_chat_member(chat_id, uid)
        await bot.unban_chat_member(chat_id, uid, only_if_banned=True)
    elif kind == "mute":
        await bot.restrict_chat_member(chat_id, uid, MUTED, until_date=until)
    else:
        raise ValueError(f"unknown action {kind}")


async def prep(update, context, check_admin=True):
    uid, who, rest = await get_target(update, context)
    if not uid:
        await reply(update, "Reply to a user's message, or give a numeric user id.")
        return None
    if uid == context.bot.id:
        await reply(update, "I'm not going to do that to myself 😅")
        return None
    if check_admin and await is_admin_id(context, update.effective_chat.id, uid):
        await reply(update, "I don't take action against admins.")
        return None
    return uid, who, rest


def _make(cmd, kind, past, icon, silent=False, delete=False, timed=False):
    desc = f"{kind.title()} a user"
    if timed:
        desc += " for a duration (10m, 2h, 1d)"
    if delete:
        desc += " and delete the replied message"
    if silent:
        desc += " silently (removes the command)"

    @command(cmd, CAT, desc, admin=True, group_only=True)
    async def handler(update, context):
        r = await prep(update, context)
        if not r:
            return
        uid, who, rest = r
        chat, msg = update.effective_chat, update.effective_message
        until = None
        if timed:
            secs = parse_duration(rest[0]) if rest else None
            if not secs:
                return await reply(update, f"Usage: /{cmd} &lt;10m|2h|1d&gt; [reason] (reply to a user)")
            until = datetime.now(timezone.utc) + timedelta(seconds=secs)
            duration = rest[0]
            rest = rest[1:]
        if delete and msg.reply_to_message:
            try:
                await msg.reply_to_message.delete()
            except Exception:
                pass
        await apply_action(context, chat.id, kind, uid, until)
        if silent:
            try:
                await msg.delete()
            except Exception:
                pass
            return
        reason = " ".join(rest)
        text = f"{icon} {who} was {past}."
        if timed:
            text += f" (for {esc(duration)})"
        if reason:
            text += f"\nReason: {esc(reason)}"
        await reply(update, text)

    return handler


for _kind, _past, _icon in (("ban", "banned", "🔨"), ("kick", "kicked", "👢"), ("mute", "muted", "🔇")):
    _make(_kind, _kind, _past, _icon)
    _make("s" + _kind, _kind, _past, _icon, silent=True)
    _make("d" + _kind, _kind, _past, _icon, delete=True)
    if _kind != "kick":
        _make("t" + _kind, _kind, _past, _icon, timed=True)


@command("unban", CAT, "Unban a user", admin=True, group_only=True)
async def unban(update, context):
    r = await prep(update, context, check_admin=False)
    if r:
        await context.bot.unban_chat_member(update.effective_chat.id, r[0], only_if_banned=True)
        await reply(update, f"✅ {r[1]} was unbanned.")


@command("unmute", CAT, "Unmute a user", admin=True, group_only=True)
async def unmute(update, context):
    r = await prep(update, context, check_admin=False)
    if r:
        await context.bot.restrict_chat_member(update.effective_chat.id, r[0], FULL)
        await reply(update, f"🔊 {r[1]} was unmuted.")


@command("kickme", CAT, "Leave the group (you can rejoin)", group_only=True)
async def kickme(update, context):
    user, chat = update.effective_user, update.effective_chat
    if await is_admin_id(context, chat.id, user.id):
        return await reply(update, "Admins can't use this one.")
    await apply_action(context, chat.id, "kick", user.id)
    await reply(update, f"👋 {user.mention_html()} left the group.")


@command("del", CAT, "Delete the replied message", admin=True, group_only=True, aliases=["delete"])
async def del_(update, context):
    msg = update.effective_message
    if not msg.reply_to_message:
        return await reply(update, "Reply to the message you want to delete.")
    await msg.reply_to_message.delete()
    await msg.delete()


@command("purge", CAT, "Delete every message from the replied one to now", admin=True, group_only=True)
async def purge(update, context):
    msg, chat = update.effective_message, update.effective_chat
    if not msg.reply_to_message:
        return await reply(update, "Reply to the first message you want to purge.")
    ids = list(range(msg.reply_to_message.message_id, msg.message_id + 1))[-1000:]
    for i in range(0, len(ids), 100):
        try:
            await context.bot.delete_messages(chat.id, ids[i:i + 100])
        except Exception:
            pass
    await context.bot.send_message(chat.id, f"🧹 Purged up to {len(ids)} messages.")
