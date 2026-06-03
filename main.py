import os
import discord
from discord.ext import commands
from discord import ui
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import re  # مكتبة للتحقق من الأسماء والأرقام بدقة

# إعداد الصلاحيات الكاملة للبوت
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

# تحديد بادئة الأوامر
bot = commands.Bot(command_prefix="!", intents=intents)

# آيدي روم التقييمات العامة الخاص بسيرفرك (التي ستظهر فيها جميع التقييمات)
VOUCH_CHANNEL_ID = 1511668692889370735  

# متغيرات التقييم المتعادل
total_stars = 0.0
total_vouches = 0

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
        await interaction.response.send_modal(VouchTextModal(stars_numeric=int(self.values)))

class VouchTextModal(ui.Modal, title="اكتب تجربتك 💬"):
    def __init__(self, stars_numeric):
        super().__init__()
        self.stars_numeric = stars_numeric
        
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
        
        channel = bot.get_channel(VOUCH_CHANNEL_ID)
        if not channel:
            await interaction.response.send_message("❌ لم يتم العثور على روم التقييمات العامة، تأكد من صلاحيات البوت داخل السيرفر.", ephemeral=True)
            return

        total_stars += self.stars_numeric
        total_vouches += 1
        average_rating = total_stars / total_vouches

        star_emojis = "⭐" * self.stars_numeric if self.stars_numeric > 0 else "❌"

        embed = discord.Embed(title="📥 تقييم جديد للمتجر!", color=discord.Color.green())
        embed.add_field(name="👤 العميل المشتري:", value=interaction.user.mention, inline=False)
        embed.add_field(name="⭐ تقييمه للطلب:", value=f"{star_emojis} ({self.stars_numeric}/5)", inline=True)
        embed.add_field(name="💬 رأي العميل وتجربته:", value=self.feedback.value, inline=False)
        embed.add_field(
            name="📊 إحصائيات المتجر (تقييم متعادل):", 
            value=f"📈 معدل التقييم الحالي: **{average_rating:.1f}/5**\n👥 إجمالي عدد المقيّمين: **{total_vouches}**", 
            inline=False
        )
        if interaction.user.display_avatar:
            embed.set_thumbnail(url=interaction.user.display_avatar.url)

        await channel.send(embed=embed)
        await interaction.response.send_message("✅ بيض الله وجهك! تم تسجيل تقييمك وحساب المعدل بنجاح وسيظهر في روم التقييمات العامة.", ephemeral=True)

class VouchView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="اضغط هنا لكتابة تقييمك ⭐", style=discord.ButtonStyle.success)
    async def vouch_button(self, interaction: discord.Interaction, button: ui.Button):
        view = ui.View()
        view.add_item(StarSelect())
        await interaction.response.send_message("الرجاء اختيار عدد النجوم من القائمة أدناه لتحديد تقييمك للمنتج:", view=view, ephemeral=True)

@bot.event
async def on_ready():
    print(f"✅ البوت شغال الآن باسم: {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)

# أمر التقييم مع شرط التحقق من اسم الروم (ticket-أرقام)
@bot.command()
@commands.has_permissions(administrator=True)
async def vouch(ctx):
    # استخدام التعبير النمطي (Regex) للتأكد أن اسم الروم يبدأ بـ ticket- متبوعاً بأرقام فقط
    if re.match(r"^ticket-\d+$", ctx.channel.name):
        embed = discord.Embed(
            title="🛒 صندوق تقييم المنتجات والخدمات",
            description="عميلنا العزيز، يسعدنا جداً أن تترك تقييمك لدعم المتجر بالضغط على الزر الأخضر بالأسفل!",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed, view=VouchView())
    else:
        # رسالة تنبيه سرية للإداري تفيد بأن الروم غير مدعومة
        await ctx.reply("❌ هذا الأمر مخصص للعمل داخل رومات التيكيت فقط التي تبدأ بـ `ticket-` متبوعة بأرقام.", delete_after=5)

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is Running!")

def run_server():
    server = HTTPServer(('0.0.0.0', 8080), MyServer)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

bot.run(os.environ['DISCORD_TOKEN'])
