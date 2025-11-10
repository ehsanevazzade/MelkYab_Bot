# bot.py
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ContextTypes, ConversationHandler, filters
)
from config import TOKEN, CITY_CODES, CATEGORIES
from database import init_db
from scraper import scrape_divar_once

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CITY, CATEGORY = range(2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[KeyboardButton(city)] for city in CITY_CODES.keys()]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        'سلام! به ربات ملک‌یاب خوش اومدی\nشهر رو انتخاب کن:',
        reply_markup=reply_markup
    )
    return CITY

async def city_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = update.message.text.strip()
    if city not in CITY_CODES:
        await update.message.reply_text('شهر نامعتبر!')
        return CITY
    
    context.user_data['city_name'] = CITY_CODES[city]
    keyboard = [[KeyboardButton(cat)] for cat in CATEGORIES.keys()]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text('دسته‌بندی رو انتخاب کن:', reply_markup=reply_markup)
    return CATEGORY

async def category_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    category = update.message.text.strip()
    if category not in CATEGORIES:
        await update.message.reply_text('دسته نامعتبر!')
        return CATEGORY
    
    context.user_data['subcat'] = CATEGORIES[category]
    await update.message.reply_text('در حال جستجو...')

    ads = scrape_divar_once(
        city_name=context.user_data['city_name'],
        subcat=context.user_data['subcat'],
        limit=25
    )
    
    if not ads:
        await update.message.reply_text('آگهی جدیدی پیدا نشد!')
    else:
        for ad in ads[:10]:
            text = f"""
عنوان: {ad['title']}
قیمت: {ad['price']}
لینک: {ad['url']}
            """.strip()
            await update.message.reply_text(text)
    
    await update.message.reply_text('جستجو تموم شد! دوباره /start بزن.')
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('لغو شد.')
    return ConversationHandler.END

def main():
    init_db()
    app = Application.builder().token(TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, city_handler)],
            CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, category_handler)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    app.add_handler(conv_handler)
    print("ربات در حال اجراست...")
    app.run_polling()

if __name__ == '__main__':
    main()