import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
import os

# --- إعداد الويب ---
app = Flask("")
@app.route("/")
def home(): return "Bot is Alive"
def run_web(): app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
Thread(target=run_web).start()

# --- إعداد البوت ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# القنوات
VOUCH_CH = 1511668692889370735
LOG_CH = 1512027662665777152

@bot.event
async def on_ready():
    print(f"✅ البوت جاهز: {bot.user}")
    # إرسال رسالة واحدة فقط عند التشغيل بدلاً من التكرار
    log_channel = bot.get_channel(LOG_CH)
    if log_channel:
        await log_channel.send("🤖 البوت يعمل الآن وبدأ الاستقبال...")

# --- نظام التقييم ---
class RatingButtons(discord.ui.View):
    def __init__(self, author):
        super().__init__(timeout=120)
        self.author = author

    async def send_rating(self, interaction, stars):
        vouch = bot.get_channel(VOUCH_CH)
        embed = discord.Embed(title="تقييم جديد", description=f"التقييم: {'⭐' * stars}", color=discord.Color.gold())
        embed.add_field(name="من", value=interaction.user.mention, inline=False)
        embed.add_field(name="لـ", value=self.author.mention, inline=False)
        if vouch: await vouch.send(embed=embed)
        await interaction.response.send_message("تم إرسال تقييمك بنجاح", ephemeral=True)

    @discord.ui.button(label="⭐⭐⭐⭐⭐", style=discord.ButtonStyle.green)
    async def five_star(self, i, b): await self.send_rating(i, 5)

@bot.command()
async def تقييم(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title="قيّم العضو", description=f"اختر تقييمك لـ {member.mention}", color=discord.Color.pink())
    await ctx.send(embed=embed, view=RatingButtons(member))

# --- أوامر التعديل (تحتاج صلاحية Manage Channels في الـ Portal) ---
@bot.command()
async def طلب(ctx): 
    await ctx.channel.edit(name="🟢・طلب")
    await ctx.send("✅ تم تحديث الحالة")

@bot.command(name="شكوى")
async def شكوى(ctx): 
    await ctx.channel.edit(name="🔴・شكوى")
    await ctx.send("✅ تم تحديث الحالة")

@bot.event
async def on_message_delete(message):
    if message.author.bot: return
    log = bot.get_channel(LOG_CH)
    if log:
        embed = discord.Embed(title="رسالة محذوفة", color=discord.Color.red())
        embed.add_field(name="الكاتب", value=message.author.mention, inline=False)
        embed.add_field(name="الرسالة", value=message.content, inline=False)
        await log.send(embed=embed)

bot.run(os.getenv("DISCORD_TOKEN"))
