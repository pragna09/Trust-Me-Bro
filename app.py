"""Scoring API + streaming replay + local supplier matching. Run: uvicorn app:app --host 0.0.0.0 --port 8000"""
import asyncio
import difflib
import json

import joblib
import pandas as pd
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from core import alert_score, alert_text, parse_states, tier

bundle = joblib.load("model.joblib")
PIPE, THRESHOLD = bundle["pipe"], bundle["threshold"]
METRICS = json.load(open("metrics.json"))

replay = pd.read_csv("data/replay.csv")
for c in ["recalling_firm", "product", "reason", "dist", "code_info", "states_str", "tier", "alert"]:
    replay[c] = replay[c].fillna("").astype(str)
replay["texas"] = replay["texas"].astype(bool)
replay = replay.sort_values("class_date").reset_index(drop=True)
TX = replay[replay.texas].copy()

app = FastAPI(title="Recall Triage")


class Recall(BaseModel):
    reason: str
    product: str = ""
    distribution: str = ""
    code_info: str = ""
    firm: str = "Unknown firm"


class Suppliers(BaseModel):
    suppliers: list[str]


def records(df):
    return json.loads(df.to_json(orient="records"))


@app.get("/api/health")
def health():
    return {"status": "ok", "replay_rows": len(replay), "texas_rows": len(TX)}


@app.get("/api/metrics")
def metrics():
    return METRICS


@app.post("/api/score")
def score(r: Recall):
    X = pd.DataFrame([{"reason": r.reason, "product": r.product, "dist": r.distribution}])
    p = float(PIPE.predict_proba(X)[:, 1][0])
    states = parse_states(r.distribution)
    s = alert_score(p, states)
    return {
        "p_class1": round(p, 4), "pred_class1": int(p >= THRESHOLD), "states": states,
        "reaches_texas": bool(s > 0), "alert_score": s, "tier": tier(s),
        "alert": alert_text(r.firm, r.product, r.reason, states, r.code_info, p, s),
    }


@app.get("/api/alerts")
def alerts(limit: int = 25):
    return records(TX.sort_values("alert_score", ascending=False).head(limit))


@app.get("/api/stream")
async def stream(delay: float = 1.5, limit: int = 40):
    rows = records(TX.head(limit))

    async def gen():
        for rec in rows:
            yield f"data: {json.dumps(rec)}\n\n"
            await asyncio.sleep(delay)
        yield "event: done\ndata: {}\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")


@app.post("/api/match")
def match(body: Suppliers):
    """Supplier list is matched against recalls in memory on this instance; it is never stored or logged."""
    firms = TX.recalling_firm.unique().tolist()
    out = []
    for s in body.suppliers:
        q = s.strip().lower()
        if not q:
            continue
        hits = [f for f in firms
                if q in f.lower() or f.lower() in q
                or difflib.SequenceMatcher(None, q, f.lower()).ratio() >= 0.85]
        rows = TX[TX.recalling_firm.isin(hits)].sort_values("alert_score", ascending=False)
        out.append({"supplier": s, "matches": records(rows.head(5))})
    return out


app.mount("/", StaticFiles(directory="static", html=True), name="static")
