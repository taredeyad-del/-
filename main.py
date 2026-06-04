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

# قائمة الأزرار التفاعلية لاختيار عدد النجوم
class RatingButtons(discord.ui.View):
    def __init__(self, user_message, author):
        super().__init__(timeout=60) # تختفي الأزرار بعد دقيقة إذا لم يتم الاختيار
        self.user_message = user_message
        self.author = author

    async def process_rating(self, interaction: discord.Interaction, stars: int):
        # التأكد من أن الذي يضغط على الزر هو نفس الشخص صاحب التقييم
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("❌ | هذه الأزرار ليست لك!", ephemeral=True)
            return

        vouch_channel = bot.get_channel(VOUCH_CHANNEL_ID)
        if not vouch_channel:
            await interaction.response.send_message("❌ | لم يتم العثور على قناة التقييمات العامة.", ephemeral=True)
            return

        # إنشاء النجوم بناءً على اختيار العضو
        stars_string = "⭐" * stars + "☆" * (5 - stars)

        # بناء رسالة الإمبيد الاحترافية النهائية
        embed = discord.Embed(
            title="Customer Rating",
            description=f"{stars_string} {stars}/5\n\n{self.user_message}\n\n*— Anonymous Customer*",
            color=discord.Color.from_rgb(255, 215, 0)
        )
        
        embed.set_author(name="bl4nk Market", icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
        embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else self.author.avatar.url)
        embed.set_footer(text="bl4nk Market • Verified Purchase", icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
        
        # إرسال التقييم النهائي للقناة العامة
        await vouch_channel.send(embed=embed)
        
        # تحديث رسالة البوت وحذف الأزرار وتأكيد النجاح
        await interaction.response.edit_message(content=f"✅ تم إرسال تقييمك بنجاح في {vouch_channel.mention}!", view=None)
        self.stop()

    # أزرار التقييم من 1 إلى 5
    @discord.ui.button(label="1 ⭐", style=discord.ButtonStyle.secondary, custom_id="star_1")
    async def star_1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.process_rating(interaction, 1)

    @discord.ui.button(label="2 ⭐", style=discord.ButtonStyle.secondary, custom_id="star_2")
    async def star_2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.process_rating(interaction, 2)

    @discord.ui.button(label="3 ⭐", style=discord.ButtonStyle.secondary, custom_id="star_3")
    async def star_3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.process_rating(interaction, 3)

    @discord.ui.button(label="4 ⭐", style=discord.ButtonStyle.secondary, custom_id="star_4")
    async def star_4(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.process_rating(interaction, 4)

    @discord.ui.button(label="5 ⭐", style=discord.ButtonStyle.success, custom_id="star_5")
    async def star_5(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.process_rating(interaction, 5)

@bot.event
async def on_ready():
    print(f"✅ بوت التقييمات التلقائي جاهز ويعمل باسم: {bot.user}")

# الاستماع لأي رسالة يكتبها الأعضاء بدون الحاجة لأمر نصي
@bot.event
async def on_message(message):
    # تجاهل رسائل البوتات لعدم حدوث تكرار
    if message.author.bot:
        return

    # التحقق من وجود الإيموجي الأصفر 🟡 في اسم الروم الحالي
    if "🟡" in message.channel.name:
        # حفظ نص الرسالة ليكون هو التقييم
        user_text = message.content
        
        # التأكد من أن الرسالة ليست فارغة
        if user_text.strip() != "":
            # حذف رسالة العضو فوراً لتنظيف الشات
            await message.delete()

            # إرسال أزرار اختيار النجوم للعضو
            view = RatingButtons(user_message=user_text, author=message.author)
            await message.channel.send(f"📬 {message.author.mention}، يرجى اختيار عدد النجوم لتقييمك أدناه لإرساله:", view=view, delete_after=60)
            return

    # السماح للأوامر الأخرى بالعمل بشكل طبيعي في بقية السيرفر
    await bot.process_commands(message)

# تشغيل البوت
bot.run(os.getenv("DISCORD_TOKEN"))
