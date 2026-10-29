import time
from typing import Dict, Any

class TelemetryTracker:
    def __init__(self):
        self.active_sessions: int = 0
        self.total_turns: int = 0
        self.barge_in_count: int = 0
        self.error_count: int = 0
        self.turn_latencies: list[float] = []

    def start_turn(self) -> Dict[str, float]:
        return {"turn_start": time.perf_counter()}

    def record_mark(self, spans: Dict[str, float], mark_name: str):
        spans[mark_name] = time.perf_counter()

    def finish_turn(self, spans: Dict[str, float]) -> Dict[str, float]:
        now = time.perf_counter()
        start = spans.get("turn_start", now)
        total_latency_ms = (now - start) * 1000.0

        self.total_turns += 1
        self.turn_latencies.append(total_latency_ms)
        if len(self.turn_latencies) > 1000:
            self.turn_latencies = self.turn_latencies[-1000:]

        durations = {"total_ms": total_latency_ms}
        keys = list(spans.keys())
        for i in range(1, len(keys)):
            prev_key = keys[i - 1]
            cur_key = keys[i]
            durations[f"{prev_key}_to_{cur_key}_ms"] = (spans[cur_key] - spans[prev_key]) * 1000.0

        return durations

    def record_barge_in(self):
        self.barge_in_count += 1

    def record_error(self):
        self.error_count += 1

telemetry = TelemetryTracker()

