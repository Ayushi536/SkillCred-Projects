# api_main.py
import os, time, threading, queue
from typing import Dict, Any, List
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
from fastapi.responses import HTMLResponse

from src.config import Settings
from src.models import analyze_text
from src.data_store import DataStore, Post

# ---- App & CORS ----
app = FastAPI(title="Social Sentiment Analyzer API")

# Allow your dev frontend (adjust if needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

settings = Settings()
store = DataStore(maxlen=5000)
incoming_q: "queue.Queue[Dict[str, Any]]" = queue.Queue(maxsize=10000)

# ---- Streamers ----
from src.streamers.simulate_stream import stream as simulate_stream
try:
    from src.streamers.twitter_stream import TwitterStreamer
except Exception:
    TwitterStreamer = None

def select_streamer():
    if settings.twitter_bearer_token and TwitterStreamer is not None:
        return ("twitter", settings.hashtag)
    return ("simulate", settings.hashtag)

def collector_loop():
    mode, hashtag = select_streamer()
    if mode == "twitter":
        print(f"[stream] Using Twitter filtered stream for {hashtag}")
        ts = TwitterStreamer(settings.twitter_bearer_token, hashtag, incoming_q)
        ts.start()
        while True:
            time.sleep(1.0)
    else:
        print(f"[stream] Using simulated stream for {hashtag}")
        simulate_stream(hashtag, incoming_q)

def inference_loop():
    print("[inference] Sentiment model warming up...")
    _ = analyze_text("Model warm up.")
    print("[inference] Ready.")
    while True:
        payload = incoming_q.get()
        try:
            res = analyze_text(payload["text"])
            post = Post(
                id=str(payload.get("id")),
                text=payload.get("text",""),
                timestamp=float(payload.get("timestamp", time.time())),
                source=payload.get("source","simulate"),
                author=payload.get("author"),
                hashtags=payload.get("hashtags", []),
                label=res["label"],
                confidence=float(res["confidence"]),
                signed=float(res["signed"]),
            )
            store.add(post)
        except Exception as e:
            print("[inference] error:", e)

# Start background threads at startup
@app.on_event("startup")
def _startup():
    threading.Thread(target=collector_loop, daemon=True).start()
    threading.Thread(target=inference_loop, daemon=True).start()

# ---------- API MODELS ----------
class PostOut(BaseModel):
    id: str
    ts: str
    source: str
    author: str | None
    label: str | None
    confidence: float | None
    text: str

# ---------- API ENDPOINTS ----------
@app.get("/api/health")
def health():
    return {"status": "ok", "hashtag": settings.hashtag, "source": "twitter" if settings.twitter_bearer_token else "simulate"}

@app.get("/api/posts", response_model=List[PostOut])
def get_posts(limit: int = Query(50, ge=1, le=500)):
    df = store.recent_window(settings.rolling_window_min)
    if df.empty:
        return []
    df = df.sort_values("ts", ascending=False).head(limit)
    out = []
    for _, r in df.iterrows():
        out.append(PostOut(
            id=str(r["id"]),
            ts=r["ts"].isoformat(),
            source=str(r.get("source") or "simulate"),
            author=r.get("author"),
            label=r.get("label"),
            confidence=float(r.get("confidence")) if r.get("confidence") is not None else None,
            text=r.get("text") or "",
        ))
    return out

@app.get("/api/stats/counts")
def stats_counts(minutes: int = Query(5, ge=1, le=60)):
    df = store.recent_window(minutes)
    if df.empty:
        return {"positive": 0, "neutral": 0, "negative": 0}
    counts = df["label"].value_counts()
    return {
        "positive": int(counts.get("positive", 0)),
        "neutral": int(counts.get("neutral", 0)),
        "negative": int(counts.get("negative", 0)),
    }

@app.get("/api/stats/rolling")
def stats_rolling(minutes: int = Query(5, ge=1, le=120)):
    import pandas as pd
    df = store.to_dataframe()
    if df.empty:
        return {"points": []}
    df = df.dropna(subset=["signed"])
    if df.empty:
        return {"points": []}
    ser = df.set_index("ts").sort_index().rolling(f"{minutes}min")["signed"].mean().dropna()
    points = [{"ts": ts.isoformat(), "value": float(v)} for ts, v in ser.items()]
    return {"points": points}

# Debug helpers
@app.get("/api/_debug/buf-size")
def buf_size():
    return {"buffer": len(store.to_dataframe())}

# ---------- (Optional) Serve your built frontend at `/` ----------
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

FRONT_DIR = Path("frontend/out")

# Serve Next.js assets (_next)
app.mount(
    "/_next", StaticFiles(directory=FRONT_DIR / "_next"), name="_next"
)

# Serve static assets if any
if (FRONT_DIR / "static").exists():
    app.mount("/static", StaticFiles(directory=FRONT_DIR / "static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_file = FRONT_DIR / "index.html"
    return index_file.read_text(encoding="utf-8")

