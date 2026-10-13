#!/usr/bin/env python3
"""Price sync for the batterygenome.net ticker.
Reads meta.tickers from index.html, pulls recent daily closes with yfinance, and writes data/prices.json:
{"updated": ISO-8601 UTC, "mc_updated": ISO-8601 UTC, "items": {"TSLA": {"p": 245.12, "c": 1.23, "cur": "USD", "mc": 7.9e11}, ...}}
p = last close, c = change vs the previous close in %, mc = market capitalisation in USD (shares x last price,
converted at the latest Yahoo FX rate; refreshed once per UTC day, or every run with FORCE_MC=1).
No API key needed. Exits 0 even on partial failure so the workflow keeps the last good values for anything that
did not resolve this run."""
import json, os, re, sys, time, datetime as dt
from pathlib import Path
try:
    import yfinance as yf
except ImportError:
    sys.exit("pip install yfinance")

ROOT = Path(__file__).resolve().parents[1]
html = (ROOT / "index.html").read_text(encoding="utf-8")
meta = json.loads(re.search(r'<script type="application/json" id="big-meta">(.*?)</script>', html, re.S).group(1))
symbols = [t["s"] for t in meta.get("tickers", [])]
if not symbols:
    sys.exit("no tickers in index.html")

CUR = {".TWO": "TWD", ".SZ": "CNY", ".SS": "CNY", ".HK": "HKD", ".KS": "KRW", ".KQ": "KRW", ".T": "JPY", ".TW": "TWD", ".NS": "INR",
       ".DE": "EUR", ".PA": "EUR", ".AS": "EUR", ".BR": "EUR", ".L": "GBp", ".SW": "CHF", ".ST": "SEK", ".CO": "DKK",
       ".AX": "AUD", ".TO": "CAD"}
def currency(sym):
    for suf, cur in CUR.items():
        if sym.endswith(suf): return cur
    return "USD"

out_path = ROOT / "data" / "prices.json"
previous, prev_doc = {}, {}
if out_path.exists():
    try:
        prev_doc = json.loads(out_path.read_text())
        previous = prev_doc.get("items", {}) or {}
    except Exception: previous, prev_doc = {}, {}

items = {}
BATCH = 60
for i in range(0, len(symbols), BATCH):
    batch = symbols[i:i + BATCH]
    for attempt in range(3):
        try:
            df = yf.download(batch, period="7d", interval="1d", group_by="ticker", threads=True, progress=False, auto_adjust=False)
            break
        except Exception as e:
            print("retry", attempt, e); time.sleep(10); df = None
    if df is None or df.empty: continue
    for s in batch:
        try:
            closes = (df[s]["Close"] if len(batch) > 1 else df["Close"]).dropna()
            if len(closes) < 2: continue
            last, prev = float(closes.iloc[-1]), float(closes.iloc[-2])
            if last <= 0 or prev <= 0: continue
            items[s] = {"p": round(last, 4 if last < 10 else 2), "c": round((last / prev - 1) * 100, 2), "cur": currency(s)}
        except Exception:
            continue
    time.sleep(2)

# keep last good values for anything that failed this run
for s in symbols:
    if s not in items and s in previous: items[s] = previous[s]
# market capitalisation in USD, once per UTC day
now = dt.datetime.now(dt.timezone.utc)
mc_updated = prev_doc.get("mc_updated")
prev_mc = {s: v["mc"] for s, v in previous.items() if isinstance(v, dict) and v.get("mc")}
if os.environ.get("FORCE_MC") == "1" or not mc_updated or mc_updated[:10] != now.strftime("%Y-%m-%d"):
    fx = {"USD": 1.0}
    pairs = sorted({c for c in CUR.values()} - {"USD"})
    for cur in pairs:
        base = "GBP" if cur == "GBp" else cur
        try:
            h = yf.Ticker(f"{base}USD=X").history(period="5d")["Close"].dropna()
            if len(h): fx[cur] = float(h.iloc[-1]) / (100 if cur == "GBp" else 1)
        except Exception as e:
            print("fx failed", cur, e)
    fresh = 0
    for s in symbols:
        try:
            fi = yf.Ticker(s).fast_info
            cap, cur = fi.market_cap, fi.currency
            if cur in ("GBp", "GBX"): cur = "GBp"
            if cap and cap > 0 and cur in fx:
                prev_mc[s] = round(cap * fx[cur], -5); fresh += 1
        except Exception:
            pass
        time.sleep(0.4)
    mc_updated = now.strftime("%Y-%m-%dT%H:%MZ")
    print(f"market caps refreshed: {fresh}/{len(symbols)}; fx: {fx}")
for s, v in items.items():
    if s in prev_mc: v["mc"] = prev_mc[s]

missing = [s for s in symbols if s not in items]
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(json.dumps({"updated": now.strftime("%Y-%m-%dT%H:%MZ"), "mc_updated": mc_updated,
                                "source": "Yahoo Finance via yfinance, delayed", "items": items}, separators=(",", ":")) + "\n")
print(f"{len(items)}/{len(symbols)} symbols priced; missing: {missing}")
