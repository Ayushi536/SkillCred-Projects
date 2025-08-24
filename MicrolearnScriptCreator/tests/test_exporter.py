# tests/test_exporter.py
import json
from exports.exporter import script_to_pdf_bytes

def test_script_to_pdf_bytes():
    example = {
        "title":"Sample",
        "total_seconds":90,
        "scenes":[
            {"scene":1,"heading":"H","narration":"N","visuals":["v1","v2"],"est_seconds":30}
        ]
    }
    b = script_to_pdf_bytes(example)
    assert isinstance(b, (bytes, bytearray))
    assert len(b) > 100  # basic sanity
