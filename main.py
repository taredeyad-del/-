import discord
from discord.ext import commands
from flask import Flask, request, jsonify
from threading import Thread
import os
import sqlite3

# --- إعداد قاعدة البيانات ---
db = sqlite3.connect("invoices.db", check_same_thread=False)
cursor = db.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS invoices (id TEXT PRIMARY KEY, data TEXT)")
db.commit()

# --- إعداد الويب ---
app = Flask("")
@app.route("/webhook/sellauth", methods=["POST"])
def sellauth_webhook():
    data = request.json
    invoice_id = str(data.get("id"))
    # حفظ بيانات الفاتورة في قاعدة البيانات
    cursor.execute("INSERT OR REPLACE INTO invoices VALUES (?, ?)", (invoice_id, str(data)))
    db.commit()
    return jsonify({"status": "success"}), 200

def run_web(): app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
Thread(target=run_web).start()

# --- إعداد البوت ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.command()
async def فاتورة(ctx):
    cursor.execute("SELECT * FROM invoices")
    rows = cursor.fetchall()
    if not rows:
        await ctx.send("لا توجد فواتير محفوظة.")
        return
    for row in rows:
        await ctx.send(f"**Invoice #{row[0]}**\nالبيانات: {row[1][:100]}...")

# --- نظام التقييم التفاعلي (الذي طلبته) ---
@bot.command()
async def vouch(ctx, member: discord.Member):
    await ctx.message.delete()
    msg = await ctx.send(f"يا {member.mention}، يرجى كتابة تعليقك عن الطلب:")

    def check(m):
        return m.author == member and m.channel == ctx.channel

    try:
        comment_msg = await bot.wait_for('message', timeout=60.0, check=check)
        await comment_msg.delete()
        
        embed = discord.Embed(title="✅ تقييم جديد", color=discord.Color.gold())
        embed.add_field(name="العميل", value=member.mention, inline=False)
        embed.add_field(name="التعليق", value=comment_msg.content, inline=False)
        await ctx.send(embed=embed)
        await msg.delete()
    except:
        await msg.delete()

@bot.event
async def on_ready():
    print(f"✅ البوت متصل: {bot.user}")

bot.run(os.getenv("DISCORD_TOKEN"))
