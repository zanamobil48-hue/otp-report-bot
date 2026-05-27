import os
import json
import asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8721901672:AAF9GbmbHRAfho35VSXbUFKq2SAONBJFlQ0"
GROUP_ID = -1003837328950
REPORT_CHAT_ID = -1003837328950

sales_data = {}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != GROUP_ID:
        return
    
    text = update.message.text if update.message.text else ""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    categories = {
        "validation": "this has been sent to the validation team",
        "free_social_14": "فری سۆشیاڵ",
        "red_monthly": "پاکێجی مانگانەی RED",
        "red_25000": "RED 25,000",
        "use_15": "یووز 15",
        "use_30": "یووز 30",
        "3month_red": "پاکێجی ٣ مانگی"
    }
    
    for key, keyword in categories.items():
        if keyword in text:
            if key not in sales_data:
                sales_data[key] = []
            sales_data[key].append(now)

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not sales_data:
        await update.message.reply_text("هیچ داتایەک نییە!")
        return
    
    names = {
        "validation": "Validation",
        "free_social_14": "فری سۆشیاڵ 14 ڕۆژ",
        "red_monthly": "RED مانگانە",
        "red_25000": "RED 25,000",
        "use_15": "یووز 15",
        "use_30": "یووز 30",
        "3month_red": "RED 3 مانگ"
    }
    
    msg = "📊 ڕاپۆرتی فرۆشت:\n\n"
    total = 0
    for key, times in sales_data.items():
        count = len(times)
        total += count
        msg += f"• {names.get(key, key)}: {count} دانە\n"
    
    msg += f"\n✅ کۆی گشتی: {total} دانە"
    await update.message.reply_text(msg)

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sales_data.clear()
    await update.message.reply_text("✅ داتاکان سڕایەوە!")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("report", report))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
