import discord
from discord.ext import commands, tasks
from flask import Flask
from threading import Thread
import os

# إعدادات النسخة
BOT_VERSION = "1.1.0-beta"

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

bot = commands.Bot(command_prefix="!", intents=intents)

WELCOME_CH = 1511571690294083716
VOUCH_CH = 1511668692889370735
SLEEP_CH = 1511557359800025088
LOG_CH = 1512027662665777152

bot_deleted_messages = set()

# --- معالجة الأوامر المباشرة ---
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content.strip()

    if content == "طلب":
        await message.delete()
        await message.channel.edit(name="🟢・طلب")
        return

    if content in ["شكوى", "شكوة"]:
        await message.delete()
        await message.channel.edit(name="🔴・شكوى")
        return

    if content == "نوم":
        await message.delete()
        channel = bot.get_channel(SLEEP_CH)
        if channel:
            await channel.send(f"{message.author.mention} راح ينام، تصبحون على خير")
        return

    if content == "سلام":
        await message.delete()
        await message.channel.send(f"هلا {message.author.mention}")
        return

    # هذا السطر مهم جداً لمعالجة الأوامر التي تبدأ بـ ! (مثل !حذف)
    await bot.process_commands(message)

# --- أوامر الـ ! ---
@bot.command()
@commands.has_permissions(manage_messages=True)
async def حذف(ctx, amount: int = 1):
    deleted = await ctx.channel.purge(limit=amount + 1)
    for msg in deleted:
        bot_deleted_messages.add(msg.id)

@bot.command()
async def اوامر(ctx):
    await ctx.message.delete()
    embed = discord.Embed(title=f"أوامر البوت {BOT_VERSION}", color=discord.Color.blue())
    embed.add_field(name="طلب", value="يغير اسم الروم إلى 🟢・طلب", inline=False)
    embed.add_field(name="شكوى / شكوة", value="يغير اسم الروم إلى 🔴・شكوى", inline=False)
    embed.add_field(name="سلام", value="يرد عليك بالسلام", inline=False)
    embed.add_field(name="!حذف [رقم]", value="حذف الرسائل (للمشرفين)", inline=False)
    await ctx.send(embed=embed)

# --- أحداث البوت ---
@bot.event
async def on_ready():
    print(f"✅ البوت اشتغل: {bot.user} | الإصدار: {BOT_VERSION}")
    if not bot_status_log.is_running():
        bot_status_log.start()

@tasks.loop(seconds=300)
async def bot_status_log():
    channel = bot.get_channel(LOG_CH)
    if channel:
        await channel.send(f"🤖 البوت نشط ({BOT_VERSION})")

@bot.event
async def on_message_delete(message):
    if message.author == bot.user or message.author.bot:
        return
    if message.id in bot_deleted_messages:
        bot_deleted_messages.discard(message.id)
        return
    
    log = bot.get_channel(LOG_CH)
    if log:
        embed = discord.Embed(title="رسالة محذوفة", color=discord.Color.red())
        embed.add_field(name="الكاتب", value=message.author.mention, inline=False)
        embed.add_field(name="الرسالة", value=message.content or "لا يوجد نص", inline=False)
        await log.send(embed=embed)

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(WELCOME_CH)
    if channel:
        await channel.send(f"هلا والله {member.mention} نورت السيرفر!")

# تشغيل البوت
keep_alive()
bot.run(os.getenv("DISCORD_TOKEN"))
