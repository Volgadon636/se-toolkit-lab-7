import sys


def handle_test(command: str) -> str:
    from handlers.commands import handle_start, handle_help, handle_health, handle_labs, handle_scores
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
    else:
        return f"❓ Unknown command: {cmd}"


if __name__ == "__main__":
    if "--test" in sys.argv:
        idx = sys.argv.index("--test")
        command = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else "/start"
        print(handle_test(command))
        sys.exit(0)

    from telegram.ext import ApplicationBuilder, CommandHandler
    from handlers.commands import handle_start, handle_help, handle_health, handle_labs, handle_scores
    from config import BOT_TOKEN

    async def start(update, context):
        await update.message.reply_text(handle_start())

    async def help_cmd(update, context):
        await update.message.reply_text(handle_help())

    async def health(update, context):
        await update.message.reply_text(handle_health())

    async def labs(update, context):
        await update.message.reply_text(handle_labs())

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("health", health))
    app.add_handler(CommandHandler("labs", labs))
    app.run_polling()
