import asyncio
import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread
from openai import OpenAI

# إعداد OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- إعداد نظام الإبقاء على البوت نشطاً ---
app = Flask('')
@app.route('/')
def home(): return "البوت يعمل الآن!"
def run_flask(): app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run_flask)
    t.start()

# --- إعداد البوت ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --- إعدادات ---
VOUCH_CH = 1511668692889370735
PROTECTED_CHANNELS = [1511662934349316188, 1511663266882130042, 1511663314651058237]

# --- نظام السجن (AI Jail) ---
async def jail_user(message):
    try:
        await message.delete()
        # إرسال تحذير للعضو
        warning = await message.channel.send(f"⚠️ {message.author.mention} تم سجنك في مكافحة البيع لمدة 15 دقيقة.")
        
        # سجن العضو (منع إرسال الرسائل في هذا الروم)
        overwrite = discord.PermissionOverwrite(send_messages=False)
        await message.channel.set_permissions(message.author, overwrite=overwrite)
        
        await asyncio.sleep(900) # 15 دقيقة
        
        # فك السجن
        await message.channel.set_permissions(message.author, overwrite=None)
        await warning.delete()
    except Exception as e:
        print(f"خطأ في نظام السجن: {e}")

# --- فحص الـ AI ---
async def is_selling_attempt(content):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "أنت نظام أمني. إذا كانت الرسالة محاولة بيع أو شراء، أجب بـ 'YES'، وإلا 'NO'."},
                {"role": "user", "content": content}
            ]
        )
        return "YES" in response.choices[0].message.content.upper()
    except: return False

# --- الأحداث ---
@bot.event
async def on_message(message):
    if message.author.bot:
        await bot.process_commands(message)
        return

    # الحماية
    if message.channel.id in PROTECTED_CHANNELS and not message.content.startswith('!'):
        if await is_selling_attempt(message.content):
            await jail_user(message)
            return

    await bot.process_commands(message)

# --- الأوامر القديمة (helpot + طلبات) ---
@bot.command()
async def helpot(ctx, *, question: str):
    async with ctx.channel.typing():
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "أنت مساعد ذكي."}, {"role": "user", "content": question}]
        )
        await ctx.send(f"🤖 **المساعد الذكي:**\n{response.choices[0].message.content}")

@bot.command()
async def vouch(ctx, *, text="بدون تعليق"):
    # (كود التقييم القديم)
    await ctx.send("تم استلام التقييم!")

@bot.command()
async def طلب(ctx): await ctx.channel.edit(name="طلب-🔵")
@bot.command()
async def تماستلامطلب(ctx): await ctx.channel.edit(name="طلب-🟡")
@bot.command()
async def تمارسالطلب(ctx): await ctx.channel.edit(name="طلب-🟢")
@bot.command()
async def حذفروم(ctx): await ctx.channel.delete()

keep_alive()
bot.run(os.getenv("DISCORD_TOKEN"))
