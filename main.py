import discord
from discord.ext import commands
import os

# إعداد البوت
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# ضع هنا IDs القنوات الصحيحة الخاصة بك
VOUCH_CH = 1511668692889370735

# دالة حذف الرسائل المساعدة
async def delete_ctx(ctx):
    try: await ctx.message.delete()
    except: pass

# كلاس الأزرار مع حذف رسالة الأزرار بعد التقييم
class RatingButtons(discord.ui.View):
    def __init__(self, review_text):
        super().__init__(timeout=120)
        self.review_text = review_text

    async def send_vouch(self, interaction, stars):
        vouch_channel = bot.get_channel(VOUCH_CH)
        if vouch_channel:
            embed = discord.Embed(title="تقييم جديد ✅", color=discord.Color.gold())
            embed.add_field(name="التقييم", value="⭐" * stars, inline=False)
            embed.add_field(name="التعليق", value=self.review_text, inline=False)
            embed.add_field(name="العميل", value=interaction.user.mention, inline=False)
            await vouch_channel.send(embed=embed)
        
        await interaction.response.send_message(f"✅ تم رصد التقييم! شكراً لثقتكم بنا.", ephemeral=True)
        # هنا يتم حذف رسالة الأزرار بعد الضغط
        try: await interaction.message.delete()
        except: pass

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

# أمر الـ vouch المتكامل
@bot.command()
async def vouch(ctx, *, review_text: str = "لا يوجد تعليق"):
    await delete_ctx(ctx)
    embed = discord.Embed(title="قيّم خدماتنا", description=f"التقييم: {review_text}\n\nاختر عدد النجوم:", color=discord.Color.pink())
    await ctx.send(embed=embed, view=RatingButtons(review_text))

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
