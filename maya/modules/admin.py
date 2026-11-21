from ..registry import command
from ..utils import esc, get_target, is_admin_id, reply
from .protection import feature

CAT = "Admin"

BASIC = dict(can_delete_messages=True, can_restrict_members=True, can_pin_messages=True,
             can_invite_users=True, can_manage_video_chats=True)
LOW = dict(can_pin_messages=True, can_invite_users=True)
FULL_RIGHTS = dict(BASIC, can_change_info=True, can_promote_members=True)
NONE = dict(can_delete_messages=False, can_restrict_members=False, can_pin_messages=False,
            can_invite_users=False, can_manage_video_chats=False, can_change_info=False,
            can_promote_members=False)


async def _promote(update, context, rights, label):
    uid, who, _ = await get_target(update, context)
    if not uid:
        return await reply(update, "Reply to a user or give a numeric id.")
    await context.bot.promote_chat_member(update.effective_chat.id, uid, **rights)
    await reply(update, f"{label} {who}.")


@command("promote", CAT, "Give a user standard admin rights", admin=True, group_only=True)
async def promote(update, context):
    await _promote(update, context, BASIC, "⬆️ Promoted")


@command("lowpromote", CAT, "Give a user minimal admin rights (pin, invite)", admin=True, group_only=True)
async def lowpromote(update, context):
    await _promote(update, context, LOW, "⬆️ Promoted (low rights)")


@command("fullpromote", CAT, "Give a user full admin rights", admin=True, group_only=True)
async def fullpromote(update, context):
    await _promote(update, context, FULL_RIGHTS, "⬆️ Promoted (full rights)")


@command("demote", CAT, "Remove a user's admin rights", admin=True, group_only=True)
async def demote(update, context):
    await _promote(update, context, NONE, "⬇️ Demoted")


@command("title", CAT, "Set an admin's custom title (reply + title)", admin=True, group_only=True)
async def title(update, context):
    uid, who, rest = await get_target(update, context)
    if not uid or not rest:
        return await reply(update, "Usage: /title &lt;text&gt; (reply to an admin)")
    await context.bot.set_chat_administrator_custom_title(update.effective_chat.id, uid, " ".join(rest)[:16])
    await reply(update, f"✅ Title set for {who}.")


@command("admins", CAT, "List the group's admins", group_only=True, aliases=["adminlist", "staff"])
async def admins(update, context):
    lst = await context.bot.get_chat_administrators(update.effective_chat.id)
    lines = [f"{'👑' if a.status == 'creator' else '🛡️'} {esc(a.user.full_name)}" for a in lst if not a.user.is_bot]
    await reply(update, "<b>Admins</b>\n" + "\n".join(lines))


@command("pin", CAT, "Pin the replied message (add 'loud' to notify)", admin=True, group_only=True)
async def pin(update, context):
    r = update.effective_message.reply_to_message
    if not r:
        return await reply(update, "Reply to the message you want to pin.")
    loud = bool(context.args) and context.args[0].lower() == "loud"
    await context.bot.pin_chat_message(update.effective_chat.id, r.message_id, disable_notification=not loud)


@command("unpin", CAT, "Unpin the replied message (or the latest pin)", admin=True, group_only=True)
async def unpin(update, context):
    r = update.effective_message.reply_to_message
    await context.bot.unpin_chat_message(update.effective_chat.id, message_id=r.message_id if r else None)
    await reply(update, "📌 Unpinned.")


@command("unpinall", CAT, "Unpin every message", admin=True, group_only=True)
async def unpinall(update, context):
    await context.bot.unpin_all_chat_messages(update.effective_chat.id)
    await reply(update, "📌 All messages unpinned.")


@command("setgtitle", CAT, "Change the group title", admin=True, group_only=True)
async def setgtitle(update, context):
    if not context.args:
        return await reply(update, "Usage: /setgtitle &lt;new title&gt;")
    await context.bot.set_chat_title(update.effective_chat.id, " ".join(context.args)[:128])


@command("setgdesc", CAT, "Change the group description", admin=True, group_only=True)
async def setgdesc(update, context):
    await context.bot.set_chat_description(update.effective_chat.id, " ".join(context.args)[:255])
    await reply(update, "✅ Description updated.")


@command("invitelink", CAT, "Get the group's invite link", admin=True, group_only=True)
async def invitelink(update, context):
    await reply(update, await context.bot.export_chat_invite_link(update.effective_chat.id), parse_mode=None)


@command("report", CAT, "Report the replied message to the admins", group_only=True)
async def report(update, context):
    chat, msg = update.effective_chat, update.effective_message
    if not feature(chat.id, "reports"):
        return await reply(update, "Reports are disabled here.")
    if not msg.reply_to_message:
        return await reply(update, "Reply to the message you want to report.")
    if await is_admin_id(context, chat.id, msg.reply_to_message.from_user.id):
        return await reply(update, "You can't report admins.")
    lst = await context.bot.get_chat_administrators(chat.id)
    pings = "".join(f'<a href="tg://user?id={a.user.id}">​</a>' for a in lst if not a.user.is_bot)
    await reply(update, f"🚨 Reported to the admins.{pings}")


@command("members", CAT, "Show the member count", group_only=True, aliases=["membercount"])
async def members(update, context):
    n = await context.bot.get_chat_member_count(update.effective_chat.id)
    await reply(update, f"👥 Members: <b>{n}</b>")


@command("leave", CAT, "Make the bot leave this group (bot owner only)", sudo=True, group_only=True)
async def leave(update, context):
    await reply(update, "👋 Goodbye!")
    await context.bot.leave_chat(update.effective_chat.id)
