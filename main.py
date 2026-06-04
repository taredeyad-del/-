import discord
from discord.ext import commands, tasks
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import asyncio

# 🌍 خادم ويب وهمي لمنع ظهور خطأ المنافذ (Ports) في منصة Render
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'BSELL STORE Bot is running perfectly!')

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    print(f"🌍 Web server started on port {port}")
    server.serve_forever()

web_thread = threading.Thread(target=run_web_server)
web_thread.daemon = True
web_thread.start()

# ----------------- إعدادات البوت والصلاحيات -----------------
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  
bot = commands.Bot(command_prefix="!", intents=intents)

# ✅ إيديات الرومات الخاصة بسيرفرك معدلة وجاهزة بنسبة 100%
WELCOME_CHANNEL_ID = 1511571690294083716      # روم الترحيب
VOUCH_CHANNEL_ID = 1511668692889370735        # روم التقييمات
ANTI_SLEEP_CHANNEL_ID = 1511557359800025088   # روم منع النوم المخصص (anti sleep bot)
LOG_CHANNEL_ID = 1512027662665777152          # روم السجلات واللوج الموحد


# ----------------- نظام منع النوم التلقائي الذكي (كل 10 ثوانٍ) -----------------
@tasks.loop(seconds=10)
async def keep_alive_ping():
    channel = bot.get_channel(ANTI_SLEEP_CHANNEL_ID)
    if channel:
        try:
            # يرسل رسالة نشاط كل 10 ثوانٍ ويتركها لضمان بقائه أونلاين دائماً في Render
            await channel.send("🤖 البوت نشط حالياً والعمل مستمر...")
        except Exception:
            pass

# ----------------- نظام الترحيب بالأعضاء -----------------
@bot.event
async def on_member_join(member):
    welcome_channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if welcome_channel:
        await welcome_channel.send(f"أهلاً بك {member.mention} نورت السيرفر! ✨")


# ----------------- نظام سجل الرسائل المحذوفة -----------------
@bot.event
async def on_message_delete(message):
    if message.author.bot:
        return

    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        content = message.content if message.content else "*الرسالة لا تحتوي على نص (قد تكون صورة أو إيموجي فقط)*"
        
        embed = discord.Embed(
            title="🗑️ رسالة محذوفة",
            color=discord.Color.red(),
            timestamp=message.created_at
        )
        embed.add_field(name="العضو:", value=f"{message.author.mention} ({message.author.name})", inline=True)
        embed.add_field(name="الروم:", value=message.channel.mention, inline=True)
        embed.add_field(name="المحتوى:", value=content, inline=False)
        
        if message.attachments:
            links = "\n".join([att.url for att in message.attachments])
            embed.add_field(name="المرفقات المحذوفة:", value=links, inline=False)
            
        await log_channel.send(embed=embed)


# ----------------- نظام سجل الرسائل المعدلة -----------------
@bot.event
async def on_message_edit(before, after):
    if before.author.bot or before.content == after.content:
        return

    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        embed = discord.Embed(
            title="📝 رسالة معدلة",
            color=discord.Color.orange(),
            timestamp=after.edited_at if after.edited_at else after.created_at
        )
        embed.add_field(name="العضو:", value=f"{before.author.mention} ({before.author.name})", inline=True)
        embed.add_field(name="الروم:", value=before.channel.mention, inline=True)
        embed.add_field(name="النص القديم:", value=before.content if before.content else "*فارغ*", inline=False)
        embed.add_field(name="النص الجديد:", value=after.content if after.content else "*فارغ*", inline=False)
        
        await log_channel.send(embed=embed)


# ----------------- نظام سجل تغيير الأسماء -----------------
@bot.event
async def on_member_update(before, after):
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if not log_channel:
        return

    if before.nick != after.nick:
        old_nick = before.nick if before.nick else before.name
        new_nick = after.nick if after.nick else after.name
        
        embed = discord.Embed(
            title="👤 تغيير اللقب بالسيرفر",
            color=discord.Color.blue()
        )
        embed.add_field(name="العضو:", value=after.mention, inline=False)
        embed.add_field(name="اللقب القديم:", value=old_nick, inline=True)
        embed.add_field(name="اللقب الجديد:", value=new_nick, inline=True)
        await log_channel.send(embed=embed)


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
    if not keep_alive_ping.is_running():
        keep_alive_ping.start()

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
