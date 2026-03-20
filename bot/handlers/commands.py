import httpx
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import LMS_API_URL, LMS_API_KEY


def _headers():
    return {"Authorization": f"Bearer {LMS_API_KEY}"}


def handle_start() -> str:
    return "👋 Welcome to the LMS Bot! Use /help to see available commands."


def handle_help() -> str:
    return (
        "Available commands:\n"
        "/start — Welcome message\n"
        "/help — Show this help\n"
        "/health — Check backend status and item count\n"
        "/labs — List available labs\n"
        "/scores <lab-id> — Show per-task pass rates for a lab (e.g. /scores lab-04)"
    )


def handle_health() -> str:
    try:
        r = httpx.get(f"{LMS_API_URL}/items/", headers=_headers(), timeout=5)
        r.raise_for_status()
        items = r.json()
        return f"✅ Backend is healthy. {len(items)} items available."
    except httpx.ConnectError as e:
        return f"❌ Backend error: connection refused ({LMS_API_URL}). Check that the services are running."
    except httpx.HTTPStatusError as e:
        return f"❌ Backend error: HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down."
    except Exception as e:
        return f"❌ Backend error: {e}"


def handle_labs() -> str:
    try:
        r = httpx.get(f"{LMS_API_URL}/items/", headers=_headers(), timeout=5)
        r.raise_for_status()
        items = r.json()
        labs = [i for i in items if i.get("type") == "lab" or i.get("parent_id") is None]
        if not labs:
            # fallback: show unique lab prefixes from all items
            seen = {}
            for i in items:
                lid = i.get("lab_id") or i.get("id", "")
                name = i.get("lab_name") or i.get("name", "")
                if lid and lid not in seen:
                    seen[lid] = name
            if seen:
                lines = [f"- {name} ({lid})" for lid, name in sorted(seen.items())]
                return "Available labs:\n" + "\n".join(lines)
            return "No labs found."
        lines = [f"- {i.get('name', i.get('id', ''))}" for i in labs]
        return "Available labs:\n" + "\n".join(lines)
    except httpx.ConnectError:
        return f"❌ Backend error: connection refused ({LMS_API_URL}). Check that the services are running."
    except Exception as e:
        return f"❌ Backend error: {e}"


def handle_scores(lab_id: str) -> str:
    if not lab_id:
        return "❌ Please provide a lab ID. Example: /scores lab-04"
    try:
        r = httpx.get(f"{LMS_API_URL}/analytics/pass-rates", params={"lab": lab_id}, headers=_headers(), timeout=5)
        r.raise_for_status()
        data = r.json()
        if not data:
            return f"No data found for {lab_id}. Make sure the lab ID is correct (e.g. lab-04)."
        lines = []
        for item in data:
            name = item.get("task_name") or item.get("name") or item.get("item_id", "Unknown")
            rate = item.get("pass_rate") or item.get("rate") or 0
            attempts = item.get("attempts") or item.get("total") or 0
            lines.append(f"- {name}: {rate:.1f}% ({attempts} attempts)")
        return f"Pass rates for {lab_id}:\n" + "\n".join(lines)
    except httpx.ConnectError:
        return f"❌ Backend error: connection refused ({LMS_API_URL}). Check that the services are running."
    except httpx.HTTPStatusError as e:
        return f"❌ Backend error: HTTP {e.response.status_code}. Lab '{lab_id}' may not exist."
    except Exception as e:
        return f"❌ Backend error: {e}"
