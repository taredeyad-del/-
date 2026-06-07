import discord
from discord.ext import commands, tasks
import os
from flask import Flask
from threading import Thread
from openai import OpenAI

# إعداد OpenAI (تأكد من إضافة OPENAI_API_KEY في إعدادات Render)
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
intents.message_content = True # ضروري جداً
bot = commands.Bot(command_prefix="!", intents=intents)

# --- إعدادات القنوات والكلمات ---
VOUCH_CH = 1511668692889370735
LOOP_CH = 1511557359800025088
PROTECTED_CHANNELS = [1511662934349316188, 1511663266882130042, 1511663314651058237]

# --- دالة الذكاء الاصطناعي للفحص ---
async def is_selling_attempt(content):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "أنت نظام أمني. حلل الرسالة التالية، إذا كانت محاولة بيع أو شراء بالمال الحقيقي أو عرض خدمات تجارية أو تواصل خاص، أجب بكلمة 'YES' فقط، وإلا أجب بـ 'NO'."},
                {"role": "user", "content": content}
            ]
        )
        return "YES" in response.choices[0].message.content.upper()
    except: return False

# --- الأحداث ---
@bot.event
async def on_message(message):
    # 1. تجاهل البوت
    if message.author.bot:
        await bot.process_commands(message)
        return

    # 2. نظام الحماية الذكي في رومات معينة
    if message.channel.id in PROTECTED_CHANNELS and not message.content.startswith('!'):
        if await is_selling_attempt(message.content):
            try:
                await message.delete()
                warning = await message.channel.send(f"⚠️ {message.author.mention} تم حظر رسالتك (يمنع البيع بالمال الحقيقي).")
                await warning.delete(delay=5)
                return # يوقف المعالجة هنا
            except: pass

    # 3. معالجة الأوامر
    await bot.process_commands(message)

# --- الأوامر ---
@bot.command()
async def helpot(ctx, *, question: str):
    async with ctx.channel.typing():
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "أنت مساعد ذكي في السيرفر، أجب باحترافية."}, {"role": "user", "content": question}]
        )
        await ctx.send(f"🤖 **المساعد الذكي:**\n{response.choices[0].message.content}")

@bot.command()
async def vouch(ctx, *, review_text: str = "بدون تعليق"):
    await ctx.message.delete()
    embed = discord.Embed(title="قيّم خدماتنا", description=f"التعليق: {review_text}\nاختر عدد النجوم:", color=discord.Color.pink())
    class RatingButtons(discord.ui.View):
        def __init__(self, text):
            super().__init__(timeout=None)
            self.text = text
        @discord.ui.button(label="⭐⭐⭐⭐⭐", style=discord.ButtonStyle.success)
        async def s5(self, i, b):
            vouch_ch = bot.get_channel(VOUCH_CH)
            await vouch_ch.send(f"✅ تقييم جديد: {self.text}\nمن: {i.user.mention}")
            await i.response.edit_message(content="تم التقييم بنجاح!", embed=None, view=None)
    await ctx.send(embed=embed, view=RatingButtons(review_text))

@bot.command()
async def طلب(ctx): await ctx.channel.edit(name="طلب-🔵")
@bot.command()
async def تماستلامطلب(ctx): await ctx.channel.edit(name="طلب-🟡")
@bot.command()
async def تمارسالطلب(ctx): await ctx.channel.edit(name="طلب-🟢")
@bot.command()
async def حذفروم(ctx): await ctx.channel.delete()

# --- التشغيل ---
keep_alive()
bot.run(os.getenv("DISCORD_TOKEN"))
