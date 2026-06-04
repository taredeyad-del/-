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

# ----------------- إعدادات البوت والصلاحيات -----------------
# ⚠️ تم تفعيل صلاحية الأعضاء (members) لكي يتمكن البوت من معرفة دخولهم للسيرفر
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  
bot = commands.Bot(command_prefix="!", intents=intents)

# ✅ إيدي روم التقييمات الخاص بك
VOUCH_CHANNEL_ID = 1511668692889370735  

# ✅ ⚠️ ضَع هنا إيدي (ID) روم الترحيب الذي تريد إرسال رسائل الدخول فيه
WELCOME_CHANNEL_ID = 1511571690294083716  


# ----------------- نظام الترحيب بالأعضاء -----------------
@bot.event
async def on_member_join(member):
    # جلب قناة الترحيب المحددة
    welcome_channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if welcome_channel:
        # إرسال رسالة الترحيب المطلوبة مع منشن للعضو
        await welcome_channel.send(f"أهلاً بك {member.mention} نورت السيرفر! ✨")


# ----------------- كلاس الأزرار الخاص بالتقييمات -----------------
class RatingButtons(discord.ui.View):
    def __init__(self, user_message, author):
        super().__init__(timeout=120) 
        self.user_message = user_message
        self.author = author

    async def process_rating(self, interaction: discord.Interaction, stars: int):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("❌ | هذه الأزرار ليست لك!", ephemeral=True)
            return

        vouch_channel = bot.get_channel(VOUCH_CHANNEL_ID)
        if not vouch_channel:
            await interaction.response.send_message("❌ | لم يتم العثور على قناة التقييمات العامة.", ephemeral=True)
            return

        stars_string = "⭐" * stars + "☆" * (5 - stars)

        embed = discord.Embed(
            title="Customer Rating",
            description=f"{stars_string} {stars}/5\n\n{self.user_message}\n\n**Buyer:** {self.author.mention} ({self.author.name})",
            color=discord.Color.from_rgb(255, 215, 0)
        )
        
        embed.set_author(name="BSELL STORE", icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
        embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else self.author.avatar.url)
        embed.set_footer(text="BSELL STORE • Verified Purchase", icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
        
        await vouch_channel.send(embed=embed)
        await interaction.response.edit_message(content=f"✅ تم إرسال تقييمك بنجاح في {vouch_channel.mention}!", view=None)
        self.stop()

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
    print(f"✅ البوت جاهز ويعمل بكامل ميزاته باسم: {bot.user}")

@bot.command(name="vouch")
async def vouch(ctx, *, message: str = None):
    if "🟡" not in ctx.channel.name:
        await ctx.send("❌ | لا يمكنك التقييم هنا! هذا الأمر متاح فقط داخل غرف الشراء المخصصة والمغلقة بـ 🟡.", delete_after=5)
        await ctx.message.delete()
        return

    if message is None or message.strip() == "":
        await ctx.send("❌ | يرجى كتابة التقييم بعد الأمر. مثال: `!vouch متجر أسطوري وسريع`", delete_after=5)
        await ctx.message.delete()
        return

    await ctx.message.delete()

    view = RatingButtons(user_message=message, author=ctx.author)
    await ctx.send(f"📬 {ctx.author.mention}، يرجى اختيار عدد النجوم لتقييمك أدناه لإرساله:", view=view)

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    await bot.process_commands(message)

bot.run(os.getenv("DISCORD_TOKEN"))
