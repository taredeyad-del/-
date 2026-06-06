import discord
from discord.ext import commands, tasks
import os

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# القنوات (تأكد من تحديث الـ IDs إذا لزم الأمر)
VOUCH_CH = 1511668692889370735
LOG_CH = 1512027662665777152
LOOP_CH = 1511557359800025088

async def delete_ctx(ctx):
    try: await ctx.message.delete()
    except: pass

# --- نظام اللوق للرسائل المحذوفة ---
@bot.event
async def on_message_delete(message):
    if message.author.bot: return
    log_channel = bot.get_channel(LOG_CH)
    if log_channel:
        embed = discord.Embed(title="رسالة محذوفة", color=discord.Color.red())
        embed.add_field(name="الكاتب", value=message.author.mention, inline=False)
        embed.add_field(name="المحتوى", value=message.content or "لا يوجد نص", inline=False)
        await log_channel.send(embed=embed)

# --- نظام الرسالة الدورية ---
@tasks.loop(seconds=10)
async def periodic_message():
    channel = bot.get_channel(LOOP_CH)
    if channel:
        await channel.send("💡 **تذكير:** لا تنسَ تقييم خدماتنا باستخدام أمر `!vouch`!")

@bot.event
async def on_ready():
    print(f"✅ البوت متصل: {bot.user}")
    if not periodic_message.is_running():
        periodic_message.start()

# --- كلاس الأزرار ---
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

# --- الأوامر ---
@bot.command()
async def vouch(ctx, *, review_text: str = "بدون تعليق"):
    await delete_ctx(ctx)
    embed = discord.Embed(title="قيّم خدماتنا", description=f"التقييم: {review_text}\n\nاختر عدد النجوم:", color=discord.Color.pink())
    await ctx.send(embed=embed, view=RatingButtons(review_text))

@bot.command()
async def طلب(ctx): 
    await delete_ctx(ctx)
    await ctx.channel.edit(name="طلب • 🔵")

@bot.command()
async def تم_استلام_الطلب(ctx): 
    await delete_ctx(ctx)
    await ctx.channel.edit(name="طلب • 🟢")

@bot.command()
async def تم_إرسال_الطلب(ctx): 
    await delete_ctx(ctx)
    await ctx.channel.edit(name="طلب • 🟡")

@bot.command()
async def حذفروم(ctx):
    await delete_ctx(ctx)
    await ctx.channel.delete()

bot.run(os.getenv("DISCORD_TOKEN"))
