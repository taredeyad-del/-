import os
import discord
from discord.ext import commands
from discord import ui
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# إعداد الصلاحيات الأساسية للبوت لقراءة الرسائل
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ⚠️ ضع هنا آيدي روم التقييمات العامة (التي ستظهر فيها جميع التقييمات والمعدل)
VOUCH_CHANNEL_ID = 123456789012345678  

# متغيرات لحفظ إحصائيات التقييم المتعادل (الحسابي) في ذاكرة البوت
total_stars = 0.0
total_vouches = 0

# القائمة المنسدلة لاختيار النجوم من 0 إلى 5
class StarSelect(ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="⭐ 5/5 - ممتاز جداً", value="5"),
            discord.SelectOption(label="⭐ 4/5 - جيد جداً", value="4"),
            discord.SelectOption(label="⭐ 3/5 - مقبول", value="3"),
            discord.SelectOption(label="⭐ 2/5 - سيء", value="2"),
            discord.SelectOption(label="⭐ 1/5 - سيء جداً", value="1"),
            discord.SelectOption(label="⭐ 0/5 - لا أنصح به", value="0"),
        ]
        super().__init__(placeholder="اختر تقييمك من 0 إلى 5...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        # بعد اختيار النجوم، نفتح للمشتري نافذة كود لكتابة رأيه بالتفصيل
        await interaction.response.send_modal(VouchTextModal(stars_numeric=int(self.values[0])))

# النافذة المنبثقة لكتابة الرأي والنص
class VouchTextModal(ui.Modal, title="اكتب تجربتك 💬"):
    def __init__(self, stars_numeric):
        super().__init__()
        self.stars_numeric = stars_numeric # حفظ الرقم المختار (من 0 إلى 5)
        
        self.feedback = ui.TextInput(
            label="اكتب تقييمك وتجربتك هنا:",
            style=discord.TextStyle.paragraph,
            placeholder="الخدمة سريعة وممتازة، أنصح بالتعامل معه...",
            required=True,
            max_length=300
        )
        self.add_item(self.feedback)

    async def on_submit(self, interaction: discord.Interaction):
        global total_stars, total_vouches
        
        # البحث عن الروم العامة للتقييمات
        channel = bot.get_channel(VOUCH_CHANNEL_ID)
        if not channel:
            await interaction.response.send_message("❌ لم يتم العثور على روم التقييمات، تأكد من تغيير الآيدي داخل الكود.", ephemeral=True)
            return

        # تحديث الحسابات للتقييم المتعادل
        total_stars += self.stars_numeric
        total_vouches += 1
        average_rating = total_stars / total_vouches # حساب المعدل المتعادل

        # رسم النجوم بناءً على الاختيار للجمالية
        star_emojis = "⭐" * self.stars_numeric if self.stars_numeric > 0 else "❌"

        # تصميم شكل التقييم الحالي (Embed) الذي سيُنشر في الروم العامة للجميع
        embed = discord.Embed(title="📥 تقييم جديد للمتجر!", color=discord.Color.green())
        embed.add_field(name="👤 العميل المشتري:", value=interaction.user.mention, inline=False)
        embed.add_field(name="⭐ تقييمه للطلب:", value=f"{star_emojis} ({self.stars_numeric}/5)", inline=True)
        embed.add_field(name="💬 رأي العميل وتجربته:", value=self.feedback.value, inline=False)
        
        # إضافة جزء التقييم المتعادل والإحصائيات العامة للمتجر أسفل الرسالة
        embed.add_field(
            name="📊 إحصائيات المتجر (تقييم متعادل):", 
            value=f"📈 معدل التقييم الحالي: **{average_rating:.1f}/5**\n👥 إجمالي عدد المقيّمين: **{total_vouches}**", 
            inline=False
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)

        # إرسال الرسالة إلى الروم العامة ليراها الجميع
        await channel.send(embed=embed)
        
        # رسالة شكر مخفية تظهر للمشتري وحده كإشعار
        await interaction.response.send_message("✅ بيض الله وجهك! تم تسجيل تقييمك وحساب المعدل بنجاح.", ephemeral=True)

# إنشاء الزر التفاعلي الذي يظهر تحت الرسالة الأساسية
class VouchView(ui.View):
    def __init__(self):
        super().__init__(timeout=None) # الزر سيبقى شغالاً دائماً ولن يتوقف

    @ui.button(label="اضغط هنا لكتابة تقييمك ⭐", style=discord.ButtonStyle.success)
    async def vouch_button(self, interaction: discord.Interaction, button: ui.Button):
        # عند الضغط على الزر، تظهر قائمة الاختيارات من 0 إلى 5
        view = ui.View()
        view.add_item(StarSelect())
        await interaction.response.send_message("الرجاء اختيار عدد النجوم من القائمة أدناه لتحديد تقييمك للمنتج:", view=view, ephemeral=True)

@bot.event
async def on_ready():
    print(f"✅ البوت شغال الآن باسم: {bot.user}")

# أمر المشرفين لإنشاء رسالة التقييم في روم الشراء
@bot.command()
@commands.has_permissions(administrator=True)
async def vouch(ctx):
    embed = discord.Embed(
        title="🛒 صندوق تقييم المنتجات والخدمات",
        description="عميلنا العزيز، إذا قمت بشراء منتج أو خدمة منا، يسعدنا جداً أن تترك تقييمك لدعم المتجر بالضغط على الزر الأخضر بالأسفل!",
        color=discord.Color.blue()
    )
    # إرسال الرسالة المنسقة مع الزر الأخضر
    await ctx.send(embed=embed, view=VouchView())

# كود إضافي لإبقاء البوت شغالاً على السيرفرات السحابية كـ Web Service
class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is Running!")

def run_server():
    server = HTTPServer(('0.0.0.0', 8080), MyServer)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

# تشغيل البوت عبر التوكن المحفوظ في المتغيرات
bot.run(os.environ['DISCORD_TOKEN'])
