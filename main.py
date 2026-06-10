import discord
from discord.ext import commands, tasks
import os
import sqlite3
import re
import ast
import datetime
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
BAD_WORDS = ["كلمة1", "كلمة2"] # أضف الكلمات المسيئة هنا
ticket_sessions = {} 

db = sqlite3.connect("invoices.db", check_same_thread=False)
cursor = db.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS invoices (id TEXT PRIMARY KEY, data TEXT)")
db.commit()

# --- الأنظمة الأساسية ---
def is_admin(ctx):
    return ctx.author.id in OWNER_IDS or any(role.id in OWNER_IDS for role in ctx.author.roles)

async def delete_command(ctx):
    try: await ctx.message.delete()
    except: pass

@tasks.loop(seconds=600)
async def auto_message():
    channel = bot.get_channel(AUTO_MSG_CH)
    if channel: await channel.send("هذه رسالة تلقائية!")

# --- نظام التذكرة الذكية ---
class TicketLauncher(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎫 فتح تذكرة ذكية", style=discord.ButtonStyle.primary, custom_id="open_ticket")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        member = interaction.user
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            member: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        channel = await guild.create_text_channel(f"تذكرة-{member.name}", overwrites=overwrites)
        ticket_sessions[channel.id] = 0
        await channel.send(f"أهلاً {member.mention}، أنا مساعدك الذكي في متجر Bsell.\n⚠️ **تنبيه:** لديك 15 رسالة فقط في هذه التذكرة.")
        await interaction.response.send_message(f"✅ تم فتح تذكرتك: {channel.mention}", ephemeral=True)

@bot.command()
@commands.check(is_admin)
async def setup_ticket(ctx):
    embed = discord.Embed(title="دعم متجر Bsell", description="اضغط على الزر أدناه لفتح تذكرة ذكية.", color=discord.Color.blue())
    await ctx.send(embed=embed, view=TicketLauncher())

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

# --- أوامر الإدارة والسحب والفاتورة ---
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
            else: await ctx.send("❌ لم أجد رقم فاتورة (8 أرقام).", delete_after=5)
        else: await ctx.send("❌ هذه الرسالة لا تحتوي على بيانات.", delete_after=5)
    else: await ctx.send("⚠️ قم بعمل Reply على الفاتورة.", delete_after=5)

@bot.command()
@commands.check(is_admin)
async def فاتورة(ctx):
    await delete_command(ctx)
    await ctx.send("🔗 يرجى إرسال الرابط المطلوب وضعه في الفاتورة:")
    def check(m): return m.author == ctx.author and m.channel == ctx.channel
    try:
        url_msg = await bot.wait_for('message', timeout=60.0, check=check)
        link = url_msg.content
        await url_msg.delete()
        
        cursor.execute("SELECT data FROM invoices ORDER BY rowid DESC LIMIT 1")
        result = cursor.fetchone()
        if result:
            embed_data = ast.literal_eval(result[0])
            invoice_id = "غير معروف"
            for field in embed_data.get('fields', []):
                if "Invoice ID" in field['name']: invoice_id = field['value']
            
            new_embed = discord.Embed(title=f"Invoice #{invoice_id}", color=discord.Color.blue())
            new_embed.add_field(name="🔗 رابط المتجر", value=f"[اضغط هنا للتوجه للمتجر]({link})", inline=False)
            for field in embed_data.get('fields', []):
                if any(x in field['name'] for x in ["Price", "Product", "Payment"]):
                    new_embed.add_field(name=field['name'], value=field['value'], inline=False)
            
            await ctx.send("✅ تفضل الفاتورة:", embed=new_embed)
            try: await ctx.channel.edit(name="طلب-🟡")
            except: pass
        else: await ctx.send("❌ لا توجد فواتير مسحوبة!", delete_after=5)
    except: await ctx.send("❌ انتهى الوقت أو حدث خطأ.", delete_after=5)

# --- الحدث الرئيسي ---
@bot.event
async def on_message(message):
    if message.author.bot: return

    # 1. نظام الحظر (تايم أوت)
    if any(w in message.content.lower() for w in BAD_WORDS):
        try:
            await message.author.timeout(datetime.timedelta(minutes=15), reason="إساءة للبوت")
            await message.channel.send(f"🚫 {message.author.mention} تم إعطاؤك تايم أوت 15 دقيقة بسبب الإساءة.")
            await message.delete()
            return
        except Exception as e: print(e)

    # 2. نظام التذاكر
    if message.channel.id in ticket_sessions:
        ticket_sessions[message.channel.id] += 1
        
        if ticket_sessions[message.channel.id] >= 15:
            await message.channel.send("🚫 تم استهلاك حد الرسائل (15). سيتم إغلاق التيكت.")
            await message.channel.edit(name=f"closed-{message.channel.name}")
            await message.channel.set_permissions(message.guild.default_role, send_messages=False)
            return

        async with message.channel.typing():
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "أنت مساعد ذكي لمتجر Bsell. ردودك احترافية ولطيفة ومختصرة."},
                        {"role": "user", "content": message.content}
                    ],
                    max_tokens=150
                )
                await message.reply(response.choices[0].message.content)
            except Exception as e: print(e)
    
    await bot.process_commands(message)

@bot.event
async def on_ready():
    bot.add_view(TicketLauncher())
    auto_message.start()
    print("✅ البوت متصل ونظام التذاكر جاهز!")

bot.run(os.getenv("DISCORD_TOKEN"))
