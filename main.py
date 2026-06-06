import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
import os

app = Flask("")
@app.route("/")
def home(): return "Bot is Alive"
def run_web(): app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
Thread(target=run_web).start()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

VOUCH_CH = 1511668692889370735
LOG_CH = 1512027662665777152

# دالة حذف الرسالة (يجب أن يكون للبوت صلاحية Manage Messages)
async def try_delete(ctx):
    try:
        await ctx.message.delete()
    except:
        pass

# نظام الأزرار (النجمة الواحدة حتى الخمسة)
class RatingButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)

    async def send_vouch(self, interaction, stars):
        vouch_channel = bot.get_channel(VOUCH_CH)
        if vouch_channel:
            embed = discord.Embed(title="تقييم جديد ✅", color=discord.Color.gold())
            embed.add_field(name="التقييم", value="⭐" * stars, inline=False)
            embed.add_field(name="العميل", value=interaction.user.mention, inline=False)
            await vouch_channel.send(embed=embed)
        await interaction.response.send_message(f"✅ تم إرسال تقييمك ({stars} نجوم).", ephemeral=True)

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

# الأمر الوحيد للتقييم
@bot.command()
async def vouch(ctx):
    await try_delete(ctx)
    embed = discord.Embed(title="قيّم خدماتنا", description="اختر عدد النجوم:", color=discord.Color.pink())
    await ctx.send(embed=embed, view=RatingButtons())

@bot.command()
async def طلب(ctx): 
    await try_delete(ctx)
    await ctx.channel.edit(name="🟢・طلب")

@bot.command()
async def شكوى(ctx): 
    await try_delete(ctx)
    await ctx.channel.edit(name="🔴・شكوى")

@bot.command()
async def حذفروم(ctx):
    await try_delete(ctx)
    await ctx.channel.delete()

@bot.event
async def on_ready(): print(f"✅ البوت متصل: {bot.user}")

bot.run(os.getenv("DISCORD_TOKEN"))
