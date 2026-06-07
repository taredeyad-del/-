import discord
from discord.ext import commands, tasks
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

# --- إعدادات القنوات ---
VOUCH_CH = 1511668692889370735
LOOP_CH = 1511557359800025088
PROTECTED_CHANNELS = [1511662934349316188, 1511663266882130042, 1511663314651058237]

# --- دالة الذكاء الاصطناعي ---
async def is_selling_attempt(content):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "أنت خبير أمني. حلل الرسالة، إذا كانت محاولة بيع أو شراء بالمال الحقيقي أو طلب تواصل خاص، أجب بكلمة 'YES' فقط، وإلا أجب بـ 'NO'."},
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

    # الحماية (AI) في الرومات المحددة
    if message.channel.id in PROTECTED_CHANNELS and not message.content.startswith('!'):
        if await is_selling_attempt(message.content):
            try:
                await message.delete()
                warning = await message.channel.send(f"⚠️ {message.author.mention} تم حظر رسالتك بواسطة نظام الحماية (يمنع البيع بالمال).")
                await warning.delete(delay=5)
                return
            except: pass

    await bot.process_commands(message)

# --- أوامر المساعدة والإدارة ---
@bot.command()
async def helpot(ctx, *, question: str):
    async with ctx.channel.typing():
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "أنت مساعد ذكي في سيرفر ديسكورد، أجب باحترافية."}, {"role": "user", "content": question}]
        )
        await ctx.send(f"🤖 **المساعد الذكي:**\n{response.choices[0].message.content}")

@bot.command()
async def vouch(ctx, *, text="بدون تعليق"):
    # (كود التقييم هنا...)
    pass

@bot.command()
async def طلب(ctx): 
    await ctx.channel.edit(name="طلب-🔵")

@bot.command()
async def تماستلامطلب(ctx): 
    await ctx.channel.edit(name="طلب-🟡")

@bot.command()
async def تمارسالطلب(ctx): 
    await ctx.channel.edit(name="طلب-🟢")

# --- التشغيل ---
keep_alive()
bot.run(os.getenv("DISCORD_TOKEN"))
