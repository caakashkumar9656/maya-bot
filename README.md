# Maya 💜 — Telegram group management bot

Maya is an open-source Telegram group manager written in Python with
[python-telegram-bot](https://python-telegram-bot.org). It ships with **690+ commands** across
moderation, warnings, locks, anti-flood, notes, filters, welcome messages, utilities, converters,
text tools, math and games.

## Quick start

```bash
git clone https://github.com/YOUR_USERNAME/maya-bot.git
cd maya-bot
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt tzdata
cp .env.example .env        # then put your BOT_TOKEN (from @BotFather) in .env
python -m maya
```

Then add Maya to your group and **make her an admin** (delete messages, ban users, pin messages,
invite users). In @BotFather you can optionally run `/setprivacy` → *Disable* so she can see all
group messages (needed for locks, filters, notes and anti-flood).

Docker: `docker build -t maya . && docker run -d --env-file .env -v maya-data:/data maya`

## Commands

Send `/help` to see categories, `/help <category>` to list them, `/help <command>` for usage and
`/search <word>` to find one. Check the live total with `/cmdcount` or `python tools/count_commands.py`.

| Category | What it does |
|---|---|
| Moderation | ban / kick / mute in plain, silent (`s`), delete-reply (`d`) and timed (`t`) variants, unban, unmute, purge, del |
| Warnings | warn system with limit and action (ban / kick / mute) |
| Locks | `lock<type>` / `unlock<type>` for 33 message types (url, photo, sticker, forward, …), `lockall` |
| Protection | on/off switches for welcome, goodbye, antiflood, antibot, cleanservice, cleanwelcome, antichannel, reports |
| Admin | promote, demote, title, pin, invitelink, report, group title/description |
| Notes | notes (`#name`), filters (keyword auto-replies), blacklist |
| Welcome | welcome / goodbye templates with placeholders, rules |
| Info | help, search, id, info, chatinfo, ping, uptime |
| Fun | ~70 interaction commands (`/hug`, `/pat`, …), jokes, facts, truth/dare, `/how<trait>` meters |
| Text | 69 tools: case, encodings, hashes, fancy fonts, morse, case converters |
| Math | `/calc` plus ~70 helpers (primes, roman numerals, EMI, BMI, percentages…) |
| Converters | every unit pair as `/<from>2<to>` (e.g. `/km2mi 42`), temperature, `/convert` |
| Random / Time / Games | dice, passwords, UUIDs, 30+ timezone shortcuts, countdowns, RPS, Telegram dice games |

Most moderation commands work by **replying** to a user (or passing a numeric user id).
Telegram only lets bots show 100 commands in the menu; Maya registers a curated set there and every
other command still works when typed.

## Adding your own command

```python
# maya/modules/mine.py  (then add `mine` to maya/modules/__init__.py)
from ..registry import command
from ..utils import reply

@command("hello", "Fun", "Say hello", admin=False, group_only=False, aliases=["hi"])
async def hello(update, context):
    await reply(update, "Hello from Maya!")
```

## Development

```bash
python tests/test_pure.py        # logic checks (calculator, converters, encoders…)
python tools/count_commands.py   # prints per-category counts, fails if < 500
```

GitHub Actions (`.github/workflows/ci.yml`) runs these on every push.

## Notes

- Settings are stored per chat in a local SQLite file (`DB_PATH`).
- Admin-only commands check the sender's Telegram admin status on every call.
- Usernames can't be resolved by bots: target users by reply or numeric id.

## License

MIT
