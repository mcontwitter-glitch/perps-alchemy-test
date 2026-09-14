#!/usr/bin/env python3
"""
PERPS ALCHEMY — Scheduled Test Suite (BIGagent404 for BigFootMau5)
Runs the full QA pass on the Perps Alchemy app + its live data pipeline.
Outputs a single JSON line for logging into the PerpsTestResult entity.

Usage:
  python3 run.py            # full suite (local build + APIs + live URL if configured)
  python3 run.py --slot AM  # same, records the slot name
"""
import json, os, re, ssl, sys, time, urllib.request, urllib.error

args = sys.argv[1:]
slot_arg = None
if "--slot" in args:
    i = args.index("--slot")
    if i + 1 < len(args): slot_arg = args[i+1]
HERE = os.path.dirname(os.path.abspath(__file__))
CANON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "index.html")  # repo canon build
URL_CFG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "live_url.txt")  # fallback; defaults to the live Pages deploy below

# ---- test results container ----
res = {
    "run_date": time.strftime("%Y-%m-%d"),
    "slot": slot_arg or ("AM" if time.strftime("%H") < "12" else "PM"),
    "checks_passed": 0,
    "checks_total": 0,
    "ui_ok": False, "api_price_ok": False, "api_fng_ok": False, "api_news_ok": False,
    "acid_score": 0, "acid_test": "FAIL",
    "target_url": "local build", "notes": [],
}

def check(name, ok, note=""):
    res["checks_total"] += 1
    if ok:
        res["checks_passed"] += 1
    else:
        res["notes"].append(f"{name} failed{': ' + note if note else ''}")
    return ok

# ---------- 1) APP BUILD INTEGRITY (local canon copy) ----------
try:
    html = open(CANON, encoding="utf-8", errors="ignore").read()
    check("title", "Perps Alchemy" in html)
    check("professor_persona", "Professor" in html or "professor" in html)
    check("coach_personas", all(k in html for k in ("Roast", "Mentor")))
    check("voice_system", "SpeechRecognition" in html or "speech" in html.lower())
    check("music_modes", "Lofi" in html)
    check("xp_system", "XP" in html)
    check("risk_rating_ui", "skull" in html.lower() or "risk" in html.lower())
    check("gold_hex_fixed", "#FFD700" not in html)  # old-gold hex should be gone
    res["ui_ok"] = res["checks_passed"] == res["checks_total"]
except FileNotFoundError:
    check("app_file", False, "canon copy missing")
    res["ui_ok"] = False

# ---------- 2) LIVE DATA PIPELINE ----------
CTX = ssl.create_default_context()

def fetch(url, timeout=12):
    t0 = time.time()
    req = urllib.request.Request(url, headers={"User-Agent": "BIGagent404-PerpsQA/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
            body = r.read(512 * 1024)
            return True, round((time.time() - t0) * 1000), r.status, body
    except Exception as e:
        return False, round((time.time() - t0) * 1000), getattr(e, "code", 0), str(e)[:120].encode()

ok, ms, code, _ = fetch("https://api.exchange.coinbase.com/products/BTC-USD/candles?granularity=86400")
check("coinbase_btc", ok and code == 200, f"HTTP {code} {ms}ms")
res["api_price_ok"] = ok and code == 200

ok, ms, code, body = fetch("https://api.alternative.me/fng/")
check("fear_greed", ok and code == 200 and b"value" in body, f"HTTP {code} {ms}ms")
res["api_fng_ok"] = ok and code == 200 and b"value" in body

ok, ms, code, body = fetch("https://api.rss2json.com/v1/api.json?rss_url=https%3A%2F%2Fcointelegraph.com%2Frss")
check("news_rss", ok and code == 200 and (b"items" in body or b"status" in body), f"HTTP {code} {ms}ms")
res["api_news_ok"] = ok and code == 200

ok, ms, code, body = fetch("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd")
check("coingecko", ok and code == 200 and b"bitcoin" in body, f"HTTP {code} {ms}ms")

# ---------- 3) LIVE DEPLOYMENT (if URL configured) ----------
live = ""
if os.path.exists(URL_CFG):
    live = open(URL_CFG).read().strip()
if not live:
    live = "https://mcontwitter-glitch.github.io/perps-alchemy-test/"  # default: live GitHub Pages deploy
ok, ms, code, body = fetch(live)
check("live_site", ok and code == 200, f"HTTP {code} {ms}ms")
res["target_url"] = live

# ---------- verdict ----------
ratio = res["checks_passed"] / max(res["checks_total"], 1)
res["acid_score"] = round(ratio * 100)
# ACID TEST LAW (Mau5, Sept 7 2026): 69% = FAIL, anything above 69% = PASS
res["acid_test"] = "PASS" if res["acid_score"] > 69 else "FAIL"
res["status"] = "Pass" if res["acid_test"] == "PASS" else "Fail"
res["notes"] = "; ".join(res["notes"])[:500] or "all green"
print(json.dumps(res))
