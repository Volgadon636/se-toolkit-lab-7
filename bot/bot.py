import sys
from handlers.commands import handle_start, handle_help, handle_health, handle_labs, handle_scores


def handle_test(command: str) -> str:
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
