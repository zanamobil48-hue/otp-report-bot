import logging
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = "8721901672:AAF9GbmbHRAfho35VSXbUFKq2SAONBJFlQ0"

sales_data = []
validation_numbers = []

CATEGORIES = {
    "validation": "validation team",
    "free_social_14": "free social",
    "red_monthly": "RED monthly",
    "red_25000": "RED 25,000",
    "use_15": "use 15",
    "use_30": "use 30",
    "3month_red": "3month red"
}

NAMES = {
    "validation": "Validation",
    "free_social_14": "Free Social 14",
    "red_monthly": "RED 15000",
    "red_25000": "RED 25,000",
    "use_15": "Use 15",
    "use_30": "Use 30",
    "3month_red": "RED 3 Month"
}

def make_report(filtered, val_numbers):
    counts = {}
    for s in filtered:
        counts[s["type"]] = counts.get(s["type"], 0) + 1
    if counts:
        msg = "📊 Report:\n\n"
        total = 0
        for key, count in counts.items():
            total += count
            msg += f"- {NAMES.get(key, key)}: {count}\n"
        msg += f"\n✅ Total: {total}"
    else:
        msg = "No data!"
    keyboard = [[InlineKeyboardButton(f"📋 SIM activated ({len(val_numbers)})", callback_data="show_validation")]]
    return msg, keyboard

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    text = update.message.text
    if "validation team" in text:
        phone = re.search(r'07\d{8}', text)
        if phone:
            validation_numbers.append({"number": phone.group(), "time": datetime.now()})
        sales_data.append({"type": "validation", "time": datetime.now()})
        return
    if context.user_data.get("waiting_custom"):
        parts = text.strip().split()
        if len(parts) == 2:
            try:
                start = datetime.strptime(parts[0], "%Y-%m-%d")
                end = datetime.strptime(parts[1], "%Y-%m-%d").replace(hour=23, minute=59)
                filtered = [s for s in sales_data if start <= s["time"] <= end]
                val = [v for v in validation_numbers if start <= v["time"] <= end]
                msg, keyboard = make_report(filtered, val)
                context.user_data["waiting_custom"] = False
                await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
                return
            except:
                await update.message.reply_text("Error! Example:\n2026-05-01 2026-05-28")
                return
    for key, keyword in CATEGORIES.items():
        if keyword in text:
            sales_data.append({"type": key, "time": datetime.now()})
            break

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    now = datetime.now()
    if query.data == "show_validation":
        if not validation_numbers:
            await query.edit_message_text("No SIM activated!")
            return
        msg = "📋 SIM activated:\n\n"
        for i, v in enumerate(validation_numbers, 1):
            msg += f"{i}. {v['number']} - {v['time'].strftime('%m-%d %H:%M')}\n"
        await query.edit_message_text(msg)
        return
    if query.data == "daily":
        start = now.replace(hour=0, minute=0, second=0)
        filtered = [s for s in sales_data if s["time"] >= start]
        val = [v for v in validation_numbers if v["time"] >= start]
    elif query.data == "weekly":
        start = now - timedelta(days=7)
        filtered = [s for s in sales_data if s["time"] >= start]
        val = [v for v in validation_numbers if v["time"] >= start]
    elif query.data == "monthly":
        start = now - timedelta(days=30)
        filtered = [s for s in sales_data if s["time"] >= start]
        val = [v for v in validation_numbers if v["time"] >= start]
    elif query.data == "all":
        filtered = sales_data
        val = validation_numbers
    elif query.data == "custom":
        context.user_data["waiting_custom"] = True
        await query.edit_message_text("Write date:\n2026-05-01 2026-05-28")
        return
    msg, keyboard = make_report(filtered, val)
    await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📅 Daily", callback_data="daily"),
         InlineKeyboardButton("📆 Weekly", callback_data="weekly")],
        [InlineKeyboardButton("🗓 Monthly", callback_data="monthly"),
         InlineKeyboardButton("📊 All", callback_data="all")],
        [InlineKeyboardButton("✏️ Custom", callback_data="custom")]
    ]
    await update.message.reply_text("Which report?", reply_markup=InlineKeyboardMarkup(keyboard))

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sales_data.clear()
    validation_numbers.clear()
    await update.message.reply_text("✅ Cleared!")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("report", report))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
