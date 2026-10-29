import json
import pytest
from starlette.testclient import TestClient
from backend.app.main import app

def test_websocket_realtime_turn():
    client = TestClient(app)
    with client.websocket_connect("/v1/realtime?session_id=test_ws_turn") as ws:
        # Receive initial state
        initial_msg = json.loads(ws.receive_text())
        assert initial_msg["type"] == "state"
        assert initial_msg["value"] == "idle"

        # Send text message
        ws.send_text(json.dumps({
            "type": "text.message",
            "text": "Namaste",
            "language": "hi"
        }))

        # Expect events from the turn
        received_types = []
        for _ in range(8):
            try:
                raw = ws.receive_text()
                data = json.loads(raw)
                received_types.append(data.get("type"))
                if data.get("type") == "state" and data.get("value") in ["speaking", "listening"]:
                    break
            except Exception:
                break

        assert "stt.final" in received_types
        assert "llm.delta" in received_types

