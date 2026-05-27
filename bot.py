import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = "8721901672:AAF9GbmbHRAfho35VSXbUFKq2SAONBJFlQ0"
GROUP_ID = -1003837328950

sales_data = {}

CATEGORIES = {
    "validation": "validation team",
    "free_social_14": "فری سۆشیاڵ",
    "red_monthly": "پاکێجی مانگانەی RED",
    "red_25000": "RED 25,000",
    "use_15": "یووز 15",
    "use_30": "یووز 30",
    "3month_red": "پاکێجی ٣ مانگی"
}

NAMES = {
    "validation": "Validation",
    "free_social_14": "فری سۆشیاڵ 14 ڕۆژ",
    "red_monthly": "RED مانگانە 15000",
    "red_25000": "RED 25,000",
    "use_15": "یووز 15",
    "use_30": "یووز 30",
    "3month_red": "RED 3 مانگ"
}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    text = update.message.text
    for key, keyword in CATEGORIES.items():
        if keyword in text:
            if key not in sales_data:
                sales_data[key] = 0
            sales_data[key] += 1
            break

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not sales_data:
        await update.message.reply_text("هیچ داتایەک نییە!")
        return
    msg = "📊 ڕاپۆرتی فرۆشت:\n\n"
    total = 0
    for key, count in sales_data.items():
        total += count
        msg += f"• {NAMES.get(key, key)}: {count} دانە\n"
    msg += f"\n✅ کۆی گشتی: {total} دانە"
    await update.message.reply_text(msg)

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sales_data.clear()
    await update.message.reply_text("✅ داتاکان سڕایەوە!")

if __name__ == "__main__":
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("report", report))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.run_polling(allowed_updates=Update.ALL_TYPES)
