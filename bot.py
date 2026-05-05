import discord
from discord.ext import commands
import os

# 创建机器人实例（允许斜杠指令）
bot = commands.Bot(command_prefix="!")  # 前缀备用，但主要用斜杠指令

@bot.event
async def on_ready():
    print(f"✓ 已登录为 {bot.user}")
    # 手动同步斜杠指令到 Discord（可选，有时候会自动同步）
    await bot.sync_commands()
    print("✓ 斜杠指令已同步")

# ---------- 添加你的斜杠指令在这里 ----------
@bot.slash_command(name="ping", description="测试机器人的响应速度")
async def ping(ctx: discord.ApplicationContext):
    """简单的 ping/pong 命令"""
    latency = round(bot.latency * 1000)
    await ctx.respond(f"🏓 Pong！延迟 {latency} 毫秒")

@bot.slash_command(name="hello", description="打个招呼")
async def hello(ctx: discord.ApplicationContext):
    await ctx.respond(f"你好 {ctx.author.name}！")

# -----------------------------------------

# 启动机器人（从环境变量读取 Token，更安全）
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    print("错误：未设置 DISCORD_TOKEN 环境变量")
    exit(1)

bot.run(TOKEN)
