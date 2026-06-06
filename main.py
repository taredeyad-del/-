import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
import os

# --- إعداد الويب 24/7 ---
app = Flask("")
@app.route("/")
def home(): return "Bot is Alive"
def run_web(): app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
Thread(target=run_web).start()

# --- إعداد البوت ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

VOUCH_CH = 1511668692889370735
LOG_CH = 1512027662665777152

# --- 1. نظام التقييم بالأزرار (5 نجوم) ---
class RatingButtons(discord.ui.View):
    def __init__(self, member):
        super().__init__(timeout=120)
        self.member = member

    async def send_vouch(self, interaction, stars):
        vouch_channel = bot.get_channel(VOUCH_CH)
        if vouch_channel:
            embed = discord.Embed(title="تقييم جديد ✅", color=discord.Color.gold())
            embed.add_field(name="التقييم", value="⭐" * stars, inline=False)
            embed.add_field(name="العميل", value=interaction.user.mention, inline=False)
            embed.add_field(name="التقييم لـ", value=self.member.mention, inline=False)
            await vouch_channel.send(embed=embed)
        await interaction.response.send_message(f"✅ تم إرسال تقييمك ({stars} نجوم) للروم بنجاح.", ephemeral=True)

    @discord.ui.button(label="⭐", style=discord.ButtonStyle.secondary)
    async def s1(self, i, b): await self.send_vouch(i, 1)
    @discord.ui.button(label="⭐⭐", style=discord.ButtonStyle.secondary)
    async def s2(self, i, b): await self.send_vouch(i, 2)
    @discord.ui.button(label="⭐⭐⭐", style=discord.ButtonStyle.secondary)
    async def s3(self, i, b): await self.send_vouch(i, 3)
    @discord.ui.button(label="⭐⭐⭐⭐", style=discord.ButtonStyle.secondary)
    async def s4(self, i, b): await self.send_vouch(i, 4)
    @discord.ui.button(label="⭐⭐⭐⭐⭐", style=discord.ButtonStyle.success)
    async def s5(self, i, b): await self.send_vouch(i, 5)

# --- 2. الأوامر ---
@bot.command()
async def vouch(ctx):
    await ctx.send("✅ **تم رصد التقييم! شكراً لثقتكم بنا.**")

@bot.command()
async def تقييم(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title="اختر عدد النجوم للتقييم", description=f"قيّم العضو {member.mention}", color=discord.Color.pink())
    await ctx.send(embed=embed, view=RatingButtons(member))

@bot.command()
async def طلب(ctx): await ctx.channel.edit(name="🟢・طلب")
@bot.command()
async def شكوى(ctx): await ctx.channel.edit(name="🔴・شكوى")
@bot.command()
async def حذفروم(ctx): await ctx.channel.delete()

# --- 3. اللوق ---
@bot.event
async def on_message_delete(message):
    if message.author.bot: return
    log = bot.get_channel(LOG_CH)
    if log:
        embed = discord.Embed(title="رسالة محذوفة", color=discord.Color.red())
        embed.add_field(name="الكاتب", value=message.author.mention, inline=False)
        embed.add_field(name="الرسالة", value=message.content or "لا يوجد نص", inline=False)
        await log.send(embed=embed)

@bot.event
async def on_ready(): print(f"✅ البوت متصل: {bot.user}")

bot.run(os.getenv("DISCORD_TOKEN"))
