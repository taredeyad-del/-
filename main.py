import discord
from discord.ext import commands, tasks
from flask import Flask
from threading import Thread
import os
import asyncio
import io

# --- 1. إعداد الويب للعمل 24/7 ---
app = Flask("")
@app.route("/")
def home(): return "Bot is Online!"
def run_web(): app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
Thread(target=run_web).start()

# --- 2. إعداد البوت ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# الإيديات المسموح لها
AUTHORIZED_IDS = [1511553830838468628, 1511553933053661224, 1511675475825787010]

def is_authorized(ctx):
    return ctx.author.id in AUTHORIZED_IDS

# --- 3. الأوامر ---

@bot.command(name="ارسالبياناتطلب")
@commands.check(is_authorized)
async def archive_ticket(ctx):
    # شرط وجود الدائرة الخضراء
    if "🟢" not in ctx.channel.name:
        return await ctx.send("❌ لا يمكن أرشفة التيكت إلا بعد إرساله (يجب وجود 🟢 في اسم القناة).")
    
    ticket_owner = next((m for m in ctx.channel.members if not m.bot), None)
    if not ticket_owner:
        return await ctx.send("❌ لم أجد صاحب التيكت!")
    
    await ctx.send("⏳ جاري الأرشفة...")
    messages = [msg async for msg in ctx.channel.history(limit=None, oldest_first=True)]
    transcript = "\n".join([f"{msg.author.name}: {msg.content}" for msg in messages])
    
    file = io.BytesIO(transcript.encode('utf-8'))
    try:
        await ticket_owner.send(f"📬 ملف محادثة التيكت:", file=discord.File(file, filename=f"ticket_{ctx.channel.name}.txt"))
        await ctx.send("✅ تم الإرسال لصاحب التيكت في الخاص.")
    except:
        await ctx.send("❌ الخاص مغلق، تعذر إرسال الملف.")

@bot.command(name="حذفروم")
@commands.check(is_authorized)
async def delete_channel(ctx):
    await ctx.send("⚠️ سيتم حذف الروم في 3 ثوانٍ...")
    await asyncio.sleep(3)
    await ctx.channel.delete()

@bot.command(name="طلب")
@commands.check(is_authorized)
async def o(ctx): 
    if "ticket" in ctx.channel.name.lower(): await ctx.channel.edit(name="طلب-عميل-🔵")

@bot.command(name="تمارسال")
@commands.check(is_authorized)
async def s(ctx):
    if "ticket" in ctx.channel.name.lower(): await ctx.channel.edit(name="طلب-عميل-🟢")

@bot.command(name="شكوة", aliases=["شكوه"])
@commands.check(is_authorized)
async def c(ctx):
    if "ticket" in ctx.channel.name.lower(): await ctx.channel.edit(name="شكوة-عميل-🔴")

# --- 4. معالج الأخطاء الصامت ---
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound): return
    if isinstance(error, commands.CheckFailure): return
    raise error

# --- 5. التشغيل ---
@bot.event
async def on_ready():
    print(f"✅ جاهز: {bot.user}")

bot.run(os.getenv("DISCORD_TOKEN"))
