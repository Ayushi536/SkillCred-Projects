# tests/test_generate_local.py
import json
from backend import generator



class DummyResp:
    def __init__(self, text):
        self.text = text

def test_generate_script_json_parse(monkeypatch):
    fake_json = {
        "title": "Test Title",
        "total_seconds": 90,
        "scenes": [
            {"scene": 1, "heading": "Hook", "narration": "Hook text", "visuals": ["visual1"], "est_seconds": 15},
            {"scene": 2, "heading": "Core", "narration": "Core text", "visuals": ["visual2"], "est_seconds": 60},
            {"scene": 3, "heading": "Wrap", "narration": "Wrap text", "visuals": ["visual3"], "est_seconds": 15}
        ]
    }
    def fake_generate_content(model, contents, config=None):
        return DummyResp(text=json.dumps(fake_json))
    monkeypatch.setattr(generator.CLIENT.models, "generate_content", fake_generate_content)

    result = generator.generate_script("Quantum Computing", audience="students", difficulty="beginner", tone="fun")
    assert result["title"] == "Test Title"
    assert len(result["scenes"]) == 3
