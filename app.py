import discord
from discord.ext import commands
import json
import os

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# File buat nyimpen XP
DATA_FILE = "leaderboard.json"

def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# XP per chat = 10 XP, Level naik tiap 100 XP
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    data = load_data()
    user_id = str(message.author.id)
    
    if user_id not in data:
        data[user_id] = {"xp": 0, "level": 1, "messages": 0, "name": message.author.name}
    
    data[user_id]["xp"] += 10
    data[user_id]["messages"] += 1
    data[user_id]["name"] = message.author.name

    # Cek naik level
    xp = data[user_id]["xp"]
    level = data[user_id]["level"]
    need_xp = level * 100

    if xp >= need_xp:
        data[user_id]["level"] += 1
        await message.channel.send(f"🎉 Selamat {message.author.mention}! Kamu naik ke **Level {data[user_id]['level']}**!")

    save_data(data)
    await bot.process_commands(message)

@bot.event
async def on_ready():
    print(f"✅ Bot login sebagai {bot.user}")

# !rank - Liat rank kau sendiri
@bot.command()
async def rank(ctx):
    data = load_data()
    user_id = str(ctx.author.id)
    if user_id not in data:
        await ctx.send("Kamu belum ada XP, chat dulu!")
        return
    
    u = data[user_id]
    need = u["level"] * 100
    await ctx.send(f"🏆 **{ctx.author.name}**\nLevel: {u['level']}\nXP: {u['xp']} / {need}\nTotal Chat: {u['messages']}")

# !leaderboard - Liat Top 10
@bot.command(aliases=["lb", "top"])
async def leaderboard(ctx):
    data = load_data()
    if not data:
        await ctx.send("Belum ada data, chat dulu!")
        return

    # Urutin dari XP paling gede
    sorted_users = sorted(data.items(), key=lambda x: x[1]["xp"], reverse=True)[:10]

    text = "**🏆 LEADERBOARD CIOO - TOP 10 🏆**\n\n"
    medals = ["🥇", "🥈", "🥉", "4.", "5.", "6.", "7.", "8.", "9.", "10."]
    
    for i, (user_id, u) in enumerate(sorted_users):
        text += f"{medals[i]} **{u['name']}** - Level {u['level']} | {u['xp']} XP | {u['messages']} chat\n"

    await ctx.send(text)

# !mostonline - Yang paling banyak chat (Most Online)
@bot.command()
async def mostonline(ctx):
    data = load_data()
    if not data:
        await ctx.send("Belum ada data!")
        return

    sorted_users = sorted(data.items(), key=lambda x: x[1]["messages"], reverse=True)[:10]

    text = "**🔥 MOST ONLINE - PALING BANYAK CHAT 🔥**\n\n"
    medals = ["🥇", "🥈", "🥉", "4.", "5.", "6.", "7.", "8.", "9.", "10."]

    for i, (user_id, u) in enumerate(sorted_users):
        text += f"{medals[i]} **{u['name']}** - {u['messages']} chat | Level {u['level']}\n"

    await ctx.send(text)

bot.run(os.getenv("DISCORD_TOKEN"))
