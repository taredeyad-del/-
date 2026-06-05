import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
import os

app = Flask("")

@app.route("/")
def home():
    return "Bot is alive"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    Thread(target=run_web).start()


intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

WELCOME_CH = 1511571690294083716
VOUCH_CH = 1511668692889370735
SLEEP_CH = 1511557359800025088
LOG_CH = 1512027662665777152

bot_deleted_messages = set()


@bot.event
async def on_ready():
    print(f"✅ البوت اشتغل: {bot.user}")


@bot.event
async def on_member_join(member):
    channel = bot.get_channel(WELCOME_CH)
    if channel:
        embed = discord.Embed(
            title="Welcome!",
            description=f"هلا والله {member.mention} نورت السيرفر",
            color=discord.Color.pink()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await channel.send(embed=embed)


@bot.event
async def on_message_delete(message):
    if message.author == bot.user:
        return

    if message.id in bot_deleted_messages:
        bot_deleted_messages.remove(message.id)
        return

    if message.author.bot:
        return

    log = bot.get_channel(LOG_CH)
    if log:
        embed = discord.Embed(title="رسالة محذوفة", color=discord.Color.red())
        embed.add_field(name="الكاتب", value=message.author.mention, inline=False)
        embed.add_field(name="القناة", value=message.channel.mention, inline=False)
        embed.add_field(
            name="الرسالة",
            value=message.content if message.content else "لا يوجد نص",
            inline=False
        )
        await log.send(embed=embed)


@bot.command()
@commands.has_permissions(manage_messages=True)
async def حذف(ctx, amount: int = 1):
    deleted = await ctx.channel.purge(limit=amount + 1)

    for msg in deleted:
        bot_deleted_messages.add(msg.id)

    msg = await ctx.send(f"تم حذف {amount} رسالة")
    bot_deleted_messages.add(msg.id)
    await msg.delete(delay=3)


@bot.command()
async def طلب(ctx):
    await ctx.channel.edit(name="🟢・طلب")
    await ctx.send("تم تحويل التذكرة إلى طلب")


@bot.command(name="شكوى")
async def شكوى(ctx):
    await ctx.channel.edit(name="🔴・شكوى")
    await ctx.send("تم تحويل التذكرة إلى شكوى")


@bot.command(name="شكوة")
async def شكوة(ctx):
    await ctx.channel.edit(name="🔴・شكوى")
    await ctx.send("تم تحويل التذكرة إلى شكوى")


@bot.command()
async def نوم(ctx):
    channel = bot.get_channel(SLEEP_CH)
    if channel:
        await channel.send(f"{ctx.author.mention} راح ينام، تصبحون على خير")
    else:
        await ctx.send("قناة النوم غير موجودة")


class RatingButtons(discord.ui.View):
    def __init__(self, author):
        super().__init__(timeout=120)
        self.author = author

    @discord.ui.button(label="⭐", style=discord.ButtonStyle.gray)
    async def one_star(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.send_rating(interaction, 1)

    @discord.ui.button(label="⭐⭐", style=discord.ButtonStyle.gray)
    async def two_star(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.send_rating(interaction, 2)

    @discord.ui.button(label="⭐⭐⭐", style=discord.ButtonStyle.gray)
    async def three_star(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.send_rating(interaction, 3)

    @discord.ui.button(label="⭐⭐⭐⭐", style=discord.ButtonStyle.gray)
    async def four_star(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.send_rating(interaction, 4)

    @discord.ui.button(label="⭐⭐⭐⭐⭐", style=discord.ButtonStyle.green)
    async def five_star(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.send_rating(interaction, 5)

    async def send_rating(self, interaction, stars):
        vouch = bot.get_channel(VOUCH_CH)

        embed = discord.Embed(
            title="تقييم جديد",
            description=f"التقييم: {'⭐' * stars}",
            color=discord.Color.gold()
        )
        embed.add_field(name="من", value=interaction.user.mention, inline=False)
        embed.add_field(name="لـ", value=self.author.mention, inline=False)

        if vouch:
            await vouch.send(embed=embed)

        await interaction.response.send_message("تم إرسال تقييمك بنجاح", ephemeral=True)


@bot.command()
async def تقييم(ctx, member: discord.Member = None):
    member = member or ctx.author

    embed = discord.Embed(
        title="قيّم العضو",
        description=f"اختر تقييمك لـ {member.mention}",
        color=discord.Color.pink()
    )

    await ctx.send(embed=embed, view=RatingButtons(member))


@bot.command()
async def سلام(ctx):
    await ctx.send(f"هلا {ctx.author.mention}")


@bot.command()
async def اوامر(ctx):
    embed = discord.Embed(title="أوامر البوت", color=discord.Color.blue())
    embed.add_field(name="!طلب", value="يغير اسم الروم إلى 🟢・طلب", inline=False)
    embed.add_field(name="!شكوى", value="يغير اسم الروم إلى 🔴・شكوى", inline=False)
    embed.add_field(name="!شكوة", value="نفس أمر الشكوى", inline=False)
    embed.add_field(name="!تقييم @user", value="يفتح أزرار تقييم", inline=False)
    embed.add_field(name="!نوم", value="يرسل رسالة في قناة النوم", inline=False)
    embed.add_field(name="!حذف رقم", value="يحذف رسائل بدون ما تطلع في اللوق", inline=False)
    embed.add_field(name="!سلام", value="يرد عليك", inline=False)
    await ctx.send(embed=embed)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return

    if isinstance(error, commands.MissingPermissions):
        await ctx.send("ما عندك صلاحية تستخدم هذا الأمر")
        return

    raise error


keep_alive()
bot.run(os.getenv("DISCORD_TOKEN"))
