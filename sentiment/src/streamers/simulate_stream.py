import json, time, random, queue, pathlib
from typing import Dict, Any, List

def _load_seed() -> List[Dict[str, Any]]:
    seed_path = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "sample_posts.jsonl"
    items = []
    if seed_path.exists():
        with open(seed_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    items.append(json.loads(line))
                except Exception:
                    pass
    return items

# Example sentiment templates
POSITIVE_TEXTS = [
    "I love this!", "Absolutely fantastic result", "This is stunning",
    "What a great day", "This rocks!", "Exceeded expectations"
]
NEUTRAL_TEXTS = [
    "Not sure about this", "Meh, it's okay", "Could be better",
    "Just average", "Neutral vibes here", "Fine, nothing special"
]
NEGATIVE_TEXTS = [
    "I hate this", "This is terrible", "So disappointing",
    "Worst experience", "Not happy at all", "Really bad outcome"
]

def stream(hashtag: str, out_queue: "queue.Queue[Dict[str, Any]]"):
    seed = _load_seed()
    i = 0
    while True:
        batch = random.randint(1, 3)
        for _ in range(batch):
            # Pick sentiment category
            sentiment = random.choices(
                ["positive", "neutral", "negative"], 
                weights=[0.4, 0.3, 0.3], 
                k=1
            )[0]

            # Pick text accordingly
            if sentiment == "positive":
                text = random.choice(POSITIVE_TEXTS)
            elif sentiment == "neutral":
                text = random.choice(NEUTRAL_TEXTS)
            else:
                text = random.choice(NEGATIVE_TEXTS)

            # Base data from seed if available
            base = seed[i % len(seed)] if seed else {
                "author": f"user{random.randint(100,999)}",
                "hashtags": [hashtag.strip("#")],
            }
            i += 1

            payload = {
                "id": f"sim-{int(time.time()*1000)}-{i}",
                "text": f"{text} #{hashtag.strip('#')}",
                "timestamp": time.time(),
                "source": "simulate",
                "author": base.get("author", f"user{random.randint(1,9999)}"),
                "hashtags": [h.lower().lstrip("#") for h in base.get("hashtags",[]) if h],
                "label": sentiment,
                "confidence": round(random.uniform(0.6, 0.99), 2),
            }
            out_queue.put(payload)

        time.sleep(random.uniform(0.3, 0.8))
