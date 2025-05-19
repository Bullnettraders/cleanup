import os
import discord
from discord.ext import tasks, commands
import datetime
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("TARGET_CHANNEL_ID"))

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot ist eingeloggt als {bot.user}")
    cleanup_old_messages.start()

@tasks.loop(hours=24)
async def cleanup_old_messages():
    await bot.wait_until_ready()

    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print("⚠️ Channel nicht gefunden.")
        return

    print(f"🧹 Starte Cleanup für Channel: {channel.name}")
    now = datetime.datetime.utcnow()
    cutoff = now - datetime.timedelta(weeks=4)
    deleted = 0

    async for message in channel.history(limit=None, oldest_first=True):
        if message.created_at < cutoff:
            try:
                await message.delete()
                deleted += 1
            except Exception as e:
                print(f"❌ Fehler beim Löschen: {e}")
    print(f"✅ {deleted} alte Nachrichten gelöscht.")

bot.run(TOKEN)
