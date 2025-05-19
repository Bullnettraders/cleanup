import os
import asyncio
import discord
from discord.ext import tasks, commands
import datetime
from dotenv import load_dotenv

# .env laden (lokal), in Railway werden diese als Umgebungsvariablen gesetzt
load_dotenv()

# Bot-Token und Channel-IDs aus Environment
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_IDS = [int(id.strip()) for id in os.getenv("TARGET_CHANNEL_ID").split(",")]

# Discord Intents
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

# Bot-Instanz
bot = commands.Bot(command_prefix="!", intents=intents)

# Starte den Cleanup-Task, wenn der Bot bereit ist
@bot.event
async def on_ready():
    print(f"✅ Bot ist eingeloggt als {bot.user}")
    cleanup_old_messages.start()

# Cleanup-Task: läuft alle 24 Stunden
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
                        await asyncio.sleep(0.5)  # Rate Limit beachten
                        deleted += 1
                    except discord.Forbidden:
                        print(f"🚫 Keine Berechtigung zum Löschen in {channel.name}.")
                    except discord.HTTPException as e:
                        print(f"❌ Fehler beim Löschen: {e}")
        except Exception as e:
            print(f"❌ Fehler beim Zugriff auf Channel {channel.name}: {e}")

        print(f"✅ {deleted} alte Nachrichten gelöscht in {channel.name}")

# Bot starten
bot.run(TOKEN)
