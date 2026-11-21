import random

from ..registry import command
from ..utils import reply

CAT = "Games"


def _mk_dice(name, emoji, desc):
    @command(name, CAT, desc)
    async def handler(update, context):
        await update.effective_message.reply_dice(emoji=emoji)


_mk_dice("dice", "🎲", "Roll a Telegram dice")
_mk_dice("dart", "🎯", "Throw a dart")
_mk_dice("basket", "🏀", "Shoot a basketball")
_mk_dice("football", "⚽", "Kick a football")
_mk_dice("bowling", "🎳", "Roll a bowling ball")
_mk_dice("slot", "🎰", "Spin the slot machine")


@command("rps", CAT, "Rock paper scissors: /rps rock")
async def rps(update, context):
    opts = ("rock", "paper", "scissors")
    mine = context.args[0].lower() if context.args else ""
    if mine not in opts:
        return await reply(update, "Usage: /rps &lt;rock|paper|scissors&gt;")
    bot = random.choice(opts)
    wins = {("rock", "scissors"), ("paper", "rock"), ("scissors", "paper")}
    result = "🤝 Draw!" if mine == bot else "🎉 You win!" if (mine, bot) in wins else "😎 I win!"
    await reply(update, f"You: {mine} · Maya: {bot}\n{result}", parse_mode=None)


@command("guess", CAT, "Guess my number from 1-10: /guess 7")
async def guess(update, context):
    if not context.args or not context.args[0].isdigit():
        return await reply(update, "Usage: /guess &lt;1-10&gt;")
    n = random.randint(1, 10)
    await reply(update, "🎉 Correct!" if int(context.args[0]) == n else f"❌ Nope, it was {n}.", parse_mode=None)
