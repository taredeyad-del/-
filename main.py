import discord
from discord.ext import commands, tasks
from flask import Flask
from threading import Thread
import os

# --- جزء تشغيل الويب (ضروري لـ Render) ---
app = Flask("")
@app.route("/")
def home(): return "Bot is Online!"
def run_web(): app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
Thread(target=run_web).start()

# --- كود البوت الخاص بك ---
intents = discord.Intents.default()
intents.message_content, intents.members = True, True
bot = commands.Bot(command_prefix="!", intents=intents)

# (ضع الإيديات الخاصة بك هنا)
WELCOME_CH = 1511571690294083716
VOUCH_CH = 1511668692889370735
SLEEP_CH = 1511557359800025088
LOG_CH = 1512027662665777152

class RatingButtons(discord.ui.View):
    def __init__(self, msg, auth):
        super().__init__(timeout=120)
        self.msg, self.auth = msg, auth

    async def rate(self, interaction: discord.Interaction, stars: int):
        if interaction.user.id != self.auth.id:
            return await interaction.response.send_message("❌ ليست لك!", ephemeral=True)
        ch = bot.get_channel(VOUCH_CH)
        embed = discord.Embed(title="Customer Rating", description=f"{'⭐'*stars}{'☆'*(5-stars)} {stars}/5\n\n{self.msg}\n\n**Buyer:** {self.auth.mention}", color=0xFFD700)
        await ch.send(embed=embed)
        await interaction.response.edit_message(content=f"✅ تم الإرسال!", view=None)
        self.stop()

    @discord.ui.button(label="5 ⭐", style=discord.ButtonStyle.success)
    async def s5(self, ix, b): await self.rate(ix, 5)
    # يمكنك إضافة بقية الأزرار (1-4) هنا بنفس الطريقة

@tasks.loop(minutes=5) # تم التغيير لـ 5 دقائق لتجنب السبام
async def keep_alive():
    ch = bot.get_channel(SLEEP_CH)
    if ch: 
        try: await ch.send("🤖 البوت نشط...")
        except: pass

@bot.event
async def on_ready():
    print(f"✅ جاهز: {bot.user}")
    keep_alive.start()

# ... (ضع بقية أحداثك (on_message_delete, on_raw_message_edit, الخ) هنا) ...

bot.run(os.getenv("DISCORD_TOKEN"))
