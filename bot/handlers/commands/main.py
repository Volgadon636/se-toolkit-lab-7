import httpx
from config import LMS_API_URL, LMS_API_KEY


def handle_start() -> str:
    return "👋 Welcome to the LMS Bot! Use /help to see available commands."


def handle_help() -> str:
    return (
        "Available commands:\n"
        "/start — Welcome message\n"
        "/help — Show this help\n"
        "/health — Check backend status\n"
        "/labs — List available labs\n"
        "/scores <lab-id> — Show scores for a lab"
    )


def handle_health() -> str:
    try:
        r = httpx.get(f"{LMS_API_URL}/health", headers={"Authorization": f"Bearer {LMS_API_KEY}"}, timeout=5)
        return f"✅ Backend is up! Status: {r.status_code}"
    except Exception as e:
        return f"❌ Backend is down: {e}"


def handle_labs() -> str:
    return "🚧 Not implemented yet"


def handle_scores(lab_id: str) -> str:
    return f"🚧 Scores for {lab_id} — not implemented yet"
