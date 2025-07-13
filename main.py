import os
import logging
import sqlite3
from telegram import Update, Document
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from utils import parse_blacklist_file, ensure_database, insert_records, search_blacklist

TOKEN = os.getenv("TELEGRAM_TOKEN")

# 初始化資料庫
ensure_database()

# 記錄 log
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# /start 指令
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("嗨，我是黑名單機器人！請使用 /查詢 或傳送名單檔案上傳。")

# 查詢黑名單指令
async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("請輸入：/查詢 姓名 身分證字號")
        return

    name = context.args[0]
    id_number = context.args[1]
    result = search_blacklist(id_number)

    if result:
        await update.message.reply_text(f"⚠️ 發現黑名單：\n\n姓名：{result[1]}\n身分證：{result[2]}\n狀態：{result[3]}")
    else:
        await update.message.reply_text("✅ 沒有查到此人黑名單紀錄")

# 處理檔案上傳
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document: Document = update.message.document
    file = await context.bot.get_file(document.file_id)
    file_path = f"/tmp/{document.file_name}"
    await file.download_to_drive(file_path)

    try:
        records = parse_blacklist_file(file_path)
        insert_records(records)
        await update.message.reply_text(f"✅ 已成功匯入 {len(records)} 筆資料！")
    except Exception as e:
        await update.message.reply_text(f"❌ 上傳失敗：{str(e)}")

# 建立 bot 應用程式
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("查詢", check))
app.add_handler(MessageHandler(filters.Document.ALL, handle_document))

if __name__ == "__main__":
    print("✅ Bot 正在啟動中...")
    app.run_polling()
