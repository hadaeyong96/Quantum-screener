# VERSION : PRO_APP_V1
# QUANTUM INSTITUTIONAL OS — PRO VERSION
# 순수 데이터 기반 기관형 리더주 선별 엔진
# 설명·그래프 없음 / 숫자·신호·등급만

import warnings; warnings.filterwarnings("ignore")
import io, sys, json, requests
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf
import streamlit as st

# ── Google Sheets ─────────────────────────────────────────
try:
    import gspread
    from google.oauth2.service_account import Credentials
    _GS_OK = True
except ImportError:
    _GS_OK = False

# ═══════════════════════════════════════════════════════════
# 설정
# ═══════════════════════════════════════════════════════════
PRO_VERSION   = "PRO_V1"
SHEET_TAB     = "History_PRO"      # 교육용(History)과 분리
SHEET_SCOPES  = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
SHEET_HEADER  = [
    "Date","Ticker","EntryPrice","LeaderScore","LeaderGrade",
    "RS","MA200","AccScore","LiqStage","RecRisk",
    "EPS","CondCount","Breakout","VolSurge","Sector"
]

# 스크리닝 종목 (ETF·헤지 제외한 성장주)
SCREEN_TICKERS = [
    # 빅테크 / AI
    "NVDA","MSFT","META","AMZN","GOOGL","AAPL","TSLA","NFLX","COST",
    # 반도체
    "AVGO","AMD","QCOM","TXN","AMAT","MU","MRVL","LRCX","KLAC","NXPI","ADI",
    # 소프트웨어 / 클라우드
    "NOW","ADBE","CRM","ORCL","INTU","CDNS","SNPS","WDAY","TEAM","ANSS",
    # 사이버보안
    "PANW","CRWD","FTNT","ZS","CYBR",
    # 데이터 / AI 플랫폼
    "PLTR","DDOG","MDB","SNOW","HUBS","GTLB",
    # 헬스케어
    "ISRG","DXCM","IDXX","GEHC","MRNA","REGN","BIIB",
    # 소비 / 여행
    "BKNG","ABNB","LULU","MELI","SBUX","PCAR",
    # 금융 / 핀테크
    "PYPL","COIN","APP","AXON",
    # 통신 / 기타
    "CMCSA","TMUS","FANG","CEG","SMCI",
]

SECTOR_MAP = {
    "NVDA":"반도체","MSFT":"빅테크","META":"빅테크","AMZN":"빅테크",
    "GOOGL":"빅테크","AAPL":"빅테크","TSLA":"전기차","NFLX":"미디어",
    "COST":"소비재","AVGO":"반도체","AMD":"반도체","QCOM":"반도체",
    "TXN":"반도체","AMAT":"반도체","MU":"반도체","MRVL":"반도체",
    "LRCX":"반도체","KLAC":"반도체","NXPI":"반도체","ADI":"반도체",
    "NOW":"소프트웨어","ADBE":"소프트웨어","CRM":"소프트웨어",
    "ORCL":"소프트웨어","INTU":"소프트웨어","CDNS":"소프트웨어",
    "SNPS":"소프트웨어","WDAY":"소프트웨어","TEAM":"소프트웨어",
    "ANSS":"소프트웨어","PANW":"사이버보안","CRWD":"사이버보안",
    "FTNT":"사이버보안","ZS":"사이버보안","CYBR":"사이버보안",
    "PLTR":"AI플랫폼","DDOG":"AI플랫폼","MDB":"AI플랫폼",
    "SNOW":"AI플랫폼","HUBS":"AI플랫폼","GTLB":"AI플랫폼",
    "ISRG":"헬스케어","DXCM":"헬스케어","IDXX":"헬스케어",
    "GEHC":"헬스케어","MRNA":"헬스케어","REGN":"헬스케어","BIIB":"헬스케어",
    "BKNG":"여행","ABNB":"여행","LULU":"소비재","MELI":"핀테크",
    "SBUX":"소비재","PCAR":"산업재","PYPL":"핀테크","COIN":"핀테크",
    "APP":"소프트웨어","AXON":"산업재","CMCSA":"미디어","TMUS":"통신",
    "FANG":"에너지","CEG":"에너지","SMCI":"반도체",
}

# ═══════════════════════════════════════════════════════════
# Streamlit 설정
# ═══════════════════════════════════════════════════════════
st.set_page_config(
    page_title="QUANTUM PRO",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
/* BASE — 라이트 테마 */
.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"],section.main
    { background-color:#F7F8FA !important; }
[data-testid="stHeader"]
    { background-color:#FFFFFF !important; border-bottom:1px solid #E2E6ED !important; }
body,p,span,div,label
    { color:#0D1117 !important; font-family:'Inter',sans-serif !important; }
h1,h2,h3
    { font-family:'Space Mono',monospace !important; color:#0D1117 !important; }

/* SIDEBAR */
[data-testid="stSidebar"]
    { background-color:#FFFFFF !important; border-right:1px solid #E2E6ED !important; }
[data-testid="stSidebar"] *
    { color:#374151 !important; }

/* TABS */
[data-testid="stTabs"] [role="tablist"]
    { background:#FFFFFF !important; border-bottom:2px solid #E2E6ED !important; }
[data-testid="stTabs"] button
    { color:#6B7280 !important; font-family:'Inter',sans-serif !important;
      font-size:13px !important; font-weight:500 !important;
      padding:10px 20px !important; background:transparent !important;
      border:none !important; border-bottom:2px solid transparent !important; }
[data-testid="stTabs"] button:hover
    { color:#0D1117 !important; background:#F3F4F6 !important; }
[data-testid="stTabs"] button[aria-selected="true"]
    { color:#0D1117 !important; border-bottom:2px solid #374151 !important;
      font-weight:700 !important; background:#F9FAFB !important; }

/* BUTTON */
.stButton button
    { background:#FFFFFF !important; border:1px solid #D1D5DB !important;
      color:#374151 !important; font-family:'Inter',sans-serif !important;
      font-size:11px !important; font-weight:500 !important;
      border-radius:3px !important; padding:4px 10px !important; }
.stButton button:hover
    { background:#F3F4F6 !important; border-color:#9CA3AF !important;
      color:#0D1117 !important; }

/* DATAFRAME */
[data-testid="stDataFrame"]
    { background:#FFFFFF !important; border:1px solid #E2E6ED !important;
      border-radius:3px !important; }

/* METRIC */
div[data-testid="metric-container"]
    { background:#FFFFFF !important; border:1px solid #E2E6ED !important;
      border-radius:3px !important; padding:8px !important; }

/* HR */
hr { border-color:#E2E6ED !important; }

/* SPINNER */
.stSpinner > div { border-top-color:#9CA3AF !important; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# 유틸리티
# ═══════════════════════════════════════════════════════════
def _safe_float(v, default=0.0):
    try:
        f = float(v)
        return default if (np.isnan(f) or np.isinf(f)) else f
    except Exception:
        return default

def _fred_val(sid, api_key, limit=2):
    """FRED 최신값 반환"""
    try:
        url = (f"https://api.stlouisfed.org/fred/series/observations"
               f"?series_id={sid}&api_key={api_key}&file_type=json"
               f"&sort_order=desc&limit={limit}")
        r = requests.get(url, timeout=12)
        if r.status_code != 200: return None
        obs = [o for o in r.json().get("observations",[])
               if o["value"] not in (".",""," ")]
        return float(obs[0]["value"]) if obs else None
    except Exception:
        return None

def _fred_series(sid, api_key, start="2018-01-01"):
    """FRED 시계열 반환 (pd.Series)"""
    try:
        url = (f"https://api.stlouisfed.org/fred/series/observations"
               f"?series_id={sid}&api_key={api_key}&file_type=json"
               f"&sort_order=asc&observation_start={start}")
        r = requests.get(url, timeout=15)
        if r.status_code != 200: return None
        obs = r.json().get("observations",[])
        data = {o["date"]: float(o["value"])
                for o in obs if o["value"] not in (".",""," ")}
        s = pd.Series(data)
        s.index = pd.to_datetime(s.index)
        return s.sort_index() if not s.empty else None
    except Exception:
        return None

# ═══════════════════════════════════════════════════════════
# Google Sheets
# ═══════════════════════════════════════════════════════════
def _get_sheet(debug=False):
    if not _GS_OK:
        if debug: return None, "gspread 미설치"
        return None
    try:
        _cd = dict(st.secrets["gcp_service_account"])
    except Exception as e:
        if debug: return None, f"gcp_service_account 키 없음: {e}"
        return None
    try:
        _cr = Credentials.from_service_account_info(_cd, scopes=SHEET_SCOPES)
        _gc = gspread.authorize(_cr)
    except Exception as e:
        if debug: return None, f"인증 실패: {e}"
        return None
    try:
        _url = st.secrets.get("SHEETS_URL","")
        if not _url:
            if debug: return None, "SHEETS_URL 없음"
            return None
        _sh = _gc.open_by_url(_url)
        if debug: return _sh, "OK"
        return _sh
    except Exception as e:
        _err_detail = f"Sheets 열기 실패: {type(e).__name__}: {e} | URL={_url[:50] if _url else 'EMPTY'}"
        if debug: return None, _err_detail
        return None

def _get_or_create_tab(sh, tab_name):
    """시트 탭 가져오기 (없으면 생성)"""
    try:
        ws = sh.worksheet(tab_name)
        # 헤더 확인 후 필요시 추가
        vals = ws.row_values(1)
        if not vals:
            ws.append_row(SHEET_HEADER)
        return ws
    except Exception:
        ws = sh.add_worksheet(title=tab_name, rows=5000, cols=20)
        ws.append_row(SHEET_HEADER)
        return ws

def save_pro_results(rows: list, liq_stage: int, rec_risk: float):
    """PRO 결과를 History_PRO 탭에 저장 (종목별 1행)"""
    try:
        sh = _get_sheet()
        if sh is None: return False, "Sheets 연결 실패"
        ws = _get_or_create_tab(sh, SHEET_TAB)

        today = datetime.now().strftime("%Y-%m-%d")

        # 오늘 기존 데이터 삭제 (중복 방지)
        all_vals = ws.get_all_values()
        del_rows = [i+1 for i,r in enumerate(all_vals)
                    if r and r[0] == today]
        for ri in sorted(del_rows, reverse=True):
            ws.delete_rows(ri)

        # 신규 저장
        new_rows = []
        for r in rows:
            new_rows.append([
                today,
                r.get("Ticker",""),
                r.get("EntryPrice", 0),
                r.get("LeaderScore", 0),
                r.get("LeaderGrade",""),
                r.get("RS", 0),
                "Y" if r.get("MA200") else "N",
                r.get("AccScore", 0),
                liq_stage,
                round(rec_risk, 1),
                r.get("EPS", 0),
                r.get("CondCount", 0),
                "Y" if r.get("Breakout") else "N",
                "Y" if r.get("VolSurge") else "N",
                r.get("Sector",""),
            ])

        if new_rows:
            ws.append_rows(new_rows, value_input_option="RAW")

        return True, f"{len(new_rows)}개 저장 완료"
    except Exception as e:
        return False, str(e)

@st.cache_data(ttl=300)
def load_pro_history():
    """History_PRO 전체 데이터 로드"""
    try:
        sh = _get_sheet()
        if sh is None: return pd.DataFrame()
        ws = sh.worksheet(SHEET_TAB)
        all_vals = ws.get_all_values()
        if len(all_vals) < 2: return pd.DataFrame()
        df = pd.DataFrame(all_vals[1:], columns=all_vals[0])
        # 타입 변환
        for col in ["EntryPrice","LeaderScore","RS","AccScore",
                    "RecRisk","EPS","CondCount","LiqStage"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df["MA200_bool"] = df["MA200"] == "Y"
        return df.dropna(subset=["Date"])
    except Exception:
        return pd.DataFrame()

# ═══════════════════════════════════════════════════════════
# INSTITUTIONAL LEADER ENGINE
# ═══════════════════════════════════════════════════════════
def calculate_leader_score(row: dict, mctx: dict) -> dict:
    """
    기관형 리더주 종합 점수 (CLAUDE_RULES.md v2)
    12단계 평가 → score / grade / reasons / acc_score
    """
    score   = 0
    reasons = []

    liq   = mctx.get("liq_stage", 3)
    rec   = mctx.get("rec_risk", 50)
    vix   = mctx.get("vix", 20)
    trend = mctx.get("qqq_trend", "NEUTRAL")
    drop  = mctx.get("mkt_drop", 0)

    # 1. 시장 환경
    if liq <= 2:   score -= 20; reasons.append("유동성위험")
    elif liq >= 4: score += 10; reasons.append("💧유동성우호")
    if rec >= 70:  score -= 25; reasons.append("침체위험")
    elif rec <= 35: score += 10
    if vix >= 28:  score -= 25; reasons.append("VIX급등")
    elif vix <= 18: score += 5
    if trend == "BULL": score += 10; reasons.append("📈상승추세")
    elif trend == "BEAR": score -= 15; reasons.append("📉하락추세")

    # 2. RS 상대강도
    rs = _safe_float(row.get("RS", 0))
    if rs >= 95:   score += 35; reasons.append("🚀RS초강세")
    elif rs >= 90: score += 25
    elif rs >= 80: score += 15
    elif rs < 70:  score -= 25; reasons.append("RS약세")

    # 3. MA200 필터 (핵심 방어선)
    above_ma200 = row.get("MA200", False)
    if not above_ma200:
        score -= 40; reasons.append("⛔MA200하회")
    else:
        score += 20; reasons.append("📊MA200위")

    # 4. 신고가 근처
    hd = _safe_float(row.get("HighDist", -100))
    if hd >= -5:    score += 25; reasons.append("🔥신고가근처")
    elif hd >= -10: score += 15
    elif hd <= -25: score -= 20; reasons.append("신고가대비약세")

    # 5. 기관 거래량
    vr = _safe_float(row.get("VolRatio", 1), 1)
    if vr >= 2.0:   score += 25; reasons.append("🏦기관거래량")
    elif vr >= 1.5: score += 15
    elif vr <= 0.7: score -= 10

    # 6. 실적 성장
    eps = _safe_float(row.get("EPS", 0))
    rev = _safe_float(row.get("Rev", 0))
    if eps >= 50:   score += 25; reasons.append("📈초고성장EPS")
    elif eps >= 30: score += 20; reasons.append("📈EPS고성장")
    elif eps < 0:   score -= 25; reasons.append("EPS감소")
    if rev >= 30:   score += 15
    elif rev >= 20: score += 10
    elif rev < 0:   score -= 10

    # 7. MA 추세 (MA50)
    if row.get("MA50", False): score += 10
    if row.get("MA20", False): score += 5

    # 8. 하락장 생존 리더 (핵심 차별화)
    if drop <= -10:
        if rs >= 90 and hd >= -10:
            score += 35; reasons.append("🛡️하락장생존")
        if vr >= 1.5: score += 10

    # 9. 섹터 점수
    ss = _safe_float(row.get("SectorScore", 50), 50)
    if ss >= 85:   score += 20; reasons.append("🏆리더섹터")
    elif ss >= 70: score += 10
    elif ss <= 40: score -= 10

    # 10. 실적 발표 위험
    if row.get("EarningsWarn"): score -= 10; reasons.append("⚠️실적임박")

    # 11. Accumulation Score (기관 매집)
    acc = 0
    if _safe_float(row.get("UpVolRatio",1)) >= 1.3: acc += 10
    if row.get("GapHold",  False): acc += 10
    if row.get("AboveVWAP",False): acc += 10
    if _safe_float(row.get("OBVTrend",0)) > 0:      acc += 10
    if row.get("Breakout",False) and vr >= 1.5:      acc += 10
    score += acc
    if acc >= 25: reasons.append("🏦기관매집")

    # 12. 침체 × RS 제한
    if rec >= 75 and rs < 95: score -= 15

    # 등급
    if   score >= 140: grade = "🚀 ELITE"
    elif score >= 110: grade = "🔥 STRONG"
    elif score >= 80:  grade = "✅ WATCH"
    else:              grade = "⚠️ WEAK"

    return {"score": round(score,1), "grade": grade,
            "reasons": " | ".join(reasons), "acc": acc}

# ═══════════════════════════════════════════════════════════
# 데이터 로드
# ═══════════════════════════════════════════════════════════
@st.cache_data(ttl=3600, show_spinner=False)
def load_fred(api_key, _bust=0):
    """FRED 핵심 지표 로드"""
    d = {}
    series = {
        "FedFunds":    "FEDFUNDS",
        "M2":          "M2SL",
        "RRP":         "RRPONTSYD",
        "TGA":         "WDTGAL",
        "Reserves":    "WRESBAL",
        "RealRate":    "DFII10",
        "CreditSpread":"BAMLH0A0HYM2",
        "T10Y2Y":      "T10Y2Y",
        "SAHM":        "SAHMREALTIME",
        "UNRATE":      "UNRATE",
    }
    for k, sid in series.items():
        s = _fred_series(sid, api_key)
        if s is not None:
            d[k] = s
    return d

@st.cache_data(ttl=900, show_spinner=False)
def load_market(_bust=0):
    """QQQ 시장 데이터 + FRED VIX"""
    out = {}
    # QQQ / SPY
    try:
        for tk in ["QQQ", "SPY"]:
            _d = yf.download(tk, period="1y", interval="1d",
                auto_adjust=True, progress=False)
            if _d.empty: continue
            # 단일 종목은 컬럼이 단순 또는 멀티레벨 둘 다 가능
            if isinstance(_d.columns, pd.MultiIndex):
                _close = _d["Close"][tk].dropna()
            elif "Close" in _d.columns:
                _close = _d["Close"].dropna()
            else:
                continue
            if len(_close) > 10:
                out[tk] = _close
    except Exception: pass
    # VIX — FRED VIXCLS (가장 안정적)
    try:
        _fred_key = ""
        try: _fred_key = st.secrets.get("FRED_API_KEY","")
        except: pass
        if _fred_key:
            _vix_s = _fred_series("VIXCLS", _fred_key, start="2024-01-01")
            if _vix_s is not None and len(_vix_s) > 0:
                out["^VIX"] = _vix_s
    except Exception: pass
    # VIX — yfinance 백업
    if "^VIX" not in out:
        try:
            _vd = yf.download("^VIX", period="30d",
                auto_adjust=True, progress=False)
            if not _vd.empty and "Close" in _vd.columns:
                out["^VIX"] = _vd["Close"].dropna()
        except Exception: pass
    return out

@st.cache_data(ttl=1800, show_spinner=False)
def load_stocks(_bust=0):
    """종목 전체 데이터 수집 + 스코어링"""
    results = []
    try:
        sys.stderr = io.StringIO()
        raw = yf.download(
            SCREEN_TICKERS + ["QQQ"],
            period="1y", interval="1d",
            auto_adjust=True, progress=False,
            threads=True, group_by="ticker"
        )
        sys.stderr = sys.__stderr__
    except Exception:
        sys.stderr = sys.__stderr__
        return []

    # QQQ 기준 수익률
    try:
        qqq_c = raw["QQQ"]["Close"].dropna()
        qqq_r = qqq_c.pct_change().dropna()
    except Exception:
        qqq_c = pd.Series(dtype=float)
        qqq_r = pd.Series(dtype=float)

    for tk in SCREEN_TICKERS:
        try:
            try:
                close  = raw[tk]["Close"].dropna()
                volume = raw[tk]["Volume"].dropna()
                high   = raw[tk]["High"].dropna()
                open_  = raw[tk]["Open"].dropna()
            except Exception:
                continue
            if len(close) < 60: continue

            cur   = _safe_float(close.iloc[-1])
            ret   = close.pct_change().dropna()

            # RS Score (1m·3m·6m·12m 가중 평균)
            def _rs(n):
                _n = min(n, len(ret), len(qqq_r))
                if _n < 5: return 50.0
                tk_r  = (1+ret.iloc[-_n:]).prod()-1
                qq_r  = (1+qqq_r.iloc[-_n:]).prod()-1
                return float(np.clip(50+(tk_r-qq_r)*100*2, 0, 100))

            rs = round(_rs(20)*0.25+_rs(60)*0.30+_rs(120)*0.25+_rs(250)*0.20, 1)

            # MA
            ma20  = _safe_float(close.rolling(20).mean().iloc[-1])  if len(close)>=20  else cur
            ma50  = _safe_float(close.rolling(50).mean().iloc[-1])  if len(close)>=50  else cur
            ma200 = _safe_float(close.rolling(200).mean().iloc[-1]) if len(close)>=200 else cur
            above_ma20  = cur > ma20
            above_ma50  = cur > ma50
            above_ma200 = cur > ma200

            # 52주 고점
            hi52    = _safe_float(close.rolling(min(252,len(close))).max().iloc[-1])
            high_dist = round((cur-hi52)/hi52*100, 1) if hi52>0 else -100

            # 거래량
            avg_v   = _safe_float(close.rolling(20).mean().iloc[-1]) if len(volume)>=20 else 1
            avg_v   = _safe_float(volume.iloc[-21:-1].mean()) if len(volume)>=21 else 1
            vol_ratio = _safe_float(volume.iloc[-1]) / avg_v if avg_v > 0 else 1.0

            # 브레이크아웃
            breakout = (cur > _safe_float(close.iloc[-22:-1].max())) if len(close)>=22 else False

            # 거래량 급증
            vol_surge = vol_ratio >= 1.5

            # 3연상
            try:
                consec = all(close.iloc[-i] > close.iloc[-i-1] for i in range(1,4))
            except Exception:
                consec = False

            # OBV 추세
            try:
                pdiff = close.diff().iloc[-20:]
                obv_d = volume.iloc[-20:] * pdiff.apply(
                    lambda x: 1 if x>0 else(-1 if x<0 else 0))
                obv_c = obv_d.cumsum()
                obv_trend = 1 if _safe_float(obv_c.iloc[-1]) > _safe_float(obv_c.iloc[0]) else -1
            except Exception:
                obv_trend = 0

            # 양봉 거래량 비율
            try:
                up_d  = close.diff().iloc[-10:] > 0
                up_v  = _safe_float(volume.iloc[-10:][up_d].mean())  if up_d.any()  else 0
                dn_v  = _safe_float(volume.iloc[-10:][~up_d].mean()) if (~up_d).any() else 1
                up_vr = up_v/dn_v if dn_v > 0 else 1.0
            except Exception:
                up_vr = 1.0

            # VWAP 근사 (5일)
            try:
                vwap = _safe_float(
                    (close.iloc[-5:]*volume.iloc[-5:]).sum() /
                    volume.iloc[-5:].sum()
                ) if volume.iloc[-5:].sum()>0 else cur
                above_vwap = cur >= vwap
            except Exception:
                above_vwap = False

            # 갭업 유지
            try:
                gap_hold = (
                    _safe_float(open_.iloc[-1]) > _safe_float(high.iloc[-2])*1.01
                    and cur >= _safe_float(open_.iloc[-1])*0.99
                )
            except Exception:
                gap_hold = False

            # RSI
            try:
                dlt = close.diff()
                up  = dlt.clip(lower=0).rolling(14).mean()
                dn  = (-dlt.clip(upper=0)).rolling(14).mean()
                rsi = round(float(100 - 100/(1+up/dn.replace(0,1e-9))).iloc[-1],1)
            except Exception:
                rsi = 50.0

            # EPS / Rev (yfinance fast_info)
            eps = rev = 0.0
            try:
                info = yf.Ticker(tk).fast_info
                eps  = round(_safe_float(getattr(info,"earnings_growth",0))*100,1)
            except Exception:
                pass
            try:
                info2 = yf.Ticker(tk).info
                rev   = round(_safe_float(info2.get("revenueGrowth",0))*100,1)
            except Exception:
                pass

            # 실적 발표 임박 (3일 이내)
            earnings_warn = False
            try:
                cal = yf.Ticker(tk).calendar
                if cal is not None and "Earnings Date" in cal:
                    ed = pd.to_datetime(cal["Earnings Date"][0])
                    earnings_warn = 0 <= (ed - pd.Timestamp.now()).days <= 3
            except Exception:
                pass

            # 조건 카운트
            cond_count = sum([
                True,            # 유동성 (외부 판단)
                breakout,
                vol_surge,
                rs >= 80,
                above_ma200,
                high_dist >= -10,
                rsi < 70,
                above_ma50,
                eps > 30,
            ])

            results.append({
                "Ticker":      tk,
                "Sector":      SECTOR_MAP.get(tk,"기타"),
                "EntryPrice":  round(cur, 2),
                "RS":          rs,
                "MA200":       above_ma200,
                "MA50":        above_ma50,
                "MA20":        above_ma20,
                "HighDist":    high_dist,
                "VolRatio":    round(vol_ratio, 2),
                "Breakout":    breakout,
                "VolSurge":    vol_surge,
                "Consec":      consec,
                "OBVTrend":    obv_trend,
                "UpVolRatio":  round(up_vr, 2),
                "AboveVWAP":   above_vwap,
                "GapHold":     gap_hold,
                "RSI":         rsi,
                "EPS":         eps,
                "Rev":         rev,
                "EarningsWarn":earnings_warn,
                "CondCount":   cond_count,
                "SectorScore": 50,   # 섹터 점수는 market 로드 후 업데이트
            })
        except Exception:
            continue

    return results

# ═══════════════════════════════════════════════════════════
# 유동성 + 경기침체 점수 계산
# ═══════════════════════════════════════════════════════════
def calc_liq_score(fred: dict) -> tuple:
    """유동성 점수 (0~100) + 단계 (1~5)"""
    score = 50
    detail = {}

    ff = _safe_float(fred.get("FedFunds", pd.Series([5])).iloc[-1] if isinstance(fred.get("FedFunds"), pd.Series) else 5)
    rr = _safe_float(fred.get("RealRate", pd.Series([1])).iloc[-1] if isinstance(fred.get("RealRate"), pd.Series) else 1)
    cs = _safe_float(fred.get("CreditSpread", pd.Series([4])).iloc[-1] if isinstance(fred.get("CreditSpread"), pd.Series) else 4)
    rrp= _safe_float(fred.get("RRP",  pd.Series([500])).iloc[-1] if isinstance(fred.get("RRP"),  pd.Series) else 500)
    res= _safe_float(fred.get("Reserves",pd.Series([3000])).iloc[-1] if isinstance(fred.get("Reserves"), pd.Series) else 3000)

    if ff > 5:    score -= 10; detail["금리"] = f"긴축({ff:.1f}%)"
    elif ff < 2:  score += 10; detail["금리"] = f"완화({ff:.1f}%)"
    else:         detail["금리"] = f"중립({ff:.1f}%)"

    if rr > 2:    score -= 10; detail["실질금리"] = f"높음({rr:.2f}%)"
    elif rr < 0:  score += 10; detail["실질금리"] = f"마이너스({rr:.2f}%)"
    else:         detail["실질금리"] = f"중립({rr:.2f}%)"

    if cs > 5:    score -= 15; detail["크레딧"] = f"위험({cs:.2f}%)"
    elif cs < 3.5:score += 10; detail["크레딧"] = f"안정({cs:.2f}%)"
    else:         detail["크레딧"] = f"주의({cs:.2f}%)"

    if rrp > 1000: score -= 5; detail["RRP"] = f"잠김({rrp/1e3:.1f}T)"
    else:          score += 5; detail["RRP"] = f"해소({rrp/1e3:.1f}T)"

    if res < 2000: score -= 10; detail["준비금"] = f"부족({res/1e3:.1f}T)"
    elif res > 3000:score += 5; detail["준비금"] = f"충분({res/1e3:.1f}T)"
    else:          detail["준비금"] = f"보통({res/1e3:.1f}T)"

    score = max(0, min(100, score))
    if   score >= 80: stage = 5
    elif score >= 60: stage = 4
    elif score >= 40: stage = 3
    elif score >= 20: stage = 2
    else:             stage = 1
    return score, stage, detail

def calc_rec_score(fred: dict) -> float:
    """경기침체 위험 점수 (0~100)"""
    signals = []
    t10y2y = fred.get("T10Y2Y")
    if t10y2y is not None and len(t10y2y)>0:
        v = _safe_float(t10y2y.iloc[-1])
        signals.append(90 if v < -0.5 else (65 if v < 0 else (35 if v < 0.5 else 10)))
    sahm = fred.get("SAHM")
    if sahm is not None and len(sahm)>0:
        v = _safe_float(sahm.iloc[-1])
        signals.append(95 if v>=0.5 else (60 if v>=0.3 else (30 if v>=0.1 else 5)))
    cs = fred.get("CreditSpread")
    if cs is not None and len(cs)>0:
        v = _safe_float(cs.iloc[-1])
        signals.append(95 if v>7 else (70 if v>5 else (45 if v>4 else (20 if v>3 else 8))))
    unrate = fred.get("UNRATE")
    if unrate is not None and len(unrate)>=4:
        v  = _safe_float(unrate.iloc[-1])
        pp = _safe_float(unrate.iloc[-4])
        chg= v-pp
        signals.append(80 if chg>0.5 else (50 if chg>0.2 else (25 if chg>0 else 8)))
    return round(sum(signals)/len(signals), 1) if signals else 50.0

def build_market_ctx(liq_stage, rec_score, mkt_data):
    """시장 컨텍스트 생성"""
    ctx = {"liq_stage":liq_stage,"rec_risk":rec_score,
           "vix":20.0,"qqq_trend":"NEUTRAL","mkt_drop":0}
    try:
        vix = mkt_data.get("^VIX", mkt_data.get("VIX"))
        if vix is not None and len(vix)>0:
            ctx["vix"] = _safe_float(vix.iloc[-1])
        qqq = mkt_data.get("QQQ")
        if qqq is not None and len(qqq)>=50:
            c    = _safe_float(qqq.iloc[-1])
            ma20 = _safe_float(qqq.rolling(20).mean().iloc[-1])
            ma50 = _safe_float(qqq.rolling(50).mean().iloc[-1])
            if c > ma20 > ma50: ctx["qqq_trend"] = "BULL"
            elif c < ma20 < ma50: ctx["qqq_trend"] = "BEAR"
            hi52 = _safe_float(qqq.rolling(min(252,len(qqq))).max().iloc[-1])
            if hi52 > 0: ctx["mkt_drop"] = round((c-hi52)/hi52*100,1)
    except Exception: pass
    return ctx

# ═══════════════════════════════════════════════════════════
# 메인 앱
# ═══════════════════════════════════════════════════════════

# ── 헤더 ─────────────────────────────────────────────────
st.markdown(
    f"<div style='display:flex;justify-content:space-between;"
    f"align-items:center;padding:6px 0;border-bottom:1px solid #1E2D3D;"
    f"margin-bottom:12px'>"
    f"<span style='font-family:Space Mono,monospace;font-size:14px;"
    f"font-weight:700;color:#0D1117'>⚡ QUANTUM PRO</span>"
    f"<span style='font-size:10px;color:#6B7280'>{PRO_VERSION} &nbsp;|&nbsp; "
    f"{datetime.now().strftime('%Y-%m-%d %H:%M')}</span>"
    f"</div>",
    unsafe_allow_html=True)

# ── 세션 초기화 ──────────────────────────────────────────
if "cache_key" not in st.session_state:
    st.session_state["cache_key"] = 0
if "pro_results" not in st.session_state:
    st.session_state["pro_results"] = []

# ── API 키 로드 ──────────────────────────────────────────
try:
    FRED_API_KEY = st.secrets.get("FRED_API_KEY","")
except Exception:
    FRED_API_KEY = ""

# ── 사이드바 ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("**⚡ QUANTUM PRO**")
    st.markdown("---")
    if st.button("🔄 데이터 새로고침", use_container_width=True):
        st.session_state["cache_key"] += 1
        st.session_state["pro_results"] = []
        st.cache_data.clear()
        st.rerun()
    st.markdown(f"<div style='font-size:9px;color:#6B7280;margin-top:4px'>"
                f"🕐 {datetime.now().strftime('%H:%M:%S')}</div>",
                unsafe_allow_html=True)
    st.markdown("---")
    _ck = st.session_state["cache_key"]
    st.markdown(f"<div style='font-size:9px;color:#6B7280'>"
                f"FRED: {'✅' if FRED_API_KEY else '❌'}<br>"
                f"Sheets: {'✅' if _GS_OK else '❌'}<br>"
                f"Cache: #{_ck}</div>", unsafe_allow_html=True)

# ── 탭 ───────────────────────────────────────────────────
t_market, t_leaders, t_backtest = st.tabs([
    "📊 MARKET", "🏆 LEADERS", "📈 BACKTEST"
])

# ════════════════════════════════════════════════════════════
# TAB 0 — MARKET
# ════════════════════════════════════════════════════════════
with t_market:
    _ck = st.session_state["cache_key"]
    with st.spinner("데이터 로드 중..."):
        fred = load_fred(FRED_API_KEY, _bust=_ck)
        mkt  = load_market(_bust=_ck)

    liq_score, liq_stage, liq_detail = calc_liq_score(fred)
    rec_score = calc_rec_score(fred)
    mkt_ctx   = build_market_ctx(liq_stage, rec_score, mkt)

    # session_state 저장 → LEADERS 탭에서 사용
    st.session_state["liq_score"]  = liq_score
    st.session_state["liq_stage"]  = liq_stage
    st.session_state["rec_score"]  = rec_score
    st.session_state["mkt_ctx"]    = mkt_ctx

    # ── 핵심 지표 카드 ───────────────────────────────────
    c1,c2,c3,c4 = st.columns(4)

    # ── 핵심 지표 — 엑셀형 소형 카드 ──────────────────────
    _lc = "#B91C1C" if liq_stage<=2 else ("#92400E" if liq_stage==3 else "#166534")
    _rc = "#B91C1C" if rec_score>=70 else ("#92400E" if rec_score>=50 else ("#92400E" if rec_score>=30 else "#166534"))
    _vc = "#B91C1C" if mkt_ctx["vix"]>=28 else ("#92400E" if mkt_ctx["vix"]>=20 else "#166534")
    _qc = "#166534" if mkt_ctx["qqq_trend"]=="BULL" else ("#B91C1C" if mkt_ctx["qqq_trend"]=="BEAR" else "#374151")
    _qi = "BULL" if mkt_ctx["qqq_trend"]=="BULL" else ("BEAR" if mkt_ctx["qqq_trend"]=="BEAR" else "NEUTRAL")

    def _mini_card(col, label, val, sub, color):
        col.markdown(
            f"<div style='background:#FFFFFF;border:1px solid #E2E6ED;"
            f"border-radius:3px;padding:5px 8px;margin:0'>"
            f"<div style='font-size:9px;color:#9CA3AF;line-height:1.2'>{label}</div>"
            f"<div style='font-size:18px;font-weight:700;color:{color};line-height:1.3'>{val}</div>"
            f"<div style='font-size:9px;color:#6B7280;line-height:1.2'>{sub}</div>"
            f"</div>", unsafe_allow_html=True)

    _mini_card(c1, "유동성", f"{liq_stage}단계", f"{liq_score:.0f}점/100", _lc)
    _mini_card(c2, "침체위험", f"{rec_score:.0f}점", "/100", _rc)
    _mini_card(c3, "VIX", f"{mkt_ctx['vix']:.1f}", "변동성지수", _vc)
    _mini_card(c4, "QQQ추세", _qi, f"{mkt_ctx['mkt_drop']:+.1f}% (52W)", _qc)


    st.markdown("---")

    # ── 유동성 상세 ──────────────────────────────────────
    st.markdown(
        "<div style='font-size:11px;color:#374151;"
        "font-family:Space Mono,monospace;margin-bottom:8px'>"
        "LIQUIDITY BREAKDOWN</div>",
        unsafe_allow_html=True)

    _liq_df = pd.DataFrame([
        {"지표": k, "상태": v,
         "신호": "🟢" if any(x in v for x in ["완화","해소","충분","안정","마이너스"])
                 else ("🔴" if any(x in v for x in ["긴축","잠김","부족","위험","높음"])
                 else "🟡")}
        for k, v in liq_detail.items()
    ])
    st.dataframe(
        _liq_df, use_container_width=True, hide_index=True,
        column_config={
            "지표":  st.column_config.TextColumn("지표", width="small"),
            "상태":  st.column_config.TextColumn("상태"),
            "신호":  st.column_config.TextColumn("신호", width="small"),
        })

    st.markdown("---")

    # ── 투자 행동 지침 ───────────────────────────────────
    if rec_score >= 70:
        _a_color="#EF4444"; _a_title="🚨 침체 고위험 — 매수 전면 중단"
        _actions = ["신규매수 금지","포지션 50%↑ 현금화",
                    "GLD·TLT 헤지 확대","손절 -5% 강화"]
    elif rec_score >= 50:
        _a_color="#F59E0B"; _a_title="⚠️ 침체 주의 — 방어적 포지션"
        _actions = ["신규매수 투자금 20% 이하","현금 40~50% 유지",
                    "RS 90↑ 생존 리더만","손절 -6% 강화"]
    elif rec_score >= 30:
        _a_color="#FBBF24"; _a_title="🟡 침체 관찰 — 선택적 진입"
        _actions = ["유동성 확인 후 분할매수","현금 30% 유지",
                    "리더섹터 집중","손절 -8% 표준"]
    else:
        _a_color="#10B981"; _a_title="🟢 침체 안전 — 공격 가능"
        _actions = ["유동성 단계 기준 적극매수","현금 20% 이하",
                    "ELITE·STRONG 우선 진입","손절 -8% 표준"]

    st.markdown(
        f"<div style='background:#FFFFFF;border:1px solid {_a_color};"
        f"border-radius:3px;padding:6px 8px'>"
        f"<div style='font-size:12px;font-weight:700;color:{_a_color};"
        f"margin-bottom:4px'>{_a_title}</div>"
        + "".join(
            f"<div style='font-size:11px;color:#374151;padding:2px 0'>"
            f"<span style='color:{_a_color};margin-right:6px'>→</span>{a}</div>"
            for a in _actions)
        + "</div>",
        unsafe_allow_html=True)

    # ── FRED 실시간 주요 수치 ──────────────────────────
    st.markdown("---")
    st.markdown(
        "<div style='font-size:11px;color:#374151;"
        "font-family:Space Mono,monospace;margin-bottom:8px'>"
        "FRED LIVE DATA</div>",
        unsafe_allow_html=True)

    _fred_display = []
    for name, sid in [
        ("기준금리","FedFunds"),("실질금리","RealRate"),
        ("크레딧스프레드","CreditSpread"),("장단기금리차","T10Y2Y"),
        ("Sahm Rule","SAHM"),("실업률","UNRATE"),
    ]:
        s = fred.get(sid)
        if s is not None and len(s) > 0:
            v = _safe_float(s.iloc[-1])
            d = str(s.index[-1])[:10]
            _fred_display.append({"지표": name, "현재값": round(v,3),
                                   "기준일": d})

    if _fred_display:
        st.dataframe(
            pd.DataFrame(_fred_display),
            use_container_width=True, hide_index=True,
            column_config={
                "지표":  st.column_config.TextColumn("지표",  width="medium"),
                "현재값":st.column_config.NumberColumn("현재값",format="%.3f"),
                "기준일":st.column_config.TextColumn("기준일",width="small"),
            })

# ════════════════════════════════════════════════════════════
# TAB 1 — LEADERS
# ════════════════════════════════════════════════════════════
with t_leaders:
    _ck = st.session_state["cache_key"]
    _liq_stage = st.session_state.get("liq_stage", 3)
    _rec_score = st.session_state.get("rec_score", 50)
    _mkt_ctx   = st.session_state.get("mkt_ctx",
        {"liq_stage":3,"rec_risk":50,"vix":20,"qqq_trend":"NEUTRAL","mkt_drop":0})

    # 유동성 단계 경고
    if _liq_stage <= 2:
        st.markdown(
            "<div style='background:#FFFFFF;border:1px solid #EF4444;"
            "border-radius:3px;padding:10px;margin-bottom:10px;"
            "font-size:12px;color:#EF4444;font-weight:700'>"
            "🚨 유동성 2단계 이하 — 신규 매수 금지 구간</div>",
            unsafe_allow_html=True)

    # 데이터 로드
    if not st.session_state.get("pro_results"):
        with st.spinner(f"📡 {len(SCREEN_TICKERS)}개 종목 분석 중..."):
            _raw_results = load_stocks(_bust=_ck)
            st.session_state["pro_results"] = _raw_results
    else:
        _raw_results = st.session_state["pro_results"]

    if not _raw_results:
        st.error("종목 데이터 로드 실패")
        st.stop()

    # Leader Score 계산
    _scored = []
    for r in _raw_results:
        _res = calculate_leader_score(r, _mkt_ctx)
        _scored.append({**r, **{
            "LeaderScore": _res["score"],
            "LeaderGrade": _res["grade"],
            "Signal":      _res["reasons"],
            "AccScore":    _res["acc"],
        }})

    df = pd.DataFrame(_scored)

    # ── MA200 필터 표시 ──────────────────────────────────
    df_above = df[df["MA200"]].copy()
    df_below = df[~df["MA200"]].copy()

    # Leader Score 기준 정렬
    df_above = df_above.sort_values("LeaderScore", ascending=False).reset_index(drop=True)
    df_above.index = df_above.index + 1

    # ── 필터 옵션 ────────────────────────────────────────
    _fc1, _fc2, _fc3 = st.columns([1,1,2])
    with _fc1:
        _min_grade = st.selectbox("최소 등급",
            ["전체","✅ WATCH↑","🔥 STRONG↑","🚀 ELITE"],
            key="pro_grade_filter")
    with _fc2:
        _min_rs = st.number_input("최소 RS", 0, 100, 70, 5, key="pro_rs_filter")
    with _fc3:
        _sectors = ["전체"] + sorted(df["Sector"].unique().tolist())
        _sec_sel = st.selectbox("섹터", _sectors, key="pro_sector_filter")

    # 필터 적용
    _fdf = df_above.copy()
    if _min_grade == "🚀 ELITE":
        _fdf = _fdf[_fdf["LeaderGrade"].str.contains("ELITE")]
    elif _min_grade == "🔥 STRONG↑":
        _fdf = _fdf[_fdf["LeaderGrade"].str.contains("ELITE|STRONG")]
    elif _min_grade == "✅ WATCH↑":
        _fdf = _fdf[_fdf["LeaderGrade"].str.contains("ELITE|STRONG|WATCH")]
    if _min_rs > 0:
        _fdf = _fdf[_fdf["RS"] >= _min_rs]
    if _sec_sel != "전체":
        _fdf = _fdf[_fdf["Sector"] == _sec_sel]

    # ── 요약 카운터 ──────────────────────────────────────
    _s1,_s2,_s3,_s4,_s5 = st.columns(5)
    _s1.metric("전체", len(df))
    _s2.metric("MA200 위", len(df_above))
    _s3.metric("🚀 ELITE",  len(df_above[df_above["LeaderGrade"].str.contains("ELITE")]))
    _s4.metric("🔥 STRONG", len(df_above[df_above["LeaderGrade"].str.contains("STRONG")]))
    _s5.metric("⛔ MA200 아래", len(df_below), delta=None)

    st.markdown("---")

    # ── 메인 테이블 ──────────────────────────────────────
    st.markdown(
        "<div style='font-size:11px;color:#374151;"
        "font-family:Space Mono,monospace;margin-bottom:6px'>"
        f"MA200 위 종목 ({len(_fdf)}개) — Leader Score 순위</div>",
        unsafe_allow_html=True)

    _disp_cols = ["Ticker","Sector","LeaderGrade","LeaderScore","AccScore",
                  "RS","HighDist","VolRatio","EPS","RSI",
                  "Breakout","VolSurge","Consec","EntryPrice","CondCount"]
    _disp = _fdf[[c for c in _disp_cols if c in _fdf.columns]].copy()

    # bool → 기호 변환
    for bc in ["Breakout","VolSurge","Consec"]:
        if bc in _disp.columns:
            _disp[bc] = _disp[bc].map({True:"✅", False:"—"})

    st.dataframe(
        _disp,
        use_container_width=True,
        column_config={
            "Ticker":      st.column_config.TextColumn("Ticker",   width="small"),
            "Sector":      st.column_config.TextColumn("섹터",     width="small"),
            "LeaderGrade": st.column_config.TextColumn("🏆등급",   width="small"),
            "LeaderScore": st.column_config.NumberColumn("리더점수", format="%.0f"),
            "AccScore":    st.column_config.NumberColumn("매집",    format="%.0f", width="small"),
            "RS":          st.column_config.NumberColumn("RS",      format="%.1f", width="small"),
            "HighDist":    st.column_config.NumberColumn("신고가%", format="%.1f", width="small"),
            "VolRatio":    st.column_config.NumberColumn("거래량배율",format="%.2f",width="small"),
            "EPS":         st.column_config.NumberColumn("EPS성장%",format="%.1f",width="small"),
            "RSI":         st.column_config.NumberColumn("RSI",     format="%.1f", width="small"),
            "Breakout":    st.column_config.TextColumn("돌파",      width="small"),
            "VolSurge":    st.column_config.TextColumn("거래량",    width="small"),
            "Consec":      st.column_config.TextColumn("3연상",     width="small"),
            "EntryPrice":  st.column_config.NumberColumn("현재가",  format="$%.2f"),
            "CondCount":   st.column_config.NumberColumn("조건수",  format="%.0f", width="small"),
        },
        hide_index=False,
    )


    # ── MA200 이하 종목 — session_state 토글 (expander 사용 금지) ──
    if "show_ma200_below" not in st.session_state:
        st.session_state["show_ma200_below"] = False
    _btn_lbl = (
        f"▼ MA200 이하 종목 ({len(df_below)}개) 숨기기"
        if st.session_state["show_ma200_below"]
        else f"▶ MA200 이하 종목 ({len(df_below)}개) — 매수 금지"
    )
    if st.button(_btn_lbl, key="toggle_ma200_below"):
        st.session_state["show_ma200_below"] = not st.session_state["show_ma200_below"]
        st.rerun()
    if st.session_state["show_ma200_below"]:
        st.markdown(
            "<div style='background:#FEF2F2;border:1px solid #FECACA;"
            "border-radius:3px;padding:8px 12px;margin-bottom:6px;"
            "font-size:11px;color:#B91C1C;font-weight:600'>"
            "⛔ 아래 종목은 MA200 이하 — 등급 무관 매수 금지</div>",
            unsafe_allow_html=True)
        _db = df_below[["Ticker","Sector","RS","HighDist","EntryPrice"]].copy()
        _db.columns = ["Ticker","섹터","RS","신고가%","현재가"]
        st.dataframe(
            _db, use_container_width=True, hide_index=True,
            column_config={
                "Ticker":  st.column_config.TextColumn("Ticker",  width="small"),
                "섹터":    st.column_config.TextColumn("섹터",    width="small"),
                "RS":      st.column_config.NumberColumn("RS",    format="%.1f", width="small"),
                "신고가%": st.column_config.NumberColumn("신고가%", format="%.1f", width="small"),
                "현재가":  st.column_config.NumberColumn("현재가", format="$%.2f"),
            })

    st.markdown("---")

    # ── Google Sheets 저장 ───────────────────────────────
    st.markdown(
        "<div style='font-size:11px;color:#374151;"
        "font-family:Space Mono,monospace;margin-bottom:6px'>"
        "SAVE TO SHEETS</div>",
        unsafe_allow_html=True)

    _save_c1, _save_c2 = st.columns([2,1])
    with _save_c1:
        st.markdown(
            f"<div style='font-size:10px;color:#6B7280'>"
            f"저장 탭: <b style='color:#374151'>History_PRO</b> &nbsp;|&nbsp; "
            f"오늘 날짜 + 종목별 1행 + 진입가 포함</div>",
            unsafe_allow_html=True)
    with _save_c2:
        if st.button("💾 Sheets 저장", use_container_width=True, key="pro_save"):
            # ── 연결 진단 먼저 ──
            _sh_diag, _diag_msg = _get_sheet(debug=True)
            if _sh_diag is None:
                st.error(f"❌ Sheets 연결 실패: {_diag_msg}")
            else:
                # MA200 위 + WATCH 이상만 저장
                _save_rows = [
                    r for r in _scored
                    if r.get("MA200") and r.get("LeaderScore",0) >= 80
                ]
                if not _save_rows:
                    st.warning("저장할 종목 없음 (MA200 위 + 80점↑ 조건 미충족)")
                else:
                    with st.spinner(f"{len(_save_rows)}개 저장 중..."):
                        _ok, _msg = save_pro_results(
                            _save_rows,
                            st.session_state.get("liq_stage", 3),
                            st.session_state.get("rec_score", 50),
                        )
                    if _ok:
                        st.success(f"✅ {_msg}")
                    else:
                        st.error(f"❌ {_msg}")

    # ── Signal 상세 (ELITE만) ────────────────────────────
    _elite = df_above[df_above["LeaderGrade"].str.contains("ELITE|STRONG")].head(5)
    if not _elite.empty:
        st.markdown("---")
        st.markdown(
            "<div style='font-size:11px;color:#374151;"
            "font-family:Space Mono,monospace;margin-bottom:6px'>"
            "TOP 5 SIGNAL DETAIL</div>",
            unsafe_allow_html=True)
        for _, row in _elite.iterrows():
            _gc = "#00D4FF" if "ELITE" in str(row["LeaderGrade"]) else "#10B981"
            st.markdown(
                f"<div style='background:#FFFFFF;border:1px solid {_gc};"
                f"border-radius:4px;padding:4px 8px;margin-bottom:3px;"
                f"display:flex;gap:12px;align-items:center'>"
                f"<span style='color:{_gc};font-weight:700;min-width:60px'>"
                f"{row['Ticker']}</span>"
                f"<span style='color:#374151;font-size:10px'>{row.get('LeaderGrade','')}</span>"
                f"<span style='color:#6B7280;font-size:10px'>점수:{row.get('LeaderScore',0):.0f}</span>"
                f"<span style='color:#6B7280;font-size:9px'>{row.get('Signal','')[:80]}</span>"
                f"</div>",
                unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# TAB 2 — BACKTEST
# ════════════════════════════════════════════════════════════
with t_backtest:
    st.markdown(
        "<div style='font-size:11px;color:#374151;"
        "font-family:Space Mono,monospace;margin-bottom:10px'>"
        "BACKTEST — History_PRO 누적 데이터 분석</div>",
        unsafe_allow_html=True)

    with st.spinner("Sheets 데이터 로드 중..."):
        hist = load_pro_history()

    if hist.empty:
        st.markdown(
            "<div style='background:#FFFFFF;border:1px solid #1E2D3D;"
            "border-radius:3px;padding:10px;text-align:center;"
            "color:#6B7280;font-size:11px'>"
            "📊 아직 데이터 없음<br><br>"
            "LEADERS 탭에서 💾 Sheets 저장을 실행하면<br>"
            "매일 데이터가 쌓이고 여기서 분석할 수 있습니다.<br><br>"
            "<b>30일 이상 축적 후 의미 있는 백테스트 가능</b></div>",
            unsafe_allow_html=True)
    else:
        # 현재가 수집 (수익률 계산용)
        _all_tks = hist["Ticker"].unique().tolist()
        @st.cache_data(ttl=900)
        def _get_current_prices(tks):
            try:
                raw = yf.download(list(tks), period="5d",
                    auto_adjust=True, progress=False)["Close"]
                return {tk: _safe_float(raw[tk].dropna().iloc[-1])
                        for tk in tks if tk in raw.columns}
            except Exception:
                return {}

        _cur_prices = _get_current_prices(tuple(_all_tks))

        # 수익률 계산
        hist["CurPrice"]  = hist["Ticker"].map(_cur_prices)
        hist["Return%"]   = ((hist["CurPrice"] - hist["EntryPrice"])
                              / hist["EntryPrice"] * 100).round(2)
        hist["Days"]      = (datetime.now() - hist["Date"]).dt.days

        # QQQ 기준 수익률 (동기간)
        @st.cache_data(ttl=900)
        def _qqq_return_since(entry_date_str):
            try:
                s  = yf.download("QQQ", start=entry_date_str,
                    auto_adjust=True, progress=False)["Close"].dropna()
                if len(s) < 2: return 0.0
                return round((_safe_float(s.iloc[-1])-_safe_float(s.iloc[0]))
                              / _safe_float(s.iloc[0])*100, 2)
            except Exception:
                return 0.0

        # ── 요약 지표 ────────────────────────────────────
        _total  = len(hist)
        _profitable = len(hist[hist["Return%"] > 0]) if "Return%" in hist.columns else 0
        _avg_ret= hist["Return%"].mean() if "Return%" in hist.columns else 0
        _days_range = f"{hist['Date'].min().strftime('%Y-%m-%d')} ~ {hist['Date'].max().strftime('%Y-%m-%d')}"

        _b1,_b2,_b3,_b4 = st.columns(4)
        _b1.metric("총 기록",   f"{_total}건")
        _b2.metric("수익 종목", f"{_profitable}건",
                   f"{_profitable/_total*100:.0f}%" if _total>0 else "0%")
        _b3.metric("평균 수익률", f"{_avg_ret:+.2f}%")
        _b4.metric("기간", f"{hist['Days'].max():.0f}일")
        st.markdown(
            f"<div style='font-size:10px;color:#6B7280;margin-bottom:10px'>"
            f"데이터 기간: {_days_range}</div>",
            unsafe_allow_html=True)

        st.markdown("---")

        # ── 등급별 수익률 분석 ────────────────────────────
        st.markdown(
            "<div style='font-size:11px;color:#374151;"
            "font-family:Space Mono,monospace;margin-bottom:6px'>"
            "GRADE별 성과 분석</div>",
            unsafe_allow_html=True)

        _grade_stats = []
        for grade in ["🚀 ELITE","🔥 STRONG","✅ WATCH"]:
            _g = hist[hist["LeaderGrade"].str.contains(
                grade.split()[-1], na=False)]
            if len(_g) > 0:
                _grade_stats.append({
                    "등급": grade,
                    "건수": len(_g),
                    "평균수익률": round(_g["Return%"].mean(), 2),
                    "승률%": round(len(_g[_g["Return%"]>0])/len(_g)*100, 1),
                    "최대수익": round(_g["Return%"].max(), 2),
                    "최대손실": round(_g["Return%"].min(), 2),
                })

        if _grade_stats:
            st.dataframe(
                pd.DataFrame(_grade_stats),
                use_container_width=True, hide_index=True,
                column_config={
                    "등급":      st.column_config.TextColumn("등급"),
                    "건수":      st.column_config.NumberColumn("건수",   format="%d건"),
                    "평균수익률":st.column_config.NumberColumn("평균수익률",format="%+.2f%%"),
                    "승률%":     st.column_config.NumberColumn("승률",   format="%.1f%%"),
                    "최대수익":  st.column_config.NumberColumn("최대수익",format="%+.2f%%"),
                    "최대손실":  st.column_config.NumberColumn("최대손실",format="%+.2f%%"),
                })

        st.markdown("---")

        # ── MA200 필터 효과 검증 ──────────────────────────
        st.markdown(
            "<div style='font-size:11px;color:#374151;"
            "font-family:Space Mono,monospace;margin-bottom:6px'>"
            "MA200 필터 효과 검증</div>",
            unsafe_allow_html=True)

        _ma_above = hist[hist["MA200_bool"]]
        _ma_below = hist[~hist["MA200_bool"]]
        _ma_cmp = pd.DataFrame([
            {"구분":"MA200 위",   "건수":len(_ma_above),
             "평균수익률": round(_ma_above["Return%"].mean(),2) if len(_ma_above)>0 else 0,
             "승률%": round(len(_ma_above[_ma_above["Return%"]>0])/len(_ma_above)*100,1)
                       if len(_ma_above)>0 else 0},
            {"구분":"MA200 아래", "건수":len(_ma_below),
             "평균수익률": round(_ma_below["Return%"].mean(),2) if len(_ma_below)>0 else 0,
             "승률%": round(len(_ma_below[_ma_below["Return%"]>0])/len(_ma_below)*100,1)
                       if len(_ma_below)>0 else 0},
        ])
        st.dataframe(
            _ma_cmp, use_container_width=True, hide_index=True,
            column_config={
                "구분":      st.column_config.TextColumn("구분"),
                "건수":      st.column_config.NumberColumn("건수",   format="%d건"),
                "평균수익률":st.column_config.NumberColumn("평균수익률",format="%+.2f%%"),
                "승률%":     st.column_config.NumberColumn("승률",   format="%.1f%%"),
            })

        st.markdown("---")

        # ── 전체 기록 테이블 ──────────────────────────────
        st.markdown(
            "<div style='font-size:11px;color:#374151;"
            "font-family:Space Mono,monospace;margin-bottom:6px'>"
            "전체 기록</div>",
            unsafe_allow_html=True)

        _hist_disp = hist[[
            "Date","Ticker","LeaderGrade","LeaderScore",
            "EntryPrice","CurPrice","Return%","Days",
            "RS","MA200","AccScore","LiqStage","RecRisk"
        ]].copy().sort_values(["Date","LeaderScore"],
                              ascending=[False,False])

        _hist_disp["MA200"] = _hist_disp["MA200"].map({"Y":"✅","N":"⛔"})
        _hist_disp["Date"]  = _hist_disp["Date"].dt.strftime("%Y-%m-%d")

        st.dataframe(
            _hist_disp,
            use_container_width=True, hide_index=True,
            column_config={
                "Date":       st.column_config.TextColumn("날짜",    width="small"),
                "Ticker":     st.column_config.TextColumn("Ticker",  width="small"),
                "LeaderGrade":st.column_config.TextColumn("등급",    width="small"),
                "LeaderScore":st.column_config.NumberColumn("점수",  format="%.0f"),
                "EntryPrice": st.column_config.NumberColumn("진입가", format="$%.2f"),
                "CurPrice":   st.column_config.NumberColumn("현재가", format="$%.2f"),
                "Return%":    st.column_config.NumberColumn("수익률", format="%+.2f%%"),
                "Days":       st.column_config.NumberColumn("보유일", format="%d일"),
                "RS":         st.column_config.NumberColumn("RS",    format="%.1f"),
                "MA200":      st.column_config.TextColumn("MA200",   width="small"),
                "AccScore":   st.column_config.NumberColumn("매집",  format="%.0f"),
                "LiqStage":   st.column_config.NumberColumn("유동성",format="%d"),
                "RecRisk":    st.column_config.NumberColumn("침체%", format="%.1f"),
            })

# ── 푸터 ─────────────────────────────────────────────────
st.markdown(
    f"<div style='text-align:center;font-size:9px;color:#1E2D3D;"
    f"margin-top:20px;padding-top:8px;border-top:1px solid #0D1117'>"
    f"QUANTUM PRO {PRO_VERSION} &nbsp;|&nbsp; "
    f"데이터: FRED·yfinance &nbsp;|&nbsp; "
    f"본 앱은 정보 제공 목적이며 투자 권유가 아닙니다</div>",
    unsafe_allow_html=True)
