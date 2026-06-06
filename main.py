import discord
from discord.ext import commands, tasks
from flask import Flask
from threading import Thread
import os

# إعدادات النسخة
BOT_VERSION = "1.0.0-beta"
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

bot = commands.Bot(command_prefix="!", intents=intents)

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
    beta_tag = "[BETA]" if BETA_MODE else ""
    print(f"✅ {beta_tag} البوت اشتغل: {bot.user} | الإصدار: {BOT_VERSION}")
    if not bot_status_log.is_running():
        bot_status_log.start()

@tasks.loop(seconds=300) # تم زيادة الوقت لتقليل الضغط
async def bot_status_log():
    channel = bot.get_channel(LOG_CH)
    if channel:
        status_msg = f"🤖 البوت نشط ({BOT_VERSION})..."
        if BETA_MODE: status_msg = f"⚠️ [BETA] {status_msg}"
        await channel.send(status_msg)

# ... (باقي الأحداث كما هي: on_member_join, on_message_delete) ...

@bot.command()
async def اوامر(ctx):
    await delete_command(ctx)
    embed = discord.Embed(
        title=f"أوامر البوت {BOT_VERSION}", 
        description="هذه النسخة تجريبية (Beta)، قد تواجه بعض الأخطاء.",
        color=discord.Color.purple() if BETA_MODE else discord.Color.blue()
    )
    # ... (إضافة الحقول بنفس الترتيب السابق) ...
    embed.add_field(name="!طلب", value="يغير اسم الروم إلى 🟢・طلب", inline=False)
    embed.add_field(name="!شكوى / !شكوة", value="يغير اسم الروم إلى 🔴・شكوى", inline=False)
    embed.add_field(name="!تقييم @user", value="يفتح أزرار تقييم", inline=False)
    embed.add_field(name="!نوم", value="يرسل رسالة في قناة النوم", inline=False)
    embed.add_field(name="!حذف [العدد]", value="حذف الرسائل", inline=False)
    
    await ctx.send(embed=embed)

# ملاحظة: تأكد من إبقاء باقي الدوال (حذف، طلب، شكوى، نوم، تقييم) كما هي في كودك الأصلي
keep_alive()
bot.run(os.getenv("DISCORD_TOKEN"))
