# ClanVox Localhost Activity & History Tracker

This folder automatically tracks and archives all activity happening on your ClanVox localhost server:

- **`activity.log`**: Chronological, human-readable log of all localhost interactions (user messages, AI assistant replies, tool executions, latency benchmarks, language detection, and session state changes).
- **`activity_YYYY-MM-DD.jsonl`**: Machine-readable JSONL logs partitioned by day for easy inspection, analysis, and debugging.
- **`sessions/`**:
  - `{session_id}.json`: Structured JSON containing complete session metadata, timestamps, language/voice configurations, and chat messages.
  - `{session_id}.md`: Formatted Markdown transcripts for reading past conversations.
