import discord
from discord.ext import commands, tasks
from flask import Flask
from threading import Thread
import os

# --- إعداد الويب للحماية من النوم (Render) ---
app = Flask("")
@app.route("/")
def home(): return "Bot is Online and Active!"
def run_web(): app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
Thread(target=run_web).start()

# --- إعداد البوت ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# إيديات القنوات (استبدلها بأرقام قنواتك الحقيقية)
WELCOME_CH = 1511571690294083716
VOUCH_CH = 1511668692889370735
SLEEP_CH = 1511557359800025088
LOG_CH = 1512027662665777152

# --- نظام أزرار التقييم ---
class RatingButtons(discord.ui.View):
    def __init__(self, msg, auth):
        super().__init__(timeout=120)
        self.msg, self.auth = msg, auth

    async def rate(self, interaction: discord.Interaction, stars: int):
        if interaction.user.id != self.auth.id:
            return await interaction.response.send_message("❌ ليست لك!", ephemeral=True)
        ch = bot.get_channel(VOUCH_CH)
        embed = discord.Embed(title="Customer Rating", description=f"{'⭐'*stars}{'☆'*(5-stars)} {stars}/5\n\n{self.msg}\n\n**Buyer:** {self.auth.mention}", color=0xFFD700)
        await ch.send(embed=embed)
        await interaction.response.edit_message(content=f"✅ تم الإرسال!", view=None)
        self.stop()

    @discord.ui.button(label="1 ⭐")
    async def s1(self, ix, b): await self.rate(ix, 1)
    @discord.ui.button(label="2 ⭐")
    async def s2(self, ix, b): await self.rate(ix, 2)
    @discord.ui.button(label="3 ⭐")
    async def s3(self, ix, b): await self.rate(ix, 3)
    @discord.ui.button(label="4 ⭐")
    async def s4(self, ix, b): await self.rate(ix, 4)
    @discord.ui.button(label="5 ⭐", style=discord.ButtonStyle.success)
    async def s5(self, ix, b): await self.rate(ix, 5)

# --- المهام التلقائية ---
@tasks.loop(minutes=10)
async def keep_alive():
    ch = bot.get_channel(SLEEP_CH)
    if ch: 
        try: await ch.send("🤖 البوت نشط...")
        except: pass

@bot.event
async def on_ready():
    print(f"✅ البوت يعمل: {bot.user}")
    keep_alive.start()

# --- المراقبة واللوج ---
@bot.event
async def on_member_join(m):
    ch = bot.get_channel(WELCOME_CH)
    if ch: await ch.send(f"أهلاً بك {m.mention} نورت السيرفر! ✨")

@bot.event
async def on_message_delete(msg):
    if msg.author.bot: return
    ch = bot.get_channel(LOG_CH)
    if ch:
        emb = discord.Embed(title="🗑️ رسالة محذوفة", color=discord.Color.red())
        emb.add_field(name="العضو:", value=msg.author.mention).add_field(name="الروم:", value=msg.channel.mention)
        emb.add_field(name="المحتوى:", value=msg.content or "*صورة/ملف*", inline=False)
        await ch.send(embed=emb)

@bot.event
async def on_raw_message_edit(p):
    ch = bot.get_channel(LOG_CH)
    if not ch or (p.data.get("author") and p.data["author"].get("bot")): return
    old = p.cached_message.content if p.cached_message else "*رسالة قديمة*"
    new = p.data.get("content", "*مرفقات*")
    if old == new: return
    emb = discord.Embed(title="📝 رسالة معدلة", color=discord.Color.orange())
    emb.add_field(name="العضو:", value=f"<@{p.data['author']['id']}>").add_field(name="الروم:", value=ch.mention)
    emb.add_field(name="القديم:", value=old, inline=False).add_field(name="الجديد:", value=new, inline=False)
    await ch.send(embed=emb)

# --- الأوامر ---
@bot.command()
async def vouch(ctx, *, message: str = None):
    if "🟡" not in ctx.channel.name or not message:
        return await ctx.send("❌ يرجى كتابة التقييم داخل روم 🟡.", delete_after=5)
    await ctx.message.delete()
    await ctx.send(f"📬 {ctx.author.mention} اختر النجوم:", view=RatingButtons(message, ctx.author))

@bot.command()
@commands.has_permissions(manage_channels=True)
async def طلب(ctx):
    if "ticket" in ctx.channel.name.lower():
        await ctx.channel.edit(name="طلب-عميل-🔵")
        await ctx.message.delete()

@bot.command(aliases=["شكوه"])
@commands.has_permissions(manage_channels=True)
async def شكوة(ctx):
    if "ticket" in ctx.channel.name.lower():
        await ctx.channel.edit(name="شكوة-عميل-🔴")
        await ctx.message.delete()

@bot.command()
@commands.has_permissions(manage_channels=True)
async def تمارسال(ctx):
    if "ticket" in ctx.channel.name.lower() or "طلب" in ctx.channel.name.lower():
        await ctx.channel.edit(name="طلب-عميل-🟢")
        await ctx.message.delete()

bot.run(os.getenv("DISCORD_TOKEN"))
