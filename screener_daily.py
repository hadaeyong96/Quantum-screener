# screener_daily.py — QUANTUM 자동 스크리닝
# GitHub Actions에서 매일 오전 9시 실행
# APP.py와 동일한 core.py 함수 사용 → 점수 완전 일치

import os, sys, warnings
warnings.filterwarnings("ignore")

# ── streamlit 없이 실행하기 위한 mock ──────────────────────
class _SecretsMock:
    def get(self, key, default=""):
        return os.environ.get(key, default)
    def __getitem__(self, key):
        val = os.environ.get(key)
        if val is None: raise KeyError(key)
        import json
        try: return json.loads(val)
        except: return val

class _CacheMock:
    def __call__(self, fn=None, **kw):
        if fn: return fn
        return lambda f: f
    def clear(self): pass

class _StMock:
    secrets  = _SecretsMock()
    cache_data = _CacheMock()
    session_state = {}
    def spinner(self, *a, **kw):
        class _CM:
            def __enter__(self): pass
            def __exit__(self, *a): pass
        return _CM()

import sys
sys.modules.setdefault("streamlit", _StMock())

import streamlit as st  # → mock

# ── core.py 공유 모듈 import ───────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core import (
    _safe_float, load_fred, load_market, load_stocks,
    calc_liq_score, calc_rec_score, build_market_ctx,
    calc_auto_stance, get_optimal_strategies,
    calculate_leader_score, apply_strategy_bonus,
    save_pro_results, STRATEGY_DEFINITIONS,
    SCREEN_TICKERS, COMPANY_NAME, SECTOR_MAP,
    _DEFAULTS,
)

import pandas as pd
from datetime import datetime

# ── 환경변수 로드 ─────────────────────────────────────────
FRED_API_KEY = os.environ.get("FRED_API_KEY", "")

def main():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] QUANTUM 자동 스크리닝 시작")

    if not FRED_API_KEY:
        print("❌ FRED_API_KEY 없음 — 종료")
        sys.exit(1)

    # ── 1. 시장 데이터 로드 ───────────────────────────────
    print("📡 FRED 데이터 로드 중...")
    fred = load_fred(FRED_API_KEY, _bust=0)

    print("📡 시장 데이터 로드 중...")
    mkt  = load_market(_bust=0)

    liq_score, liq_stage, liq_detail = calc_liq_score(fred)
    rec_score = calc_rec_score(fred)
    mkt_ctx   = build_market_ctx(liq_stage, rec_score, mkt)
    auto_stance = calc_auto_stance(liq_stage, liq_score, rec_score, mkt_ctx.get("vix",20))
    opt_strats  = get_optimal_strategies(liq_stage, rec_score, mkt_ctx.get("vix",20))

    print(f"📊 유동성: {liq_stage}단계 ({liq_score:.0f}점) | 침체: {rec_score:.0f}점 | 스탠스: {auto_stance['label']}")

    # ── 2. 종목 스크리닝 ─────────────────────────────────
    print(f"📡 {len(SCREEN_TICKERS)}개 종목 분석 중...")
    raw_results = load_stocks(_bust=0)

    if not raw_results:
        print("❌ 종목 데이터 없음 — 종료")
        sys.exit(1)

    # ── 3. Leader Score 계산 (APP.py와 동일) ─────────────
    cfg = _DEFAULTS.copy()
    active_strats = opt_strats.get("strategies", {})

    scored = []
    for r in raw_results:
        res         = calculate_leader_score(r, mkt_ctx, cfg)
        strat_bonus = apply_strategy_bonus(r, active_strats)
        final_score = res["score"] + strat_bonus

        # 등급 계산
        if   final_score >= cfg["cfg_elite_min"]:  grade = "A"
        elif final_score >= cfg["cfg_strong_min"]: grade = "B"
        elif final_score >= cfg["cfg_watch_min"]:  grade = "C"
        else:                                       grade = "D"

        scored.append({**r,
            "LeaderScore": final_score,
            "LeaderGrade": grade,
            "Signal":      res["reasons"],
            "AccScore":    res["acc"],
        })

    # 통계
    above = [r for r in scored if r.get("MA200")]
    elite = [r for r in above if r["LeaderGrade"] == "A"]
    strong= [r for r in above if r["LeaderGrade"] == "B"]
    watch = [r for r in above if r["LeaderGrade"] == "C"]

    print(f"✅ 스크리닝 완료: MA200 위 {len(above)}개 | A {len(elite)} | B {len(strong)} | C {len(watch)}")

    # 상위 5개 출력
    top5 = sorted(above, key=lambda x: x["LeaderScore"], reverse=True)[:5]
    for r in top5:
        print(f"   {r['Ticker']:6s} {r['LeaderGrade']} {r['LeaderScore']:.0f}점 RS={r['RS']:.1f}")

    # ── 4. Sheets 저장 ────────────────────────────────────
    if not auto_stance.get("save_ok", True):
        print(f"⚠️  {auto_stance['label']} — 저장 중단")
        return

    save_rows = [r for r in scored if r.get("MA200") and r["LeaderScore"] >= cfg["cfg_watch_min"]]
    save_rows += [r for r in scored if not r.get("MA200")]

    print(f"💾 Sheets 저장 중... ({len(save_rows)}개)")
    ok, msg = save_pro_results(save_rows, liq_stage, rec_score)

    if ok:
        print(f"✅ {msg}")
    else:
        print(f"❌ 저장 실패: {msg}")
        sys.exit(1)

if __name__ == "__main__":
    main()
