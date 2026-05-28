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
PRO_VERSION   = "PRO_V1"
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
    page_title="QUANTUM PRO",
    page_icon="⚡",
    layout="centered",
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

    # 4. 신고가 근처
    hd = _safe_float(row.get("HighDist", -100))
    if hd >= -5:    score += _hd_w; reasons.append("🔥신고가근처")
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
    if   score >= 140: grade = "🚀 ELITE"
    elif score >= 110: grade = "🔥 STRONG"
    elif score >= 80:  grade = "🔍 WATCH"
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
        "CPI":         "CPIAUCSL",
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
        "min_grade":   표시 최소 등급 ("WATCH" / "STRONG" / "ELITE"),
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
            "min_grade": "ELITE",
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
            "min_grade": "STRONG",
            "save_ok":   True,
            "buy_ok":    True,
            "reason":    reason_str,
            "alert":     False,
            "actions":   [
                "STRONG↑ 등급만 매수",
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
            "min_grade": "WATCH",
            "save_ok":   True,
            "buy_ok":    True,
            "reason":    reason_str,
            "alert":     False,
            "actions":   [
                f"유동성 {liq_stage}단계 — 적극 매수 가능",
                "ELITE·STRONG 우선 진입",
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

# ── 설정값 기본값 초기화 ──────────────────────────────
_DEFAULTS = {
    "cfg_liq_min":      3,    # 유동성 최소 단계
    "cfg_rec_max":      70,   # 침체 위험 상한
    "cfg_vix_warn":     28,   # VIX 경고 기준
    "cfg_rs95_w":       35,   # RS 95↑ 가중치
    "cfg_rs90_w":       25,   # RS 90↑ 가중치
    "cfg_rs80_w":       15,   # RS 80↑ 가중치
    "cfg_ma200_pen":    40,   # MA200 패널티
    "cfg_ma200_bon":    20,   # MA200 보너스
    "cfg_vol_w":        25,   # 기관거래량 가중치
    "cfg_hd_w":         25,   # 신고가 가중치
    "cfg_survive_w":    35,   # 하락장 생존 보너스
    "cfg_elite_min":    140,  # ELITE 기준점수
    "cfg_strong_min":   110,  # STRONG 기준점수
    "cfg_watch_min":    80,   # WATCH 기준점수
    "cfg_min_rs":       70,   # 최소 RS 표시 기준
    "cfg_liq_block":    True, # 유동성 2단계↓ 저장 중단
    "cfg_rec_elite":    False,# 침체 70↑ ELITE만 표시
}
for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

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
t_market, t_leaders, t_backtest, t_settings = st.tabs([
    "📊 MARKET", "🏆 LEADERS", "📈 BACKTEST", "⚙️ 설정"
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

    # 자동 스탠스 계산
    _auto_stance = calc_auto_stance(
        liq_stage, liq_score, rec_score, mkt_ctx.get("vix", 20))

    st.session_state.update({
        "liq_score":   liq_score,
        "liq_stage":   liq_stage,
        "rec_score":   rec_score,
        "mkt_ctx":     mkt_ctx,
        "auto_stance": _auto_stance,
        "fred_ready":  True,
    })

    # ══ 1. 유동성 5단계 범례 ════════════════════════════════
    # ══ 2. 핵심 시장 지표 제목 + 범례 ════════════════════════
    st.markdown(
        "<div style='font-size:11px;color:#374151;"
        "font-family:Space Mono,monospace;margin-bottom:2px'>"
        "핵심 시장 지표</div>"
        "<div style='font-size:9px;color:#6B7280;margin-bottom:6px'>"
        "유동성·침체·변동성·추세 종합 현황</div>",
        unsafe_allow_html=True)

    # 유동성 범례
    st.markdown(
        "<div style='display:flex;gap:4px;margin-bottom:8px;overflow-x:auto'>"
        "<div style='font-size:9px;white-space:nowrap;background:#FFFFFF;"
        "border:1px solid #E2E6ED;border-radius:20px;padding:2px 7px'>🚀 5단계 80↑ 파티</div>"
        "<div style='font-size:9px;white-space:nowrap;background:#FFFFFF;"
        "border:1px solid #E2E6ED;border-radius:20px;padding:2px 7px'>🟢 4단계 60↑ 분할매수</div>"
        "<div style='font-size:9px;white-space:nowrap;background:#FFFFFF;"
        "border:1px solid #E2E6ED;border-radius:20px;padding:2px 7px'>🟡 3단계 40↑ 현금50%</div>"
        "<div style='font-size:9px;white-space:nowrap;background:#FFFFFF;"
        "border:1px solid #E2E6ED;border-radius:20px;padding:2px 7px'>🔴 2단계 20↑ 매수중단</div>"
        "<div style='font-size:9px;white-space:nowrap;background:#FFFFFF;"
        "border:1px solid #E2E6ED;border-radius:20px;padding:2px 7px'>🔴 1단계 0↑ 전액현금</div>"
        "</div>",
        unsafe_allow_html=True)

    c1,c2 = st.columns(2)
    c3,c4 = st.columns(2)
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

    _mini_card(c1, "유동성",   f"{liq_stage}단계",        f"{liq_score:.0f}점/100", _lc)
    _mini_card(c2, "침체위험", f"{rec_score:.0f}점",       "/100",                   _rc)
    _mini_card(c3, "VIX",      f"{mkt_ctx['vix']:.1f}",   "변동성지수",             _vc)
    _mini_card(c4, "QQQ추세",  _qi, f"{mkt_ctx['mkt_drop']:+.1f}% (52W)",           _qc)

    # ══ 3. 투자 행동 지침 (결론 먼저) ═══════════════════════
    st.markdown("---")
    def _liq_evidence(det):
        evs = []
        for k, v in det.items():
            if isinstance(v, tuple) and v[2] == "🟢":
                if k == "기준금리":        evs.append(f"금리 {v[0]} 우호")
                elif k == "M2 통화량":     evs.append("M2 증가 중")
                elif k == "RRP 역레포":    evs.append("RRP 해소")
                elif k == "은행 준비금":   evs.append("준비금 충분")
                elif k == "실질금리":      evs.append(f"실질금리 {v[0]}")
                elif k == "크레딧 스프레드":evs.append("스프레드 안정")
        return " · ".join(evs[:3]) if evs else ""

    _evidence = _liq_evidence(liq_detail)

    # ══ 자동 스탠스 표시 (Auto Stance Engine) ══════════════
    _st = _auto_stance
    _act_list = list(_st["actions"])
    if _evidence:
        _act_list.insert(0, f"근거: {_evidence}")

    st.markdown(
        f"<div style='background:{_st['bg']};"
        f"border:1.5px solid {_st['border']};"
        f"border-left:4px solid {_st['color']};"
        f"border-radius:3px;padding:8px 12px'>"
        f"<div style='display:flex;align-items:center;"
        f"justify-content:space-between;margin-bottom:5px'>"
        f"<span style='font-size:13px;font-weight:700;"
        f"color:{_st['color']}'>{_st['label']}</span>"
        f"<span style='font-size:10px;color:#6B7280'>"
        f"{_st['reason']}</span></div>"
        + "".join(
            f"<div style='font-size:11px;color:#374151;padding:2px 0'>"
            f"<span style='color:{_st['color']};margin-right:6px'>→</span>{a}</div>"
            for a in _act_list)
        + f"<div style='font-size:9px;color:#9CA3AF;margin-top:6px'>"
        f"자동 판단 · 수동 변경: ⚙️ 설정 탭</div>"
        + "</div>",
        unsafe_allow_html=True)


    # ══ 4. LIQUIDITY BREAKDOWN 표 (점수만, 막대그래프 없음) ══
    st.markdown("---")
    st.markdown(
        "<div style='font-size:11px;color:#374151;"
        "font-family:Space Mono,monospace;margin-bottom:6px'>"
        "LIQUIDITY BREAKDOWN</div>",
        unsafe_allow_html=True)

    # FRED 링크 매핑
    _FRED_LINKS = {
        "기준금리":       ("FEDFUNDS",     "https://fred.stlouisfed.org/series/FEDFUNDS"),
        "M2 통화량":      ("M2SL",         "https://fred.stlouisfed.org/series/M2SL"),
        "RRP 역레포":     ("RRPONTSYD",    "https://fred.stlouisfed.org/series/RRPONTSYD"),
        "TGA 재무부":     ("WDTGAL",       "https://fred.stlouisfed.org/series/WDTGAL"),
        "은행 준비금":    ("WRESBAL",      "https://fred.stlouisfed.org/series/WRESBAL"),
        "실질금리":       ("DFII10",       "https://fred.stlouisfed.org/series/DFII10"),
        "크레딧 스프레드":("BAMLH0A0HYM2", "https://fred.stlouisfed.org/series/BAMLH0A0HYM2"),
        "CPI 물가":       ("CPIAUCSL",     "https://fred.stlouisfed.org/series/CPIAUCSL"),
        "장단기 금리차":  ("T10Y2Y",       "https://fred.stlouisfed.org/series/T10Y2Y"),
    }

    _liq_rows = []
    for _k, _v in liq_detail.items():
        _val   = _v[0] if isinstance(_v, tuple) else str(_v)
        _score = _v[1] if isinstance(_v, tuple) else 50
        _sig   = _v[2] if isinstance(_v, tuple) else "🟡"
        _sid, _url = _FRED_LINKS.get(_k, ("", ""))
        _fred_link = _url if _url else ""
        _liq_rows.append({
            "지표":   _k,
            "현재값": _val,
            "점수":   _score,
            "신호":   _sig,
            "FRED":   _fred_link,
            "_sid":   _sid,
        })

    _liq_df = pd.DataFrame(_liq_rows).drop(columns=["_sid"], errors="ignore")
    st.dataframe(
        _liq_df, use_container_width=True, hide_index=True,
        column_config={
            "지표":   st.column_config.TextColumn("지표",   width="small"),
            "현재값": st.column_config.TextColumn("현재값", width="small"),
            "점수":   st.column_config.NumberColumn("점수", format="%d점", width="small"),
            "신호":   st.column_config.TextColumn("신호",   width="small"),
            "FRED":   st.column_config.LinkColumn("FRED",
                        display_text=r"https://fred\.stlouisfed\.org/series/(.+)",
                        width="small"),
        })

    # ── 섹터 자금 흐름 ─────────────────────────────────────
    st.markdown("---")
    st.markdown(
        "<div style='font-size:11px;color:#374151;"
        "font-family:Space Mono,monospace;margin-bottom:2px'>"
        "SECTOR FLOW — 자금 흐름 분석</div>"
        "<div style='font-size:9px;color:#9CA3AF;margin-bottom:6px'>"
        "* 섹터 ETF 가격 기준 · 거래량 미수집 · 방향성 참고용</div>",
        unsafe_allow_html=True)


    _SECTOR_META = {
        "XLK":  ("기술",      "반도체·소프트웨어·하드웨어"),
        "XLC":  ("통신",      "구글·메타·넷플릭스"),
        "XLY":  ("임의소비재","아마존·테슬라·소비재"),
        "XLV":  ("헬스케어",  "제약·의료기기·보험"),
        "XLF":  ("금융",      "은행·보험·자산운용"),
        "XLI":  ("산업재",    "항공우주·방산·물류"),
        "XLE":  ("에너지",    "정유·가스·신재생"),
        "XLP":  ("필수소비재","식품·음료·생활용품"),
        "XLB":  ("소재",      "화학·금속·광물"),
        "XLU":  ("유틸리티",  "전력·가스·수도"),
        "XLRE": ("부동산",    "리츠·부동산신탁"),
    }

    _qqq_s = mkt.get("QQQ")
    _sector_rows = []

    for _etf, (_sname, _sdesc) in _SECTOR_META.items():
        _es = mkt.get(_etf)
        if _es is None or len(_es) < 10: continue
        try:
            # 1주(5거래일) 수익률
            _r1w = (_safe_float(_es.iloc[-1]) - _safe_float(_es.iloc[-6])) / abs(_safe_float(_es.iloc[-6])) * 100 if len(_es)>=6 else 0
            # 4주(20거래일) 수익률
            _r4w = (_safe_float(_es.iloc[-1]) - _safe_float(_es.iloc[-21])) / abs(_safe_float(_es.iloc[-21])) * 100 if len(_es)>=21 else 0
            # QQQ 대비 초과수익 (1주)
            _qqq_1w = 0
            if _qqq_s is not None and len(_qqq_s)>=6:
                _qqq_1w = (_safe_float(_qqq_s.iloc[-1]) - _safe_float(_qqq_s.iloc[-6])) / abs(_safe_float(_qqq_s.iloc[-6])) * 100
            _excess = _r1w - _qqq_1w

            # 상태 판단
            if   _excess >= 2:    _status = "🔥 강세유입"
            elif _excess >= 0.5:  _status = "📈 유입"
            elif _excess >= -0.5: _status = "→ 중립"
            elif _excess >= -2:   _status = "📉 유출"
            else:                 _status = "❄️ 약세유출"

            _sector_rows.append({
                "섹터":      _sname,
                "ETF":       _etf,
                "1주수익%":  round(_r1w, 1),
                "4주수익%":  round(_r4w, 1),
                "QQQ대비%":  round(_excess, 1),
                "상태":      _status,
                "대표종목":  _sdesc,
            })
        except Exception:
            continue

    if _sector_rows:
        # QQQ 대비 수익률 기준 정렬
        _sector_df = pd.DataFrame(_sector_rows).sort_values(
            "QQQ대비%", ascending=False).reset_index(drop=True)

        st.dataframe(
            _sector_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "섹터":     st.column_config.TextColumn("섹터",    width="small"),
                "ETF":      st.column_config.TextColumn("ETF",     width="small"),
                "1주수익%": st.column_config.NumberColumn("1주%",  format="%+.1f%%", width="small"),
                "4주수익%": st.column_config.NumberColumn("4주%",  format="%+.1f%%", width="small"),
                "QQQ대비%": st.column_config.NumberColumn("QQQ대비",format="%+.1f%%",width="small"),
                "상태":     st.column_config.TextColumn("자금흐름", width="small"),
                "대표종목": st.column_config.TextColumn("대표종목", width="medium"),
            })

        # 강세 섹터 요약
        _hot = [r["섹터"] for r in _sector_rows if "강세" in r["상태"] or "유입" in r["상태"]]
        _cold= [r["섹터"] for r in _sector_rows if "약세" in r["상태"] or "유출" in r["상태"]]
        # 자금 흐름 원인 자동 분석
        def _sector_reason(hot_sectors, liq_det, rec_s, mkt_c):
            reasons = []
            _rr = 0
            for k, v in liq_det.items():
                if isinstance(v, tuple) and k == "실질금리":
                    try: _rr = float(v[0].replace("%",""))
                    except: pass

            if "기술" in hot_sectors or "통신" in hot_sectors:
                if _rr < 1.5:
                    reasons.append(f"실질금리 {_rr:.1f}% → 성장주 밸류에이션 우호")
                if mkt_c.get("qqq_trend") == "BULL":
                    reasons.append("QQQ 상승 추세 → 기술 섹터 모멘텀 지속")
            if "에너지" in hot_sectors:
                reasons.append("에너지 가격 상승 또는 지정학적 리스크 반영")
            if "헬스케어" in hot_sectors or "필수소비재" in hot_sectors:
                reasons.append("경기 방어주 선호 → 위험 회피 심리 일부 작동")
            if "금융" in hot_sectors:
                reasons.append("금리 안정화 기대 → 은행·보험 수익성 개선 전망")
            if rec_s >= 50 and ("유틸리티" in hot_sectors or "필수소비재" in hot_sectors):
                reasons.append(f"침체 위험 {rec_s:.0f}점 → 방어 섹터로 자금 이동")
            return reasons

        _reasons = _sector_reason(_hot, liq_detail, rec_score, mkt_ctx)

        if _hot:
            st.markdown(
                f"<div style='background:#FFFFFF;border:1px solid #E2E6ED;"
                f"border-left:3px solid #166534;"
                f"border-radius:3px;padding:6px 12px;margin-top:6px;"
                f"font-size:11px;color:#374151'>"
                f"📈 자금 유입: <b>{' · '.join(_hot)}</b></div>",
                unsafe_allow_html=True)
        if _cold:
            st.markdown(
                f"<div style='background:#FFFFFF;border:1px solid #E2E6ED;"
                f"border-left:3px solid #B91C1C;"
                f"border-radius:3px;padding:6px 12px;margin-top:4px;"
                f"font-size:11px;color:#374151'>"
                f"📉 자금 유출: <b>{' · '.join(_cold)}</b></div>",
                unsafe_allow_html=True)
        if _reasons:
            _r_html = " &nbsp;·&nbsp; ".join(_reasons)
            st.markdown(
                f"<div style='background:#FFFFFF;border:1px solid #E2E6ED;"
                f"border-left:3px solid #374151;"
                f"border-radius:3px;padding:6px 12px;margin-top:4px;"
                f"font-size:10px;color:#374151'>"
                f"💡 분석: {_r_html}</div>",
                unsafe_allow_html=True)
    else:
        st.info("섹터 데이터 로드 중...")

# ════════════════════════════════════════════════════════════
# TAB 1 — LEADERS
# ════════════════════════════════════════════════════════════
with t_leaders:
    _ck = st.session_state["cache_key"]
    _liq_stage = st.session_state.get("liq_stage", 3)
    _rec_score = st.session_state.get("rec_score", 50)
    _mkt_ctx   = st.session_state.get("mkt_ctx",
        {"liq_stage":3,"rec_risk":50,"vix":20,"qqq_trend":"NEUTRAL","mkt_drop":0})

    # 자동 스탠스 로드
    _auto_stance = st.session_state.get("auto_stance", None)
    if _auto_stance is None:
        _auto_stance = calc_auto_stance(
            _liq_stage,
            st.session_state.get("liq_score", 50),
            _rec_score,
            _mkt_ctx.get("vix", 20)
        )

    # 스탠스 배너 (항상 상단 표시)
    st.markdown(
        f"<div style='background:{_auto_stance['bg']};"
        f"border:1px solid {_auto_stance['border']};"
        f"border-left:4px solid {_auto_stance['color']};"
        f"border-radius:3px;padding:6px 12px;margin-bottom:10px;"
        f"display:flex;justify-content:space-between;align-items:center'>"
        f"<span style='font-size:12px;font-weight:700;"
        f"color:{_auto_stance['color']}'>{_auto_stance['label']}</span>"
        f"<span style='font-size:10px;color:#6B7280'>"
        f"근거: {_auto_stance['reason']} &nbsp;|&nbsp; "
        f"표시: {_auto_stance['min_grade']}↑</span></div>",
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

    # 설정값 로드
    _cfg = {k: st.session_state.get(k, v)
            for k, v in _DEFAULTS.items()}

    # 연속 선택일 계산 (Sheets 누적 데이터 기반)
    _consec_map = {}
    try:
        _hist_for_consec = load_pro_history()
        if not _hist_for_consec.empty:
            _consec_map = calc_consecutive_days(_hist_for_consec)
    except Exception:
        _consec_map = {}

    # 시장 환경 자동 규칙 확인
    _liq_blocked = (_cfg["cfg_liq_block"] and _liq_stage <= 2)
    _rec_elite   = (_cfg["cfg_rec_elite"] and _rec_score >= _cfg["cfg_rec_max"])

    if _liq_blocked:
        st.markdown(
            "<div style='background:#FEF2F2;border:1.5px solid #FECACA;"
            "border-radius:4px;padding:8px 14px;margin-bottom:8px;"
            "font-size:12px;font-weight:700;color:#B91C1C'>"
            "🚨 유동성 2단계 이하 — 매수 금지 / Sheets 저장 중단</div>",
            unsafe_allow_html=True)

    if _rec_elite:
        st.markdown(
            "<div style='background:#FFF7ED;border:1px solid #FED7AA;"
            "border-radius:4px;padding:6px 14px;margin-bottom:8px;"
            "font-size:11px;color:#C2410C'>"
            f"⚠️ 침체 위험 {_rec_score:.0f}점 — ELITE 등급만 표시 중</div>",
            unsafe_allow_html=True)

    # Leader Score 계산
    _scored = []
    _min_rs = _cfg.get("cfg_min_rs", 70)
    for r in _raw_results:
        _res = calculate_leader_score(r, _mkt_ctx, _cfg)
        _tk = r.get("Ticker","")
        _cd = _consec_map.get(_tk, (0, ""))
        _consec_str = f"{_cd[0]}일" if _cd[0] > 0 else "신규"
        _scored.append({**r, **{
            "LeaderScore": _res["score"],
            "LeaderGrade": _res["grade"],
            "Signal":      _res["reasons"],
            "AccScore":    _res["acc"],
            "연속선택":    _consec_str,
        }})

    df = pd.DataFrame(_scored)

    # ── MA200 필터 표시 ──────────────────────────────────
    df_above = df[df["MA200"]].copy()
    df_below = df[~df["MA200"]].copy()

    # 침체 위험 → ELITE만 표시
    if _rec_elite:
        df_above = df_above[df_above["LeaderGrade"].str.contains("ELITE", na=False)]

    # RS 최소 기준 필터
    if _min_rs > 0:
        df_above = df_above[df_above["RS"] >= _min_rs]

    # Leader Score 기준 정렬 (강한 상승 종목 위로)
    df_above = df_above.sort_values("LeaderScore", ascending=False).reset_index(drop=True)
    df_above.index = df_above.index + 1


    # 자동 스탠스 기반 필터 + 설정 탭 RS 기준
    _fdf = df_above.copy()
    _stance_min = _auto_stance.get("min_grade", "WATCH")
    if _stance_min == "ELITE":
        _fdf = _fdf[_fdf["LeaderGrade"].str.contains("ELITE", na=False)]
    elif _stance_min == "STRONG":
        _fdf = _fdf[_fdf["LeaderGrade"].str.contains("ELITE|STRONG", na=False)]
    if _min_rs > 0:
        _fdf = _fdf[_fdf["RS"] >= _min_rs]


    # ── 스크리닝 현황 요약 ───────────────────────────────
    st.markdown(
        "<div style='font-size:11px;color:#374151;"
        "font-family:Space Mono,monospace;margin-bottom:2px'>"
        "스크리닝 현황</div>"
        "<div style='font-size:9px;color:#6B7280;margin-bottom:6px'>"
        "전체 종목 중 MA200 위 매수 가능 종목 분류</div>",
        unsafe_allow_html=True)
    _elite_cnt  = len(df_above[df_above["LeaderGrade"].str.contains("ELITE", na=False)])
    _strong_cnt = len(df_above[df_above["LeaderGrade"].str.contains("STRONG", na=False)])
    _watch_cnt  = len(df_above[df_above["LeaderGrade"].str.contains("WATCH", na=False)])

    def _top_sec(d, n=2):
        if d.empty or "Sector" not in d.columns: return ""
        top = d["Sector"].value_counts().head(n)
        return " · ".join(f"{s} {v}" for s,v in top.items())

    _summary_df = pd.DataFrame([
        {"항목":"전체 종목",     "수":len(df),       "비고": _top_sec(df)},
        {"항목":"MA200 위",      "수":len(df_above), "비고": _top_sec(df_above) + " — 매수 가능"},
        {"항목":"🚀 ELITE",      "수":_elite_cnt,    "비고": _top_sec(df_above[df_above["LeaderGrade"].str.contains("ELITE",na=False)]) + " — 즉시 진입"},
        {"항목":"🔥 STRONG",     "수":_strong_cnt,   "비고": _top_sec(df_above[df_above["LeaderGrade"].str.contains("STRONG",na=False)]) + " — 분할매수"},
        {"항목":"🔍 WATCH",      "수":_watch_cnt,    "비고": "관찰 대기"},
        {"항목":"⛔ MA200 아래", "수":len(df_below), "비고": "매수 금지"},
    ])
    st.dataframe(
        _summary_df, use_container_width=True, hide_index=True,
        column_config={
            "항목": st.column_config.TextColumn("항목",   width="small"),
            "수":   st.column_config.NumberColumn("종목수", format="%d개", width="small"),
            "비고": st.column_config.TextColumn("비고",   width="medium"),
        })


    st.markdown("---")

    # ── 메인 테이블 ──────────────────────────────────────
    st.markdown(
        f"<div style='font-size:11px;color:#374151;"
        f"font-family:Space Mono,monospace;margin-bottom:2px'>"
        f"MA200 위 종목 ({len(_fdf)}개) — Leader Score 순위</div>"
        f"<div style='font-size:9px;color:#6B7280;margin-bottom:6px'>"
        f"Leader Score 높은 순 · MA200(200일선) 위 종목만 표시 · "
        f"🚀ELITE→즉시진입 🔥STRONG→분할매수 🔍WATCH→관찰</div>",
        unsafe_allow_html=True)

    _disp_cols = ["Ticker","Name","Sector","LeaderGrade","LeaderScore","연속선택",
                  "AccScore","RS","HighDist","VolRatio","EPS","RSI",
                  "Breakout","VolSurge","Consec","EntryPrice","CondCount"]
    # 모바일: 핵심 컬럼 우선 표시 (전체는 가로 스크롤)
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
            "Name":        st.column_config.TextColumn("회사명",   width="medium"),
            "Sector":      st.column_config.TextColumn("섹터",     width="small"),
            "LeaderGrade": st.column_config.TextColumn("🏆등급",   width="small"),
            "LeaderScore": st.column_config.NumberColumn("리더점수", format="%.0f"),
            "연속선택":    st.column_config.TextColumn("연속",
                            width="small",
                            help="최근 7일간 연속 선택 횟수"),
            "AccScore":    st.column_config.NumberColumn("매집",    format="%.0f", width="small"),
            "RS":          st.column_config.NumberColumn("RS",      format="%.1f", width="small"),
            "HighDist":    st.column_config.NumberColumn("신고가%", format="%.1f", width="small"),
            "VolRatio":    st.column_config.NumberColumn("거래량배율",format="%.2f",width="small"),
            "EPS":         st.column_config.NumberColumn("52주수익%*",format="%.1f",width="small",help="*EPS 미수집 — 52주 주가 수익률로 대체"),
            "RSI":         st.column_config.NumberColumn("RSI",     format="%.1f", width="small"),
            "Breakout":    st.column_config.TextColumn("돌파",      width="small"),
            "VolSurge":    st.column_config.TextColumn("거래량",    width="small"),
            "Consec":      st.column_config.TextColumn("3연상",     width="small"),
            "EntryPrice":  st.column_config.NumberColumn("현재가",  format="$%.2f"),
            "CondCount":   st.column_config.NumberColumn("조건수",  format="%.0f", width="small"),
        },
        hide_index=False,
    )


    # ── 섹터별 Leader Score 평균 ────────────────────────────
    st.markdown("---")
    st.markdown(
        "<div style='font-size:11px;color:#374151;"
        "font-family:Space Mono,monospace;margin-bottom:2px'>"
        "섹터별 강도 분석</div>"
        "<div style='font-size:9px;color:#6B7280;margin-bottom:6px'>"
        "MA200 위 종목 기준 · Leader Score 평균 · 높을수록 강한 섹터</div>",
        unsafe_allow_html=True)

    if not df_above.empty:
        _sec_grp = (
            df_above.groupby("Sector")
            .agg(
                평균점수 =("LeaderScore", "mean"),
                종목수   =("Ticker",      "count"),
                최고점수 =("LeaderScore", "max"),
                평균RS   =("RS",          "mean"),
            )
            .round(1)
            .sort_values("평균점수", ascending=False)
            .reset_index()
        )
        _sec_grp.columns = ["섹터","평균점수","종목수","최고점수","평균RS"]

        # 순위 추가
        _sec_grp.insert(0, "순위",
            [f"{i+1}위" for i in range(len(_sec_grp))])

        # ELITE·STRONG 수 추가
        _elite_by_sec = (
            df_above[df_above["LeaderGrade"].str.contains("ELITE|STRONG", na=False)]
            .groupby("Sector")["Ticker"].count()
            .rename("강세종목")
        )
        _sec_grp = _sec_grp.merge(
            _elite_by_sec, left_on="섹터", right_index=True, how="left"
        ).fillna(0)
        _sec_grp["강세종목"] = _sec_grp["강세종목"].astype(int)

        st.dataframe(
            _sec_grp,
            use_container_width=True,
            hide_index=True,
            column_config={
                "순위":   st.column_config.TextColumn("순위",   width="small"),
                "섹터":   st.column_config.TextColumn("섹터",   width="small"),
                "평균점수":st.column_config.NumberColumn("평균점수", format="%.1f점"),
                "종목수": st.column_config.NumberColumn("종목수", format="%d개",  width="small"),
                "최고점수":st.column_config.NumberColumn("최고점수",format="%.0f점",width="small"),
                "평균RS": st.column_config.NumberColumn("평균RS", format="%.1f",  width="small"),
                "강세종목":st.column_config.NumberColumn("ELITE·STRONG", format="%d개", width="small"),
            })

        # 1위 섹터 요약 멘트
        if len(_sec_grp) > 0:
            _top_sec_name = _sec_grp.iloc[0]["섹터"]
            _top_sec_score= _sec_grp.iloc[0]["평균점수"]
            _top_sec_elite= _sec_grp.iloc[0]["강세종목"]
            st.markdown(
                f"<div style='background:#FFFFFF;border:1px solid #E2E6ED;"
                f"border-left:3px solid #166534;"
                f"border-radius:3px;padding:6px 12px;margin-top:6px;"
                f"font-size:11px;color:#374151'>"
                f"📊 최강 섹터: <b>{_top_sec_name}</b> "
                f"— 평균 {_top_sec_score:.0f}점 "
                f"/ ELITE·STRONG {_top_sec_elite}개</div>",
                unsafe_allow_html=True)

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
            # ── 자동 스탠스 저장 차단 확인 ──
            if not _auto_stance.get("save_ok", True):
                st.error(
                    f"🚨 {_auto_stance['label']} — Sheets 저장 중단 "
                    f"({_auto_stance['reason']})")
            else:
                # ── 연결 진단 ──
                _sh_diag, _diag_msg = _get_sheet(debug=True)
                if _sh_diag is None:
                    st.error(f"❌ Sheets 연결 실패: {_diag_msg}")
                else:
                    # MA200 위 + WATCH 이상 저장
                    _save_rows_above = [
                        r for r in _scored
                        if r.get("MA200") and r.get("LeaderScore",0) >= _cfg.get("cfg_watch_min",80)
                    ]
                    # MA200 아래 전체 저장 (백테스트 비교용)
                    _save_rows_below = [
                        r for r in _scored
                        if not r.get("MA200")
                    ]
                    _save_rows = _save_rows_above + _save_rows_below
                    if not _save_rows:
                        st.warning("저장할 종목 없음")
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

    # ── TODAY'S LEADER — 회사 프로필 (dataframe 표 형식) ──
    _profiles = load_company_profiles()
    _show_df  = df_above[
        df_above["LeaderGrade"].str.contains("ELITE|STRONG", na=False)
    ].head(10)

    if not _show_df.empty:
        st.markdown("---")
        st.markdown(
            f"<div style='font-size:11px;color:#374151;"
            f"font-family:Space Mono,monospace;margin-bottom:2px'>"
            f"TODAY'S LEADER — 회사 프로필 ({len(_show_df)}개)</div>"
            f"<div style='font-size:9px;color:#6B7280;margin-bottom:6px'>"
            f"ELITE·STRONG 등급 종목 · 💡설명 수정: GitHub → company_profiles.json</div>",
            unsafe_allow_html=True)

        _prof_rows = []
        for _, row in _show_df.iterrows():
            _tk   = row["Ticker"]
            _prof_rows.append({
                "등급":   row.get("LeaderGrade",""),
                "Ticker": _tk,
                "회사명": row.get("Name", _tk),
                "점수":   int(row.get("LeaderScore", 0)),
                "RS":     round(_safe_float(row.get("RS",0)),1),
                "사업 요약": _profiles.get(_tk, "—"),
            })

        _prof_df = pd.DataFrame(_prof_rows)
        st.dataframe(
            _prof_df, use_container_width=True, hide_index=True,
            column_config={
                "등급":   st.column_config.TextColumn("등급",    width="small"),
                "Ticker": st.column_config.TextColumn("Ticker",  width="small"),
                "회사명": st.column_config.TextColumn("회사명",  width="small"),
                "점수":   st.column_config.NumberColumn("점수",  format="%d", width="small"),
                "RS":     st.column_config.NumberColumn("RS",    format="%.1f", width="small"),
                "사업 요약": st.column_config.TextColumn("사업 요약"),
            })

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
        # ══ 방법 2: Sheets 저장 데이터 간 수익률 계산 ══════════
        # 외부 API 불필요 · 이미 저장된 EntryPrice 활용
        # N일차 EntryPrice vs N+7일차 EntryPrice 비교

        hist = hist.sort_values(["Ticker","Date"]).reset_index(drop=True)

        def _calc_return_from_sheets(df):
            """
            같은 종목의 날짜별 EntryPrice를 이용해 수익률 계산
            기준일 EntryPrice vs 기준일+7일(이후 가장 가까운 날) EntryPrice
            """
            result = []
            for tk, grp in df.groupby("Ticker"):
                grp = grp.sort_values("Date").reset_index(drop=True)
                for i, row in grp.iterrows():
                    entry_date  = row["Date"]
                    entry_price = row["EntryPrice"]
                    if entry_price <= 0:
                        continue
                    # 7일 후 가장 가까운 기록 찾기
                    future = grp[grp["Date"] > entry_date + pd.Timedelta(days=6)]
                    if not future.empty:
                        exit_row   = future.iloc[0]
                        exit_price = exit_row["EntryPrice"]
                        exit_date  = exit_row["Date"]
                        hold_days  = (exit_date - entry_date).days
                        ret_pct    = round((exit_price - entry_price)
                                           / entry_price * 100, 2)
                        result.append({
                            "Date":        entry_date,
                            "Ticker":      tk,
                            "EntryPrice":  entry_price,
                            "ExitPrice":   exit_price,
                            "Return%":     ret_pct,
                            "Days":        hold_days,
                            "LeaderGrade": row.get("LeaderGrade",""),
                            "LeaderScore": row.get("LeaderScore", 0),
                            "MA200":       row.get("MA200","N"),
                            "RS":          row.get("RS", 0),
                            "AccScore":    row.get("AccScore", 0),
                            "LiqStage":    row.get("LiqStage", 0),
                            "Sector":      row.get("Sector",""),
                        })
            return pd.DataFrame(result) if result else pd.DataFrame()

        _bt = _calc_return_from_sheets(hist)
        _days_range = (
            f"{hist['Date'].min().strftime('%Y-%m-%d')} ~ "
            f"{hist['Date'].max().strftime('%Y-%m-%d')}"
        )

        # 데이터 부족 안내
        if _bt.empty:
            st.markdown(
                "<div style='background:#FFFBEB;border:1px solid #FDE68A;"
                "border-radius:3px;padding:10px;text-align:center;"
                "color:#92400E;font-size:11px'>"
                "⏳ 수익률 계산에는 7일 이상 간격의 데이터가 필요합니다.<br>"
                f"현재 기간: {_days_range}<br>"
                "매일 저장이 계속되면 자동으로 계산됩니다.</div>",
                unsafe_allow_html=True)
            # 데이터 없어도 요약은 표시
            _total       = len(hist)
            _profitable  = 0
            _avg_ret     = float("nan")
        else:
            _total      = len(_bt)
            _profitable = len(_bt[_bt["Return%"] > 0])
            _avg_ret    = round(_bt["Return%"].mean(), 2)


        # ── 요약 지표 (방법 2: _bt 기반) ─────────────────
        _days_range = _days_range  # 이미 위에서 계산됨"

        st.markdown(
            "<div style='font-size:11px;color:#374151;"
            "font-family:Space Mono,monospace;margin-bottom:2px'>"
            "누적 성과 요약</div>"
            "<div style='font-size:9px;color:#6B7280;margin-bottom:6px'>"
            "진입가 기준 수익률 · 30일 이상 축적 후 의미있는 분석 가능</div>",
            unsafe_allow_html=True)
        # 누적 기간 계산 (hist 기반)
        _days_max = int((hist['Date'].max() - hist['Date'].min()).days) if len(hist) > 1 else 0
        _win_rate = f"{_profitable/_total*100:.0f}%" if _total > 0 else "0%"
        _avg_ret_str = f"{_avg_ret:+.2f}%" if not pd.isna(_avg_ret) else "집계 중"
        _bt_df = pd.DataFrame([
            {"항목": "총 기록",    "값": f"{_total}건",      "비고": _days_range},
            {"항목": "수익 종목",  "값": f"{_profitable}건", "비고": f"승률 {_win_rate}"},
            {"항목": "평균 수익률","값": _avg_ret_str,        "비고": "7일 보유 기준"},
            {"항목": "데이터 기간","값": f"{_days_max}일",   "비고": "누적 일수"},
        ])
        st.dataframe(
            _bt_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "항목": st.column_config.TextColumn("항목", width="small"),
                "값":   st.column_config.TextColumn("값",   width="small"),
                "비고": st.column_config.TextColumn("비고", width="medium"),
            })

        st.markdown("---")

        # ── 등급별 수익률 분석 ────────────────────────────
        st.markdown(
            "<div style='font-size:11px;color:#374151;"
            "font-family:Space Mono,monospace;margin-bottom:6px'>"
            "GRADE별 성과 분석</div>",
            unsafe_allow_html=True)

        _grade_stats = []
        _bt_src = _bt if not _bt.empty else pd.DataFrame()
        for grade in ["🚀 ELITE","🔥 STRONG","🔍 WATCH"]:
            _g = _bt_src[_bt_src["LeaderGrade"].str.contains(
                grade.split()[-1], na=False)] if not _bt_src.empty else pd.DataFrame()
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

        # MA200 필터: _bt 기반 (7일 수익률 비교)
        _bt_ma = _bt.copy() if not _bt.empty else pd.DataFrame(
            columns=["MA200","Return%"])
        if not _bt_ma.empty:
            _bt_ma["MA200_bool"] = _bt_ma["MA200"] == "Y"
            _ma_above = _bt_ma[_bt_ma["MA200_bool"]]
            _ma_below = _bt_ma[~_bt_ma["MA200_bool"]]
        else:
            _ma_above = pd.DataFrame()
            _ma_below = pd.DataFrame()
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

        if not _bt.empty:
            _hist_disp = _bt[[
                c for c in ["Date","Ticker","LeaderGrade","LeaderScore",
                "EntryPrice","ExitPrice","Return%","Days",
                "RS","MA200","AccScore","LiqStage","Sector"]
                if c in _bt.columns
            ]].copy().sort_values(["Date","LeaderScore"],
                                  ascending=[False,False])
            _hist_disp["MA200"] = _hist_disp["MA200"].map(
                {"Y":"✅","N":"⛔"}).fillna("—")
            _hist_disp["Date"] = pd.to_datetime(
                _hist_disp["Date"]).dt.strftime("%Y-%m-%d")
        else:
            _hist_disp = pd.DataFrame()

        if _hist_disp.empty:
            st.info("7일 이상 데이터가 쌓이면 전체 기록이 표시됩니다.")
        else:
         st.dataframe(
            _hist_disp,
            use_container_width=True, hide_index=True,
            column_config={
                "Date":       st.column_config.TextColumn("날짜",    width="small"),
                "Ticker":     st.column_config.TextColumn("Ticker",  width="small"),
                "LeaderGrade":st.column_config.TextColumn("등급",    width="small"),
                "LeaderScore":st.column_config.NumberColumn("점수",  format="%.0f"),
                "EntryPrice": st.column_config.NumberColumn("진입가",   format="$%.2f"),
                "ExitPrice":  st.column_config.NumberColumn("청산가",   format="$%.2f"),
                "Return%":    st.column_config.NumberColumn("7일수익률",format="%+.2f%%"),
                "Days":       st.column_config.NumberColumn("보유일",   format="%d일"),
                "RS":         st.column_config.NumberColumn("RS",    format="%.1f"),
                "MA200":      st.column_config.TextColumn("MA200",   width="small"),
                "AccScore":   st.column_config.NumberColumn("매집",  format="%.0f"),
                "LiqStage":   st.column_config.NumberColumn("유동성",format="%d"),
                "RecRisk":    st.column_config.NumberColumn("침체%", format="%.1f"),
            })


# ════════════════════════════════════════════════════════════
# TAB 3 — ⚙️ 설정
# ════════════════════════════════════════════════════════════
with t_settings:

    st.markdown(
        "<div style='font-size:11px;color:#374151;"
        "font-family:Space Mono,monospace;margin-bottom:2px'>"
        "SCREENER CONFIGURATION</div>"
        "<div style='font-size:9px;color:#6B7280;margin-bottom:8px'>"
        "변경 즉시 LEADERS 탭에 반영 · 기본값 기준으로 조정</div>",
        unsafe_allow_html=True)

    def _num_row(label, key, default, step=5, min_v=0, max_v=200, unit="점", first=False, last=False):
        """표 행처럼 보이는 +/- 버튼 행"""
        cur = st.session_state.get(key, default)
        _changed = cur != default
        _border_top    = "border-top:1px solid #E2E6ED;" if first else ""
        _border_bottom = "border-bottom:1px solid #E2E6ED;"
        _bg = "#FFFBEB" if _changed else "#FFFFFF"

        _c0, _c1, _c2, _c3 = st.columns([3.5, 1.2, 0.4, 0.4])
        _c0.markdown(
            f"<div style='background:{_bg};{_border_top}{_border_bottom}"
            f"padding:6px 8px;font-size:11px;color:#374151;"
            f"border-left:1px solid #E2E6ED;'>"
            f"{'⚠️ ' if _changed else ''}{label}</div>",
            unsafe_allow_html=True)
        _c1.markdown(
            f"<div style='background:{_bg};{_border_top}{_border_bottom}"
            f"padding:6px 0;text-align:center;"
            f"font-size:12px;font-weight:700;color:#0D1117;'>"
            f"{cur}{unit}</div>",
            unsafe_allow_html=True)
        if _c2.button("＋", key=f"plus_{key}"):
            st.session_state[key] = min(max_v, cur + step)
            st.rerun()
        if _c3.button("－", key=f"minus_{key}"):
            st.session_state[key] = max(min_v, cur - step)
            st.rerun()
        return st.session_state.get(key, default)

    def _section_header(text):
        st.markdown(
            f"<div style='background:#F3F4F6;border:1px solid #E2E6ED;"
            f"border-bottom:none;padding:5px 8px;"
            f"font-size:10px;font-weight:700;color:#374151;"
            f"font-family:Space Mono,monospace'>{text}</div>",
            unsafe_allow_html=True)

    # ══ ① 시장 환경 임계값 ══════════════════════════════════
    _section_header("① 시장 환경 임계값")
    _num_row("유동성 최소 단계 — 이하면 매수 금지",
             "cfg_liq_min", 3, step=1, min_v=1, max_v=5, unit="단계", first=True)
    _num_row("침체 위험 상한 — 이상이면 경고",
             "cfg_rec_max", 70, step=5, min_v=30, max_v=100, unit="점")
    _num_row("VIX 경고 기준 — 이상이면 패널티",
             "cfg_vix_warn", 28, step=1, min_v=15, max_v=50, unit="", last=True)
    st.markdown("<div style='margin-bottom:10px'></div>", unsafe_allow_html=True)

    # ══ ② RS 가중치 ═════════════════════════════════════════
    _section_header("② RS 상대강도 가중치")
    _num_row("RS 95↑ 가중치 — 초강세", "cfg_rs95_w", 35, step=5, min_v=0, max_v=60, first=True)
    _num_row("RS 90↑ 가중치 — 강세",   "cfg_rs90_w", 25, step=5, min_v=0, max_v=50)
    _num_row("RS 80↑ 가중치 — 상승",   "cfg_rs80_w", 15, step=5, min_v=0, max_v=40)
    _num_row("최소 RS 표시 기준 — 이하 숨김",
             "cfg_min_rs", 70, step=5, min_v=0, max_v=95, last=True)
    st.markdown("<div style='margin-bottom:10px'></div>", unsafe_allow_html=True)

    # ══ ③ MA200 가중치 ══════════════════════════════════════
    _section_header("③ MA200 가중치")
    _num_row("MA200 위 보너스",   "cfg_ma200_bon", 20, step=5, min_v=0,  max_v=50, first=True)
    _num_row("MA200 아래 패널티", "cfg_ma200_pen", 40, step=5, min_v=10, max_v=80, last=True)
    st.markdown("<div style='margin-bottom:10px'></div>", unsafe_allow_html=True)

    # ══ ④ 기타 가중치 ═══════════════════════════════════════
    _section_header("④ 기타 가중치")
    _num_row("기관 거래량 — 2배↑", "cfg_vol_w",     25, step=5, min_v=0, max_v=50, first=True)
    _num_row("신고가 근처 — -5%↑", "cfg_hd_w",      25, step=5, min_v=0, max_v=50)
    _num_row("하락장 생존 보너스",  "cfg_survive_w", 35, step=5, min_v=0, max_v=60, last=True)
    st.markdown("<div style='margin-bottom:10px'></div>", unsafe_allow_html=True)

    # ══ ⑤ 등급 기준점수 ═════════════════════════════════════
    _section_header("⑤ 등급 기준점수")
    _num_row("🚀 ELITE 기준",  "cfg_elite_min",  140, step=5, min_v=80,  max_v=200, first=True)
    _num_row("🔥 STRONG 기준", "cfg_strong_min", 110, step=5, min_v=60,  max_v=180)
    _num_row("🔍 WATCH 기준",  "cfg_watch_min",   80, step=5, min_v=40,  max_v=150, last=True)
    st.markdown("<div style='margin-bottom:10px'></div>", unsafe_allow_html=True)

    # ══ ⑥ 자동 스탠스 설정 ══════════════════════════════════
    st.markdown(
        "<div style='font-size:11px;color:#374151;"
        "font-family:Space Mono,monospace;margin-bottom:4px'>"
        "⑥ 자동 스탠스 설정</div>",
        unsafe_allow_html=True)

    # 현재 자동 스탠스 표시
    _cur_st = st.session_state.get("auto_stance", {})
    _cur_label = _cur_st.get("label", "계산 중...")
    _cur_reason= _cur_st.get("reason", "MARKET 탭 먼저 접속")
    st.markdown(
        f"<div style='background:#F3F4F6;border:1px solid #E2E6ED;"
        f"border-radius:3px;padding:6px 10px;margin-bottom:8px;"
        f"font-size:10px;color:#374151'>"
        f"현재 자동 판단: <b>{_cur_label}</b> — {_cur_reason}</div>",
        unsafe_allow_html=True)

    # 수동 오버라이드
    _manual_override = st.selectbox(
        "수동 오버라이드",
        ["자동 (권장)", "🟢 공격 강제", "🟡 방어 강제", "🔴 위험 강제"],
        index=0, key="manual_stance_override")

    if _manual_override != "자동 (권장)":
        _map = {
            "🟢 공격 강제": calc_auto_stance(4, 80, 20, 15),
            "🟡 방어 강제": calc_auto_stance(3, 55, 25, 20),
            "🔴 위험 강제": calc_auto_stance(2, 80, 75, 35),
        }
        st.session_state["auto_stance"] = _map[_manual_override]
        st.info(f"수동 설정 적용됨: {_manual_override}")

    st.markdown("---")

    # ══ 현재 설정 상태 표 ════════════════════════════════════
    st.markdown(
        "<div style='font-size:11px;color:#374151;"
        "font-family:Space Mono,monospace;margin-bottom:4px'>"
        "현재 설정값</div>",
        unsafe_allow_html=True)

    _cfg_rows = []
    _cfg_meta = [
        ("유동성 최소 단계",  "cfg_liq_min",     3,   "단계"),
        ("침체 위험 상한",    "cfg_rec_max",     70,  "점"),
        ("VIX 경고 기준",     "cfg_vix_warn",    28,  ""),
        ("RS 95↑ 가중치",     "cfg_rs95_w",      35,  "점"),
        ("RS 90↑ 가중치",     "cfg_rs90_w",      25,  "점"),
        ("RS 80↑ 가중치",     "cfg_rs80_w",      15,  "점"),
        ("최소 RS 기준",      "cfg_min_rs",      70,  ""),
        ("MA200 위 보너스",   "cfg_ma200_bon",   20,  "점"),
        ("MA200 아래 패널티", "cfg_ma200_pen",   40,  "점"),
        ("기관거래량 가중치", "cfg_vol_w",       25,  "점"),
        ("신고가 가중치",     "cfg_hd_w",        25,  "점"),
        ("하락장 생존 보너스","cfg_survive_w",   35,  "점"),
        ("ELITE 기준",        "cfg_elite_min",  140,  "점"),
        ("STRONG 기준",       "cfg_strong_min", 110,  "점"),
        ("WATCH 기준",        "cfg_watch_min",   80,  "점"),
    ]
    for _lbl, _key, _def, _unit in _cfg_meta:
        _cur = st.session_state.get(_key, _def)
        _changed = "⚠️ 변경" if _cur != _def else "기본값"
        _cfg_rows.append({
            "항목":   _lbl,
            "현재값": f"{_cur}{_unit}",
            "기본값": f"{_def}{_unit}",
            "상태":   _changed,
        })

    st.dataframe(
        pd.DataFrame(_cfg_rows),
        use_container_width=True, hide_index=True,
        column_config={
            "항목":   st.column_config.TextColumn("항목",   width="medium"),
            "현재값": st.column_config.TextColumn("현재값", width="small"),
            "기본값": st.column_config.TextColumn("기본값", width="small"),
            "상태":   st.column_config.TextColumn("상태",   width="small"),
        })

    if st.button("🔄 기본값으로 초기화", key="cfg_reset"):
        for _k, _v in _DEFAULTS.items():
            st.session_state[_k] = _v
        st.success("✅ 기본값으로 초기화됐습니다")
        st.rerun()

st.markdown(
    f"<div style='text-align:center;font-size:9px;color:#1E2D3D;"
    f"margin-top:20px;padding-top:8px;border-top:1px solid #0D1117'>"
    f"QUANTUM PRO {PRO_VERSION} &nbsp;|&nbsp; "
    f"데이터: FRED·yfinance &nbsp;|&nbsp; "
    f"본 앱은 정보 제공 목적이며 투자 권유가 아닙니다</div>",
    unsafe_allow_html=True)
