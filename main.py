import discord
from discord.ext import commands, tasks
from flask import Flask
from threading import Thread
import os

# إعدادات النسخة
BOT_VERSION = "1.0.1-beta"
BETA_MODE = True

app = Flask("")

@app.route("/")
def home():
    return "Bot is alive - Beta Version"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    Thread(target=run_web).start()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Prefix فارغ ليقبل الأوامر المباشرة
bot = commands.Bot(command_prefix=["!", ""], intents=intents)

WELCOME_CH = 1511571690294083716
VOUCH_CH = 1511668692889370735
SLEEP_CH = 1511557359800025088
LOG_CH = 1512027662665777152

bot_deleted_messages = set()

async def delete_command(ctx):
    try:
        bot_deleted_messages.add(ctx.message.id)
        await ctx.message.delete()
    except:
        pass

@bot.event
async def on_ready():
    print(f"✅ البوت اشتغل: {bot.user} | الإصدار: {BOT_VERSION}")
    if not bot_status_log.is_running():
        bot_status_log.start()

@tasks.loop(seconds=300)
async def bot_status_log():
    channel = bot.get_channel(LOG_CH)
    if channel:
        await channel.send(f"🤖 البوت يعمل (إصدار: {BOT_VERSION})")

@bot.event
async def on_message_delete(message):
    if message.author == bot.user or message.author.bot:
        return
    if message.id in bot_deleted_messages:
        bot_deleted_messages.remove(message.id)
        return
    
    log = bot.get_channel(LOG_CH)
    if log:
        embed = discord.Embed(title="رسالة محذوفة", color=discord.Color.red())
        embed.add_field(name="الكاتب", value=message.author.mention, inline=False)
        embed.add_field(name="الرسالة", value=message.content or "لا يوجد نص", inline=False)
        await log.send(embed=embed)

# الأوامر
@bot.command()
async def طلب(ctx):
    await delete_command(ctx)
    await ctx.channel.edit(name="🟢・طلب")

@bot.command(name="شكوى")
async def شكوى(ctx):
    await delete_command(ctx)
    await ctx.channel.edit(name="🔴・شكوى")

@bot.command(name="شكوة")
async def شكوة(ctx):
    await delete_command(ctx)
    await ctx.channel.edit(name="🔴・شكوى")

@bot.command()
async def نوم(ctx):
    await delete_command(ctx)
    channel = bot.get_channel(SLEEP_CH)
    if channel:
        await channel.send(f"{ctx.author.mention} راح ينام، تصبحون على خير")

@bot.command()
async def اوامر(ctx):
    await delete_command(ctx)
    embed = discord.Embed(title=f"أوامر البوت {BOT_VERSION}", color=discord.Color.blue())
    embed.add_field(name="طلب", value="يغير اسم الروم إلى 🟢・طلب", inline=False)
    embed.add_field(name="شكوى", value="يغير اسم الروم إلى 🔴・شكوى", inline=False)
    embed.add_field(name="سلام", value="يرد عليك بالسلام", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def سلام(ctx):
    await delete_command(ctx)
    await ctx.send(f"هلا {ctx.author.mention}")

# تشغيل البوت
keep_alive()
bot.run(os.getenv("DISCORD_TOKEN"))
