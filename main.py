import discord
from discord.ext import commands, tasks
import os

intents = discord.Intents.default()
intents.message_content, intents.members = True, True
bot = commands.Bot(command_prefix="!", intents=intents)

# إيديات القنوات الخاصة بسيرفرك
WELCOME_CH, VOUCH_CH, SLEEP_CH, LOG_CH = 1511571690294083716, 1511668692889370735, 1511557359800025088, 1512027662665777152

class RatingButtons(discord.ui.View):
    def __init__(self, msg, auth):
        super().__init__(timeout=120)
        self.msg, self.auth = msg, auth

    async def rate(self, interaction: discord.Interaction, stars: int):
        if interaction.user.id != self.auth.id:
            return await interaction.response.send_message("❌ ليست لك!", ephemeral=True)
        
        ch = bot.get_channel(VOUCH_CH)
        embed = discord.Embed(title="Customer Rating", description=f"{'⭐'*stars}{'☆'*(5-stars)} {stars}/5\n\n{self.msg}\n\n**Buyer:** {self.auth.mention}", color=0xFFD700)
        embed.set_author(name="BSELL STORE", icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
        embed.set_footer(text="BSELL STORE • Verified Purchase")
        
        await ch.send(embed=embed)
        await interaction.response.edit_message(content=f"✅ تم الإرسال في {ch.mention}!", view=None)
        self.stop()

    @discord.ui.button(label="1 ⭐")
    async def s1(self, ix, b): await self.rate(ix, 1)
    @discord.ui.button(label="2 ⭐")
    async def s2(self, ix, b): await self.rate(ix, 2)
    @discord.ui.button(label="3 ⭐")
    async def s3(self, ix, b): await self.rate(ix, 3)
    @discord.ui.button(label="4 ⭐")
    async def s4(self, ix, b): await self.rate(ix, 4)
    @discord.ui.button(label="5 ⭐", style=discord.ButtonStyle.success)
    async def s5(self, ix, b): await self.rate(ix, 5)

@tasks.loop(seconds=10)
async def keep_alive():
    ch = bot.get_channel(SLEEP_CH)
    if ch: await ch.send("🤖 البوت نشط...")

@bot.event
async def on_ready():
    print(f"✅ جاهز: {bot.user}")
    if not keep_alive.is_running(): keep_alive.start()

@bot.event
async def on_member_join(m):
    ch = bot.get_channel(WELCOME_CH)
    if ch: await ch.send(f"أهلاً بك {m.mention} نورت السيرفر! ✨")

@bot.event
async def on_message_delete(msg):
    if msg.author.bot: return
    ch = bot.get_channel(LOG_CH)
    if ch:
        emb = discord.Embed(title="🗑️ رسالة محذوفة", color=discord.Color.red())
        emb.add_field(name="العضو:", value=msg.author.mention).add_field(name="الروم:", value=msg.channel.mention)
        emb.add_field(name="المحتوى:", value=msg.content or "*صورة/ملف*", inline=False)
        await ch.send(embed=emb)

@bot.event
async def on_raw_message_edit(p):
    ch = bot.get_channel(LOG_CH)
    if not ch or (p.data.get("author") and p.data["author"].get("bot")): return
    old = p.cached_message.content if p.cached_message else "*رسالة قديمة*"
    new = p.data.get("content", "*مرفقات*")
    if old == new: return
    emb = discord.Embed(title="📝 رسالة معدلة", color=discord.Color.orange())
    emb.add_field(name="العضو:", value=f"<@{p.data['author']['id']}>").add_field(name="الروم:", value=ch.mention)
    emb.add_field(name="القديم:", value=old, inline=False).add_field(name="الجديد:", value=new, inline=False)
    await ch.send(embed=emb)

@bot.command(name="vouch")
async def vouch(ctx, *, message: str = None):
    if "🟡" not in ctx.channel.name or not message:
        return await ctx.send("❌ يرجى كتابة التقييم داخل روم 🟡.", delete_after=5)
    await ctx.message.delete()
    await ctx.send(f"📬 {ctx.author.mention} اختر النجوم:", view=RatingButtons(message, ctx.author))

async def change_name(ctx, name, msg):
    if "ticket" not in ctx.channel.name.lower(): return
    await ctx.channel.edit(name=name)
    await ctx.send(msg)
    await ctx.message.delete()

@bot.command(name="طلب")
@commands.has_permissions(manage_channels=True)
async def o(ctx): await change_name(ctx, "طلب-عميل-🔵", "🔵 تم تغيير الاسم لطلب عميل.")

@bot.command(name="شكوة")
@commands.has_permissions(manage_channels=True)
async def c(ctx): await change_name(ctx, "شكوة-عميل-🔴", "🔴 تم تغيير الاسم لشكوى عميل.")

@bot.command(name="تمارسال")
@commands.has_permissions(manage_channels=True)
async def s(ctx):
    if "ticket" in ctx.channel.name or "طلب" in ctx.channel.name:
        await ctx.channel.edit(name="طلب-عميل-🟢")
        await ctx.send("🟢 تم الشحن والإرسال.")
        await ctx.message.delete()

@bot.event
async def on_message(m):
    if not m.author.bot: await bot.process_commands(m)

bot.run(os.getenv("DISCORD_TOKEN"))
