import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler,CallbackQueryHandler, MessageHandler, filters
from db_conn import bot_token, chat_id
from handler.command import status, device
from handler.menu import start, menu_handler, device_callback

def main():
    app = ApplicationBuilder().token(bot_token).build()

    # monitoring commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, menu_handler))
    app.add_handler(CallbackQueryHandler(device_callback, pattern="^device:"))
    app.add_handler(CommandHandler("device", device))
    app.add_handler(CommandHandler("status", status))

    # menu (text button)
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, menu_handler)
    )

    print("🤖 Bot monitoring + alert berjalan...")
    app.run_polling()

if __name__ == "__main__":
    main()
