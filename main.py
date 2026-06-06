import discord
from discord.ext import commands
import os

# إعداد البوت
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

VOUCH_CH = 1511668692889370735

# دالة حذف الرسالة الموحدة
async def delete_ctx(ctx):
    try:
        await ctx.message.delete()
    except:
        pass

# نظام الأزرار
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

# الأوامر مع دالة الحذف
@bot.command()
async def vouch(ctx):
    await delete_ctx(ctx)
    embed = discord.Embed(title="قيّم خدماتنا", description="اختر عدد النجوم:", color=discord.Color.pink())
    await ctx.send(embed=embed, view=RatingButtons())

@bot.command()
async def طلب(ctx): 
    await delete_ctx(ctx)
    await ctx.channel.edit(name="🟢・طلب")

@bot.command()
async def شكوى(ctx): 
    await delete_ctx(ctx)
    await ctx.channel.edit(name="🔴・شكوى")

@bot.command()
async def حذفروم(ctx):
    await delete_ctx(ctx)
    await ctx.channel.delete()

bot.run(os.getenv("DISCORD_TOKEN"))
