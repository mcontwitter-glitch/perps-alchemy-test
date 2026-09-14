# PERPS ALCHEMY — ACID TEST SPEC (the data behind the 100%)

This is the **exact** test suite BIGagent404 runs on the schedule (AM + PM daily) against this repo's `index.html` and the live deploy at https://mcontwitter-glitch.github.io/perps-alchemy-test/

**Whoever builds on this repo (Reaper included):** if your build passes these checks, it passes our scheduled QA. Nothing here is secret — it's the full contract.

## The verdict law

- **ACID SCORE** = `checks_passed / checks_total * 100`
- **ACID TEST LAW (Mau5, Sept 7 2026):** score **> 69% = PASS**, **<= 69% = FAIL**
- The label in scheduled reports reads **INFRA 13/13 PASS** (renamed from "ACID: 100 PASS" so nobody misreads infra health as call accuracy).

## The 13 checks

### A) App build integrity — run against repo `index.html` (7 checks)

| # | Check | Passes when |
|---|-------|-------------|
| 1 | `title` | the string "Perps Alchemy" exists in the build |
| 2 | `professor_persona` | "Professor" / "professor" exists |
| 3 | `coach_personas` | BOTH "Roast" AND "Mentor" exist (the coach persona set) |
| 4 | `voice_system` | "SpeechRecognition" or "speech" present (voice pipeline wired) |
| 5 | `music_modes` | "Lofi" present (music mode system) |
| 6 | `xp_system` | "XP" present |
| 7 | `gold_hex_fixed` | the old `#FFD700` hex is GONE from the build (black & gold palette uses the new hexes) |

### B) Live data pipeline — real API calls (4 checks)

| # | Check | Endpoint | Passes when |
|---|-------|----------|-------------|
| 8 | `coinbase_btc` | `https://api.exchange.coinbase.com/products/BTC-USD/candles?granularity=86400` | HTTP 200 |
| 9 | `fear_greed` | `https://api.alternative.me/fng/` | HTTP 200 AND body contains `"value"` |
| 10 | `news_rss` | `https://api.rss2json.com/v1/api.json?rss_url=https%3A%2F%2Fcointelegraph.com%2Frss` | HTTP 200 AND body contains `items` or `status` |
| 11 | `coingecko` | `https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd` | HTTP 200 AND body contains `bitcoin` |

### C) Live deployment (1 check)

| # | Check | Passes when |
|---|-------|-------------|
| 12 | `live_site` | the live URL (default: the GitHub Pages deploy) returns HTTP 200 |

*(13th: when a `live_url.txt` sits next to the suite, it overrides the default live URL — used when staging alternates.)*

**Note:** `ui_ok` (the app-build flag in our entity log) = all of section A green. `api_price_ok` / `api_fng_ok` / `api_news_ok` mirror checks 8/9/10.

## Run it yourself

```bash
python3 tests/acid-test/acid-test-suite.py            # full suite, auto AM/PM slot
python3 tests/acid-test/acid-test-suite.py --slot AM   # explicit slot
```

Prints one JSON line: `run_date`, `slot`, `checks_passed/checks_total`, `acid_score`, `acid_test` (PASS/FAIL), per-section flags, `notes`.

## Why 100% is expected (and honest)

This suite measures **infrastructure** — build integrity + data plumbing + deployment health. 100% means the app is structurally intact and every data feed answers. It is **not** a measure of trading-call skill; call grading happens separately in-app (daily calls resolve on real Hyperliquid 5m candles, first-touch, stop-before-target, losses at -1R).

## Known-fixed audit items baked into this build

- bonus-scan survivorship valve removed (re-rolled calls no longer wipe history)
- INFRA label rename shipped (kills the ACID-100 accuracy misread)
- coach memory observation system (strong/weak pattern tracking)
- live Hyperliquid snapshot fetch

— BIGagent404, Sept 14 2026
