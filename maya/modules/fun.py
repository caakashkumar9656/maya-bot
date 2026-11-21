import hashlib
import random

from ..registry import command
from ..utils import esc, get_target, raw_args, reply

CAT = "Fun"

# name|emoji|phrase  -> "<emoji> <you> <phrase> <target>"
VERBS = """hug|🤗|hugs
pat|👋|pats
slap|🖐️|slaps
kiss|😘|kisses
poke|👉|pokes
tickle|🪶|tickles
cuddle|🥰|cuddles
bite|😬|bites
punch|👊|punches
highfive|🙌|high-fives
wave|👋|waves at
wink|😉|winks at
boop|👃|boops
bonk|🔨|bonks
squeeze|🤏|squeezes
nuzzle|🐾|nuzzles
lick|👅|licks
yeet|🚀|yeets
throw|🎯|throws something at
toss|🪃|tosses
tackle|🏈|tackles
shove|🫸|shoves
nudge|🫷|nudges
salute|🫡|salutes
bow|🙇|bows to
clap|👏|claps for
cheer|📣|cheers for
thank|🙏|thanks
praise|🌟|praises
congratulate|🎉|congratulates
applaud|👏|applauds
serenade|🎻|serenades
tease|😜|teases
feed|🍪|feeds
carry|💪|carries
tuck|🛏️|tucks in
protect|🛡️|protects
guard|⚔️|guards
rescue|🚒|rescues
adopt|🐶|adopts
hire|💼|hires
fire|🔥|fires
ignore|🙈|ignores
glare|😠|glares at
stare|👀|stares at
facepalm|🤦|facepalms at
shrug|🤷|shrugs at
dance|💃|dances with
sing|🎤|sings to
hum|🎵|hums for
cook|🍳|cooks for
bake|🧁|bakes for
serve|🍽️|serves
gift|🎁|gifts
dub|⚜️|dubs
knight|🗡️|knights
crown|👑|crowns
banish|🌌|banishes
summon|🔮|summons
challenge|⚡|challenges
duel|🤺|duels
race|🏁|races
outsmart|🧠|outsmarts
trip|🍌|trips
tag|🏷️|tags
scare|👻|scares
spook|🎃|spooks
haunt|🕯️|haunts
annoy|🦟|annoys
bother|🔔|bothers
miss|💔|misses
trust|🤝|trusts"""


def _target_name(update):
    uid_user = None
    r = update.effective_message.reply_to_message
    if r and r.from_user:
        uid_user = r.from_user.mention_html()
    return uid_user


def _mk_verb(name, icon, phrase):
    @command(name, CAT)
    async def handler(update, context):
        actor = update.effective_user.mention_html()
        target = _target_name(update) or (esc(" ".join(context.args)) if context.args else "themselves")
        await reply(update, f"{icon} {actor} {phrase} {target}")


for _line in VERBS.splitlines():
    _n, _i, _p = _line.split("|")
    _mk_verb(_n, _i, _p)

PICKS = {
    "8ball": ("Yes.", "No.", "Maybe...", "Ask again later.", "Definitely!", "Very doubtful.",
              "Signs point to yes.", "Don't count on it."),
    "joke": ("Why do programmers prefer dark mode? Because light attracts bugs.",
             "I told my computer I needed a break. Now it won't stop sending me Kit-Kat ads.",
             "Why was the math book sad? It had too many problems.",
             "I would tell you a UDP joke, but you might not get it.",
             "Why did the scarecrow win an award? He was outstanding in his field."),
    "fact": ("Honey never spoils; edible honey has been found in ancient tombs.",
             "Octopuses have three hearts.", "A day on Venus is longer than its year.",
             "Bananas are berries, but strawberries are not.", "Sharks are older than trees."),
    "quote": ("Small steps every day add up to big changes.", "Done is better than perfect.",
              "You don't have to be great to start, but you have to start to be great.",
              "Be kind; everyone is fighting a battle you can't see.",
              "Progress, not perfection."),
    "truth": ("What's the most embarrassing thing you've done online?", "What's a skill you pretend to have?",
              "What's your most useless talent?", "Who was your first celebrity crush?",
              "What's the last lie you told?"),
    "dare": ("Send the last emoji you used five times in a row.", "Change your profile photo to a potato for an hour.",
             "Speak only in questions for the next 10 minutes.", "Post a voice note singing your favourite song.",
             "Compliment every person in this chat."),
    "wyr": ("Would you rather always be 10 minutes late or 20 minutes early?",
            "Would you rather fly or be invisible?", "Would you rather lose your phone or your wallet?",
            "Would you rather have unlimited pizza or unlimited tacos?"),
    "compliment": ("You make this chat better.", "Your ideas are genuinely great.", "You have excellent taste.",
                   "You light up the room.", "You're doing better than you think."),
    "roast": ("You're the human equivalent of a participation trophy. (love you though)",
              "If you were a spice you'd be flour.", "You bring everyone together — to wonder what you meant.",
              "Your Wi-Fi password is probably 'password'.", "You'd lose a staring contest to a potato."),
    "pickup": ("Are you a keyboard? Because you're just my type.", "Are you Wi-Fi? I'm feeling a connection.",
               "Do you have a map? I keep getting lost in your messages.",
               "Is your name Google? Because you have everything I'm searching for."),
    "advice": ("Drink some water.", "Sleep on it.", "Back up your files.", "Take a short walk.",
               "Ask for help early."),
    "fortune": ("A pleasant surprise is waiting for you.", "Good news will arrive soon.",
                "Today is a good day to start something new.", "An old friend will reach out.",
                "Luck follows the curious."),
    "riddle": ("What has keys but can't open locks? — A piano.", "What gets wetter the more it dries? — A towel.",
               "What has a head and a tail but no body? — A coin."),
    "twister": ("She sells seashells by the seashore.", "Peter Piper picked a peck of pickled peppers.",
                "How much wood would a woodchuck chuck if a woodchuck could chuck wood?"),
    "proverb": ("A stitch in time saves nine.", "Actions speak louder than words.",
                "Don't count your chickens before they hatch.", "Better late than never.",
                "Rome wasn't built in a day."),
    "motivate": ("You've survived every bad day so far.", "Start where you are.", "One more try.",
                 "Your future self will thank you.", "Keep going — you're closer than you think."),
    "protip": ("Use the two-minute rule: if it takes two minutes, do it now.", "Plan tomorrow before you finish today.",
            "Turn off notifications while you focus.", "Work in 25-minute blocks.", "Write it down; don't memorise it."),
    "shower": ("Every ocean is connected, yet we name them separately.", "Your age is just a number you update yearly.",
               "Nobody has ever seen their own face without a mirror or camera.",
               "Passwords are just tiny secrets we forget."),
    "excuse": ("My cat unplugged the router.", "I was stuck in a very important meeting with my bed.",
               "The dog ate my homework — and my laptop.", "My alarm was on strike.", "I'm on airplane mode, in spirit."),
    "whateat": ("Pizza 🍕", "Biryani 🍛", "Sushi 🍣", "Tacos 🌮", "Pasta 🍝", "Burger 🍔", "Salad 🥗", "Dosa 🥞"),
    "movie": ("A comedy tonight.", "A thriller.", "An animated classic.", "A sci-fi epic.", "A feel-good drama.",
              "A documentary."),
    "activity": ("Go for a walk.", "Call a friend.", "Cook something new.", "Read 20 pages.", "Tidy one drawer.",
                 "Learn a new song."),
    "animal": ("🐶 Dog", "🐱 Cat", "🦊 Fox", "🐼 Panda", "🐧 Penguin", "🦉 Owl", "🐙 Octopus"),
    "color": ("Red", "Orange", "Yellow", "Green", "Blue", "Indigo", "Violet", "Teal", "Magenta"),
    "emoji": ("😀", "😎", "🤖", "🌈", "🔥", "🍀", "🎲", "🚀", "🧠", "🦄"),
}


def _mk_pick(name, items):
    @command(name, CAT)
    async def handler(update, context):
        await reply(update, random.choice(items), parse_mode=None)


for _name, _items in PICKS.items():
    _mk_pick(_name, _items)

METERS = ("cool", "smart", "lucky", "brave", "funny", "kind", "lazy", "nerdy", "sus", "vibes", "pro", "chill")


def _pct(text, salt):
    return int(hashlib.sha256(f"{salt}:{text.lower()}".encode()).hexdigest(), 16) % 101


def _subject(update, context):
    r = update.effective_message.reply_to_message
    if r and r.from_user and not context.args:
        return r.from_user.full_name
    return " ".join(context.args) if context.args else update.effective_user.full_name


def _mk_meter(m):
    @command(f"how{m}", CAT)
    async def handler(update, context):
        who = _subject(update, context)
        await reply(update, f"📊 {esc(who)} is {_pct(who, m)}% {m}.")


for _m in METERS:
    _mk_meter(_m)


@command("ship", CAT, "Compatibility of two names: /ship a b")
async def ship(update, context):
    if len(context.args) < 2:
        return await reply(update, "Usage: /ship &lt;name1&gt; &lt;name2&gt;")
    a, b = sorted(x.lower() for x in context.args[:2])
    await reply(update, f"💘 {esc(context.args[0])} + {esc(context.args[1])} = {_pct(a + b, 'ship')}% match")


@command("rate", CAT, "Rate something out of 10")
async def rate(update, context):
    what = raw_args(update) or "that"
    await reply(update, f"⭐ I rate {esc(what)} a {_pct(what, 'rate') // 10}/10.")
