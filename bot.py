import discord
from discord.ext import commands
import os
import hashlib
import aiofiles
import asyncio

bot = commands.Bot(command_prefix="!")

# 简单的内存存储（重启后丢失）
# 实际应用应该用数据库
stored_files = {}  # file_id -> {"path": 路径, "password_hash": 哈希值, "uploader": 用户ID, "filename": 原名}

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

@bot.event
async def on_ready():
    print(f"✅ 已登录为 {bot.user}")
    await bot.sync_commands()
    print("✅ 斜杠指令已同步")

# ---------- 上传指令 ----------
@bot.slash_command(name="upload", description="上传文件并设置密码")
async def upload(
    ctx: discord.ApplicationContext,
    file: discord.Option(discord.Attachment, "要上传的文件"),
    password: discord.Option(str, "下载时需要输入的密码")
):
    await ctx.defer()  # 防止超时
    # 生成唯一文件ID
    file_id = str(hash(str(ctx.author.id) + file.filename + str(os.urandom(8))))
    # 保存文件到本地（Railway 的临时存储）
    save_path = f"/tmp/{file_id}_{file.filename}"
    await file.save(save_path)
    # 存储元数据
    stored_files[file_id] = {
        "path": save_path,
        "password_hash": hash_password(password),
        "uploader": ctx.author.id,
        "filename": file.filename
    }
    await ctx.respond(f"✅ 文件已上传！\n文件ID: `{file_id}`\n请妥善保管此ID和密码。", ephemeral=True)

# ---------- 下载指令 ----------
@bot.slash_command(name="download", description="通过文件ID和密码下载文件")
async def download(
    ctx: discord.ApplicationContext,
    file_id: discord.Option(str, "上传时获得的文件ID"),
    password: discord.Option(str, "文件设置的密码")
):
    await ctx.defer()
    # 检查文件是否存在
    if file_id not in stored_files:
        await ctx.respond("❌ 文件ID不存在。", ephemeral=True)
        return
    info = stored_files[file_id]
    # 验证密码
    if hash_password(password) != info["password_hash"]:
        await ctx.respond("❌ 密码错误。", ephemeral=True)
        return
    # 发送文件
    try:
        file = discord.File(info["path"], filename=info["filename"])
        await ctx.respond(file=file)
    except Exception as e:
        await ctx.respond(f"❌ 发送文件失败: {e}", ephemeral=True)

# 启动机器人
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    print("错误：未设置 DISCORD_TOKEN 环境变量")
    exit(1)
bot.run(TOKEN)
