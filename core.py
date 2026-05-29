# core.py — QUANTUM 공유 모듈
# APP.py + screener_daily.py 공통 함수
# 이 파일만 수정하면 두 앱 모두 반영됩니다

import warnings; warnings.filterwarnings("ignore")
import io, sys, json, requests
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf
import streamlit as st

# ── 회사 프로필 로드 ───────────────────────────────────────
@st.cache_data(ttl=3600)
def load_company_profiles():
    """company_profiles.json 로드 (여러 경로 시도)"""
    import os
    # 시도할 경로 목록
    _candidates = [
        "company_profiles.json",                          # 현재 디렉토리
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "company_profiles.json"),
        "/mount/src/quantum-screener/company_profiles.json",  # Streamlit Cloud 경로
        "/app/company_profiles.json",
    ]
    for _path in _candidates:
        try:
            if os.path.exists(_path):
                with open(_path, "r", encoding="utf-8") as _f:
                    _data = json.load(_f)
                    if _data:
                        return _data
        except Exception:
            continue
    return {}

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
APP_VERSION   = "V1"
SHEET_TAB     = "History_PRO"      # 교육용(History)과 분리
SHEET_SCOPES  = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
SHEET_HEADER  = [
    "Date","Ticker","Name","EntryPrice","LeaderScore","LeaderGrade",
    "RS","MA200","AccScore","LiqStage","RecRisk",
    "EPS","CondCount","Breakout","VolSurge","Sector"
]

# 스크리닝 종목 (ETF·헤지 제외한 성장주)
SCREEN_TICKERS = [
    # 빅테크 / AI
    "NVDA","MSFT","META","AMZN","GOOGL","AAPL","TSLA","NFLX","COST",
    # 반도체
    "AVGO","AMD","QCOM","TXN","AMAT","MU","MRVL","LRCX","KLAC","NXPI","ADI","SMCI","QRVO",
    # 소프트웨어 / 클라우드
    "NOW","ADBE","CRM","ORCL","INTU","CDNS","SNPS","WDAY","TEAM","ANSS",
    # 사이버보안
    "PANW","CRWD","FTNT","ZS","CYBR","S","OKTA",
    # AI / 데이터 플랫폼
    "PLTR","DDOG","MDB","SNOW","HUBS","GTLB","TTD","APP",
    # 헬스케어
    "ISRG","DXCM","IDXX","GEHC","MRNA","REGN","BIIB","VEEV","PODD",
    # 소비 / 여행 / 모빌리티
    "BKNG","ABNB","LULU","MELI","SBUX","UBER","DASH","CELH","DUOL",
    # 금융 / 핀테크
    "PYPL","COIN","AXON","AFRM","SOFI",
    # 방산 / 산업재
    "LMT","RTX","NOC","CPRT","CTAS","PCAR","ODFL",
    # 에너지 / 기타
    "FANG","CEG","VST","TMUS","CMCSA",
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
    # 신규 추가
    "QRVO":"반도체","S":"사이버보안","OKTA":"사이버보안",
    "TTD":"AI플랫폼","VEEV":"헬스케어","PODD":"헬스케어",
    "UBER":"모빌리티","DASH":"모빌리티","CELH":"소비재","DUOL":"교육",
    "AFRM":"핀테크","SOFI":"핀테크",
    "LMT":"방산","RTX":"방산","NOC":"방산",
    "CPRT":"산업재","CTAS":"산업재","ODFL":"산업재",
    "VST":"에너지",
}

# 회사명 사전
COMPANY_NAME = {
    "NVDA":"엔비디아","MSFT":"마이크로소프트","META":"메타","AMZN":"아마존",
    "GOOGL":"알파벳","AAPL":"애플","TSLA":"테슬라","NFLX":"넷플릭스","COST":"코스트코",
    "AVGO":"브로드컴","AMD":"AMD","QCOM":"퀄컴","TXN":"텍사스인스트루먼트",
    "AMAT":"어플라이드머티리얼즈","MU":"마이크론","MRVL":"마벨테크","LRCX":"램리서치",
    "KLAC":"KLA","NXPI":"NXP반도체","ADI":"아날로그디바이스","SMCI":"슈퍼마이크로",
    "QRVO":"코르보","NOW":"서비스나우","ADBE":"어도비","CRM":"세일즈포스",
    "ORCL":"오라클","INTU":"인튜이트","CDNS":"케이던스","SNPS":"시놉시스",
    "WDAY":"워크데이","TEAM":"아틀라시안","ANSS":"앤시스","PANW":"팔로알토",
    "CRWD":"크라우드스트라이크","FTNT":"포티넷","ZS":"지스케일러","CYBR":"사이버아크",
    "S":"센티넬원","OKTA":"옥타","PLTR":"팔란티어","DDOG":"데이터독","MDB":"몽고DB",
    "SNOW":"스노우플레이크","HUBS":"허브스팟","GTLB":"깃랩","TTD":"더트레이드데스크",
    "APP":"앱러빈","ISRG":"인튜이티브서지컬","DXCM":"덱스컴","IDXX":"아이덱스",
    "GEHC":"GE헬스케어","MRNA":"모더나","REGN":"리제네론","BIIB":"바이오젠",
    "VEEV":"비바시스템즈","PODD":"인슐렛","BKNG":"부킹홀딩스","ABNB":"에어비앤비",
    "LULU":"룰루레몬","MELI":"메르카도리브레","SBUX":"스타벅스","UBER":"우버",
    "DASH":"도어대시","CELH":"셀시우스","DUOL":"듀오링고","PYPL":"페이팔",
    "COIN":"코인베이스","AXON":"액슨","AFRM":"어펌","SOFI":"소파이",
    "LMT":"록히드마틴","RTX":"레이시온","NOC":"노스롭그루먼","CPRT":"코파트",
    "CTAS":"신타스","PCAR":"팩카","ODFL":"올드도미니언","FANG":"다이아몬드백에너지",
    "CEG":"콘스텔레이션에너지","VST":"비스트라","TMUS":"T-모바일","CMCSA":"컴캐스트",
}

# ═══════════════════════════════════════════════════════════
# Streamlit 설정
# ═══════════════════════════════════════════════════════════
st.set_page_config(
    page_title="QUANTUM",
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

/* MOBILE 최적화 */
@media (max-width: 768px) {
    /* 폰트 크기 조정 */
    body, p, span, div, label
        { font-size:13px !important; }
    /* 최소 폰트 11px 보장 */
    small { font-size:11px !important; }
    /* 탭 버튼 작게 */
    [data-testid="stTabs"] button
        { font-size:11px !important; padding:8px 10px !important; }
    /* 메트릭 카드 */
    div[data-testid="metric-container"]
        { padding:6px !important; }
    /* 버튼 */
    .stButton button
        { font-size:11px !important; padding:6px 8px !important; }
    /* 데이터프레임 스크롤 */
    [data-testid="stDataFrame"]
        { overflow-x: auto !important; }
}

/* SELECTBOX 모바일 대비 스타일 고정 */
[data-testid="stSelectbox"] > div > div
    { background-color:#FFFFFF !important;
      color:#0D1117 !important; }
[data-testid="stSelectbox"] > div > div > div
    { color:#0D1117 !important; }
[data-testid="stSelectbox"] span
    { color:#0D1117 !important; }
[data-testid="stSelectbox"] svg
    { fill:#6B7280 !important; }
[data-testid="stSelectbox"] > label
    { color:#374151 !important; }

/* 드롭다운 펼쳐진 목록 */
[role="listbox"]
    { background-color:#FFFFFF !important; }
[role="option"]
    { background-color:#FFFFFF !important;
      color:#0D1117 !important; }
[role="option"]:hover
    { background-color:#F3F4F6 !important; }
[role="option"][aria-selected="true"]
    { background-color:#F3F4F6 !important;
      color:#0D1117 !important; }

/* NUMBER INPUT 모바일 */
[data-testid="stNumberInput"] input
    { background-color:#FFFFFF !important;
      color:#0D1117 !important;
      border-color:#D1D5DB !important; }
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
                r.get("Name", COMPANY_NAME.get(r.get("Ticker",""), "")),
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

def calc_consecutive_days(hist_df: "pd.DataFrame") -> dict:
    """
    Sheets History_PRO에서 종목별 연속 선택일 계산
    → {ticker: (연속일수, 아이콘)}
    최근 7일 기준
    """
    if hist_df.empty: return {}
    try:
        _today = pd.Timestamp.now().normalize()
        _7days = _today - pd.Timedelta(days=7)

        # 최근 7일 MA200 위 + WATCH 이상 종목만
        _recent = hist_df[
            (hist_df["Date"] >= _7days) &
            (hist_df["MA200"].isin(["Y", True, "True"]))
        ].copy()

        if _recent.empty: return {}

        # 날짜 정규화
        _recent["Date"] = pd.to_datetime(_recent["Date"]).dt.normalize()
        _dates = sorted(_recent["Date"].unique(), reverse=True)

        result = {}
        for tk in _recent["Ticker"].unique():
            tk_dates = set(
                _recent[_recent["Ticker"]==tk]["Date"].dt.normalize()
            )
            # 연속 선택일 (오늘부터 역순으로 연속된 날짜 수)
            count = 0
            for d in _dates:
                if d in tk_dates:
                    count += 1
                else:
                    break

            if count == 0: count = 1  # 최소 1일
            icon = "🔥" if count >= 5 else ("✅" if count >= 3 else "🟡")
            result[tk] = (count, icon)

        return result
    except Exception:
        return {}


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
def calculate_leader_score(row: dict, mctx: dict, cfg: dict = None) -> dict:
    """
    기관형 리더주 종합 점수 (CLAUDE_RULES.md v2)
    12단계 평가 → score / grade / reasons / acc_score
    cfg: 설정탭 가중치 (없으면 기본값)
    """
    if cfg is None: cfg = {}
    score   = 0
    reasons = []

    liq   = mctx.get("liq_stage", 3)
    rec   = mctx.get("rec_risk", 50)
    vix   = mctx.get("vix", 20)
    trend = mctx.get("qqq_trend", "NEUTRAL")
    drop  = mctx.get("mkt_drop", 0)

    # 설정값 로드 (기본값 fallback)
    _rs95_w    = cfg.get("cfg_rs95_w",    35)
    _rs90_w    = cfg.get("cfg_rs90_w",    25)
    _rs80_w    = cfg.get("cfg_rs80_w",    15)
    _ma200_pen = cfg.get("cfg_ma200_pen", 40)
    _ma200_bon = cfg.get("cfg_ma200_bon", 20)
    _vol_w     = cfg.get("cfg_vol_w",     25)
    _hd_w      = cfg.get("cfg_hd_w",     25)
    _surv_w    = cfg.get("cfg_survive_w", 35)
    _vix_warn  = cfg.get("cfg_vix_warn",  28)
    _rec_max   = cfg.get("cfg_rec_max",   70)

    # 1. 시장 환경
    if liq <= 2:   score -= 20; reasons.append("유동성위험")
    elif liq >= 4: score += 10; reasons.append("💧유동성우호")
    if rec >= _rec_max:  score -= 25; reasons.append("침체위험")
    elif rec <= 35:      score += 10
    if vix >= _vix_warn: score -= 25; reasons.append("VIX급등")
    elif vix <= 18:      score += 5
    if trend == "BULL":  score += 10; reasons.append("📈상승추세")
    elif trend == "BEAR":score -= 15; reasons.append("📉하락추세")

    # 2. RS 상대강도
    rs = _safe_float(row.get("RS", 0))
    if rs >= 95:   score += _rs95_w; reasons.append("🚀RS초강세")
    elif rs >= 90: score += _rs90_w
    elif rs >= 80: score += _rs80_w
    elif rs < 70:  score -= 25; reasons.append("RS약세")

    # 3. MA200 필터 (핵심 방어선)
    above_ma200 = row.get("MA200", False)
    if not above_ma200:
        score -= _ma200_pen; reasons.append("⛔MA200하회")
    else:
        score += _ma200_bon; reasons.append("📊MA200위")

    # 4. 신고가 근처 + 52주 신고가 돌파
    hd = _safe_float(row.get("HighDist", -100))
    b52 = row.get("Breakout52", False)

    if b52:
        score += 30; reasons.append("🔥52주신고가돌파")  # 최강 신호
    elif hd >= -5:    score += _hd_w; reasons.append("🔥신고가근처")
    elif hd >= -10: score += int(_hd_w * 0.6)
    elif hd <= -25: score -= 20; reasons.append("신고가대비약세")

    # 5. 기관 거래량
    vr = _safe_float(row.get("VolRatio", 1), 1)
    if vr >= 2.0:   score += _vol_w; reasons.append("🏦기관거래량")
    elif vr >= 1.5: score += int(_vol_w * 0.6)
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
            score += _surv_w; reasons.append("🛡️하락장생존")
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
    if   score >= 140: grade = "A"
    elif score >= 110: grade = "B"
    elif score >= 80:  grade = "C"
    else:              grade = "D"

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
        "CPI":         "CPIAUCSL",
        "USDKRW":      "DEXKOUS",
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
    # 섹터 ETF
    _sector_etfs = ["XLK","XLV","XLE","XLF","XLI","XLC","XLY","XLP","XLB","XLU","XLRE"]
    try:
        for _se in _sector_etfs:
            _sd = yf.download(_se, period="3mo", interval="1d",
                auto_adjust=True, progress=False)
            if not _sd.empty and "Close" in _sd.columns:
                _sc = _sd["Close"].dropna()
                if isinstance(_sc, pd.DataFrame):
                    _sc = _sc.iloc[:,0]
                if len(_sc) > 10:
                    out[_se] = _sc
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

            # 20일 브레이크아웃
            breakout = (cur > _safe_float(close.iloc[-22:-1].max())) if len(close)>=22 else False

            # 52주 신고가 돌파 (오늘 종가 > 52주 최고가 × 거래량 확인)
            hi52_prev = _safe_float(close.rolling(min(251,len(close)-1)).max().iloc[-2]) if len(close)>=3 else hi52
            breakout52 = (
                cur >= hi52 * 0.999          # 52주 고점 돌파 (0.1% 오차 허용)
                and hi52_prev < hi52          # 오늘 새로운 고점 경신
                and vol_ratio >= 1.5          # 거래량 확인 (가짜 돌파 필터)
            )

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
            # EPS 대신 52주·3개월 주가 수익률 사용
            # (Streamlit Cloud에서 yfinance EPS API 차단)
            eps = rev = 0.0
            try:
                if len(close) >= 252:
                    eps = round(
                        (float(close.iloc[-1]) - float(close.iloc[-252]))
                        / abs(float(close.iloc[-252])) * 100, 1)
                elif len(close) >= 60:
                    eps = round(
                        (float(close.iloc[-1]) - float(close.iloc[-60]))
                        / abs(float(close.iloc[-60])) * 100, 1)
            except Exception:
                pass
            try:
                if len(close) >= 60:
                    rev = round(
                        (float(close.iloc[-1]) - float(close.iloc[-60]))
                        / abs(float(close.iloc[-60])) * 100, 1)
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
                "Name":        COMPANY_NAME.get(tk, tk),
                "Sector":      SECTOR_MAP.get(tk,"기타"),
                "EntryPrice":  round(cur, 2),
                "RS":          rs,
                "MA200":       above_ma200,
                "MA50":        above_ma50,
                "MA20":        above_ma20,
                "HighDist":    high_dist,
                "VolRatio":    round(vol_ratio, 2),
                "Breakout":    breakout,
                "Breakout52":  breakout52,
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
def _fred_last(fred, key, default):
    """FRED 시리즈 최신값 안전 추출"""
    s = fred.get(key)
    if isinstance(s, pd.Series) and len(s) > 0:
        return _safe_float(s.iloc[-1])
    return default

def calc_liq_score(fred: dict) -> tuple:
    """유동성 점수 (0~100) + 단계 (1~5) + 9개 지표 상세"""
    score = 50
    detail = {}  # {지표명: (현재값, 점수0~100, 신호🟢🟡🔴)}

    # ① 기준금리
    ff = _fred_last(fred, "FedFunds", 5.0)
    if   ff > 5.0: _fs=-10; _fg="🔴"; _fsc=25
    elif ff > 3.0: _fs=0;   _fg="🟡"; _fsc=50
    elif ff < 2.0: _fs=10;  _fg="🟢"; _fsc=85
    else:          _fs=5;   _fg="🟢"; _fsc=70
    score += _fs
    detail["기준금리"] = (f"{ff:.2f}%", _fsc, _fg)

    # ② M2 통화량
    m2s = fred.get("M2")
    _m2_v="N/A"; _m2_g="🟡"; _m2_sc=50
    if isinstance(m2s, pd.Series) and len(m2s) >= 52:
        _cur = _safe_float(m2s.iloc[-1])
        _prev= _safe_float(m2s.iloc[-52])
        if _prev > 0:
            _yoy = (_cur - _prev) / _prev * 100
            _m2_v = f"{_cur/1000:.1f}T$ ({_yoy:+.1f}%)"
            if   _yoy > 5:  score+=8;  _m2_g="🟢"; _m2_sc=80
            elif _yoy > 0:  score+=3;  _m2_g="🟢"; _m2_sc=65
            elif _yoy > -2: pass;      _m2_g="🟡"; _m2_sc=45
            else:           score-=8;  _m2_g="🔴"; _m2_sc=20
    detail["M2 통화량"] = (_m2_v, _m2_sc, _m2_g)

    # ③ RRP 역레포
    rrp = _fred_last(fred, "RRP", 500)
    if   rrp > 1500: score-=8;  _rg="🔴"; _rsc=20
    elif rrp > 500:  score-=3;  _rg="🟡"; _rsc=45
    elif rrp > 100:  score+=5;  _rg="🟢"; _rsc=70
    else:            score+=8;  _rg="🟢"; _rsc=85
    detail["RRP 역레포"] = (f"{rrp/1e3:.2f}T$", _rsc, _rg)

    # ④ TGA 재무부
    tga = _fred_last(fred, "TGA", 700)
    if   tga > 1000: score-=5;  _tg="🔴"; _tsc=30
    elif tga > 500:  pass;      _tg="🟡"; _tsc=50
    else:            score+=5;  _tg="🟢"; _tsc=72
    detail["TGA 재무부"] = (f"{tga/1e3:.2f}T$", _tsc, _tg)

    # ⑤ 은행 준비금
    res = _fred_last(fred, "Reserves", 3000)
    if   res < 2000: score-=10; _sg="🔴"; _ssc=20
    elif res < 2500: score-=3;  _sg="🟡"; _ssc=45
    elif res > 3000: score+=5;  _sg="🟢"; _ssc=80
    else:            pass;      _sg="🟢"; _ssc=65
    detail["은행 준비금"] = (f"{res/1e3:.2f}T$", _ssc, _sg)

    # ⑥ 실질금리
    rr = _fred_last(fred, "RealRate", 1.0)
    if   rr > 2.5:  score-=12; _rg2="🔴"; _rsc2=15
    elif rr > 1.0:  score-=5;  _rg2="🟡"; _rsc2=40
    elif rr > 0:    pass;      _rg2="🟡"; _rsc2=55
    elif rr > -1:   score+=8;  _rg2="🟢"; _rsc2=75
    else:           score+=12; _rg2="🟢"; _rsc2=90
    detail["실질금리"] = (f"{rr:.2f}%", _rsc2, _rg2)

    # ⑦ 크레딧 스프레드
    cs = _fred_last(fred, "CreditSpread", 3.5)
    if   cs > 6.0:  score-=15; _csg="🔴"; _cssc=10
    elif cs > 5.0:  score-=10; _csg="🔴"; _cssc=25
    elif cs > 4.0:  score-=5;  _csg="🟡"; _cssc=40
    elif cs > 3.5:  pass;      _csg="🟡"; _cssc=55
    else:           score+=10; _csg="🟢"; _cssc=80
    detail["크레딧 스프레드"] = (f"{cs:.2f}%", _cssc, _csg)

    # ⑧ CPI 물가
    cpis = fred.get("CPI")
    _cpi_v="N/A"; _cpi_g="🟡"; _cpi_sc=50
    if isinstance(cpis, pd.Series) and len(cpis) > 0:
        _cpi = _safe_float(cpis.iloc[-1])
        _cpi_v = f"{_cpi:.1f}%"
        if   _cpi > 5.0: score-=8;  _cpi_g="🔴"; _cpi_sc=20
        elif _cpi > 3.0: score-=3;  _cpi_g="🟡"; _cpi_sc=45
        elif _cpi > 2.0: score+=2;  _cpi_g="🟢"; _cpi_sc=65
        else:            score+=5;  _cpi_g="🟢"; _cpi_sc=82
    detail["CPI 물가"] = (_cpi_v, _cpi_sc, _cpi_g)

    # ⑨ 장단기 금리차 (T10Y2Y)
    t10s = fred.get("T10Y2Y")
    _ty_v="N/A"; _ty_g="🟡"; _ty_sc=50
    if isinstance(t10s, pd.Series) and len(t10s) > 0:
        _ty = _safe_float(t10s.iloc[-1])
        _ty_v = f"{_ty:+.2f}%"
        if   _ty < -0.5: score-=8;  _ty_g="🔴"; _ty_sc=20
        elif _ty < 0:    score-=3;  _ty_g="🟡"; _ty_sc=40
        elif _ty < 0.5:  score+=2;  _ty_g="🟢"; _ty_sc=62
        else:            score+=5;  _ty_g="🟢"; _ty_sc=80
    detail["장단기 금리차"] = (_ty_v, _ty_sc, _ty_g)

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

# =========================================================
# MARKET INTERPRETATION ENGINE
# 유동성 단계별 시장 해석 + 행동 지침 자동 생성
# =========================================================

MARKET_INTERPRETATION = {
    5: {
        "interpret": (
            "유동성이 최고조에 달해 시장에 돈이 넘칩니다. "
            "RRP 완전 해소 · 은행 준비금 충분 · 실질금리 우호적으로 "
            "위험자산 선호 심리가 극대화된 구간입니다. "
            "기관 매집이 가장 활발하며 강한 종목은 더 강해지는 환경입니다."
        ),
        "actions": [
            "A등급 종목 적극 매수 (투자금 80~100%)",
            "52주 신고가 돌파 종목 즉시 진입",
            "손절 -8% 표준 유지",
        ],
    },
    4: {
        "interpret": (
            "유동성이 충분히 풀려 있고 침체 위험이 낮습니다. "
            "VIX 안정 + QQQ 상승 추세로 위험자산 선호 환경이 지속되고 있습니다. "
            "기관 매집이 활발한 구간으로 분할 매수 진입이 적합합니다."
        ),
        "actions": [
            "A·B등급 우선 분할 매수 (투자금 40~60%)",
            "눌림목 조정 시 추가 진입 검토",
            "현금 20~30% 유지 · 손절 -8% 표준",
        ],
    },
    3: {
        "interpret": (
            "유동성이 혼조 구간입니다. 시장에 돈이 있지만 "
            "방향성이 불명확하며 변동성이 높아질 수 있습니다. "
            "강한 종목과 약한 종목의 차별화가 심화되는 시기입니다. "
            "섣부른 진입보다 관찰 후 선택적 접근이 유효합니다."
        ),
        "actions": [
            "RS 90↑ A·B등급만 소량 진입 (투자금 20~30%)",
            "현금 50% 이상 유지",
            "손절 -6% 강화 · 신규 진입 최소화",
        ],
    },
    2: {
        "interpret": (
            "유동성이 수축 중입니다. 시장에서 돈이 빠져나가고 있으며 "
            "기관이 매도 우위로 전환 중입니다. "
            "아무리 강해 보이는 종목도 하락 압력을 받을 수 있습니다. "
            "현금 보유가 최선의 전략입니다."
        ),
        "actions": [
            "신규 매수 전면 중단",
            "기존 포지션 50% 이상 현금화",
            "손절 -5% 강화 · 회복 후보 관찰만",
        ],
    },
    1: {
        "interpret": (
            "유동성 위기 단계입니다. 시장 전반에 매도 압력이 강하며 "
            "기관이 전방위로 현금화에 나서고 있습니다. "
            "반등 시도는 모두 매도 기회로 활용됩니다. "
            "자산 보존이 최우선 목표입니다."
        ),
        "actions": [
            "전액 현금화 (투자금 0%)",
            "GLD·TLT 등 안전자산 헤지 검토",
            "시장 회복 신호 확인 전 절대 매수 금지",
        ],
    },
}


# =========================================================
# INVESTMENT STRATEGY ENGINE
# 유동성 단계별 최적 투자 전략 자동 계산
# =========================================================

STRATEGY_DEFINITIONS = {
    "momentum":    {"label": "모멘텀",      "desc": "RS 강세 + 신고가 근처 추격", "score_bonus": 10},
    "breakout52":  {"label": "신고가 돌파", "desc": "52주 고점 당일 돌파",         "score_bonus": 20},
    "breakout20":  {"label": "브레이크아웃","desc": "20일 고점 + 거래량 급증",      "score_bonus": 15},
    "pullback":    {"label": "눌림목",       "desc": "강한 종목 단기 조정 매수",    "score_bonus": 20},
    "recovery":    {"label": "회복 후보",    "desc": "MA200 돌파 20일 이내",        "score_bonus": 25},
    "sector_rot":  {"label": "섹터 순환",   "desc": "자금 유입 1위 섹터 집중",     "score_bonus": 15},
}

def get_optimal_strategies(liq_stage: int, rec_score: float, vix: float) -> dict:
    """
    유동성·침체·VIX 기반 최적 전략 조합 자동 반환
    반환: {전략키: bool, "label": str, "desc": str}
    """
    s = {k: False for k in STRATEGY_DEFINITIONS}

    if liq_stage >= 5 and rec_score < 30 and vix < 20:
        s["momentum"]   = True
        s["breakout52"] = True
        s["breakout20"] = True
        label = "🚀 공격 최대 — 강한 것이 더 강해진다"
        desc  = "유동성 최고 · 침체 안전 · VIX 안정 → 모멘텀 집중"

    elif liq_stage >= 4 and rec_score < 50:
        s["momentum"]   = True
        s["breakout52"] = True
        s["breakout20"] = True
        s["pullback"]   = True
        s["sector_rot"] = True
        label = "🟢 균형 공격 — 모멘텀 + 눌림목 병행"
        desc  = "유동성 우호 · 침체 낮음 → 모멘텀 추격 + 눌림 진입 병행"

    elif liq_stage == 3 or (rec_score >= 50 and rec_score < 70):
        s["pullback"]   = True
        s["sector_rot"] = True
        s["recovery"]   = True
        label = "🟡 선택 방어 — 눌림목·회복 후보만"
        desc  = "혼조 구간 → 강한 종목 단기 조정 시만 진입"

    elif liq_stage <= 2 or rec_score >= 70:
        s["recovery"]   = True
        label = "🔴 현금 보존 — 관찰만"
        desc  = "위험 구간 → 회복 후보 관찰, 신규 매수 금지"

    else:
        s["momentum"]   = True
        s["pullback"]   = True
        label = "🟢 표준 — 기본 전략"
        desc  = "표준 환경 → 모멘텀 + 눌림목"

    return {"strategies": s, "label": label, "desc": desc}


def apply_strategy_bonus(row: dict, strategies: dict) -> int:
    """활성화된 전략 조건 충족 시 보너스 점수 계산"""
    bonus = 0
    rs       = float(row.get("RS", 0) or 0)
    hd       = float(row.get("HighDist", -100) or -100)
    rsi      = float(row.get("RSI", 50) or 50)
    breakout = row.get("Breakout", False)
    vol_r    = float(row.get("VolRatio", 1) or 1)
    ma200    = row.get("MA200", False)
    ma50     = row.get("MA50", False)

    # 모멘텀: RS 90↑ + 신고가 5%↑
    if strategies.get("momentum") and rs >= 90 and hd >= -5:
        bonus += STRATEGY_DEFINITIONS["momentum"]["score_bonus"]

    # 신고가 돌파: 52주 고점 근접 + 브레이크아웃
    if strategies.get("breakout52") and hd >= -2 and breakout:
        bonus += STRATEGY_DEFINITIONS["breakout52"]["score_bonus"]

    # 브레이크아웃: 20일 고점 돌파 + 거래량
    if strategies.get("breakout20") and breakout and vol_r >= 1.5:
        bonus += STRATEGY_DEFINITIONS["breakout20"]["score_bonus"]

    # 눌림목: RS 80↑ + RSI 45~58 + MA200 위
    if strategies.get("pullback") and rs >= 80 and 42 <= rsi <= 58 and ma200:
        bonus += STRATEGY_DEFINITIONS["pullback"]["score_bonus"]

    # 회복 후보: MA200 위 + MA50 위 (최근 돌파 추정)
    if strategies.get("recovery") and ma200 and ma50 and rs >= 70 and hd >= -15:
        bonus += STRATEGY_DEFINITIONS["recovery"]["score_bonus"]

    return bonus


# =========================================================
# AUTO STANCE ENGINE
# 유동성·침체 기반 자동 투자 스탠스 판단
# 텔레그램 알림·자동 저장 규칙과 연동 가능하도록 설계
# =========================================================

def calc_auto_stance(liq_stage: int, liq_score: float,
                     rec_score: float, vix: float) -> dict:
    """
    시장 환경 기반 자동 스탠스 계산
    반환값: {
        "stance":      "ATTACK" / "DEFENSE" / "DANGER",
        "label":       "🟢 공격" / "🟡 방어" / "🔴 위험",
        "color":       색상 코드,
        "min_grade":   표시 최소 등급 ("C" / "B" / "A"),
        "save_ok":     Sheets 저장 허용 여부,
        "buy_ok":      매수 허용 여부,
        "reason":      판단 근거 문자열 (텔레그램 알림에 재사용),
        "alert":       True/False (알림 발송 필요 여부),
    }
    """
    reasons = []

    # ── 위험 조건 (하나라도 해당) ──────────────────────────
    is_danger = False
    if liq_stage <= 2:
        is_danger = True
        reasons.append(f"유동성 {liq_stage}단계")
    if rec_score >= 70:
        is_danger = True
        reasons.append(f"침체위험 {rec_score:.0f}점")
    if vix >= 35:
        is_danger = True
        reasons.append(f"VIX {vix:.1f}")

    # ── 방어 조건 ──────────────────────────────────────────
    is_defense = False
    if not is_danger:
        if liq_stage == 3:
            is_defense = True
            reasons.append(f"유동성 {liq_stage}단계")
        if 50 <= rec_score < 70:
            is_defense = True
            reasons.append(f"침체주의 {rec_score:.0f}점")
        if 28 <= vix < 35:
            is_defense = True
            reasons.append(f"VIX {vix:.1f}")

    reason_str = " · ".join(reasons) if reasons else "정상"

    if is_danger:
        return {
            "stance":    "DANGER",
            "label":     "🔴 위험 스탠스",
            "color":     "#B91C1C",
            "bg":        "#FEF2F2",
            "border":    "#FECACA",
            "min_grade": "A",
            "save_ok":   False,
            "buy_ok":    False,
            "reason":    reason_str,
            "alert":     True,
            "actions":   [
                "신규매수 전면 금지",
                "포지션 50%↑ 현금화",
                "GLD·TLT 헤지 검토",
                "손절 -5% 강화",
            ],
        }
    elif is_defense:
        return {
            "stance":    "DEFENSE",
            "label":     "🟡 방어 스탠스",
            "color":     "#92400E",
            "bg":        "#FFFBEB",
            "border":    "#FDE68A",
            "min_grade": "B",
            "save_ok":   True,
            "buy_ok":    True,
            "reason":    reason_str,
            "alert":     False,
            "actions":   [
                "B↑ 등급만 매수",
                "현금 40% 이상 유지",
                "분할 매수 (투자금 30% 이하)",
                "손절 -6% 강화",
            ],
        }
    else:
        return {
            "stance":    "ATTACK",
            "label":     "🟢 공격 스탠스",
            "color":     "#166534",
            "bg":        "#F0FDF4",
            "border":    "#86EFAC",
            "min_grade": "C",
            "save_ok":   True,
            "buy_ok":    True,
            "reason":    reason_str,
            "alert":     False,
            "actions":   [
                f"유동성 {liq_stage}단계 — 적극 매수 가능",
                "A·B등급 우선 진입",
                "현금 20% 이하",
                "손절 -8% 표준",
            ],
        }


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
# ── 설정 기본값 (screener_daily.py에서도 사용) ──────────────
_DEFAULTS = {
    "cfg_liq_min":      3,
    "cfg_rec_max":      70,
    "cfg_vix_warn":     28,
    "cfg_rs95_w":       35,
    "cfg_rs90_w":       25,
    "cfg_rs80_w":       15,
    "cfg_ma200_pen":    40,
    "cfg_ma200_bon":    20,
    "cfg_vol_w":        25,
    "cfg_hd_w":         25,
    "cfg_survive_w":    35,
    "cfg_elite_min":    140,
    "cfg_strong_min":   110,
    "cfg_watch_min":    80,
    "cfg_min_rs":       70,
    "cfg_liq_block":    True,
    "cfg_rec_elite":    False,
}
