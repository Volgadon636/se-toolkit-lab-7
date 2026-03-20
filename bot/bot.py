import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def handle_test(command: str) -> str:
    from handlers.commands import handle_start, handle_help, handle_health, handle_labs, handle_scores
    from services.llm_router import route

    parts = command.strip().split(maxsplit=1)
    cmd = parts[0]
    arg = parts[1] if len(parts) > 1 else ""

    if cmd == "/start":
        return handle_start()
    elif cmd == "/help":
        return handle_help()
    elif cmd == "/health":
        return handle_health()
    elif cmd == "/labs":
        return handle_labs()
    elif cmd == "/scores":
        return handle_scores(arg)
    elif cmd.startswith("/"):
        return f"❓ Unknown command: {cmd}. Use /help to see available commands."
    else:
        return route(command)


if __name__ == "__main__":
    if "--test" in sys.argv:
        idx = sys.argv.index("--test")
        command = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else "/start"
        print(handle_test(command))
        sys.exit(0)

    from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    from handlers.commands import handle_start, handle_help, handle_health, handle_labs, handle_scores
    from services.llm_router import route
    from config import BOT_TOKEN

    async def start(update, context):
        keyboard = [
            [InlineKeyboardButton("📋 Labs", callback_data="/labs"),
             InlineKeyboardButton("❤️ Health", callback_data="/health")],
            [InlineKeyboardButton("📊 Scores lab-04", callback_data="/scores lab-04"),
             InlineKeyboardButton("❓ Help", callback_data="/help")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(handle_start(), reply_markup=reply_markup)

    async def help_cmd(update, context):
        await update.message.reply_text(handle_help())

    async def health(update, context):
        await update.message.reply_text(handle_health())

    async def labs(update, context):
        await update.message.reply_text(handle_labs())

    async def scores(update, context):
        arg = " ".join(context.args) if context.args else ""
        await update.message.reply_text(handle_scores(arg))

    async def handle_message(update, context):
        text = update.message.text
        response = route(text)
        await update.message.reply_text(response)

    async def handle_callback(update, context):
        query = update.callback_query
        await query.answer()
        cmd = query.data
        parts = cmd.strip().split(maxsplit=1)
        c = parts[0]
        arg = parts[1] if len(parts) > 1 else ""
        if c == "/labs":
            resp = handle_labs()
        elif c == "/health":
            resp = handle_health()
        elif c == "/scores":
            resp = handle_scores(arg)
        elif c == "/help":
            resp = handle_help()
        else:
            resp = route(cmd)
        await query.edit_message_text(resp)

    from telegram.ext import CallbackQueryHandler
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("health", health))
    app.add_handler(CommandHandler("labs", labs))
    app.add_handler(CommandHandler("scores", scores))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
