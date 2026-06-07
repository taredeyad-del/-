import discord
from discord.ext import commands
from discord import ui
import sqlite3
import os

# --- إعداد قاعدة البيانات ---
db = sqlite3.connect("invoices.db", check_same_thread=False)
cursor = db.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS invoices (id TEXT PRIMARY KEY, embed_data TEXT)")
db.commit()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# --- الكلاسات الخاصة بالتفاعل ---
class InvoiceSelect(ui.Select):
    def __init__(self, rows):
        options = [discord.SelectOption(label=f"Invoice #{r[0]}", value=str(r[0])) for r in rows]
        super().__init__(placeholder="اختر فاتورة...", options=options)
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"✅ تم اختيار الفاتورة {self.values[0]}. أرسل 'رابط الفاتورة' الآن.", ephemeral=True)
        # تخزين الفاتورة المختارة في الـ View
        self.view.selected_id = self.values[0]

class InvoiceView(ui.View):
    def __init__(self, rows):
        super().__init__()
        self.add_item(InvoiceSelect(rows))
        self.selected_id = None

# --- الأوامر ---
@bot.command()
async def سحب(ctx):
    channel = bot.get_channel(1513129732378726440)
    count = 0
    async for message in channel.history(limit=50):
        if message.embeds:
            embed = message.embeds[0]
            if "Invoice" in (embed.title or ""):
                inv_id = embed.title.replace("Invoice #", "")
                cursor.execute("INSERT OR REPLACE INTO invoices VALUES (?, ?)", (inv_id, str(embed.to_dict())))
                db.commit()
                count += 1
    await ctx.send(f"✅ تم سحب {count} فاتورة!")

@bot.command()
async def فاتورة(ctx):
    cursor.execute("SELECT * FROM invoices")
    rows = cursor.fetchall()
    if not rows:
        await ctx.send("لا توجد فواتير.", ephemeral=True)
        return
    
    view = InvoiceView(rows)
    await ctx.send("قائمة الفواتير المتاحة:", view=view, ephemeral=True)

@bot.event
async def on_ready():
    print(f"✅ البوت {bot.user} جاهز للعمل!")

bot.run(os.getenv("DISCORD_TOKEN"))
