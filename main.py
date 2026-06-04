import discord
from discord.ext import commands
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# 🌍 خادم ويب وهمي لمنع ظهور خطأ المنافذ (Ports) في منصة Render
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Bot is running perfectly!')

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    print(f"🌍 Web server started on port {port}")
    server.serve_forever()

web_thread = threading.Thread(target=run_web_server)
web_thread.daemon = True
web_thread.start()

# ----------------- إعدادات البوت -----------------
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ✅ إيدي روم التقييمات الخاص بك
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
    if message is None or message.strip() == "":
        await ctx.send("❌ | يرجى كتابة التقييم بعد الأمر. مثال: `!vouch سريع ومضمون`", delete_after=5)
        await ctx.message.delete()
        return

    # 3. جلب قناة التقييمات العامة
    vouch_channel = bot.get_channel(VOUCH_CHANNEL_ID)
    if not vouch_channel:
        await ctx.send("❌ | لم يتم العثور على قناة التقييمات العامة، يرجى التأكد من صلاحيات البوت لرؤية الروم.", delete_after=5)
        return

    # 4. بناء رسالة الإمبيد الاحترافية (تم تعديل النجوم إلى الأرقام 12345)
    embed = discord.Embed(
        title="Customer Rating",
        description=f"12345 5/5\n\n{message}\n\n*— Anonymous Customer*",
        color=discord.Color.from_rgb(255, 215, 0) # اللون الأصفر الجانبي المضيء
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
    
    # 5. إرسال التقييم وحذف الرسالة الأصلية لتنظيف الشات
    await vouch_channel.send(embed=embed)
    await ctx.send(f"✅ {ctx.author.mention} شكرًا لتقييمك! تم بنجاح نقل التقييم إلى {vouch_channel.mention}.", delete_after=5)
    await ctx.message.delete()

# تشغيل البوت
bot.run(os.getenv("DISCORD_TOKEN"))
