import discord
from discord.ext import commands, tasks
import requests
from datetime import datetime, timezone
import asyncio
import os

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# ---------- EPIC GAMES ----------
def get_epic_free():
    url = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"
    data = requests.get(url).json()
    games = []

    elements = data["data"]["Catalog"]["searchStore"]["elements"]

    for game in elements:
        promos = game.get("promotions")
        if promos and promos.get("promotionalOffers"):
            slug = game["productSlug"]
            title = game["title"]
            image = game["keyImages"][0]["url"]

            link = f"https://store.epicgames.com/p/{slug}"

            games.append({
                "title": title,
                "link": link,
                "image": image,
                "store": "Epic Games"
            })

    return games

# ---------- STEAM ----------
def get_steam_free():
    url = "https://www.reddit.com/r/FreeGamesOnSteam/new.json?limit=5"
    headers = {"User-Agent": "Mozilla/5.0"}
    data = requests.get(url, headers=headers).json()
    games = []

    for post in data["data"]["children"]:
        post_data = post["data"]
        title = post_data["title"]

        if "Free" not in title:
            continue

        link = post_data["url"]

        image = post_data.get("thumbnail")
        if image and image.startswith("http"):
            img = image
        else:
            img = None

        games.append({
            "title": title,
            "link": link,
            "image": img,
            "store": "Steam"
        })

    return games

# ---------- DAILY TASK ----------
@tasks.loop(hours=24)
async def daily_check():
    await bot.wait_until_ready()
    channel = bot.get_channel(CHANNEL_ID)

    epic_games = get_epic_free()
    steam_games = get_steam_free()

    all_games = epic_games + steam_games

    if not all_games:
        return

    for game in all_games:
        embed = discord.Embed(
            title=game["title"],
            url=game["link"],
            color=0x00ff00,
            timestamp=datetime.now(timezone.utc)
        )

        embed.add_field(name="Obchod", value=game["store"], inline=True)
        embed.add_field(name="Cena", value="ZDARMA 🎁", inline=True)

        if game["image"]:
            embed.set_image(url=game["image"])

        await channel.send(embed=embed)
        await asyncio.sleep(1)  # aby Discord nebyl spamován

@bot.command()
async def free(ctx):
    epic_games = get_epic_free()
    steam_games = get_steam_free()
    all_games = epic_games + steam_games

    if not all_games:
        await ctx.send("Teď nejsou žádné hry zdarma.")
        return

    for game in all_games:
        embed = discord.Embed(
            title=game["title"],
            url=game["link"],
            color=0x00ff00,
            timestamp=datetime.now(timezone.utc)
        )
        embed.add_field(name="Obchod", value=game["store"], inline=True)
        embed.add_field(name="Cena", value="ZDARMA 🎁", inline=True)
        if game["image"]:
            embed.set_image(url=game["image"])
        await ctx.send(embed=embed)
        await asyncio.sleep(1)

@bot.event
async def on_ready():
    print(f"Přihlášen jako {bot.user}")
    if not daily_check.is_running():
        daily_check.start()

bot.run(TOKEN)



