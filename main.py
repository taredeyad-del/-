import discord
from discord.ext import commands
from discord import ui
from flask import Flask
from threading import Thread
import os
import sqlite3
import re

# --- إعداد الويب ---
app = Flask("")
@app.route("/")
def home(): return "Bot is alive"
def run_web(): app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
Thread(target=run_web).start()

# --- إعداد قاعدة البيانات ---
db = sqlite3.connect("invoices.db", check_same_thread=False)
cursor = db.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS invoices (id TEXT PRIMARY KEY, embed_data TEXT)")
db.commit()

# --- إعداد البوت ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# الثوابت
VOUCH_CH = 1511668692889370735
INVOICE_CH = 1513129732378726440
OWNER_IDS = [1511553830838468628, 1511553933053661224]
bot_deleted_messages = set()

def is_admin(ctx):
    return ctx.author.id in OWNER_IDS or any(role.id in OWNER_IDS for role in ctx.author.roles)

async def delete_command(ctx):
    try:
        bot_deleted_messages.add(ctx.message.id)
        await ctx.message.delete()
    except: pass

# --- نظام الفاتورة (جديد) ---
class InvoiceSelect(ui.Select):
    def __init__(self, rows):
        options = [discord.SelectOption(label=f"Invoice #{r[0]}", value=str(r[0])) for r in rows]
        super().__init__(placeholder="اختر فاتورة...", options=options)
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"✅ تم اختيار الفاتورة {self.values[0]}", ephemeral=True)

class InvoiceView(ui.View):
    def __init__(self, rows):
        super().__init__()
        self.add_item(InvoiceSelect(rows))

# --- نظام التقييم الأصلي الخاص بك ---
class RatingButtons(discord.ui.View):
    def __init__(self, author, comment):
        super().__init__(timeout=120)
        self.author = author
        self.comment = comment

    async def send_vouch(self, interaction, stars):
        vouch_channel = bot.get_channel(VOUCH_CH)
        if vouch_channel:
            embed = discord.Embed(title="✅ تقييم جديد", color=discord.Color.gold())
            embed.add_field(name="العميل", value=self.author.mention, inline=False)
            embed.add_field(name="التعليق", value=self.comment, inline=False)
            embed.add_field(name="التقييم", value=f"{'⭐' * stars}", inline=False)
            await vouch_channel.send(embed=embed)
        await interaction.response.send_message("تم إرسال تقييمك بنجاح!", ephemeral=True)
        await interaction.message.delete()

    @discord.ui.button(label="⭐", style=discord.ButtonStyle.gray)
    async def s1(self, i, b): await self.send_vouch(i, 1)
    @discord.ui.button(label="⭐⭐", style=discord.ButtonStyle.gray)
    async def s2(self, i, b): await self.send_vouch(i, 2)
    @discord.ui.button(label="⭐⭐⭐", style=discord.ButtonStyle.gray)
    async def s3(self, i, b): await self.send_vouch(i, 3)
    @discord.ui.button(label="⭐⭐⭐⭐", style=discord.ButtonStyle.gray)
    async def s4(self, i, b): await self.send_vouch(i, 4)
    @discord.ui.button(label="⭐⭐⭐⭐⭐", style=discord.ButtonStyle.green)
    async def s5(self, i, b): await self.send_vouch(i, 5)

# --- الأوامر ---
@bot.command()
async def vouch(ctx, member: discord.Member):
    await delete_command(ctx)
    msg = await ctx.send(f"يا {member.mention}، يرجى كتابة تعليقك عن الطلب:")
    def check(m): return m.author == member and m.channel == ctx.channel
    try:
        comment_msg = await bot.wait_for('message', timeout=60.0, check=check)
        await msg.edit(content=f"تعليقك: '{comment_msg.content}'\nالآن اختر عدد النجوم:", view=RatingButtons(member, comment_msg.content))
        await comment_msg.delete()
    except: await msg.delete()

@bot.command()
async def سحب(ctx):
    channel = bot.get_channel(INVOICE_CH)
    count = 0
    async for message in channel.history(limit=None):
        if message.embeds:
            text = (message.embeds[0].title or "") + (message.embeds[0].description or "")
            match = re.search(r'(\d{8})', text)
            if match:
                cursor.execute("INSERT OR REPLACE INTO invoices VALUES (?, ?)", (match.group(1), "تم الحفظ"))
                count += 1
    db.commit()
    await ctx.send(f"✅ تم سحب {count} فاتورة!", ephemeral=True)

@bot.command()
async def فاتورة(ctx):
    cursor.execute("SELECT id FROM invoices")
    rows = cursor.fetchall()
    if not rows: return await ctx.send("لا توجد فواتير.", ephemeral=True)
    await ctx.send("📋 اختر الفاتورة:", view=InvoiceView(rows), ephemeral=True)

# --- أوامر تغيير اسم الروم ---
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

@bot.event
async def on_ready(): print(f"✅ البوت متصل: {bot.user}")

bot.run(os.getenv("DISCORD_TOKEN"))
