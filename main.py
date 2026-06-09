import discord
from discord.ext import commands, tasks
import os
import sqlite3
import re
import ast
from openai import OpenAI
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# --- إعدادات Keep-Alive ---
app = Flask('')
@app.route('/')
def home(): return "البوت يعمل الآن!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run)
    t.start()

load_dotenv()
keep_alive()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# الثوابت
INVOICE_CH = 1513129732378726440
VOUCH_CH = 1511668692889370735
AUTO_MSG_CH = 1511557359800025088
OWNER_IDS = [1511553830838468628, 1511553933053661224]
BAD_WORDS = ["كلمة1", "كلمة2"]

db = sqlite3.connect("invoices.db", check_same_thread=False)
cursor = db.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS invoices (id TEXT PRIMARY KEY, data TEXT)")
db.commit()

@tasks.loop(seconds=600) # تم تعديل الوقت لـ 10 دقائق لتجنب الحظر
async def auto_message():
    channel = bot.get_channel(AUTO_MSG_CH)
    if channel:
        await channel.send("هذه رسالة تلقائية!")

def is_admin(ctx):
    return ctx.author.id in OWNER_IDS or any(role.id in OWNER_IDS for role in ctx.author.roles)

async def delete_command(ctx):
    try: await ctx.message.delete()
    except: pass

# --- نظام التقييم ---
class RatingButtons(discord.ui.View):
    def __init__(self, author, comment):
        super().__init__(timeout=None)
        self.author = author
        self.comment = comment

    async def send_vouch(self, interaction, stars):
        vouch_channel = bot.get_channel(VOUCH_CH)
        if vouch_channel:
            embed = discord.Embed(title="✅ تقييم جديد", color=discord.Color.gold())
            embed.add_field(name="العميل", value=self.author.mention, inline=False)
            embed.description = f"**التعليق:**\n{self.comment}"
            embed.add_field(name="التقييم", value=f"{'⭐' * stars}", inline=False)
            await vouch_channel.send(embed=embed)
        await interaction.response.send_message("تم إرسال تقييمك!", ephemeral=True)

    @discord.ui.button(label="⭐", style=discord.ButtonStyle.secondary)
    async def s1(self, i, b): await self.send_vouch(i, 1)
    @discord.ui.button(label="⭐⭐", style=discord.ButtonStyle.secondary)
    async def s2(self, i, b): await self.send_vouch(i, 2)
    @discord.ui.button(label="⭐⭐⭐", style=discord.ButtonStyle.secondary)
    async def s3(self, i, b): await self.send_vouch(i, 3)
    @discord.ui.button(label="⭐⭐⭐⭐", style=discord.ButtonStyle.secondary)
    async def s4(self, i, b): await self.send_vouch(i, 4)
    @discord.ui.button(label="⭐⭐⭐⭐⭐", style=discord.ButtonStyle.green)
    async def s5(self, i, b): await self.send_vouch(i, 5)

@bot.command()
async def vouch(ctx, member: discord.Member):
    await delete_command(ctx)
    msg = await ctx.send(f"يا {member.mention}، يرجى كتابة تعليقك هنا:")
    def check(m): return m.author == member and m.channel == ctx.channel
    try:
        comment_msg = await bot.wait_for('message', timeout=120.0, check=check)
        await msg.edit(content=f"تم استلام تعليقك. اختر عدد النجوم:", view=RatingButtons(member, comment_msg.content))
        await comment_msg.delete()
    except: await msg.delete()

# --- أوامر الإدارة ---
@bot.command()
@commands.check(is_admin)
async def طلب(ctx): await delete_command(ctx); await ctx.channel.edit(name="طلب-🔵")
@bot.command()
@commands.check(is_admin)
async def تمارسالطلب(ctx): await delete_command(ctx); await ctx.channel.edit(name="طلب-🟡")
@bot.command()
@commands.check(is_admin)
async def تماستلامطلب(ctx): await delete_command(ctx); await ctx.channel.edit(name="طلب-🟢")
@bot.command()
@commands.check(is_admin)
async def شكوى(ctx): await delete_command(ctx); await ctx.channel.edit(name="شكوة-🔴")
@bot.command()
@commands.check(is_admin)
async def اغلاق(ctx): await delete_command(ctx); await ctx.channel.edit(name="شكوة-🟢")
@bot.command()
@commands.check(is_admin)
async def حذفروم(ctx): await delete_command(ctx); await ctx.channel.delete()

# --- نظام السحب الجديد ---
@bot.command()
async def سحب(ctx):
    await delete_command(ctx)
    if ctx.message.reference and ctx.message.reference.resolved:
        target_message = ctx.message.reference.resolved
        if target_message.embeds:
            embed = target_message.embeds[0]
            full_text = "".join([f"{f.name} {f.value}" for f in embed.fields]) + (embed.title or "")
            match = re.search(r'\d{8}', full_text)
            if match:
                cursor.execute("INSERT OR REPLACE INTO invoices VALUES (?, ?)", (match.group(0), str(embed.to_dict())))
                db.commit()
                await ctx.send(f"✅ تم حفظ الفاتورة رقم: {match.group(0)}", delete_after=5)
            else: await ctx.send("❌ لم أجد رقم فاتورة في هذه الرسالة.", delete_after=5)
        else: await ctx.send("❌ هذه الرسالة لا تحتوي على بيانات.", delete_after=5)
    else: await ctx.send("⚠️ قم بعمل Reply على الفاتورة لاستخدام هذا الأمر.", delete_after=5)

@bot.command()
@commands.check(is_admin)
async def فاتورة(ctx, invoice_id: str):
    await delete_command(ctx)
    cursor.execute("SELECT data FROM invoices WHERE id = ?", (invoice_id,))
    result = cursor.fetchone()
    if result:
        embed = discord.Embed.from_dict(ast.literal_eval(result[0]))
        embed.add_field(name="🔗 رابط المتجر", value="[اضغط هنا للتوجه للمتجر](https://bsell.mysellauth.com/)", inline=False)
        await ctx.send("✅ تفضل الفاتورة المطلوبة:", embed=embed)
        try: await ctx.channel.edit(name="طلب-🟡")
        except: pass
    else: await ctx.send(f"❌ الفاتورة {invoice_id} غير موجودة.", delete_after=5)

# --- الذكاء الاصطناعي ---
@bot.command()
async def helpot(ctx, *, prompt):
    res = client.chat.completions.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}])
    await ctx.send(res.choices[0].message.content)

@bot.event
async def on_message(message):
    if not message.author.bot and any(w in message.content.lower() for w in BAD_WORDS):
        await message.delete()
    else: await bot.process_commands(message)

@bot.event
async def on_ready():
    print("✅ البوت متصل!")
    auto_message.start()

bot.run(os.getenv("DISCORD_TOKEN"))
