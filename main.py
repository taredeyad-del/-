import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ⚠️ ضَع هنا إيدي (ID) روم التقييمات العام (الذي تظهر فيه كل التقييمات منسقة)
VOUCH_CHANNEL_ID = 1511668692889370735  

@bot.event
async def on_ready():
    print(f"✅ بوت التقييمات الذكي جاهز ويعمل باسم: {bot.user}")

@bot.command(name="vouch")
async def vouch(ctx, *, message: str = None):
    # 1. التحقق من وجود الإيموجي الأصفر 🟡 في اسم الروم الحالي
    if "🟡" not in ctx.channel.name:
        await ctx.send("❌ | لا يمكنك التقييم هنا! هذا الأمر متاح فقط داخل غرف الشراء المخصصة والمغلقة بـ 🟡.", delete_after=5)
        await ctx.message.delete()
        return

    # 2. التأكد من أن العضو كتب نص التقييم
    if not message:
        await ctx.send("❌ | يرجى كتابة التقييم بعد الأمر. مثال: `!vouch سريع ومضمون`", delete_after=5)
        await ctx.message.delete()
        return

    # 3. جلب قناة التقييمات العامة
    vouch_channel = bot.get_channel(VOUCH_CHANNEL_ID)
    if not vouch_channel:
        await ctx.send("❌ | لم يتم العثور على قناة التقييمات العامة، يرجى التأكد من الـ ID في الكود.", delete_after=5)
        return

    # 4. بناء رسالة الإمبيد الاحترافية (نفس ستايل الصورة)
    embed = discord.Embed(
        title="Customer Rating",
        description=f"⭐⭐⭐⭐⭐ 5/5\n\n{message}\n\n*— {ctx.author.name}*",
        color=discord.Color.from_rgb(255, 215, 0) # لون أصفر جانبى مطابق للصورة
    )
    
    embed.set_author(
        name="bl4nk Market", 
        icon_url=ctx.guild.icon.url if ctx.guild.icon else None
    )
    
    embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else ctx.author.avatar.url)
    
    embed.set_footer(
        text="bl4nk Market • Verified Purchase", 
        icon_url=ctx.guild.icon.url if ctx.guild.icon else None
    )
    
    # 5. إرسال التقييم وحذف الرسالة الأصلية
    await vouch_channel.send(embed=embed)
    await ctx.send(f"✅ {ctx.author.mention} شكرًا لتقييمك! تم بنجاح نقل التقييم إلى {vouch_channel.mention}.", delete_after=5)
    await ctx.message.delete()

# تشغيل البوت
bot.run(os.getenv("DISCORD_TOKEN"))
