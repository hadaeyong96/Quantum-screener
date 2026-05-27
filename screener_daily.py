"""
screener_daily.py — PRO_APP 전용 자동 스크리닝
─────────────────────────────────────────────
GitHub Actions에서 매일 오전 9시 자동 실행
→ Leader Score 계산 + History_PRO 탭에 저장

GitHub Secrets 필요:
  FRED_API_KEY             : FRED API 키
  GCP_SERVICE_ACCOUNT_JSON : JSON 파일 전체 내용 (한 줄)
  SHEETS_URL               : Google Sheets URL
"""

import os, sys, json, requests, warnings
from datetime import datetime
import numpy as np
import pandas as pd
import yfinance as yf
import gspread
from google.oauth2.service_account import Credentials

warnings.filterwarnings("ignore")

# ═══════════════════════════════════════════════════════
# 환경변수
# ═══════════════════════════════════════════════════════
FRED_API_KEY = os.environ.get("FRED_API_KEY", "")
SHEETS_URL   = os.environ.get("SHEETS_URL", "")
GCP_JSON_STR = os.environ.get("GCP_SERVICE_ACCOUNT_JSON", "")

SHEET_TAB = "History_PRO"
SHEET_HEADER = [
    "Date","Ticker","Name","EntryPrice","LeaderScore","LeaderGrade",
    "RS","MA200","AccScore","LiqStage","RecRisk",
    "EPS","CondCount","Breakout","VolSurge","Sector"
]

SCREEN_TICKERS = [
    "NVDA","MSFT","META","AMZN","GOOGL","AAPL","TSLA","NFLX","COST",
    "AVGO","AMD","QCOM","TXN","AMAT","MU","MRVL","LRCX","KLAC","NXPI","ADI",
    "NOW","ADBE","CRM","ORCL","INTU","CDNS","SNPS","WDAY","TEAM","ANSS",
    "PANW","CRWD","FTNT","ZS","CYBR",
    "PLTR","DDOG","MDB","SNOW","HUBS","GTLB",
    "ISRG","DXCM","IDXX","GEHC","MRNA","REGN","BIIB",
    "BKNG","ABNB","LULU","MELI","SBUX","PCAR",
    "PYPL","COIN","APP","AXON",
    "CMCSA","TMUS","FANG","CEG","SMCI",
]

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

# ═══════════════════════════════════════════════════════
# 유틸
# ═══════════════════════════════════════════════════════
def sf(v, d=0.0):
    try:
        f = float(v)
        return d if (np.isnan(f) or np.isinf(f)) else f
    except: return d

def fred_val(sid):
    try:
        url = (f"https://api.stlouisfed.org/fred/series/observations"
               f"?series_id={sid}&api_key={FRED_API_KEY}&file_type=json"
               f"&sort_order=desc&limit=5")
        r = requests.get(url, timeout=15)
        obs = [o for o in r.json().get("observations",[])
               if o["value"] not in (".",""," ")]
        return float(obs[0]["value"]) if obs else None
    except: return None

def fred_series(sid, start="2018-01-01"):
    try:
        url = (f"https://api.stlouisfed.org/fred/series/observations"
               f"?series_id={sid}&api_key={FRED_API_KEY}&file_type=json"
               f"&sort_order=asc&observation_start={start}")
        r = requests.get(url, timeout=15)
        obs = r.json().get("observations",[])
        data = {o["date"]: float(o["value"])
                for o in obs if o["value"] not in (".",""," ")}
        s = pd.Series(data)
        s.index = pd.to_datetime(s.index)
        return s.sort_index() if not s.empty else None
    except: return None

# ═══════════════════════════════════════════════════════
# 유동성 + 침체 점수
# ═══════════════════════════════════════════════════════
def calc_liq(fred):
    score = 50
    ff  = sf(fred.get("FedFunds",  pd.Series([5])).iloc[-1]   if isinstance(fred.get("FedFunds"),  pd.Series) else 5)
    rr  = sf(fred.get("RealRate",  pd.Series([1])).iloc[-1]   if isinstance(fred.get("RealRate"),  pd.Series) else 1)
    cs  = sf(fred.get("CreditSpread",pd.Series([4])).iloc[-1] if isinstance(fred.get("CreditSpread"),pd.Series) else 4)
    rrp = sf(fred.get("RRP",       pd.Series([500])).iloc[-1] if isinstance(fred.get("RRP"),       pd.Series) else 500)
    res = sf(fred.get("Reserves",  pd.Series([3000])).iloc[-1]if isinstance(fred.get("Reserves"),  pd.Series) else 3000)

    if ff > 5:    score -= 10
    elif ff < 2:  score += 10
    if rr > 2:    score -= 10
    elif rr < 0:  score += 10
    if cs > 5:    score -= 15
    elif cs < 3.5:score += 10
    if rrp > 1000:score -= 5
    else:         score += 5
    if res < 2000:score -= 10
    elif res > 3000:score += 5

    score = max(0, min(100, score))
    stage = 5 if score>=80 else (4 if score>=60 else (3 if score>=40 else (2 if score>=20 else 1)))
    print(f"  유동성: {score:.0f}점 → {stage}단계")
    return score, stage

def calc_rec(fred):
    signals = []
    t = fred.get("T10Y2Y")
    if t is not None and len(t)>0:
        v = sf(t.iloc[-1])
        signals.append(90 if v<-0.5 else (65 if v<0 else (35 if v<0.5 else 10)))
    s = fred.get("SAHM")
    if s is not None and len(s)>0:
        v = sf(s.iloc[-1])
        signals.append(95 if v>=0.5 else (60 if v>=0.3 else (30 if v>=0.1 else 5)))
    c = fred.get("CreditSpread")
    if c is not None and len(c)>0:
        v = sf(c.iloc[-1])
        signals.append(95 if v>7 else (70 if v>5 else (45 if v>4 else (20 if v>3 else 8))))
    u = fred.get("UNRATE")
    if u is not None and len(u)>=4:
        chg = sf(u.iloc[-1]) - sf(u.iloc[-4])
        signals.append(80 if chg>0.5 else (50 if chg>0.2 else (25 if chg>0 else 8)))
    rec = round(sum(signals)/len(signals),1) if signals else 50.0
    print(f"  침체위험: {rec:.0f}점")
    return rec

# ═══════════════════════════════════════════════════════
# Leader Score
# ═══════════════════════════════════════════════════════
def leader_score(row, mctx):
    score = 0; reasons = []
    liq=mctx["liq_stage"]; rec=mctx["rec_risk"]
    vix=mctx["vix"];        drop=mctx["mkt_drop"]
    trend=mctx["qqq_trend"]

    if liq<=2:   score-=20; reasons.append("유동성위험")
    elif liq>=4: score+=10
    if rec>=70:  score-=25; reasons.append("침체위험")
    elif rec<=35:score+=10
    if vix>=28:  score-=25
    elif vix<=18:score+=5
    if trend=="BULL": score+=10
    elif trend=="BEAR":score-=15

    rs=sf(row.get("RS",0))
    if rs>=95:   score+=35; reasons.append("RS초강세")
    elif rs>=90: score+=25
    elif rs>=80: score+=15
    elif rs<70:  score-=25

    if not row.get("MA200",False):
        score-=40; reasons.append("MA200하회")
    else:
        score+=20

    hd=sf(row.get("HighDist",-100))
    if hd>=-5:   score+=25; reasons.append("신고가근처")
    elif hd>=-10:score+=15
    elif hd<=-25:score-=20

    vr=sf(row.get("VolRatio",1),1)
    if vr>=2.0:  score+=25; reasons.append("기관거래량")
    elif vr>=1.5:score+=15
    elif vr<=0.7:score-=10

    eps=sf(row.get("EPS",0))
    if eps>=50:  score+=25
    elif eps>=30:score+=20
    elif eps<0:  score-=25

    if row.get("MA50",False):  score+=10
    if row.get("MA20",False):  score+=5

    if drop<=-10:
        if rs>=90 and hd>=-10:
            score+=35; reasons.append("하락장생존")
        if vr>=1.5: score+=10

    acc=0
    if sf(row.get("UpVolRatio",1))>=1.3: acc+=10
    if row.get("GapHold",False):          acc+=10
    if row.get("AboveVWAP",False):        acc+=10
    if sf(row.get("OBVTrend",0))>0:       acc+=10
    if row.get("Breakout",False) and vr>=1.5: acc+=10
    score+=acc
    if acc>=25: reasons.append("기관매집")

    if rec>=75 and rs<95: score-=15

    grade = ("🚀 ELITE" if score>=140 else
             "🔥 STRONG" if score>=110 else
             "✅ WATCH" if score>=80 else "⚠️ WEAK")

    return round(score,1), grade, acc

# ═══════════════════════════════════════════════════════
# 종목 스크리닝
# ═══════════════════════════════════════════════════════
def screen(mctx):
    print(f"\n  {len(SCREEN_TICKERS)}개 종목 데이터 수집 중...")
    try:
        raw = yf.download(
            SCREEN_TICKERS + ["QQQ"],
            period="1y", interval="1d",
            auto_adjust=True, progress=False,
            threads=True, group_by="ticker"
        )
    except Exception as e:
        print(f"  yfinance 오류: {e}"); return []

    try:
        qqq_c = raw["QQQ"]["Close"].dropna()
        qqq_r = qqq_c.pct_change().dropna()
    except:
        qqq_c = pd.Series(dtype=float)
        qqq_r = pd.Series(dtype=float)

    results = []
    for tk in SCREEN_TICKERS:
        try:
            close  = raw[tk]["Close"].dropna()
            volume = raw[tk]["Volume"].dropna()
            high   = raw[tk]["High"].dropna()
            open_  = raw[tk]["Open"].dropna()
            if len(close) < 60: continue

            cur = sf(close.iloc[-1])
            ret = close.pct_change().dropna()

            # RS
            def _rs(n):
                _n = min(n, len(ret), len(qqq_r))
                if _n < 5: return 50.0
                return float(np.clip(
                    50+((1+ret.iloc[-_n:]).prod()-(1+qqq_r.iloc[-_n:]).prod())*100*2,0,100))
            rs = round(_rs(20)*0.25+_rs(60)*0.30+_rs(120)*0.25+_rs(250)*0.20,1)

            # MA
            ma20  = sf(close.rolling(20).mean().iloc[-1])  if len(close)>=20  else cur
            ma50  = sf(close.rolling(50).mean().iloc[-1])  if len(close)>=50  else cur
            ma200 = sf(close.rolling(200).mean().iloc[-1]) if len(close)>=200 else cur

            # 신고가
            hi52 = sf(close.rolling(min(252,len(close))).max().iloc[-1])
            hd   = round((cur-hi52)/hi52*100,1) if hi52>0 else -100

            # 거래량
            avg_v    = sf(volume.iloc[-21:-1].mean()) if len(volume)>=21 else 1
            vol_ratio= sf(volume.iloc[-1])/avg_v if avg_v>0 else 1.0
            breakout = cur > sf(close.iloc[-22:-1].max()) if len(close)>=22 else False
            vol_surge= vol_ratio >= 1.5

            # OBV
            try:
                pd_ = close.diff().iloc[-20:]
                obv = (volume.iloc[-20:]*pd_.apply(
                    lambda x:1 if x>0 else(-1 if x<0 else 0))).cumsum()
                obv_trend = 1 if sf(obv.iloc[-1])>sf(obv.iloc[0]) else -1
            except: obv_trend=0

            # 양봉비율
            try:
                ud = close.diff().iloc[-10:]>0
                uv = sf(volume.iloc[-10:][ud].mean()) if ud.any() else 0
                dv = sf(volume.iloc[-10:][~ud].mean()) if (~ud).any() else 1
                up_vr = uv/dv if dv>0 else 1.0
            except: up_vr=1.0

            # VWAP
            try:
                vwap = sf((close.iloc[-5:]*volume.iloc[-5:]).sum()/volume.iloc[-5:].sum()) if volume.iloc[-5:].sum()>0 else cur
                above_vwap = cur>=vwap
            except: above_vwap=False

            # 갭홀드
            try:
                gap_hold = (sf(open_.iloc[-1])>sf(high.iloc[-2])*1.01 and cur>=sf(open_.iloc[-1])*0.99)
            except: gap_hold=False

            # RSI
            try:
                dlt=close.diff(); up=dlt.clip(lower=0).rolling(14).mean()
                dn=(-dlt.clip(upper=0)).rolling(14).mean()
                rsi=round(float((100-100/(1+up/dn.replace(0,1e-9))).iloc[-1]),1)
            except: rsi=50.0

            # EPS
            eps=0.0
            try:
                info=yf.Ticker(tk).fast_info
                eps=round(sf(getattr(info,"earnings_growth",0))*100,1)
            except: pass

            cond_count = sum([
                True, breakout, vol_surge, rs>=80,
                cur>ma200, hd>=-10, rsi<70, cur>ma50, eps>30
            ])

            row = {
                "Ticker":    tk,
                "Sector":    SECTOR_MAP.get(tk,"기타"),
                "EntryPrice":round(cur,2),
                "RS":        rs,
                "MA200":     cur>ma200,
                "MA50":      cur>ma50,
                "MA20":      cur>ma20,
                "HighDist":  hd,
                "VolRatio":  round(vol_ratio,2),
                "Breakout":  breakout,
                "VolSurge":  vol_surge,
                "OBVTrend":  obv_trend,
                "UpVolRatio":round(up_vr,2),
                "AboveVWAP": above_vwap,
                "GapHold":   gap_hold,
                "EPS":       eps,
                "CondCount": cond_count,
            }
            ls, grade, acc = leader_score(row, mctx)
            row["LeaderScore"] = ls
            row["LeaderGrade"] = grade
            row["AccScore"]    = acc
            results.append(row)

            if grade in ("🚀 ELITE","🔥 STRONG","✅ WATCH") and cur>ma200:
                print(f"    {grade} {tk}: {ls:.0f}점 RS={rs:.1f}")

        except Exception as e:
            print(f"    ⚠️ {tk}: {e}")
            continue

    results.sort(key=lambda x: x["LeaderScore"], reverse=True)
    return results

# ═══════════════════════════════════════════════════════
# Google Sheets 저장
# ═══════════════════════════════════════════════════════
def save_to_sheets(results, liq_stage, rec_risk):
    if not GCP_JSON_STR or not SHEETS_URL:
        print("  ⚠️ GCP 키 또는 SHEETS_URL 없음"); return False
    try:
        creds_dict = json.loads(GCP_JSON_STR)
        creds = Credentials.from_service_account_info(
            creds_dict,
            scopes=["https://spreadsheets.google.com/feeds",
                    "https://www.googleapis.com/auth/drive"]
        )
        gc = gspread.authorize(creds)
        sh = gc.open_by_url(SHEETS_URL)

        # History_PRO 탭
        try:
            ws = sh.worksheet(SHEET_TAB)
            if not ws.row_values(1):
                ws.append_row(SHEET_HEADER)
        except:
            ws = sh.add_worksheet(title=SHEET_TAB, rows=5000, cols=20)
            ws.append_row(SHEET_HEADER)

        today = datetime.now().strftime("%Y-%m-%d")

        # 오늘 기존 데이터 삭제
        all_vals = ws.get_all_values()
        del_rows = [i+1 for i,r in enumerate(all_vals) if r and r[0]==today]
        for ri in sorted(del_rows, reverse=True):
            ws.delete_rows(ri)

        # MA200 위 + WATCH 이상 저장
        save_rows_above = [
            r for r in results
            if r.get("MA200") and r.get("LeaderScore",0)>=80
        ]
        # MA200 아래 전체 저장 (백테스트 비교용)
        save_rows_below = [
            r for r in results
            if not r.get("MA200")
        ]
        save_rows = save_rows_above + save_rows_below

        new_rows = []
        for r in save_rows:
            new_rows.append([
                today, r["Ticker"],
                COMPANY_NAME.get(r["Ticker"], r["Ticker"]),
                r["EntryPrice"],
                r["LeaderScore"], r["LeaderGrade"],
                r["RS"], "Y" if r["MA200"] else "N",
                r["AccScore"], liq_stage, round(rec_risk,1),
                r["EPS"], r["CondCount"],
                "Y" if r["Breakout"] else "N",
                "Y" if r["VolSurge"] else "N",
                r["Sector"],
            ])

        if new_rows:
            ws.append_rows(new_rows, value_input_option="RAW")
            print(f"  ✅ {len(new_rows)}개 종목 저장 완료 ({today})")
        else:
            print("  ⚠️ 저장 조건 충족 종목 없음")
        return True

    except Exception as e:
        print(f"  ❌ Sheets 저장 실패: {e}"); return False

# ═══════════════════════════════════════════════════════
# 메인
# ═══════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 55)
    print(f"QUANTUM PRO — 자동 스크리닝")
    print(f"실행: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print("=" * 55)

    # 1. FRED 데이터
    print("\n[1] FRED 데이터 수집 중...")
    fred = {}
    for k, sid in [
        ("FedFunds","FEDFUNDS"),("RealRate","DFII10"),
        ("CreditSpread","BAMLH0A0HYM2"),("RRP","RRPONTSYD"),
        ("Reserves","WRESBAL"),("T10Y2Y","T10Y2Y"),
        ("SAHM","SAHMREALTIME"),("UNRATE","UNRATE"),
    ]:
        s = fred_series(sid)
        if s is not None:
            fred[k] = s
            print(f"  ✅ {k}: {sf(s.iloc[-1]):.3f}")
        else:
            print(f"  ❌ {k}: 로드 실패")

    # 2. 유동성 + 침체
    print("\n[2] 시장 환경 분석...")
    liq_score, liq_stage = calc_liq(fred)
    rec_risk = calc_rec(fred)

    # 3. QQQ 추세
    print("\n[3] QQQ 추세 분석...")
    mkt_ctx = {"liq_stage":liq_stage,"rec_risk":rec_risk,
               "vix":20,"qqq_trend":"NEUTRAL","mkt_drop":0}
    try:
        qqq = yf.download("QQQ", period="1y",
            auto_adjust=True, progress=False)["Close"].dropna()
        vix = yf.download("^VIX", period="30d",
            auto_adjust=True, progress=False)["Close"].dropna()
        c=sf(qqq.iloc[-1]); ma20=sf(qqq.rolling(20).mean().iloc[-1])
        ma50=sf(qqq.rolling(50).mean().iloc[-1])
        if c>ma20>ma50:   mkt_ctx["qqq_trend"]="BULL"
        elif c<ma20<ma50: mkt_ctx["qqq_trend"]="BEAR"
        hi52=sf(qqq.rolling(min(252,len(qqq))).max().iloc[-1])
        if hi52>0: mkt_ctx["mkt_drop"]=round((c-hi52)/hi52*100,1)
        if len(vix)>0: mkt_ctx["vix"]=sf(vix.iloc[-1])
        print(f"  QQQ: {mkt_ctx['qqq_trend']} | VIX: {mkt_ctx['vix']:.1f} | 낙폭: {mkt_ctx['mkt_drop']:.1f}%")
    except Exception as e:
        print(f"  QQQ 분석 실패: {e}")

    if liq_stage <= 2:
        print(f"\n⚠️ 유동성 {liq_stage}단계 — 매수 금지 구간")
        print("  빈 결과로 Sheets 기록")
        save_to_sheets([], liq_stage, rec_risk)
        sys.exit(0)

    # 4. 종목 스크리닝
    print(f"\n[4] 종목 스크리닝 (유동성 {liq_stage}단계)...")
    results = screen(mkt_ctx)

    elite  = [r for r in results if "ELITE"  in r.get("LeaderGrade","")]
    strong = [r for r in results if "STRONG" in r.get("LeaderGrade","")]
    watch  = [r for r in results if "WATCH"  in r.get("LeaderGrade","")]
    print(f"\n  결과: ELITE {len(elite)}개 | STRONG {len(strong)}개 | WATCH {len(watch)}개")

    # 5. Sheets 저장
    print("\n[5] Google Sheets 저장 중...")
    save_to_sheets(results, liq_stage, rec_risk)

    print("\n✅ 완료")
    print("=" * 55)
