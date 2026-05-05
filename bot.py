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

# ---------- 1. 定义文件管理功能 ----------
# 当用户上传文件时，保存并生成密码
@bot.event
async def on_message(message):
    if message.attachments:
        for attachment in message.attachments:
            # 安全警告: 直接从消息附件下载文件到服务器存在安全风险
            # 在实际生产环境中，你需要对文件内容进行安全扫描，并谨慎处理文件路径
            await attachment.save(f"stored_files/{attachment.filename}")
            # 这里需要向数据库存储：文件名、上传者ID、文件路径等
            # 并向上传者返回文件ID
            await message.channel.send(f"文件已收到！文件ID为：{generate_file_id()}")

# 获取文件
@bot.slash_command(name="get_file", description="申请下载文件")
async def get_file(
    ctx,
    file_id: discord.Option(str, "文件ID"),
    requester: discord.Option(discord.Member, "申请者"),
):
    # 检查文件是否存在
    if file_id not in file_database:
        await ctx.respond("文件不存在！", ephemeral=True)
        return
    # 检查申请者是否有权限
    if not has_permission(requester, file_id):
        await ctx.respond("你没有权限下载此文件！", ephemeral=True)
        return
    # 发送文件
    file_path = file_database[file_id]["file_path"]
    file = discord.File(file_path)
    await ctx.respond(file=file)

# 启动机器人（从环境变量读取 Token，更安全）
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    print("错误：未设置 DISCORD_TOKEN 环境变量")
    exit(1)

bot.run(TOKEN)
