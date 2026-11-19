import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .config import BASE_DIR
from .logging import logger

HISTORY_DIR = BASE_DIR / "history"
SESSIONS_DIR = HISTORY_DIR / "sessions"

class HistoryLogger:
    """Manages activity logging and session archiving in the local history folder."""

    def __init__(self, history_dir: Path = HISTORY_DIR):
        self.history_dir = history_dir
        self.sessions_dir = history_dir / "sessions"
        self._ensure_dirs()

    def _ensure_dirs(self):
        try:
            self.history_dir.mkdir(parents=True, exist_ok=True)
            self.sessions_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to create history directories: {e}")

    def _safe_session_id(self, session_id: str) -> str:
        return re.sub(r"[^a-zA-Z0-9_\-]", "_", str(session_id))

    def log_activity(self, event_type: str, session_id: str, details: Any):
        """Append an activity event to activity.log and daily JSONL."""
        self._ensure_dirs()
        now = datetime.now(timezone.utc)
        ts_str = now.strftime("%Y-%m-%d %H:%M:%S UTC")
        date_str = now.strftime("%Y-%m-%d")
        safe_sid = self._safe_session_id(session_id)

        # Human-readable text format
        if isinstance(details, dict):
            details_str = json.dumps(details, ensure_ascii=False)
        else:
            details_str = str(details)

        log_line = f"[{ts_str}] [SESSION: {safe_sid}] [EVENT: {event_type}] {details_str}\n"

        try:
            # 1. Main chronological human-readable activity log
            activity_file = self.history_dir / "activity.log"
            with open(activity_file, "a", encoding="utf-8") as f:
                f.write(log_line)

            # 2. Daily structured JSONL log
            jsonl_file = self.history_dir / f"activity_{date_str}.jsonl"
            record = {
                "timestamp": now.isoformat(),
                "session_id": safe_sid,
                "event": event_type,
                "details": details if isinstance(details, dict) else {"message": details_str}
            }
            with open(jsonl_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.error(f"Failed to write history log: {e}")

    def log_message(self, session_id: str, role: str, content: str, lang: str = "en", meta: Optional[Dict[str, Any]] = None):
        """Log a conversational turn."""
        details = {
            "role": role,
            "lang": lang,
            "content": content
        }
        if meta:
            details["metadata"] = meta
        self.log_activity(f"chat.{role}", session_id, details)

    def log_tool_execution(self, session_id: str, tool_name: str, args: dict, result: Any, duration_ms: Optional[float] = None):
        """Log tool execution."""
        details = {
            "tool": tool_name,
            "args": args,
            "result": result,
            "duration_ms": duration_ms
        }
        self.log_activity("tool.execution", session_id, details)

    def save_session_snapshot(self, session_id: str, session_data: Dict[str, Any]):
        """Persist structured session state (JSON) and readable Markdown transcript."""
        self._ensure_dirs()
        safe_sid = self._safe_session_id(session_id)
        json_file = self.sessions_dir / f"{safe_sid}.json"
        md_file = self.sessions_dir / f"{safe_sid}.md"

        now = datetime.now(timezone.utc).isoformat()
        session_data["last_saved_at"] = now

        try:
            # 1. Structured JSON
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)

            # 2. Markdown transcript
            history = session_data.get("history", [])
            lang = session_data.get("language", "auto")
            mode = session_data.get("mode", "voice")
            gender = session_data.get("voice_gender", "female")
            created_at = session_data.get("created_at", now)

            md_lines = [
                f"# ClanVox Session Transcript: `{safe_sid}`",
                f"- **Started**: {created_at}",
                f"- **Last Updated**: {now}",
                f"- **Mode**: `{mode}`",
                f"- **Language**: `{lang}`",
                f"- **Voice Persona**: `{gender}`",
                f"- **Total Messages**: {len(history)}",
                "",
                "---",
                "## Conversation History",
                ""
            ]

            for msg in history:
                role = msg.get("role", "unknown").upper()
                msg_lang = msg.get("lang", lang)
                msg_ts = msg.get("created_at", "")
                text = msg.get("content", "")
                badge = f"**[{role}]** *(lang: {msg_lang}, {msg_ts})*"
                md_lines.append(f"{badge}\n\n> {text}\n")

            with open(md_file, "w", encoding="utf-8") as f:
                f.write("\n".join(md_lines))
        except Exception as e:
            logger.error(f"Failed to save session snapshot: {e}")

    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all archived sessions from the history folder."""
        self._ensure_dirs()
        sessions = []
        for p in self.sessions_dir.glob("*.json"):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    history = data.get("history", [])
                    last_msg = history[-1]["content"] if history else ""
                    sessions.append({
                        "session_id": data.get("session_id", p.stem),
                        "created_at": data.get("created_at"),
                        "last_saved_at": data.get("last_saved_at"),
                        "language": data.get("language"),
                        "message_count": len(history),
                        "last_message": last_msg[:120] if last_msg else ""
                    })
            except Exception:
                continue
        sessions.sort(key=lambda s: s.get("last_saved_at") or "", reverse=True)
        return sessions

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific session from disk."""
        safe_sid = self._safe_session_id(session_id)
        json_file = self.sessions_dir / f"{safe_sid}.json"
        if json_file.exists():
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return None
        return None

history_logger = HistoryLogger()
