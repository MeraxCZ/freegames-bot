import discord
from discord.ext import commands, tasks
import requests
from datetime import datetime

TOKEN = "PASTE_DISCORD_BOT_TOKEN"
CHANNEL_ID = 1463811139946414163

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

def get_epic_free():
    url = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"
    data = requests.get(url).json()
    games = []

    for game in data["data"]["Catalog"]["searchStore"]["elements"]:
        promos = game.get("promotions")
        if promos and promos.get("promotionalOffers"):
            games.append(game["title"])

    return games

def get_steam_free():
    url = "https://www.reddit.com/r/FreeGamesOnSteam/new.json?limit=5"
    headers = {"User-Agent": "Mozilla/5.0"}
    data = requests.get(url, headers=headers).json()
    games = []

    for post in data["data"]["children"]:
        title = post["data"]["title"]
        if "Free" in title:
            games.append(title)

    return games

@tasks.loop(hours=24)
async def daily_check():
    channel = bot.get_channel(CHANNEL_ID)

    epic = get_epic_free()
    steam = get_steam_free()

    if not epic and not steam:
        return

    embed = discord.Embed(
        title="🎮 Hry zdarma právě teď!",
        color=0x00ff00,
        timestamp=datetime.utcnow()
    )

    if epic:
        embed.add_field(name="Epic Games", value="\n".join(epic), inline=False)
    if steam:
        embed.add_field(name="Steam", value="\n".join(steam), inline=False)

    await channel.send(embed=embed)

@bot.event
async def on_ready():
    print(f"Přihlášen jako {bot.user}")
    daily_check.start()

bot.run(TOKEN)
