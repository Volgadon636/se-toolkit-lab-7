import httpx
import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import LMS_API_URL, LMS_API_KEY, LLM_API_KEY, LLM_API_BASE_URL, LLM_API_MODEL


def _lms_headers():
    return {"Authorization": f"Bearer {LMS_API_KEY}"}


TOOLS = [
    {"type": "function", "function": {"name": "get_items", "description": "List all labs and tasks available in the LMS", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "get_learners", "description": "List enrolled students and their groups", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "get_scores", "description": "Get score distribution (4 buckets) for a lab", "parameters": {"type": "object", "properties": {"lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"}}, "required": ["lab"]}}},
    {"type": "function", "function": {"name": "get_pass_rates", "description": "Get per-task average scores and attempt counts for a lab", "parameters": {"type": "object", "properties": {"lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"}}, "required": ["lab"]}}},
    {"type": "function", "function": {"name": "get_timeline", "description": "Get submissions per day timeline for a lab", "parameters": {"type": "object", "properties": {"lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"}}, "required": ["lab"]}}},
    {"type": "function", "function": {"name": "get_groups", "description": "Get per-group scores and student counts for a lab", "parameters": {"type": "object", "properties": {"lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"}}, "required": ["lab"]}}},
    {"type": "function", "function": {"name": "get_top_learners", "description": "Get top N learners by score for a lab", "parameters": {"type": "object", "properties": {"lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"}, "limit": {"type": "integer", "description": "Number of top learners to return", "default": 5}}, "required": ["lab"]}}},
    {"type": "function", "function": {"name": "get_completion_rate", "description": "Get completion rate percentage for a lab", "parameters": {"type": "object", "properties": {"lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"}}, "required": ["lab"]}}},
    {"type": "function", "function": {"name": "trigger_sync", "description": "Refresh data from autochecker API", "parameters": {"type": "object", "properties": {}}}},
]


def call_tool(name: str, args: dict) -> str:
    try:
        h = _lms_headers()
        if name == "get_items":
            r = httpx.get(f"{LMS_API_URL}/items/", headers=h, timeout=10)
            data = r.json()
            print(f"[tool] Result: {len(data)} items", file=sys.stderr)
            return json.dumps(data)
        elif name == "get_learners":
            r = httpx.get(f"{LMS_API_URL}/learners/", headers=h, timeout=10)
            data = r.json()
            print(f"[tool] Result: {len(data)} learners", file=sys.stderr)
            return json.dumps(data)
        elif name == "get_scores":
            r = httpx.get(f"{LMS_API_URL}/analytics/scores", params={"lab": args["lab"]}, headers=h, timeout=10)
            data = r.json()
            print(f"[tool] Result: {len(data)} score buckets", file=sys.stderr)
            return json.dumps(data)
        elif name == "get_pass_rates":
            r = httpx.get(f"{LMS_API_URL}/analytics/pass-rates", params={"lab": args["lab"]}, headers=h, timeout=10)
            data = r.json()
            print(f"[tool] Result: {len(data)} tasks", file=sys.stderr)
            return json.dumps(data)
        elif name == "get_timeline":
            r = httpx.get(f"{LMS_API_URL}/analytics/timeline", params={"lab": args["lab"]}, headers=h, timeout=10)
            data = r.json()
            print(f"[tool] Result: timeline data", file=sys.stderr)
            return json.dumps(data)
        elif name == "get_groups":
            r = httpx.get(f"{LMS_API_URL}/analytics/groups", params={"lab": args["lab"]}, headers=h, timeout=10)
            data = r.json()
            print(f"[tool] Result: {len(data)} groups", file=sys.stderr)
            return json.dumps(data)
        elif name == "get_top_learners":
            r = httpx.get(f"{LMS_API_URL}/analytics/top-learners", params={"lab": args["lab"], "limit": args.get("limit", 5)}, headers=h, timeout=10)
            data = r.json()
            print(f"[tool] Result: {len(data)} learners", file=sys.stderr)
            return json.dumps(data)
        elif name == "get_completion_rate":
            r = httpx.get(f"{LMS_API_URL}/analytics/completion-rate", params={"lab": args["lab"]}, headers=h, timeout=10)
            data = r.json()
            print(f"[tool] Result: completion rate data", file=sys.stderr)
            return json.dumps(data)
        elif name == "trigger_sync":
            r = httpx.post(f"{LMS_API_URL}/pipeline/sync", headers=h, timeout=30)
            data = r.json()
            print(f"[tool] Result: sync done", file=sys.stderr)
            return json.dumps(data)
        else:
            return f"Unknown tool: {name}"
    except Exception as e:
        return f"Error calling {name}: {e}"


def route(message: str) -> str:
    messages = [
        {"role": "system", "content": "You are an LMS assistant. Use the available tools to answer questions about labs, scores, and students. Always call tools to get real data before answering. Be concise and specific."},
        {"role": "user", "content": message}
    ]

    for _ in range(10):
        try:
            r = httpx.post(
                f"{LLM_API_BASE_URL}/chat/completions",
                headers={"Authorization": f"Bearer {LLM_API_KEY}", "Content-Type": "application/json"},
                json={"model": LLM_API_MODEL, "messages": messages, "tools": TOOLS, "tool_choice": "auto"},
                timeout=60
            )
            r.raise_for_status()
            resp = r.json()
        except Exception as e:
            return f"LLM error: {e}"

        choice = resp["choices"][0]["message"]
        messages.append(choice)

        if choice.get("tool_calls"):
            for tc in choice["tool_calls"]:
                name = tc["function"]["name"]
                args = json.loads(tc["function"]["arguments"] or "{}")
                print(f"[tool] LLM called: {name}({args})", file=sys.stderr)
                result = call_tool(name, args)
                messages.append({"role": "tool", "tool_call_id": tc["id"], "content": result})
            print(f"[summary] Feeding {len(choice['tool_calls'])} tool results back to LLM", file=sys.stderr)
        else:
            return choice.get("content", "No response")

    return "Could not complete the request after multiple steps."
