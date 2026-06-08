import discord
from discord.ext import commands
from discord import ui
import sqlite3
import re
import ast
from openai import OpenAI

# --- الإعدادات ---
client = OpenAI(api_key="YOUR_OPENAI_API_KEY") 
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# الثوابت
VOUCH_CH = 1511668692889370735
INVOICE_CH = 1513129732378726440
ADMIN_ROLES = [1511553933053661224, 1513230926916620378, 1511553830838468628]
BAD_WORDS = ["سب1", "سب2", "كلمة_نابية"]

# قاعدة البيانات
db = sqlite3.connect("invoices.db", check_same_thread=False)
cursor = db.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS invoices (id TEXT PRIMARY KEY, embed_data TEXT)")
db.commit()

def is_admin(ctx):
    return any(role.id in ADMIN_ROLES for role in ctx.author.roles)

async def delete_command(ctx):
    try: await ctx.message.delete()
    except: pass

# --- الحماية من السب ---
@bot.event
async def on_message(message):
    if message.author.bot: return
    if any(word in message.content.lower() for word in BAD_WORDS):
        await message.delete()
        await message.channel.send(f"⚠️ {message.author.mention} ممنوع السب!", delete_after=3)
        return
    await bot.process_commands(message)

# --- أوامر الطلبات والشكاوى (محصورة بالرتب) ---
@bot.command()
@commands.check(is_admin)
async def طلب(ctx): await delete_command(ctx); await ctx.channel.edit(name="طلب • 🔵")

@bot.command()
@commands.check(is_admin)
async def تمارسالطلب(ctx): await delete_command(ctx); await ctx.channel.edit(name="طلب • 🟡")

@bot.command()
@commands.check(is_admin)
async def تماستلامطلب(ctx): await delete_command(ctx); await ctx.channel.edit(name="طلب • 🟢")

@bot.command()
@commands.check(is_admin)
async def شكوى(ctx): await delete_command(ctx); await ctx.channel.edit(name="شكوة • 🔴")

@bot.command()
@commands.check(is_admin)
async def اغلاق(ctx): await delete_command(ctx); await ctx.channel.edit(name="شكوة • 🟢")

@bot.command()
@commands.check(is_admin)
async def حذفروم(ctx): await delete_command(ctx); await ctx.channel.delete()

# --- أمر الذكاء الاصطناعي ---
@bot.command()
async def helpot(ctx, *, prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "أنت مساعد ذكي ومفيد."}, {"role": "user", "content": prompt}]
        )
        await ctx.send(response.choices[0].message.content)
    except:
        await ctx.send("حدث خطأ في الاتصال بالذكاء الاصطناعي.")

# --- الأوامر الأخرى (سحب، فاتورة، vouch) ---
@bot.command()
async def vouch(ctx, member: discord.Member):
    await delete_command(ctx)
    msg = await ctx.send(f"يا {member.mention}، اكتب تعليقك:")
    try:
        comment_msg = await bot.wait_for('message', timeout=60.0, check=lambda m: m.author == member)
        await msg.edit(content=f"تعليقك: '{comment_msg.content}'\nاختر التقييم:", view=RatingButtons(member, comment_msg.content))
        await comment_msg.delete()
    except: await msg.delete()

@bot.command()
async def سحب(ctx):
    await delete_command(ctx)
    channel = bot.get_channel(INVOICE_CH)
    count = 0
    async for message in channel.history(limit=200):
        if message.embeds:
            emb = message.embeds[0]
            text = (emb.title or "") + (emb.description or "") + "".join([f.value for f in emb.fields])
            match = re.search(r'\d{8}', text)
            if match:
                cursor.execute("INSERT OR REPLACE INTO invoices VALUES (?, ?)", (match.group(0), str(emb.to_dict())))
                count += 1
    db.commit()
    await ctx.send(f"✅ تم سحب {count} فاتورة!", delete_after=5)

@bot.command()
async def فاتورة(ctx):
    await delete_command(ctx)
    cursor.execute("SELECT id FROM invoices")
    rows = cursor.fetchall()
    if not rows: return await ctx.send("لا توجد فواتير.", ephemeral=True)
    await ctx.send("📋 اختر الفاتورة:", view=InvoiceView(rows), ephemeral=True)

@bot.event
async def on_ready(): print(f"✅ البوت متصل: {bot.user}")

bot.run(os.getenv("DISCORD_TOKEN"))
