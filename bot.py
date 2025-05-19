import os
import discord
from discord.ext import tasks, commands
import datetime
from dotenv import load_dotenv

# Lade Umgebungsvariablen aus .env (für lokale Tests)
load_dotenv()

# Discord-Bot Token und Channel-IDs laden
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_IDS = [int(id.strip()) for id in os.getenv("TARGET_CHANNEL_ID").split(",")]

# Intents aktivieren
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

# Bot erstellen
bot = commands.Bot(command_prefix="!", intents=intents)

# Wenn der Bot bereit ist, starte den Cleanup-Task
@bot.event
async def on_ready():
    print(f"✅ Bot ist eingeloggt als {bot.user}")
    cleanup_old_messages.start()

# Wiederkehrender Task: läuft alle 24 Stunden
@tasks.loop(hours=24)
async def cleanup_old_messages():
    await bot.wait_until_ready()
    now = datetime.datetime.now(datetime.UTC)
    cutoff = now - datetime.timedelta(weeks=4)

    for channel_id in CHANNEL_IDS:
        channel = bot.get_channel(channel_id)
        if not channel:
            print(f"⚠️ Channel mit ID {channel_id} nicht gefunden.")
            continue

        print(f"🧹 Starte Cleanup für Channel: {channel.name}")
        deleted = 0

        try:
            async for message in channel.history(limit=None, oldest_first=True):
                if message.created_at < cutoff:
                    try:
                        await message.delete()
                        deleted += 1
                    except discord.Forbidden:
                        print(f"🚫 Keine Berechtigung zum Löschen in {channel.name}.")
                    except discord.HTTPException as e:
                        print(f"❌ Fehler beim Löschen: {e}")
        except Exception as e:
            print(f"❌ Fehler beim Zugriff auf Channel {channel.name}: {e}")

        print(f"✅ {deleted} alte Nachrichten gelöscht in {channel.name}")

# Starte den Bot
bot.run(TOKEN)
