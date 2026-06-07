import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
import os

# --- إعداد الويب ---
app = Flask("")
@app.route("/")
def home(): return "Bot is alive"
def run_web(): app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
Thread(target=run_web).start()

# --- إعداد البوت ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# الثوابت
VOUCH_CH = 1511668692889370735
LOG_CH = 1512027662665777152
OWNER_IDS = [1511553830838468628, 1511553933053661224]
bot_deleted_messages = set()

def is_admin(ctx):
    return ctx.author.id in OWNER_IDS or any(role.id in OWNER_IDS for role in ctx.author.roles)

async def delete_command(ctx):
    try:
        bot_deleted_messages.add(ctx.message.id)
        await ctx.message.delete()
    except: pass

# --- الأوامر الإدارية ---
@bot.command()
@commands.check(is_admin)
async def طلب(ctx): 
    await delete_command(ctx)
    await ctx.channel.edit(name="طلب • 🔵")

@bot.command()
@commands.check(is_admin)
async def تمارسالطلب(ctx): 
    await delete_command(ctx)
    await ctx.channel.edit(name="طلب • 🟡")

@bot.command()
@commands.check(is_admin)
async def تماستلامطلب(ctx): 
    await delete_command(ctx)
    await ctx.channel.edit(name="طلب • 🟢")

@bot.command()
@commands.check(is_admin)
async def شكوى(ctx): 
    await delete_command(ctx)
    await ctx.channel.edit(name="شكوة • 🔴")

@bot.command()
@commands.check(is_admin)
async def اغلاق(ctx): 
    await delete_command(ctx)
    await ctx.channel.edit(name="شكوة • 🟢")

@bot.command()
@commands.check(is_admin)
async def حذفروم(ctx):
    await delete_command(ctx)
    await ctx.channel.delete()

# --- نظام التقييم التفاعلي ---
@bot.command()
async def vouch(ctx, member: discord.Member):
    await delete_command(ctx)
    msg = await ctx.send(f"يا {member.mention}، يرجى كتابة عدد النجوم التي تستحقها (من 1 إلى 5) في هذه القناة.")

    def check(m):
        return m.author == member and m.channel == ctx.channel and m.content.isdigit()

    try:
        response = await bot.wait_for('message', timeout=60.0, check=check)
        stars = int(response.content)
        
        if 1 <= stars <= 5:
            vouch_channel = bot.get_channel(VOUCH_CH)
            if vouch_channel:
                embed = discord.Embed(title="✅ تقييم جديد", color=discord.Color.gold())
                embed.add_field(name="العميل", value=member.mention, inline=False)
                embed.add_field(name="التقييم", value=f"{'⭐' * stars}", inline=False)
                await vouch_channel.send(embed=embed)
            await response.delete()
            await msg.delete()
        else:
            await ctx.send("يرجى إدخال رقم بين 1 و 5 فقط.", delete_after=5)
            await msg.delete()
    except:
        await msg.delete()

# --- اللوج ---
@bot.event
async def on_message_delete(message):
    if message.author.bot or message.id in bot_deleted_messages: return
    log = bot.get_channel(LOG_CH)
    if log:
        embed = discord.Embed(title="رسالة محذوفة", color=discord.Color.red())
        embed.add_field(name="الكاتب", value=message.author.mention, inline=False)
        embed.add_field(name="الرسالة", value=message.content or "لا يوجد نص", inline=False)
        await log.send(embed=embed)

@bot.event
async def on_ready(): print(f"✅ البوت متصل: {bot.user}")

bot.run(os.getenv("DISCORD_TOKEN"))
