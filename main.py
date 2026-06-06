import discord
from discord.ext import commands, tasks
import os
from flask import Flask
from threading import Thread

# --- إعداد نظام الإبقاء على البوت نشطاً ---
app = Flask('')
@app.route('/')
def home(): return "البوت يعمل الآن!"
def run_flask(): app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run_flask)
    t.start()

# --- إعداد البوت ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# --- إعدادات القنوات والرتب ---
VOUCH_CH = 1511668692889370735
LOG_CH = 1512027662665777152
LOOP_CH = 1511557359800025088
AUTO_ROLE_ID = 1511674988602855566

async def delete_ctx(ctx):
    try: await ctx.message.delete()
    except: pass

# --- الأحداث ---
@bot.event
async def on_member_join(member):
    role = member.guild.get_role(AUTO_ROLE_ID)
    if role:
        try: await member.add_roles(role)
        except Exception as e: print(f"خطأ في إعطاء الرتبة: {e}")

@bot.event
async def on_message_delete(message):
    if message.author.bot: return
    log_channel = bot.get_channel(LOG_CH)
    if log_channel:
        embed = discord.Embed(title="رسالة محذوفة", color=discord.Color.red())
        embed.add_field(name="الكاتب", value=message.author.mention, inline=False)
        embed.add_field(name="المحتوى", value=message.content or "لا يوجد نص", inline=False)
        await log_channel.send(embed=embed)

# --- نظام نبض البوت ---
@tasks.loop(seconds=10)
async def periodic_message():
    channel = bot.get_channel(LOOP_CH)
    if channel:
        await channel.send("✅ **System Status: Online**")

@bot.event
async def on_ready():
    print(f"✅ البوت متصل: {bot.user}")
    if not periodic_message.is_running():
        periodic_message.start()

# --- كلاس الأزرار (نجوم دائمة) ---
class RatingButtons(discord.ui.View):
    def __init__(self, review_text):
        super().__init__(timeout=None)
        self.review_text = review_text

    async def send_vouch(self, interaction, stars):
        vouch_channel = bot.get_channel(VOUCH_CH)
        if vouch_channel:
            embed = discord.Embed(title="تقييم جديد ✅", color=discord.Color.gold())
            embed.add_field(name="التقييم", value="⭐" * stars, inline=False)
            embed.add_field(name="التعليق", value=self.review_text, inline=False)
            embed.add_field(name="العميل", value=interaction.user.mention, inline=False)
            await vouch_channel.send(embed=embed)
        await interaction.response.send_message(f"✅ تم تسجيل تقييمك بـ {stars} نجوم!", ephemeral=True)

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

# --- الأوامر ---
@bot.command()
async def vouch(ctx, *, review_text: str = "بدون تعليق"):
    await delete_ctx(ctx)
    embed = discord.Embed(title="قيّم خدماتنا", description=f"التعليق: {review_text}\nاختر عدد النجوم:", color=discord.Color.pink())
    await ctx.send(embed=embed, view=RatingButtons(review_text))

@bot.command()
async def طلب(ctx): 
    await delete_ctx(ctx)
    try: await ctx.channel.edit(name="طلب-🔵")
    except: pass

@bot.command()
async def تماستلامطلب(ctx): 
    await delete_ctx(ctx)
    try: await ctx.channel.edit(name="طلب-🟢")
    except: pass

@bot.command()
async def تمارسالطلب(ctx): 
    await delete_ctx(ctx)
    try: await ctx.channel.edit(name="طلب-🟡")
    except: pass

@bot.command()
async def حذفروم(ctx):
    await delete_ctx(ctx)
    await ctx.channel.delete()

# --- التشغيل ---
keep_alive()
bot.run(os.getenv("DISCORD_TOKEN"))
