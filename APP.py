"""
V24 Quantum Institutional OS  |  초보자용 투자 대시보드
핵심 원칙: 데이터 → 해석 → 행동
순서: 유동성 흐름 → 시장 → 주식

VERSION : APP_V111
  V111 - 앱 내 문구 편집 모드 추가
         → 사이드바 ✏️ 버튼으로 ON/OFF
         → 유동성 지표 설명을 앱에서 직접 수정·저장 (explanations.json)
  V110 - 기초 자료 버전 (APP_V001 → V110 재명명)
         → 앞으로 이 버전을 기반으로 수정 작업 진행
  V107 - ③ 섹션 원형 복원 (유동성 카드 | 시장지표 카드 분리)
         → V106에서 통합·다크카드 수정 이전 상태로 복원
  V106 - ① 매수 종목 상세 카드 → st.dataframe 표 형식 통일
         → ② 청산 검토와 동일한 방식: 손절가/목표1/목표2 컬럼 추가
  V105 - 💼 내 포트폴리오 탭 완전 삭제 (구글 시트로 이관)
         → 앱 핵심: 유동성 읽기 + 종목 추천에 집중
         → _trades_load/save 의존성 제거, 약 600줄 감소
  V104 - BUG FIX: ⚙️ 포트폴리오 관리 expander 글자 겹침 수정
         → st.expander 제거, session_state 토글 + container 방식으로 교체
  V103 - 포트폴리오 ↔ 알고리즘 연동 강화
         · 포트폴리오 탭 각 행에 매수·매도 신호 배지 직접 표시
           (💰익절 / 📉추적손절 / ⚠️EXIT / 🔁MA10회복 / 🚀강매수)
         · 분할매수 lots 가중평균가로 익절 계산 (단일 buy_price 오류 수정)
         · 버전명 전체 통일: QUANTUM INSTITUTIONAL OS V103
           (APP_VERSION, 타이틀, 사이드바, 헤더, 리포트, 푸터 6곳 동시)
         ✅ 앞으로 버전 수정 시 6곳 동시 체크 의무화
  V102 - 매수 종목 상세 카드 정리
         · 비중 바 (보유%·매도%·진행 바) 전체 제거
         · 익절 단계 텍스트 설명 제거
         · 4칸 가격 그리드만 깔끔하게 표시
           (현재가 / ATR손절 / 1차+15% / 2차+25%)
         · _hold_pct, _sold_pct, _bh, _bs, _stxt 관련 코드 정리
  V101 - STEP5 보유관리 → 💼 내 포트폴리오 통합
         · 기존 STEP5 삭제, 포트폴리오 탭이 STEP5 자리 차지 (탭 5개)
         · QQQ 비교 차트를 포트폴리오 탭 하단으로 이식
         · 📝 새 종목 추가 폼: expander 글자 겹침 버그 수정
           → st.expander 제거, st.form() 으로 교체 (재렌더링 없이 안정적)
         · ＋ 다른 구매 기록하기: expander 제거, container 인라인 폼으로 교체
         · 앞으로 펼치기 기능은 expander 대신 st.form / container 사용 원칙 적용
  V100 - 💼 내 포트폴리오 탭 신규 추가
         Google Finance 스타일 포트폴리오 UI
         · 종목별 매수 기록 직접 입력 (티커·수량·매수가·날짜)
         · 여러 번 분할매수 기록 지원 (+ 다른 구매 기록하기)
         · 현재가·일일 수익·총수익·원화 평가금액 자동 계산
         · 접힘/펼침 상세 보기 (Google Finance 동일 UX)
         · 정렬: 일일 변동률 / 수익률 / 종목명
         · 전체 포트폴리오 요약 카드 (총평가액·총수익·수익률)
         · trades.json 영구 저장
  V99  - 💻 PC 버전
        V98 전체 로직 유지 + PC 레이아웃 복원
        · 사이드바 expanded / 탭 이름 풀네임 복원
        · 지표 카드 좌(설명) + 우(차트) 2열 복원
        · 차트 height 160→220~280 복원
        · 데이터프레임 height 340→520 복원
        · 섹터·시장 3열 카드 복원
        · 종목 테이블 전체 컬럼 표시
        · STEP4 3열 행동 카드 복원
  V98 - 7가지 전면 개선 (AI 트레이더 평가 반영)
        1. 백테스트 결과 종목분석 탭 상단 표시 (승률·평균수익·MDD)
        2. trades.json 매수가 저장 → 실제 수익률 기반 익절 판단
        3. ATR 기반 포지션 사이징 (종목당 총자산 1% 리스크 룰)
        4. 실적 서프라이즈 갭업 진입 신호 (당일 +5%↑ + 거래량 3배↑)
        5. 섹터 강도 0~100점 정량화 (RS+1M+3M+MA 합산)
        6. RS Score 단기 가중치 재조정 (1M:0.25 3M:0.30 6M:0.25 12M:0.20)
        7. GLD 헤지 자산 추가 (유동성 2단계 이하 자동 비중 상향)
  V97 - 수익 확보 시스템
        · 추적 손절 (Trailing Stop): 20일 고점 -10% 이탈 → 📉 추적손절
        · 단계별 익절 신호: +15% → 💰 1차익절 (50% 매도), +25% → 💰 2차익절 (잔여 50% 절반)
        · 실적발표 3일 전 보유 시 ⚠️ 실적전축소 신호 자동 표시
        · VIX 단계별 포지션 축소 (20→경계 / 25→축소 / 28→금지)
        · MA10 이탈 2일 연속 확인 후 EXIT 확정 (횡보 손절 반복 방지)
        · 일평균 거래량 100만주 미만 자동 필터
        · get_invest_ratio VIX 단계 반영
  V96 - 🔁 MA10 재돌파 신호 추가
        3연상 거래량 최소 조건 추가 (평균 × 0.8)
        거래량 가중치 10%→15% / EPS 가중치 20%→15%
        ROE 20%↑ 보너스 +5점 밸류에이션에 반영
        ATR(14) 기반 동적 손절 컬럼 추가
  V95 - 📱 모바일 전용 버전 (Mobile-First)
        사이드바 → collapsed / 탭 이름 아이콘+단어로 축약
        모든 st.columns → 세로 스택 (모바일 1열)
        차트 height: 220→160 / 폰트 전체 -2px / 패딩 축소
        데이터프레임 height: 520→340 / 핵심 컬럼만 표시
        3열 카드 → CSS grid 2열 자동 wrap
UPDATED : 2026-05-22
CHANGES :
  V01 - 원본 기본 대시보드 (yfinance)
  V02 - FRED 연동 / 다크테마 / RS 버그 수정
  V03 - 유동성 대시보드 / 행동 가이드 / 섹터 분석
  V04 - TODAY'S ACTION 제거 / 페이지 간소화
  V05 - 탭 네비게이션 / QQQ차트 / VIX / 공포탐욕지수
  V06 - 탭 순서 재편 / 사이드바 3단계 종목 구성 / 섹터 전용 탭
  V07 - DEFAULT_TICKERS QQQ 주요 50종목으로 확장
  V08 - CNN+multpl 디자인 적용 / PE Ratio 추가 / 색상 절제
  V23 - 라이트테마 완성 / 다크잔존 전면 제거 / 데이터 타임스탬프 / 주식지도 섹터+RS색상+범례
  V43 - 유동성 섹션 체크리스트 표 형식으로 변경 (6줄 → 1줄/지표)
V42 - BUG FIX: 보고서 표시 코드 누락 복구 (화면에 아무것도 안 나오는 문제)
V41 - 보고서 "종합 전략 판단" 섹션 추가
        RSI/실질금리/환율 자동 위험 분석 + 시나리오 확률 자동 계산
        BUG FIX: 구 API 키 입력 중복 제거 (사이드바 전역 잔존 코드)
V40 - 순수 텍스트 보고서 (이모지 제거, ASCII 구조)
        유동성 섹션 강화: 지표별 역할·현재값·역사적 위치 상세 설명
        포트폴리오 표 형식: 종목/배분/주수/실매수 정렬
V39 - 보고서 전면 재설계: A4 반장 분량, 핵심만
        금리 3개만 (2Y/10Y/30Y)
        BUG FIX: M2/TGA/준비금 단위 표시 오류 (0.00TB$ → T$)
        포트폴리오: 종목별 주수 명시
V38 - BUG FIX: f-string 포맷 지정자 내 조건식 사용 불가 수정
        fg_score/pe_current 표시를 f-string 밖에서 미리 계산
V37 - BUG FIX: get_invest_ratio/SCALE_CONFIG 전역 이동 (NameError 수정)
V36 - 단일 화면 투자 지침서 (탭 제거)
        전체 수익률 커브 (1M/3M/2Y/3Y/5Y/10Y/20Y/30Y)
        HTML+텍스트 이중 보고서 (화면 시각화 + 텔레그램/다운로드)
        내 거래 탭 제거 (Google Finance 사용)
V35 - 5탭 확장: 내 거래(매수/매도/수익률) + 보고서(생성/다운로드/텔레그램)
        포트폴리오 탭: 매수 주수 계산기 (환율 자동 적용)
        내 거래: trades.json 영구 저장 + 엑셀 다운로드
        보고서: 서론/본론/결론 자동 생성 + 다운로드 + 텔레그램
V34 - 3탭 전면 재구성: 오늘의 판단 / 포트폴리오 / 설정
        load_stocks 전역 이동 (탭 진입 전 자동 로드)
        오늘의 판단: 유동성+시장+섹터+TOP5 종목 한 화면
        설정 탭: API키·투자금·텔레그램·종목관리 통합
V33 - 시장·섹터 탭 재구성: QQQ 차트 맨 앞 이동
        QQQ 차트 업그레이드: MA200 + 거래량 + RSI(14) + VIX + 52주 고점/저점
        섹터 선택 → 진입 판단 섹션 제거
        섹터 분석 → 강한섹터 순서로 정리
V32 - OS 키체인(keyring) 보안 저장 적용
        저장 우선순위: keyring > secrets.toml > config.json > 수동 입력
        keyring 미설치 시 config.json 평문 저장 자동 폴백
V31 - API 키 자동 저장 (secrets.toml 우선 → config.json 폴백 → 수동 입력)
        저장 버튼 1클릭으로 config.json 영구 저장
        사이드바 종목 목록 → 섹터별 요약으로 변경
V30 - BUG FIX: 포트폴리오 탭 단계 계산 이중화 해결
        compute_liq_stage() → LIQ_ACTION["stage"] 통일 (100점 시스템 일원화)
        투자 불가 메시지 V29 기준으로 수정
V29 - 단계 역전: 1=현금보유(최악) → 5=적극매수(최적)
        점수판 → 각 지표 차트 아래 배치 (차트+점수 연결)
        점수판 양호 색상 진한초록 → 연한초록 (#166534 → #16A34A)
V28 - BUG FIX: pandas Series "or" 연산자 사용 금지 위반 수정 (3부 규칙)
        cur_data = fred_data.get(key) or hist → 안전한 None/empty 체크로 교체
V27 - BUG FIX: 단계 바 HTML 중첩 렌더링 오류 수정 (별도 st.markdown 분리)
        BUG FIX: TGA·RRP 백분위 계산 오류 (limit=60 → 2000년 전체 역사 로드)
        BUG FIX: M2 limit=30 부족 → fred_history 전용 로더 추가
V26 - 유동성 100점 점수 시스템 (역사 백분위 기반, FRED 전체 데이터 활용)
        투자 단계 5단계 한글화 (적극매수/선별매수/관망/투자보류/현금보유)
        유동성 5단계 진행 바 + 단계별 명확한 범례 표시
        Layer 2 지표 점수판 (6개 지표 × 100점 + 위험 기준선 시각화)
        종목맵 섹터 박스 배경 진하게 수정 (흰배경 흰글씨 가독성 버그 수정)
        RISK ON/OFF → 한글 투자 행동 단계로 전면 교체
        투자금 규모(사이드바 직접 입력)에 따른 5단계 전략 자동 결정
        유동성 단계 × 시장 상태 → 실질 투자 가능 금액 자동 계산
        3계층 종목풀 (공격/방어/헤지) + 규모별 헤지 자산 자동 추가
        날짜별 분할 매수 스케줄 (1~3차 구체적 금액 표)
        포트폴리오 리스크 점수 (0~100, 섹터집중도+RS+유동성)
        청산 신호 별도 패널로 분리
        BUG FIX: _dir_arrow 절대값 임계값 → 상대값 기준으로 수정 (M2 단위 오류 해결)
        BUG FIX: pe_current falsy 체크 → is not None 패턴 통일
        BUG FIX: sector ETF 로드 기간 3mo → 6mo (마진 확보)
        BUG FIX: TAB1 주석 3중 중복 제거
        BUG FIX: dir() 체크 패턴 정리 (module-scope 변수 직접 참조)
        NEW: 실적 발표일 경고 (매수 3일 전 경고 — 우선순위 1위)
        NEW: 52주 신고가 대비 위치 게이지 시각화 (우선순위 2위)
        NEW: 환율 차트 USD/KRW · USD/JPY 세계시장 탭 추가 (우선순위 5위)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
코딩 원칙 (V106+, 모든 버전에 적용)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[데이터 정확성 원칙]
1. 핵심 판단 데이터는 항상 실시간/공식 소스에서 수집한다.
   - 주가, 배당수익률, 재무 지표 → yfinance 실제 데이터
   - 유동성 지표 → FRED API 공식 데이터
   - 하드코딩 고정값 사용 금지 (임시 fallback 포함)

2. 데이터가 불확실하거나 누락된 경우 반드시 UI에 고지한다.
   - 표시 방식: "⚠️ 데이터 없음", "N/A", "추정값" 명시
   - 추정/근사값을 실제값처럼 표시하는 것은 절대 금지
   - 고지 없이 0 또는 기본값으로 대체 금지

3. 데이터 수집 실패 시 해당 항목을 None/N/A로 표시하고
   판단 로직에서 제외한다. 오류를 숨기지 않는다.

[UI 표시 원칙]
4. 추정값·근사값·지연 데이터는 항상 출처와 기준일을 표시한다.
5. "실시간" 표현은 실제로 실시간 수집 시에만 사용한다.

[코드 품질 원칙]
6. st.expander 사용 금지 → session_state 토글 + st.container
7. st.plotly_chart에 항상 key= 포함
8. pandas Series or 연산자 사용 금지
9. 모든 종목 루프는 개별 try-except
10. 버전 수정 시 VERSION·APP_VERSION·타이틀·파일명·app.py 5곳 동시
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import io, sys, re, requests, warnings, json
from pathlib import Path
from datetime import datetime, timedelta

# ── 지표 설명 텍스트 JSON 로더 ─────────────────────────────
# 앱 내 편집 모드에서 수정 후 explanations.json에 저장됨
_EXPLAINS_PATH = Path(__file__).parent / "explanations.json"

def _load_explains():
    """JSON에서 설명 텍스트 로드. 없으면 코드 내 기본값 사용."""
    try:
        if _EXPLAINS_PATH.exists():
            with open(_EXPLAINS_PATH, encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def _save_explains(data: dict):
    """설명 텍스트를 JSON에 저장."""
    try:
        with open(_EXPLAINS_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False

# ── keyring 선택적 임포트 ────────────────────────────────
try:
    import keyring
    import keyring.errors
    _KEYRING_OK = True
except ImportError:
    _KEYRING_OK = False

# ── openpyxl (엑셀 출력) ─────────────────────────────────
try:
    import openpyxl
    from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    _OPENPYXL_OK = True
except ImportError:
    _OPENPYXL_OK = False
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st
from datetime import datetime

# ─────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────
st.set_page_config(page_title="QUANTUM INSTITUTIONAL OS V111",
                   layout="wide", initial_sidebar_state="expanded")

# ── V99: PC 전용 CSS (Desktop-First) ─────────────────────
st.markdown("""
<style>
/* PC 기본 레이아웃 */
.main .block-container {
    padding: 0.8rem 1.5rem 2rem 1.5rem !important;
    max-width: 1400px !important;
}
/* DATAFRAME */
.stDataFrame { font-size: 12px !important; overflow-x: auto !important; }
.stDataFrame th { font-size: 11px !important; padding: 5px 8px !important; }
.stDataFrame td { font-size: 11px !important; padding: 5px 8px !important; }
[data-testid="stDataFrameResizable"] { overflow-x: auto !important; }
/* SIDEBAR */
[data-testid="stSidebar"] {
    min-width: 280px !important;
    max-width: 320px !important;
}
/* TABS */
[data-testid="stTabs"] button {
    font-size: 13px !important;
    padding: 10px 20px !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    font-weight: 700 !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Space+Mono:wght@400;700&display=swap');

/* BASE */
.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"],section.main
    { background-color:#F7F8FA !important; }
[data-testid="stHeader"]
    { background-color:#FFFFFF !important; border-bottom:1px solid #E2E6ED !important; }
body,p,span,div,label
    { color:#1C2330 !important; font-family:'Inter',sans-serif !important; }
h1,h2,h3 { font-family:'Space Mono',monospace !important; color:#0D1117 !important; }

/* SIDEBAR */
[data-testid="stSidebar"]
    { background-color:#FFFFFF !important; border-right:1px solid #E2E6ED !important; }
[data-testid="stSidebar"] * { color:#374151 !important; }

/* INPUTS */
[data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea
    { background-color:#FFFFFF !important; color:#1C2330 !important;
      border:1px solid #D1D5DB !important; border-radius:6px !important; font-size:13px !important; }
[data-testid="stTextInput"] input:focus
    { border-color:#4B6EAF !important; box-shadow:0 0 0 2px rgba(75,110,175,0.1) !important; }
[data-testid="stTextInput"] label,[data-testid="stTextArea"] label
    { color:#6B7280 !important; font-size:11px !important; }

/* METRIC */
[data-testid="metric-container"]
    { background:#FFFFFF !important; border:1px solid #E2E6ED !important;
      border-radius:8px !important; padding:14px 16px !important;
      box-shadow:0 1px 3px rgba(0,0,0,0.05) !important; }
[data-testid="stMetricValue"] { color:#0D1117 !important; font-weight:600 !important; }
[data-testid="stMetricLabel"] { color:#6B7280 !important; font-size:12px !important; }
[data-testid="stDataFrame"]
    { border:1px solid #E2E6ED !important; border-radius:8px !important; background:#FFFFFF !important; }

/* TABS */
[data-testid="stTabs"] [role="tablist"]
    { background:#FFFFFF !important; border-bottom:1px solid #E2E6ED !important;
      border-radius:0 !important; padding:0 4px !important; }
[data-testid="stTabs"] button
    { color:#9CA3AF !important; font-family:'Inter',sans-serif !important;
      font-size:13px !important; font-weight:500 !important; padding:10px 20px !important;
      border:none !important; border-bottom:2px solid transparent !important;
      background:transparent !important; border-radius:0 !important; }
[data-testid="stTabs"] button:hover { color:#374151 !important; }
[data-testid="stTabs"] button[aria-selected="true"]
    { color:#0D1117 !important; border-bottom:2px solid #3B5BA5 !important; font-weight:600 !important; }

/* BUTTON */
.stButton button
    { background:#FFFFFF !important; border:1px solid #D1D5DB !important; color:#374151 !important;
      font-family:'Inter',sans-serif !important; font-size:13px !important;
      font-weight:500 !important; border-radius:6px !important; }
.stButton button:hover
    { background:#F3F4F6 !important; border-color:#3B5BA5 !important; color:#0D1117 !important; }

/* MISC */
[data-testid="stCheckbox"] label { color:#374151 !important; font-size:13px !important; }
[data-testid="stSelectbox"]>div>div
    { background:#FFFFFF !important; border:1px solid #D1D5DB !important;
      color:#1C2330 !important; border-radius:6px !important; }
[data-testid="stExpander"]
    { border:1px solid #E2E6ED !important; border-radius:6px !important;
      background:#FFFFFF !important; position:relative !important; z-index:1 !important; }
[data-testid="stExpander"] > details
    { overflow:visible !important; }
[data-testid="stExpander"] > details[open]
    { margin-bottom:8px !important; }
[data-testid="stCaptionContainer"] p { color:#9CA3AF !important; font-size:12px !important; }
hr { border-color:#E2E6ED !important; margin:20px 0 !important; }

/* SECTION HEADER — multpl style */
.sec-header { padding:0 0 8px 0; margin:20px 0 14px 0;
    border-bottom:1px solid #E2E6ED; font-family:'Space Mono',monospace;
    font-size:10px; letter-spacing:2px; color:#9CA3AF; text-transform:uppercase; }

/* ALERT BOXES */
.warn-box { background:#FEF2F2; border:1px solid #FCA5A5; border-radius:6px;
    padding:10px 14px; margin:6px 0; font-size:13px; color:#B91C1C; }
.ok-box   { background:#F0FDF4; border:1px solid #86EFAC; border-radius:6px;
    padding:10px 14px; margin:6px 0; font-size:13px; color:#15803D; }
.info-box { background:#EFF6FF; border:1px solid #93C5FD; border-radius:6px;
    padding:10px 14px; margin:6px 0; font-size:13px; color:#1D4ED8; }

/* GUIDE BOX — multpl style */
.guide-box { background:#F9FAFB; border-left:2px solid #D1D5DB; padding:10px 14px;
    margin:4px 0 12px 0; font-size:13px; color:#6B7280; line-height:1.7;
    border-radius:0 4px 4px 0; }
.guide-box b { color:#374151; font-weight:600; }
.guide-box .good { color:#15803D; font-weight:500; }
.guide-box .bad  { color:#B91C1C; font-weight:500; }
.guide-box .warn { color:#92400E; font-weight:500; }

/* multpl NUMBER DISPLAY */
.stat-big { font-family:'Space Mono',monospace; font-size:40px; font-weight:700;
    color:#0D1117; line-height:1; }
.stat-row { display:flex; gap:32px; padding:12px 0;
    border-top:1px solid #E2E6ED; border-bottom:1px solid #E2E6ED; margin:12px 0; }
.stat-item .label { font-size:10px; color:#9CA3AF; letter-spacing:1px; text-transform:uppercase; }
.stat-item .value { font-family:'Space Mono',monospace; font-size:16px; color:#374151; margin-top:4px; }

/* CARDS */
.indicator-card { background:#FFFFFF; border:1px solid #E2E6ED; border-radius:6px;
    padding:12px 14px; margin:3px 0; box-shadow:0 1px 2px rgba(0,0,0,0.04); }
.sector-ticker-box { background:#FFFFFF; border:1px solid #E2E6ED; border-radius:6px; padding:12px 16px; margin:8px 0; }
.tier-box { background:#F9FAFB; border:1px solid #E2E6ED; border-radius:6px; padding:10px 12px; margin:6px 0; }
.tier-label { font-family:'Space Mono',monospace; font-size:10px; color:#9CA3AF;
    letter-spacing:1px; margin-bottom:6px; text-transform:uppercase; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────
if "cache_key"          not in st.session_state: st.session_state.cache_key = 0
if "selected_sectors"   not in st.session_state: st.session_state.selected_sectors = set()
if "extra_manual"       not in st.session_state: st.session_state.extra_manual = ""
if "sector_selected"    not in st.session_state: st.session_state.sector_selected = None

# ─────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────
def safe(v, default=0.0):
    try:
        if v is None: return default
        f = float(v); return f if f == f else default
    except: return default

def hex_rgba(hex_color, alpha=0.09):
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
    return f"rgba({r},{g},{b},{alpha})"

def is_placeholder(v): return not v or "여기에" in v or v.strip() == ""

def get_close(symbol, period="1y"):
    """yfinance 0.2.x / 1.x MultiIndex 모두 대응 — Close 또는 Adj Close 반환"""
    try:
        _e = sys.stderr; sys.stderr = io.StringIO()
        try:
            raw = yf.download(symbol, period=period, progress=False, auto_adjust=True)
        finally:
            sys.stderr = _e
        if raw is None or raw.empty:
            return None
        # ── yfinance 0.2.28+ / 1.x: MultiIndex (Price, Ticker) ──
        if isinstance(raw.columns, pd.MultiIndex):
            lvl0 = raw.columns.get_level_values(0)
            for col_name in ["Close", "Adj Close"]:
                if col_name in lvl0:
                    sub = raw[col_name]
                    s = sub.iloc[:, 0].dropna() if isinstance(sub, pd.DataFrame) else sub.dropna()
                    if len(s) > 0:
                        return s
            return None
        # ── 구버전 단순 컬럼 ─────────────────────────────────────
        for col_name in ["Close", "Adj Close"]:
            if col_name in raw.columns:
                s = raw[col_name].dropna()
                if len(s) > 0:
                    return s
        return None
    except:
        return None

def get_fred(series_id, api_key, limit=60):
    if is_placeholder(api_key): return None
    try:
        url = (f"https://api.stlouisfed.org/fred/series/observations"
               f"?series_id={series_id}&api_key={api_key}&file_type=json"
               f"&sort_order=desc&limit={limit}")
        resp = requests.get(url, timeout=15)
        if resp.status_code != 200: return None
        obs  = resp.json().get("observations", [])
        data = {o["date"]:float(o["value"]) for o in obs if o["value"] not in (".","")}
        s = pd.Series(data); s.index = pd.to_datetime(s.index)
        return s.sort_index() if not s.empty else None
    except: return None

# ─────────────────────────────────────────────────────────
# 상수
# ─────────────────────────────────────────────────────────


# ─────────────────────────────────────────────────────────
# 유동성 5단계 진입 시기 시스템
# ─────────────────────────────────────────────────────────
LIQ_STAGE_HISTORY = {
    1: [
        ("📈 2020 Q3–2021 전체 (코로나 양적완화)",
         "연준이 무제한 양적완화를 시행했습니다. M2가 전년 대비 25% 폭증하고 "
         "RRP는 거의 0에 가까웠으며 기준금리는 제로 수준이었습니다. "
         "이 구간에서 나스닥은 18개월 만에 +100% 상승했고, "
         "NVDA 같은 반도체 종목은 500% 이상 올랐습니다."),
        ("📈 2019 Q3–Q4 (예방적 금리 인하)",
         "연준이 경기 둔화를 막기 위해 3회 연속 금리를 인하했습니다. "
         "RRP 감소와 함께 유동성이 풀리며 나스닥은 4개월 만에 +15% 상승했습니다. "
         "당시 신규 매수를 했던 투자자들은 코로나 쇼크 전까지 높은 수익을 올렸습니다."),
        ("📈 2009 Q2–Q3 (금융위기 이후 QE1)",
         "리먼 브라더스 파산 이후 연준이 사상 최초의 양적완화(QE1)를 시작했습니다. "
         "Fed BS를 1조 달러 이상 확대하며 시장에 돈을 공급했고, "
         "S&P500은 바닥(666포인트)에서 6개월 만에 +60% 반등했습니다."),
    ],
    2: [
        ("📊 2023 Q3–Q4 (RRP 급감, 회복 초기)",
         "미국 재무부의 TGA 감소와 RRP가 2.5조 달러에서 급격히 줄어들며 "
         "시장으로 유동성이 유입됐습니다. 이 구간을 포착한 투자자들은 "
         "나스닥 연간 +43% 수익의 상당 부분을 차지했습니다."),
        ("📊 2016 Q1–Q2 (연준 인상 속도 둔화)",
         "연준이 2015년 12월 첫 금리 인상 이후 속도를 조절하며 시장이 안정됐습니다. "
         "S&P500은 2016년 2월 저점에서 +20% 반등했고, "
         "이때 진입한 투자자들은 이후 2018년까지 꾸준한 수익을 올렸습니다."),
        ("📊 2012 Q3 (드라기 무제한 발언)",
         "ECB 드라기 총재의 '유로화를 지키기 위해 무슨 일이든 하겠다' 발언 이후 "
         "유럽 유동성이 회복됐습니다. 글로벌 증시가 6개월 만에 +15~20% 상승했고 "
         "이를 '드라기 바닥'이라고 부릅니다."),
    ],
    3: [
        ("⚠️ 2018 Q2–Q3 (미중 무역전쟁)",
         "유동성은 보통 수준이었지만 무역전쟁 불확실성으로 방향이 불분명했습니다. "
         "이 혼조 구간에서 성급하게 진입한 투자자들은 Q4에 -20% 급락을 그대로 맞았습니다. "
         "'잘 모르겠으면 기다린다'의 중요성을 보여준 사례입니다."),
        ("⚠️ 2014 연간 (QE 테이퍼링 진행)",
         "연준이 양적완화 규모를 단계적으로 줄이는 테이퍼링이 진행됐습니다. "
         "유동성이 줄어드는 전환점에서 변동성이 높아졌고, "
         "방향을 확신하기 어려운 구간이었습니다."),
        ("⚠️ 2024 상반기 (금리 인하 기대 혼재)",
         "연준의 금리 인하 기대와 높은 실질금리가 동시에 존재했습니다. "
         "'3월에 인하한다', '6월에 인하한다' 전망이 번갈아 나오며 "
         "방향을 잡기 어려운 환경이었습니다."),
    ],
    4: [
        ("🔴 2022 전체 (급격한 금리 인상)",
         "연준이 기준금리를 0%에서 4.5%로 급격히 올렸고 M2가 사상 처음으로 마이너스로 전환됐습니다. "
         "나스닥은 1년 만에 -33%, NVDA는 -66%, META는 -76% 하락했습니다. "
         "'좋은 기업이니까 괜찮겠지'라고 버텼던 투자자들이 큰 손실을 봤습니다."),
        ("🔴 2018 Q4 (공격적 금리 인상)",
         "파월 의장이 금리 인상을 강하게 밀어붙이며 유동성이 긴축됐습니다. "
         "나스닥은 3개월 만에 -20% 급락했고, 이후 연준이 인상 중단 신호를 보내며 반등했습니다. "
         "손절 기준을 지킨 투자자들이 더 좋은 자리에서 재진입했습니다."),
        ("🔴 2000 Q1–Q2 (닷컴버블 초기 붕괴)",
         "연준이 닷컴버블을 막기 위해 금리를 올리며 유동성이 회수됐습니다. "
         "처음엔 '잠깐 조정'으로 보였지만 이후 2년에 걸쳐 나스닥이 -80% 폭락했습니다. "
         "유동성 수축 신호를 무시하면 어떤 결과가 나오는지 보여주는 극단적 사례입니다."),
    ],
    5: [
        ("🚨 2008 Q3–Q4 (리먼 브라더스 파산)",
         "리먼 파산 직후 전 세계 신용시장이 완전히 멈췄습니다. "
         "크레딧 스프레드가 22%까지 치솟고 VIX는 80을 넘었습니다. "
         "S&P500은 6개월 만에 -50% 폭락했고 '지금이 바닥'이라 샀던 투자자들이 "
         "추가로 -30~40% 손실을 더 봤습니다. 현금만이 유일한 정답이었습니다."),
        ("🚨 2020 Q1 (코로나 쇼크)",
         "코로나19 팬데믹 선언 직후 VIX가 85까지 치솟고 S&P500이 한 달 만에 -34% 폭락했습니다. "
         "3월 16일 하루에만 -12% 폭락하기도 했습니다. "
         "연준이 3월 23일 무제한 QE를 발표한 이후에야 바닥이 확인됐습니다. "
         "패닉 구간에서 '연준의 확실한 신호' 전까지는 매수 금지가 맞았습니다."),
        ("🚨 2022 Q3 (복합 위기)",
         "금리 인상 + M2 감소 + 크레딧 스프레드 확대가 동시에 발생했습니다. "
         "이 구간에서 좋은 종목을 들고 버텼던 투자자들도 "
         "NVDA -66%, META -76%, AMZN -50% 같은 손실을 피하지 못했습니다. "
         "아무리 좋은 종목도 유동성 위기 환경에서는 예외가 없다는 교훈을 남겼습니다."),
    ],
}

STAGE_CONFIG = {
    5: {
        "title":  "🚀 단계 5 — 유동성 파티 (최적 진입 구간)",
        "color":  "#166534", "bg": "#F0FDF4", "border": "#86EFAC",
        "action": "지금이 분할 매수를 가장 공격적으로 해야 할 타이밍입니다.",
        "body": (
            "지금은 2020년 코로나 이후처럼 <b>돈이 시장으로 쏟아지는 구간</b>입니다.<br><br>"
            "M2가 강하게 증가하고, 연준과 정부의 돈이 동시에 시장으로 흘러들고 있습니다. "
            "금리도 우호적인 수준입니다. 역사적으로 이 조건이 갖춰졌을 때 "
            "나스닥은 평균 60% 이상 상승했습니다.<br><br>"
            "강한 섹터에서 RS 80 이상 종목을 골라 계획한 비중을 채워가세요."
        ),
        "sizing": "투자 예정 금액의 80~100% 투입 가능",
    },
    4: {
        "title":  "🟢 단계 4 — 회복 초기 (선별 진입 구간)",
        "color":  "#15803D", "bg": "#F0FDF4", "border": "#BBF7D0",
        "action": "RS 상위 종목부터 소량씩 분할 매수를 시작하세요.",
        "body": (
            "유동성이 서서히 풀리기 시작했습니다. "
            "2023년 하반기처럼 <b>회복 초기 구간</b>입니다.<br><br>"
            "아직 완전한 확신이 없는 단계이므로 "
            "한 번에 전부 사기보다 RS 80 이상 강한 종목만 골라 "
            "계획 비중의 40~60%를 먼저 진입하세요. "
            "유동성 지표가 더 좋아지면 비중을 늘리면 됩니다."
        ),
        "sizing": "투자 예정 금액의 40~60% 선진입",
    },
    3: {
        "title":  "🟡 단계 3 — 혼조 구간 (신중한 관망)",
        "color":  "#92400E", "bg": "#FFFBEB", "border": "#FDE68A",
        "action": "명확한 신호가 나올 때까지 기다리세요. 서두르지 않아도 됩니다.",
        "body": (
            "지금은 방향이 불분명한 구간입니다. "
            "상승 신호와 하락 신호가 섞여 있어요.<br><br>"
            "2018년 Q2처럼 방향이 불분명할 때 섣불리 투자하면 "
            "이후 Q4 급락을 그대로 맞을 수 있습니다. "
            "<b>'기다리는 것도 투자 전략'</b>입니다.<br><br>"
            "현금 비중을 높이고 유동성 지표가 명확하게 좋아질 때까지 관망하세요."
        ),
        "sizing": "현금 50% 이상 유지, 기존 보유 종목만 관리",
    },
    2: {
        "title":  "🔴 단계 2 — 유동성 수축 (신규 매수 중단)",
        "color":  "#C2410C", "bg": "#FFF7ED", "border": "#FED7AA",
        "action": "신규 매수를 멈추고 기존 포지션 손절 기준을 점검하세요.",
        "body": (
            "2022년 금리 인상기와 비슷한 패턴입니다. "
            "이때 나스닥은 1년 만에 -33%였습니다.<br><br>"
            "M2가 줄어들거나 금리가 급등하며 유동성이 회수되고 있습니다. "
            "<b>좋은 기업도 이 환경에서는 같이 내려갑니다.</b><br><br>"
            "지금은 수익을 내는 것보다 손실을 막는 게 더 중요합니다. "
            "신규 매수 중단, 기존 포지션 손절 기준 점검하세요."
        ),
        "sizing": "신규 매수 금지, 현금 비중 70% 이상으로 확대",
    },
    1: {
        "title":  "🚨 단계 1 — 위기/패닉 (전면 회피)",
        "color":  "#B91C1C", "bg": "#FEF2F2", "border": "#FECACA",
        "action": "현금이 최선입니다. 지금은 아무것도 사면 안 됩니다.",
        "body": (
            "2008년 금융위기, 2020년 코로나 쇼크 초기와 비슷한 패턴입니다. "
            "<b>지금은 현금이 가장 강합니다.</b><br><br>"
            "VIX가 급등하고 크레딧 스프레드가 벌어지고 있습니다. "
            "이때 '지금이 바닥이겠지'라고 생각하는 건 매우 위험합니다. "
            "2008년엔 바닥인 줄 알고 샀다가 추가로 -30~40% 더 하락했습니다.<br><br>"
            "연준이 금리 인하나 유동성 공급을 명확히 발표할 때까지 기다리세요."
        ),
        "sizing": "100% 현금. 바닥 확인 전 절대 매수 금지",
    },
}
def compute_liq_stage(fred_d, liq_pct_val, vix_val, hard_stops_list):
    """유동성 5단계 자동 판정 — V29: 1=위기(최악), 5=최적(최고)"""
    # 1단계 — 위기/패닉 (구 5단계)
    if vix_val and vix_val > 28:
        return 1
    if len(hard_stops_list) >= 3:
        return 1
    cs = fred_d.get("CreditSpread")
    if cs is not None and not cs.empty and float(cs.iloc[-1]) > 5:
        return 1

    # M2 방향
    m2_s = fred_d.get("M2")
    m2_trend = 0
    if m2_s is not None and len(m2_s) >= 13:
        yoy = m2_s.pct_change(12).dropna()
        if len(yoy) >= 3:
            if float(yoy.iloc[-1]) > float(yoy.iloc[-2]) > float(yoy.iloc[-3]):
                m2_trend = 2
            elif float(yoy.iloc[-1]) > float(yoy.iloc[-2]):
                m2_trend = 1
            elif float(yoy.iloc[-1]) < float(yoy.iloc[-2]):
                m2_trend = -1

    # RRP+TGA 방향
    rrp_s = fred_d.get("RRP"); tga_s = fred_d.get("TGA")
    flow_ok = 0
    if rrp_s is not None and len(rrp_s) >= 21:
        if float(rrp_s.iloc[-1]) < float(rrp_s.iloc[-20]): flow_ok += 1
    if tga_s is not None and len(tga_s) >= 21:
        if float(tga_s.iloc[-1]) < float(tga_s.iloc[-20]): flow_ok += 1

    # 2단계 — 유동성 수축 (구 4단계)
    if m2_trend < 0 and liq_pct_val < 0.35:
        return 2
    if m2_trend < 0 and flow_ok == 0:
        return 2

    # 5단계 — 유동성 파티 (구 1단계)
    if m2_trend >= 2 and flow_ok == 2 and liq_pct_val >= 0.70:
        return 5

    # 4단계 — 회복 초기 (구 2단계)
    if m2_trend >= 1 and flow_ok >= 1:
        return 4

    # 3단계 — 혼조
    return 3

INDICATOR_HELP = {
    "AI Score":   ("AI 종합 점수",   "RS·성장·밸류에이션 합산 — 80점 이상이면 강한 종목"),
    "RS Score":   ("주가 상승 힘",   "나스닥(QQQ) 대비 상승 강도 — 80 이상이면 상위 20%"),
    "PEG":        ("성장 대비 가격", "PEG 1 이하 = 저평가  /  3 이상 = 비쌈"),
    "EPS Growth%":("실적 성장률",    "기업 이익이 얼마나 빠르게 느는지 — 높을수록 좋음"),
    "Vol Ratio":  ("거래량 수준",    "1.5배 이상이면 기관이 매수 중일 가능성"),
    "52주 고점%": ("신고가 대비",    "-5% 이내면 신고가 근접  /  -30% 이상이면 하락 구간"),
}

ACTION_GUIDE = {
    "🚀 실적갭업":   {"text":"실적 서프라이즈 갭업 — 강력 진입 신호",
        "sub":"갭업 +5%↑ + 거래량 3배↑ = 기관 대량 매집. 당일 종가 부근 분할 진입",
        "color":"#166534","bg":"#F0FDF4"},
    "💰 1차익절":    {"text":"목표 +15% 달성 — 보유량 50% 매도",
        "sub":"절반 매도로 원금 회수 구간 진입. 나머지 절반은 +25% 목표로 계속 보유",
        "color":"#166534","bg":"#F0FDF4"},
    "💰 2차익절":    {"text":"목표 +25% 달성 — 잔여분 50% 추가 매도",
        "sub":"잔여 25%만 보유하며 추세 추종. MA10 이탈 시 전량 청산",
        "color":"#0F766E","bg":"#F0FDFA"},
    "📉 추적손절":   {"text":"고점 대비 -10% 이탈 — 이익 보호 청산",
        "sub":"상승분을 지키기 위한 청산. 일반 손절과 다르게 수익권에서 발생",
        "color":"#92400E","bg":"#FFFBEB"},
    "⚡ 실적전축소":  {"text":"실적 발표 3일 이내 — 비중 50% 축소 권고",
        "sub":"갭다운 위험 구간. 실적 확인 후 재진입이 더 안전합니다",
        "color":"#7C3AED","bg":"#F5F3FF"},
    "🔁 MA10 회복":  {"text":"MA10 재돌파 — 재진입 검토 구간",
        "sub":"EXIT 후 MA10 위로 복귀. 손절 물량 소화 완료 신호 — 소량 분할 진입 고려",
        "color":"#1D4ED8","bg":"#EFF6FF"},
    "🚀 STRONG BUY": {"text":"지금 분할 매수 가능 구간",
        "sub":"모멘텀 강함 + 거래량 확인 → 3~5회 나눠서 진입 권장",
        "color":"#166534","bg":"#F0FDF4"},
    "🟢 BUY":        {"text":"눌림목에서 매수 고려",
        "sub":"단기 조정이 오면 분할 매수 기회 — 급하게 진입하지 않는다",
        "color":"#166534","bg":"#F0FDF4"},
    "🟡 WATCH":      {"text":"관찰 중 — 아직 진입 조건 미충족",
        "sub":"브레이크아웃(최고가 돌파) 확인 후 진입. 지금은 기다린다",
        "color":"#92400E","bg":"#FFFBEB"},
    "⚠️ EXIT":       {"text":"MA10 이탈 — 보유 중이라면 매도 검토",
        "sub":"단기 추세가 꺾였습니다. 손실이 커지기 전에 대응하세요",
        "color":"#C2410C","bg":"#FFF7ED"},
    "⚪ AVOID":      {"text":"진입 비추천 — 지금은 관망",
        "sub":"시장 대비 약세 종목입니다. 더 강한 종목을 찾으세요",
        "color":"#B91C1C","bg":"#FEF2F2"},
}

REGIME_EXPLAIN = {
    "RISK ON": {
        "emoji":"✅","title":"RISK ON — 투자해도 괜찮은 상황",
        "color":"#166534","bg":"#F0FDF4","border":"#166534",
        "body":(
            "돈이 주식 같은 <b>위험 자산</b>으로 들어가는 환경입니다.<br><br>"
            "💬 사람들의 심리: <b>&quot;지금 투자해도 괜찮아!&quot;</b><br>"
            "📈 주식시장: 올라갈 가능성 ↑<br><br>"
            "특징<br>"
            "· 주식 상승 / 성장주 인기<br>"
            "· 돈이 시장으로 들어오는 중<br>"
            "· VIX(공포지수) 낮음 — 투자자들이 불안해하지 않는 상태<br>"
            "· VIX <b>20~28 구간</b>은 오히려 저가 매수 기회일 수 있습니다<br>"
            "  단, 매출·EPS 성장이 유지될 때만 해당됩니다<br><br>"
            "👉 <b>이 상황에서 강한 종목을 골라 분할 매수합니다</b>"
        ),
    },
    "NEUTRAL": {
        "emoji":"⚠️","title":"NEUTRAL — 방향을 정하지 못한 상황",
        "color":"#92400E","bg":"#FFFBEB","border":"#92400E",
        "body":(
            "시장이 <b>올라갈지 내려갈지 불분명</b>한 상태입니다.<br><br>"
            "💬 사람들의 심리: <b>&quot;잘 모르겠는데... 좀 더 지켜보자&quot;</b><br>"
            "📊 주식시장: 횡보 / 방향 불명확<br><br>"
            "특징<br>"
            "· 상승 신호와 하락 신호가 섞여 있음<br>"
            "· 섣불리 진입하면 손실 가능성<br>"
            "· 강한 확신이 올 때까지 기다리는 구간<br><br>"
            "👉 <b>신규 매수 자제. RS 상위 종목만 소량 진입 검토</b>"
        ),
    },
    "RISK OFF": {
        "emoji":"🔴","title":"RISK OFF — 위험 자산에서 돈이 빠지는 상황",
        "color":"#B91C1C","bg":"#FEF2F2","border":"#FECACA",
        "body":(
            "돈이 주식에서 빠져나와 <b>현금·채권 같은 안전 자산</b>으로 이동하는 환경입니다.<br><br>"
            "💬 사람들의 심리: <b>&quot;지금은 위험해, 일단 현금으로!&quot;</b><br>"
            "📉 주식시장: 내려갈 가능성 ↑<br><br>"
            "특징<br>"
            "· 주식 하락 / 변동성 급등<br>"
            "· VIX > 28 = 단순한 공포가 아닌 <b>패닉</b> — 이성적 판단이 무너진 상태<br>"
            "· <b>좋은 주식도 같이 폭락합니다</b><br>"
            "· 여기서 사면 더 내려갈 수 있습니다. 반등을 확인한 후 진입하세요<br><br>"
            "👉 <b>신규 매수 금지. 기존 보유 종목도 손절 기준 점검</b>"
        ),
    },
}

SECTOR_TICKERS = {
    "반도체":     ["NVDA","AMD","INTC","QCOM","AMAT","MU","AVGO","TXN","NXPI","ADI","MRVL","LRCX","KLAC","ASML","ON"],
    "AI·클라우드":["MSFT","GOOGL","META","AMZN","NOW","CRM","SNOW","DDOG","MDB","PLTR","AI","PATH","GTLB","CFLT"],
    "바이오":     ["LLY","ABBV","MRK","GILD","BIIB","REGN","VRTX","MRNA","BMY","AMGN","ISRG","DXCM","ALGN"],
    "소비재":     ["AMZN","TSLA","HD","NKE","SBUX","MCD","TGT","LOW","BKNG","CMG","ABNB","UBER","LYFT"],
    "금융":       ["JPM","BAC","MS","GS","WFC","BLK","V","MA","AXP","PYPL","SQ","COIN","HOOD"],
    "에너지":     ["XOM","CVX","COP","EOG","SLB","OXY","PSX","VLO","MPC","HAL","DVN","FANG","PXD"],
    "인프라":     ["CAT","DE","EMR","ETN","ITW","PH","ROK","AME","GWW","FAST","URI","PWR","PRIM"],
}

# QQQ 주요 50종목 (나스닥100 시가총액 상위 + 섹터 대표)
DEFAULT_TICKERS = [
    # 빅테크 / AI (10)
    "NVDA", "MSFT", "META", "AMZN", "GOOGL", "GOOG", "AAPL", "TSLA", "NFLX", "COST",
    # 반도체 (12)
    "AVGO", "AMD", "QCOM", "TXN", "INTC", "AMAT", "MU",
    "NXPI", "ADI", "MRVL", "LRCX", "KLAC",
    # 소프트웨어 / 클라우드 (10)
    "NOW", "ADBE", "CRM", "ORCL", "INTU", "CDNS", "SNPS", "WDAY", "TEAM", "ANSS",
    # 사이버보안 (5)
    "PANW", "CRWD", "FTNT", "ZS", "CYBR",
    # 데이터 / AI 플랫폼 (6)
    "PLTR", "DDOG", "MDB", "SNOW", "HUBS", "GTLB",
    # 헬스케어 / 바이오 (7)
    "ISRG", "DXCM", "IDXX", "GEHC", "MRNA", "REGN", "BIIB",
    # 소비 / 여행 / 스트리밍 (6)
    "BKNG", "ABNB", "LULU", "MELI", "SBUX", "PCAR",
    # 금융 / 핀테크 (5)
    "PYPL", "COIN", "HOOD", "APP", "AXON",
    # 통신 / 미디어 (4)
    "CMCSA", "TMUS", "CHTR", "FAST",
    # 에너지 / 기타 (3)
    "FANG", "CEG", "SMCI",
    # 헤지 자산 (V98: 나스닥 폭락 방어)
    "GLD",   # 금 ETF — 위기 시 반등
    "TLT",   # 장기채 ETF — 금리 하락 시 반등
    # ── 대표 ETF 10개 ───────────────────────────────────
    "QQQ",   # 나스닥100       — 벤치마크 (RS 기준 지수)
    "SPY",   # S&P500          — 시장 전체 대표 지수
    "IWM",   # 러셀2000        — 소형주 경기 선행 지표
    "SMH",   # 반도체 섹터     — NVDA·AVGO·AMD 집약
    "XLK",   # 기술 섹터       — S&P500 기술주 바스켓
    "XLV",   # 헬스케어 섹터   — 방어·성장 혼합
    "XLE",   # 에너지 섹터     — 원유·가스 대표
    "TQQQ",  # 나스닥100 3배   — 단기 모멘텀 확인용
    "ARKK",  # AI·혁신 성장주  — 고위험 성장 바스켓
    "SQQQ",  # 나스닥 인버스3배 — 하락장 헤지 시그널
    # ── 고배당주 15개 ────────────────────────────────────
    # ※ RS는 QQQ 대비 낮게 나오는 게 정상 — 배당%·추세로 판단
    "JNJ",   # 존슨앤존슨      배당 ~3.2%  배당왕 63년   헬스케어
    "KO",    # 코카콜라        배당 ~3.1%  배당왕 62년   소비재
    "PG",    # P&G             배당 ~2.4%  배당왕 68년   생활용품
    "MCD",   # 맥도날드        배당 ~2.3%  배당귀족 48년 소비재
    "VZ",    # 버라이즌        배당 ~6.5%  통신 고배당
    "T",     # AT&T            배당 ~5.8%  통신 고배당
    "PFE",   # 화이자          배당 ~6.8%  헬스케어 고배당
    "MO",    # 알트리아        배당 ~8.5%  담배 초고배당
    "ABBV",  # 애브비          배당 ~4.5%  바이오 고배당 (휴미라)
    "CVX",   # 쉐브론          배당 ~4.2%  에너지 메이저
    "XOM",   # 엑슨모빌        배당 ~3.5%  에너지 세계 1위
    "PM",    # 필립모리스      배당 ~5.5%  글로벌 담배
    "O",     # 리얼티인컴      배당 ~5.5%  월배당 REIT 대표
    "IBM",   # IBM             배당 ~3.5%  기술 고배당 전환
    "MMM",   # 쓰리엠(3M)      배당 ~5.5%  배당왕 65년  산업재
    # ── 배당성장주 15개 ──────────────────────────────────
    # ※ 배당 증가 + 주가 성장 병행 — 장기 복리 전략
    "V",     # 비자            배당 ~0.8%  성장 15년+  결제 네트워크
    "MA",    # 마스터카드      배당 ~0.6%  성장 13년+  결제 인프라
    "JPM",   # JP모건          배당 ~2.3%  성장        금융 대장주
    "HD",    # 홈디포          배당 ~2.4%  귀족 14년   소비·인프라
    "UNH",   # 유나이티드헬스  배당 ~1.5%  성장        헬스케어 1위
    "NEE",   # 넥스트에라에너지 배당 ~2.8%  성장 29년   신재생에너지
    "LMT",   # 록히드마틴      배당 ~2.5%  성장 21년   방산 1위
    "LOW",   # 로우스          배당 ~2.0%  귀족 41년   홈개선 2위
    "BLK",   # 블랙록          배당 ~2.5%  성장 14년   자산운용 1위
    "SPGI",  # S&P글로벌       배당 ~1.0%  성장 51년   신용평가
    "TGT",   # 타겟            배당 ~3.5%  귀족 55년   유통·소매
    "APD",   # 에어프로덕츠    배당 ~2.8%  왕  42년   산업가스
    "SCHD",  # Schwab 배당성장 ETF — 배당성장주 바스켓 대표
    "VYM",   # Vanguard 고배당 ETF — 광범위 분산 ~3%
    "DGRO",  # iShares 배당성장 ETF — 배당성장 지수 추종
]  # 총 112개 — 나스닥100(70) + 헤지(2) + ETF(10) + 고배당(15) + 배당성장(15) (V106)

FRED_META = {
    "M2":           ("M2SL",         "M2 통화량",       "B$", 30),
    "RRP":          ("RRPONTSYD",    "역레포 RRP",       "B$", 60),
    "TGA":          ("WDTGAL",       "재무부 TGA",       "B$", 60),  # V68: WTREGEN→WDTGAL(일별)
    "Reserves":     ("WRESBAL",      "은행 준비금",      "B$", 60),
    "RealRate":     ("DFII10",       "실질금리 10Y",     "%",  60),
    "CreditSpread": ("BAMLH0A0HYM2", "크레딧 스프레드",  "%",  60),
    "FedFunds":     ("FEDFUNDS",     "기준금리",         "%",  60),  # V68: 신규 추가
}


# ─────────────────────────────────────────────────────────
# CONFIG 보안 저장 시스템 (V32)
# 저장 우선순위: keyring(OS 키체인) > secrets.toml > config.json > 빈값
# ─────────────────────────────────────────────────────────
_APP_NAME    = "quantum_institutional_os"
_CONFIG_PATH = Path(__file__).parent / "config.json"
_TRADES_PATH = Path(__file__).parent / "trades.json"

def _trades_load() -> list:
    """거래 기록 로드 — V100: 분할매수(lots) 구조 지원"""
    try:
        if _TRADES_PATH.exists():
            data = json.loads(_TRADES_PATH.read_text(encoding="utf-8"))
            trades = data.get("trades", [])
            # V100 마이그레이션: 구버전 단일 buy_price → lots 변환
            migrated = []
            for t in trades:
                if "lots" not in t and t.get("buy_price", 0) > 0:
                    t["lots"] = [{"date": t.get("buy_date",""), "qty": t.get("qty", 0),
                                  "price": t.get("buy_price", 0)}]
                migrated.append(t)
            return migrated
    except Exception:
        pass
    return []

def _trades_save(trades: list) -> bool:
    try:
        _TRADES_PATH.write_text(
            json.dumps({"trades": trades,
                        "updated": datetime.now().isoformat()},
                       ensure_ascii=False, indent=2),
            encoding="utf-8")
        return True
    except Exception:
        return False

def _ticker_badge_color(ticker: str) -> str:
    """티커별 배지 색상 — Google Finance 스타일"""
    colors = ["#1A73E8","#0F9D58","#DB4437","#F4B400","#7B1FA2",
              "#0097A7","#E64A19","#388E3C","#1565C0","#AD1457"]
    return colors[sum(ord(c) for c in ticker) % len(colors)]

def _kr_get(key: str) -> str:
    if not _KEYRING_OK: return ""
    try:
        val = keyring.get_password(_APP_NAME, key)
        return val or ""
    except Exception:
        return ""

def _kr_set(key: str, value: str) -> bool:
    if not _KEYRING_OK: return False
    try:
        if value:
            keyring.set_password(_APP_NAME, key, value)
        else:
            try: keyring.delete_password(_APP_NAME, key)
            except Exception: pass
        return True
    except Exception:
        return False

def _kr_delete(key: str):
    if not _KEYRING_OK: return
    try: keyring.delete_password(_APP_NAME, key)
    except Exception: pass

def _cfg_load() -> dict:
    try:
        if _CONFIG_PATH.exists():
            return json.loads(_CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}

def _cfg_save(data: dict) -> bool:
    try:
        _CONFIG_PATH.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        return True
    except Exception:
        return False

def _get_saved(key: str) -> str:
    """우선순위: keyring > secrets.toml > config.json"""
    val = _kr_get(key)
    if val: return val
    try:
        val = st.secrets.get(key, "")
        if val: return val
    except Exception:
        pass
    return _cfg_load().get(key, "")

def _save_all(fred: str, bot: str, chat: str):
    """저장. 반환: (성공여부, 메시지)"""
    if _KEYRING_OK:
        ok = all([_kr_set("FRED_API_KEY", fred),
                  _kr_set("BOT_TOKEN",    bot),
                  _kr_set("CHAT_ID",      chat)])
        if ok:
            return True, "🔐 OS 키체인에 안전하게 저장됐습니다."
    ok = _cfg_save({"FRED_API_KEY": fred, "BOT_TOKEN": bot, "CHAT_ID": chat})
    if ok:
        msg = "💾 config.json에 저장됐습니다."
        if _KEYRING_OK: msg += " (키체인 실패 — 평문 저장)"
        else: msg += " (keyring 미설치 — pip install keyring 권장)"
        return True, msg
    return False, "❌ 저장 실패 — 폴더 권한을 확인하세요."

def _delete_all():
    """삭제. 반환: (성공여부, 메시지)"""
    if _KEYRING_OK:
        for k in ("FRED_API_KEY", "BOT_TOKEN", "CHAT_ID"):
            _kr_delete(k)
    try:
        if _CONFIG_PATH.exists(): _CONFIG_PATH.unlink()
    except Exception as e:
        return False, f"❌ 삭제 실패: {e}"
    return True, "🗑️ 저장된 키가 모두 삭제됐습니다."


# ─────────────────────────────────────────────────────────
# SIDEBAR — 설정
# ─────────────────────────────────────────────────────────
sb = st.sidebar

# API 키 로드 (화면 표시 없이 선처리)
_saved_fred = _get_saved("FRED_API_KEY")
_saved_bot  = _get_saved("BOT_TOKEN")
_saved_chat = _get_saved("CHAT_ID")
_kr_has_key  = bool(_KEYRING_OK and _kr_get("FRED_API_KEY"))
_cfg_has_key = bool(_cfg_load().get("FRED_API_KEY",""))
_secrets_ok  = False
try: _secrets_ok = bool(st.secrets.get("FRED_API_KEY",""))
except Exception: pass
FRED_API_KEY = _saved_fred
BOT_TOKEN    = _saved_bot
CHAT_ID      = _saved_chat

# 초기 변수
INVEST_AMOUNT_만원 = 5000.0
INVEST_AMOUNT_원   = INVEST_AMOUNT_만원 * 10000
INVEST_SCALE       = "S"
TICKERS = DEFAULT_TICKERS.copy()
selected_sectors = set()

# ── 앱 타이틀 ─────────────────────────────────────────
sb.markdown(
    "<div style='font-family:Space Mono,monospace;font-size:13px;font-weight:600;"
    "color:#3B5BA5;letter-spacing:1px;padding:6px 0 1px'>"
    "QUANTUM INSTITUTIONAL OS</div>"
    "<div style='font-size:10px;color:#9CA3AF;margin-bottom:2px'>V111 &nbsp;·&nbsp; 💻 PC VERSION</div>"
    "<div style='font-size:10px;color:#9CA3AF;margin-bottom:8px'>"
    "나스닥 중심 투자 스크리너</div>",
    unsafe_allow_html=True)
sb.markdown("<hr style='border-color:#E2E6ED;margin:6px 0'>", unsafe_allow_html=True)

# ── ① 유동성 단계 (placeholder — 데이터 로드 후 채워짐) ──
sb.markdown("<div style='font-size:9px;font-weight:500;color:#9CA3AF;"
            "letter-spacing:1px;margin-bottom:4px'>유동성 현황</div>",
            unsafe_allow_html=True)
liq_stage_placeholder = sb.empty()
liq_stage_placeholder.markdown(
    "<div style='font-size:10px;color:#9CA3AF;padding:4px'>로드 중...</div>",
    unsafe_allow_html=True)

sb.markdown("<hr style='border-color:#E2E6ED;margin:6px 0'>", unsafe_allow_html=True)

# ── ② 시장 지표 (placeholder) ─────────────────────────
sb.markdown("<div style='font-size:9px;font-weight:500;color:#9CA3AF;"
            "letter-spacing:1px;margin-bottom:4px'>미국 시장</div>",
            unsafe_allow_html=True)
mkt_panel_placeholder = sb.empty()
mkt_panel_placeholder.markdown(
    "<div style='font-size:10px;color:#9CA3AF;padding:4px'>로드 중...</div>",
    unsafe_allow_html=True)

sb.markdown("<hr style='border-color:#E2E6ED;margin:6px 0'>", unsafe_allow_html=True)

# ── ③ 국채금리 3종 (placeholder) ─────────────────────
sb.markdown("<div style='font-size:9px;font-weight:500;color:#9CA3AF;"
            "letter-spacing:1px;margin-bottom:4px'>미국 국채금리</div>",
            unsafe_allow_html=True)
yield_placeholder = sb.empty()
yield_placeholder.markdown(
    "<div style='font-size:10px;color:#9CA3AF;padding:4px'>로드 중...</div>",
    unsafe_allow_html=True)

sb.markdown("<hr style='border-color:#E2E6ED;margin:6px 0'>", unsafe_allow_html=True)

# ── ④ 한국 시장 (placeholder) ────────────────────────
sb.markdown("<div style='font-size:9px;font-weight:500;color:#9CA3AF;"
            "letter-spacing:1px;margin-bottom:4px'>한국 시장</div>",
            unsafe_allow_html=True)
kr_panel_placeholder = sb.empty()
kr_panel_placeholder.markdown(
    "<div style='font-size:10px;color:#9CA3AF;padding:4px'>로드 중...</div>",
    unsafe_allow_html=True)

sb.markdown("<hr style='border-color:#E2E6ED;margin:6px 0'>", unsafe_allow_html=True)

# ── 글로벌 자산 placeholder ────────────────────────────
sb.markdown("<div style='font-size:9px;font-weight:500;color:#9CA3AF;"
            "letter-spacing:1px;margin-bottom:4px'>글로벌 자산</div>",
            unsafe_allow_html=True)
asset_panel_placeholder = sb.empty()
asset_panel_placeholder.markdown(
    "<div style='font-size:10px;color:#9CA3AF;padding:4px'>로드 중...</div>",
    unsafe_allow_html=True)

sb.markdown("<hr style='border-color:#E2E6ED;margin:6px 0'>", unsafe_allow_html=True)

# ── 국제 지수 placeholder ──────────────────────────────
sb.markdown("<div style='font-size:9px;font-weight:500;color:#9CA3AF;"
            "letter-spacing:1px;margin-bottom:4px'>국제 지수</div>",
            unsafe_allow_html=True)
global_panel_placeholder = sb.empty()
global_panel_placeholder.markdown(
    "<div style='font-size:10px;color:#9CA3AF;padding:4px'>로드 중...</div>",
    unsafe_allow_html=True)

sb.markdown("<hr style='border-color:#E2E6ED;margin:6px 0'>", unsafe_allow_html=True)

# ── ⑤ DATA STATUS (소형) ─────────────────────────────
sb.markdown("<div style='font-size:9px;font-weight:500;color:#9CA3AF;"
            "letter-spacing:1px;margin-bottom:4px'>데이터 상태</div>",
            unsafe_allow_html=True)
status_placeholder = sb.empty()
status_placeholder.markdown(
    "<div style='font-size:10px;color:#9CA3AF;padding:4px'>데이터 로드 중...</div>",
    unsafe_allow_html=True)

sb.markdown("<hr style='border-color:#E2E6ED;margin:6px 0'>", unsafe_allow_html=True)



# ─────────────────────────────────────────────────────────

# ── ✏️ 문구 편집 모드 ────────────────────────────────────
if "edit_mode" not in st.session_state:
    st.session_state["edit_mode"] = False
if sb.button(
    "✏️ 문구 편집 ON" if not st.session_state["edit_mode"] else "✅ 문구 편집 중 (클릭해서 닫기)",
    use_container_width=True, key="toggle_edit_mode"
):
    st.session_state["edit_mode"] = not st.session_state["edit_mode"]
    st.rerun()
if st.session_state["edit_mode"]:
    sb.markdown(
        "<div style='font-size:10px;color:#D97706;background:#FFFBEB;"
        "border-radius:4px;padding:4px 8px;margin-top:2px'>"
        "유동성 탭에서 각 지표 설명을 직접 수정할 수 있습니다</div>",
        unsafe_allow_html=True)

# TITLE
# ─────────────────────────────────────────────────────────
APP_VERSION = "V111"
st.markdown(f"""
<div style="padding:16px 0 10px 0;border-bottom:1px solid #E2E6ED;margin-bottom:4px">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px">
    <div>
      <span style="font-family:'Space Mono',monospace;font-size:20px;
            color:#3B5BA5;letter-spacing:3px;font-weight:700">
        QUANTUM INSTITUTIONAL OS
      </span><br>
      <span style="font-size:11px;color:#6B7280;letter-spacing:2px">
        V111  |  유동성 → 시장 → 주식  |  데이터 → 해석 → 행동
      </span><br>
      <span style="font-size:11px;color:#9CA3AF;margin-top:4px;display:inline-block;
            border-left:3px solid #3B5BA5;padding-left:8px;line-height:1.6">
        초보 투자자가 기관처럼 판단하도록 돕는 투자 학습 도구입니다.<br>
        숫자보다 <b style="color:#374151">해석</b>,
        해석보다 <b style="color:#374151">행동 지침</b>을 제공합니다.
        투자 결과의 책임은 전적으로 본인에게 있습니다.
      </span>
    </div>
    <div style="text-align:right">
      <span style="font-family:'Space Mono',monospace;font-size:11px;
            color:#2A4A68;letter-spacing:1px">APP {APP_VERSION}</span><br>
      <span style="font-size:10px;color:#2A4A68">{datetime.now().strftime('%Y-%m-%d %H:%M')}</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)





# ─────────────────────────────────────────────────────────
# 공유 데이터 로드
# ─────────────────────────────────────────────────────────
@st.cache_data(ttl=600, show_spinner=False)
def load_fred_all(api_key, _bust=0):
    if is_placeholder(api_key): return {}
    result = {}
    for key, (sid, _, _, limit) in FRED_META.items():
        s = get_fred(sid, api_key, limit=limit)
        if s is not None: result[key] = s
    return result

@st.cache_data(ttl=1800, show_spinner=False)
def load_sp500_pe(_bust=0):
    """S&P 500 PE Ratio — 3단계 fallback
    1차: multpl.com 스크래핑 (역사적 데이터)
    2차: yfinance ^GSPC trailingPE (현재값만)
    3차: 추정값 반환 (최근 CAPE 수준 기반)
    """
    # ── 1차: multpl.com ──────────────────────────────────────
    try:
        url = "https://www.multpl.com/s-p-500-pe-ratio/table/by-year"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        resp = requests.get(url, timeout=12, headers=headers)
        if resp.status_code == 200:
            tables = pd.read_html(resp.text)
            if tables:
                df = tables[0]
                df.columns = ["Date", "Value"]
                df = df[~df["Date"].astype(str).str.contains("Estimate", na=False)]
                df["Date"]  = pd.to_datetime(df["Date"], errors="coerce")
                df["Value"] = pd.to_numeric(
                    df["Value"].astype(str).str.replace(r"[^0-9.]", "", regex=True), errors="coerce")
                df = df.dropna().sort_values("Date").reset_index(drop=True)
                if not df.empty:
                    return df
    except Exception:
        pass

    # ── 2차: yfinance ^GSPC trailingPE ───────────────────────
    try:
        import sys, io as _io
        _e = sys.stderr; sys.stderr = _io.StringIO()
        try:
            _tkr = yf.Ticker("^GSPC")
            _info = _tkr.info if hasattr(_tkr, 'info') else {}
        finally:
            sys.stderr = _e
        if isinstance(_info, dict):
            _pe = _info.get("trailingPE") or _info.get("forwardPE")
            if _pe and float(_pe) > 0:
                _today = pd.Timestamp.today().normalize()
                df_single = pd.DataFrame({
                    "Date":  [_today],
                    "Value": [round(float(_pe), 2)]
                })
                return df_single
    except Exception:
        pass

    # ── 3차: 추정값 (역사 평균 기반 플레이스홀더) ────────────
    # 데이터를 가져오지 못해도 최소한 현재 추정값 제공
    # 2024~2025년 S&P500 PER은 약 22~25배 수준
    _today = pd.Timestamp.today().normalize()
    df_est = pd.DataFrame({
        "Date":  [_today],
        "Value": [23.5]   # 2024~2025 추정 중간값
    })
    return df_est

@st.cache_data(ttl=300, show_spinner=False)
def load_market(_bust=0):
    """V93: 글로벌 자산(금/BTC/오일) + 국제지수 추가"""
    res = {}
    for sym, key in [
        # 미국 시장
        ("QQQ","QQQ"), ("SPY","SPY"), ("^VIX","VIX"),
        ("^TNX","TNX"), ("^IRX","IRX"), ("^TYX","TYX"),
        # 글로벌 자산
        ("GC=F","GOLD"),          # 금
        ("BTC-USD","BTC"),        # 비트코인
        ("CL=F","OIL"),           # WTI 원유
        # 국제 지수
        ("^N225","NIKKEI"),       # 일본 닛케이
        ("000001.SS","SHANGHAI"), # 중국 상하이
        ("^HSI","HANGSENG"),      # 홍콩 항셍
        ("^GDAXI","DAX"),         # 독일 DAX
        ("^FTSE","FTSE"),         # 영국 FTSE
        # 한국
        ("^KS11","KOSPI"),
        ("^KQ11","KOSDAQ"),
        ("USDKRW=X","USDKRW"),
    ]:
        try:
            s = get_close(sym, "2y")
            if s is not None and not s.empty: res[key] = s
        except: pass
    return res

@st.cache_data(ttl=300, show_spinner=False)
def load_sectors(_bust=0):
    """섹터 ETF → 강도 0~100점 정량화 (V98)
    RS(QQQ 대비) + 1M수익 + 3M수익 + MA위치 합산"""
    SECTORS = {"반도체":"SOXX","AI·클라우드":"SKYY","바이오":"XBI",
               "소비재":"XLY","금융":"XLF","에너지":"XLE","인프라":"PAVE"}
    qqq_s = get_close("QQQ","6mo")
    res = {}
    for name, etf in SECTORS.items():
        s = get_close(etf, "6mo")
        if s is None or len(s) < 63: continue
        try:
            r1m  = float(s.iloc[-1]/s.iloc[-21]-1)*100 if len(s)>=21 else 0.0
            r3m  = float(s.iloc[-1]/s.iloc[-63]-1)*100 if len(s)>=63 else 0.0
            ma20 = float(s.rolling(20).mean().iloc[-1])
            ma50 = float(s.rolling(50).mean().iloc[-1]) if len(s)>=50 else ma20
            above_ma20 = float(s.iloc[-1]) > ma20
            above_ma50 = float(s.iloc[-1]) > ma50
            # QQQ 대비 초과수익 (RS)
            rs_vs_qqq = 0.0
            if qqq_s is not None and len(qqq_s)>=21:
                _qqq1m = float(qqq_s.iloc[-1]/qqq_s.iloc[-21]-1)*100
                rs_vs_qqq = r1m - _qqq1m
            # 점수 합산 (0~100)
            sc  = 50.0  # 기본
            sc += min(20, max(-20, r1m * 1.5))   # 1M 수익률 ±20점
            sc += min(15, max(-15, r3m * 0.8))   # 3M 수익률 ±15점
            sc += min(10, max(-10, rs_vs_qqq * 2)) # RS ±10점
            sc += 5 if above_ma20 else -5          # MA20 ±5점
            sc += 5 if above_ma50 else -5          # MA50 ±5점 (V98)
            sc  = max(0, min(100, round(sc, 1)))
            res[name] = {
                "etf": etf, "ret_1m": round(r1m,2), "ret_3m": round(r3m,2),
                "rs_vs_qqq": round(rs_vs_qqq,2), "above_ma20": above_ma20,
                "above_ma50": above_ma50, "price": float(s.iloc[-1]),
                "sector_score": sc   # V98: 0~100 정량화
            }
        except: continue
    return res

with st.spinner("📡 FRED 데이터 로드 중..."):
    fred_data   = load_fred_all(FRED_API_KEY, st.session_state.cache_key)

# ── 백분위 계산용 전체 역사 데이터 (2000년~현재) ─────────
# load_fred_all은 limit=30~60 단기 데이터 → 백분위 계산 불가
# 별도로 전체 역사 데이터를 로드함
@st.cache_data(ttl=3600, show_spinner=False)
def load_fred_history(api_key, _bust=0):
    """6개 핵심 지표 전체 역사 데이터 (2000-01-01 ~ 현재)
    백분위 점수 계산 전용 — 탭 로드 전에 전역 범위에서 실행"""
    if is_placeholder(api_key):
        return {}
    HISTORY_SERIES = {
        "FedFunds":     "FEDFUNDS",      # V68: 신규
        "M2":           "M2SL",
        "RRP":          "RRPONTSYD",
        "TGA":          "WDTGAL",        # V68: WTREGEN→WDTGAL
        "Reserves":     "WRESBAL",
        "RealRate":     "DFII10",
        "CreditSpread": "BAMLH0A0HYM2",
    }
    result = {}
    for key, sid in HISTORY_SERIES.items():
        try:
            url = (f"https://api.stlouisfed.org/fred/series/observations"
                   f"?series_id={sid}&api_key={api_key}&file_type=json"
                   f"&sort_order=asc&observation_start=2000-01-01")
            resp = requests.get(url, timeout=20)
            if resp.status_code != 200:
                continue
            obs = resp.json().get("observations", [])
            data = {o["date"]: float(o["value"])
                    for o in obs if o["value"] not in (".", "")}
            s = pd.Series(data)
            s.index = pd.to_datetime(s.index)
            s = s.sort_index()
            if not s.empty:
                result[key] = s
        except Exception:
            pass
    return result

fred_history = load_fred_history(FRED_API_KEY, st.session_state.cache_key)

with st.spinner("📈 시장 데이터 로드 중..."):
    mkt         = load_market(st.session_state.cache_key)
    sector_data = load_sectors(st.session_state.cache_key)
# ─────────────────────────────────────────────────────────
# 종목 데이터 전역 로드 (V34: 탭 진입 전 자동 실행)
# ─────────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def load_stocks(tickers, _bust=0):
    rows=[]; failed=[]; qqq_close=get_close("QQQ","1y")
    for tk in tickers:
        try:
            close=get_close(tk,"1y")
            if close is None or len(close)<30: failed.append(tk); continue
            _e=sys.stderr; sys.stderr=io.StringIO()
            try: raw_dl=yf.download(tk,period="1y",progress=False,auto_adjust=True)
            finally: sys.stderr=_e
            if raw_dl is None or raw_dl.empty: failed.append(tk); continue
            # Volume 컬럼 — MultiIndex(yfinance 1.x) / 단순(구버전) 모두 대응
            try:
                if isinstance(raw_dl.columns, pd.MultiIndex):
                    lvl0 = raw_dl.columns.get_level_values(0)
                    if "Volume" in lvl0:
                        _vol_sub = raw_dl["Volume"]
                        volume = _vol_sub.iloc[:,0].dropna() if isinstance(_vol_sub, pd.DataFrame) else _vol_sub.dropna()
                    else:
                        volume = pd.Series(dtype=float)
                else:
                    volume = raw_dl["Volume"].dropna() if "Volume" in raw_dl.columns else pd.Series(dtype=float)
            except:
                volume = pd.Series(dtype=float)
            price=float(close.iloc[-1])
            w52h=float(close.rolling(min(252,len(close))).max().iloc[-1])
            pct_ath=round((price/w52h-1)*100,1) if w52h>0 else 0.0
            # V85: 52주 신고가 4단계 티어
            if   pct_ath >= -5:   ath_tier = "🔥 신고가근접"
            elif pct_ath >= -10:  ath_tier = "✅ 근접"
            elif pct_ath >= -20:  ath_tier = "🟡 관찰"
            else:                 ath_tier = "⚪ 원거리"
            rs_vals={"rs_1m":0.0,"rs_3m":0.0,"rs_6m":0.0,"rs_12m":0.0}
            if qqq_close is not None:
                comb=pd.concat({"s":close,"q":qqq_close},axis=1).dropna()
                if len(comb)>=30:
                    sc_s=comb["s"]; qc_s=comb["q"]
                    for days,vk in [(21,"rs_1m"),(63,"rs_3m"),(126,"rs_6m"),(252,"rs_12m")]:
                        if len(sc_s)>days:
                            sr=float(sc_s.iloc[-1]/sc_s.iloc[-days]-1)
                            qr=float(qc_s.iloc[-1]/qc_s.iloc[-days]-1)
                            rs_vals[vk]=round((sr-qr)*100,2)
            # V98: RS 가중치 단기 강화 (1M:0.25 3M:0.30 6M:0.25 12M:0.20)
            rs_raw=rs_vals["rs_1m"]*0.25+rs_vals["rs_3m"]*0.30+rs_vals["rs_6m"]*0.25+rs_vals["rs_12m"]*0.20
            breakout=vol_surge=consecutive_rise=False
            if len(close)>=27:
                # ── 브레이크아웃: 최근 5일 내 고점이 이전 20일 고점 돌파 (V94)
                _recent_high  = float(close.tail(5).max())
                _prior_high20 = float(close.iloc[-27:-5].max())
                breakout = _recent_high > _prior_high20
            elif len(close)>=22:
                breakout = float(close.iloc[-1]) > float(close.iloc[-22:-1].max())
            if len(volume)>=21:
                avg_vol=float(volume.tail(20).mean())
                # ── 거래량 급증: 최근 5일 내 1회 이상 1.5배 초과 (V94)
                vol_surge=bool((volume.tail(5)>avg_vol*1.5).any()) if avg_vol>0 else False
            # ── 3일 연속 소폭 상승: 3일 모두 양봉 + 각 일 0~5% + 거래량 평균 이상 (V96)
            if len(close)>=4:
                try:
                    _c_gains=[(float(close.iloc[-i])/float(close.iloc[-i-1])-1) for i in range(1,4)]
                    _vol_ok_3c = True
                    if len(volume)>=21:
                        _avg_v3 = float(volume.tail(20).mean())
                        _vol_3d = float(volume.tail(3).mean())
                        _vol_ok_3c = (_avg_v3 > 0) and (_vol_3d >= _avg_v3 * 0.8)
                    consecutive_rise = all(0<g<0.05 for g in _c_gains) and _vol_ok_3c
                except: consecutive_rise=False
            # ── 일평균 거래량 필터: 100만주 미만 제외 (V97)
            if len(volume) >= 20:
                _avg_vol_filter = float(volume.tail(20).mean())
                if _avg_vol_filter < 1_000_000:
                    failed.append(tk); continue
            # ── EXIT 신호: MA10 이탈 2일 연속 확인 (V97 — 횡보 손절 반복 방지)
            exit_signal = False
            ma10_recovery = False
            if len(close) >= 13:
                _ma10 = close.rolling(10).mean()
                _ma10_t  = float(_ma10.iloc[-1])
                _ma10_y  = float(_ma10.iloc[-2])
                _ma10_y2 = float(_ma10.iloc[-3])
                _c_t  = float(close.iloc[-1])
                _c_y  = float(close.iloc[-2])
                _c_y2 = float(close.iloc[-3])
                # 2일 연속 이탈 확인
                exit_signal   = (_c_t < _ma10_t) and (_c_y < _ma10_y)
                ma10_recovery = (_c_y < _ma10_y) and (_c_t > _ma10_t)
            elif len(close) >= 12:
                _ma10 = close.rolling(10).mean()
                _ma10_t = float(_ma10.iloc[-1]); _ma10_y = float(_ma10.iloc[-2])
                _c_t = float(close.iloc[-1]);    _c_y  = float(close.iloc[-2])
                exit_signal   = (_c_t < _ma10_t) and (_c_y < _ma10_y)
                ma10_recovery = (_c_y < _ma10_y) and (_c_t > _ma10_t)
            elif len(close) >= 11:
                exit_signal = float(close.iloc[-1]) < float(close.rolling(10).mean().iloc[-1])
            # ── 추적 손절: 20일 고점 대비 -10% 이탈 (V97)
            trailing_stop = False
            if len(close) >= 21:
                _roll_high = float(close.tail(20).max())
                trailing_stop = float(close.iloc[-1]) < _roll_high * 0.90
            # ── 단계별 익절 계산 (20일/60일 수익률 기반)
            profit_stage = 0
            profit_ret   = 0.0
            if len(close) >= 21:
                _ret_20d = float(close.iloc[-1] / close.iloc[-21] - 1)
                if _ret_20d >= 0.25:   profit_stage = 2; profit_ret = _ret_20d
                elif _ret_20d >= 0.15: profit_stage = 1; profit_ret = _ret_20d
            # ── 실적 서프라이즈 갭업: 당일 +5%↑ + 거래량 3배↑ (V98)
            earnings_gap_up = False
            if len(close) >= 3 and len(volume) >= 21:
                try:
                    _gap = float(close.iloc[-1]) / float(close.iloc[-2]) - 1
                    _avg_v_gap = float(volume.tail(20).mean())
                    _vol_today = float(volume.iloc[-1])
                    earnings_gap_up = (_gap >= 0.05) and (_avg_v_gap > 0) and (_vol_today >= _avg_v_gap * 3)
                except: earnings_gap_up = False
            # ── ATR(14) 기반 동적 손절 가격 계산 (V96)
            atr_val = None
            atr_stop = None
            try:
                if len(close)>=16:
                    _raw_full = raw_dl
                    if isinstance(_raw_full.columns, pd.MultiIndex):
                        _hi = _raw_full["High"].iloc[:,0]
                        _lo = _raw_full["Low"].iloc[:,0]
                    else:
                        _hi = _raw_full["High"] if "High" in _raw_full.columns else close
                        _lo = _raw_full["Low"]  if "Low"  in _raw_full.columns else close
                    _hi = _hi.squeeze().dropna()
                    _lo = _lo.squeeze().dropna()
                    _cl_prev = close.shift(1)
                    _tr = pd.concat([
                        _hi - _lo,
                        (_hi - _cl_prev).abs(),
                        (_lo - _cl_prev).abs()
                    ], axis=1).max(axis=1).dropna()
                    if len(_tr) >= 14:
                        atr_val  = round(float(_tr.rolling(14).mean().iloc[-1]), 2)
                        atr_stop = round(float(close.iloc[-1]) - atr_val * 2, 2)
            except: atr_val = None; atr_stop = None
            # ── RSI(14) 계산 (V84) ──────────────────────────
            rsi_val = None
            try:
                if len(close) >= 15:
                    _delta = close.diff().dropna()
                    _gain  = _delta.clip(lower=0).rolling(14).mean()
                    _loss  = (-_delta.clip(upper=0)).rolling(14).mean()
                    _rs    = _gain / _loss.replace(0, float('inf'))
                    _rsi_s = 100 - (100 / (1 + _rs))
                    rsi_val = round(float(_rsi_s.iloc[-1]), 1)
            except: rsi_val = None
            try:
                _e=sys.stderr; sys.stderr=io.StringIO()
                try:
                    _tkr = yf.Ticker(tk)
                    info = _tkr.info if hasattr(_tkr, 'info') else {}
                    if not isinstance(info, dict): info = {}
                except:
                    info = {}
                finally: sys.stderr=_e
            except: info={}
            peg=safe(info.get("pegRatio")); eps=safe(info.get("earningsGrowth"))*100
            rev=safe(info.get("revenueGrowth"))*100; roe=safe(info.get("returnOnEquity"))*100
            eveb=safe(info.get("enterpriseToEbitda")); ps=safe(info.get("priceToSalesTrailing12Months"))
            # ── 배당수익률: 실제 배당 지급 내역 기반 계산 (코딩 원칙 1조) ──
            # 방법: 최근 1년 실제 배당금 합계 / 현재가 × 100
            # 데이터 없으면 None 표시 (추정값·하드코딩 사용 금지)
            div_yield = None
            try:
                _div_hist = _tkr.dividends
                if _div_hist is not None and len(_div_hist) > 0:
                    _cutoff = pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=365)
                    _ttm = _div_hist[_div_hist.index >= _cutoff]
                    if len(_ttm) > 0 and price > 0:
                        div_yield = round(float(_ttm.sum()) / price * 100, 2)
            except Exception:
                div_yield = None  # 수집 실패 → None (고지: 표에서 N/A 표시)
            peg_lbl=("N/A" if peg<=0 else ("우수" if peg<1 else ("양호" if peg<=2 else ("보통" if peg<=3 else "고평가"))))
            val_sc=0.0
            if peg>0: val_sc+=min(40,(1/peg)*20)
            if eveb>0: val_sc+=max(0,20-eveb)
            if ps>0:   val_sc+=max(0,15-ps)
            if roe>=20: val_sc+=5.0   # ROE 20%↑ 보너스 (V96)
            val_sc=min(45,val_sc)     # 상한 40→45 (ROE 보너스 반영)
            avg_v=float(volume.tail(20).mean()) if len(volume)>=21 else 1.0
            vol_ratio=float(volume.iloc[-1])/avg_v if avg_v>0 else 1.0
            _liq_pct_safe = liq_pct if 'liq_pct' in dir() and isinstance(liq_pct, (int,float)) else 0.5
            # V96: 거래량 가중치 0.10→0.15 / EPS 0.20→0.15
            ai=round(max(0,min(100,
                max(rs_raw,0)*0.30 +
                max(eps,0)*0.15 +
                max(rev,0)*0.15 +
                val_sc*0.15 +
                (vol_ratio*5)*0.15 +
                (_liq_pct_safe*50)*0.10
            )),1)
            _rsi_overbought = rsi_val is not None and rsi_val >= 70
            _rsi_ok         = rsi_val is None or rsi_val < 70
            _entry_ok       = breakout or consecutive_rise

            # ── V98 신호 우선순위 ─────────────────────────────
            # 1순위: 익절
            if profit_stage == 2:
                signal = "💰 2차익절"
            elif profit_stage == 1:
                signal = "💰 1차익절"
            # 2순위: 추적 손절
            elif trailing_stop and not exit_signal:
                signal = "📉 추적손절"
            # 3순위: MA10 재돌파
            elif ma10_recovery and rs_raw > 0 and not _rsi_overbought:
                signal = "🔁 MA10 회복"
            # 4순위: EXIT
            elif exit_signal:
                signal = "⚠️ EXIT"
            # 5순위: 실적 갭업 (V98)
            elif earnings_gap_up and _rsi_ok:
                signal = "🚀 실적갭업"
            # 6순위: 실적 발표 임박
            elif earnings_warn:
                signal = "⚡ 실적전축소"
            # 7순위: 일반 진입 신호
            elif _rsi_overbought and _entry_ok:
                signal = "🔥 과열주의"
            elif ai>=80 and breakout and vol_surge and _rsi_ok:
                signal = "🚀 STRONG BUY"
            elif ai>=70 and breakout and _rsi_ok:
                signal = "🟢 BUY"
            elif ai>=65 and consecutive_rise and _rsi_ok:
                signal = "📈 꾸준상승"
            elif ai>=55:
                signal = "🟡 WATCH"
            else:
                signal = "⚪ AVOID"
            # ── 실적 발표일 (V24 신규) ──────────────────
            earnings_warn = False
            earnings_date_str = "N/A"
            try:
                cal = yf.Ticker(tk).calendar
                # yfinance calendar 반환 형식: dict or DataFrame
                if isinstance(cal, dict) and cal:
                    ed = cal.get("Earnings Date") or cal.get("earningsDate")
                    if ed is not None:
                        if hasattr(ed, '__iter__') and not isinstance(ed, str):
                            ed = list(ed)[0]
                        ed_ts = pd.Timestamp(ed)
                        days_until = (ed_ts - pd.Timestamp.now()).days
                        if 0 <= days_until <= 3:
                            earnings_warn = True
                            earnings_date_str = ed_ts.strftime('%m/%d')
                        elif days_until > 0:
                            earnings_date_str = ed_ts.strftime('%m/%d')
                elif hasattr(cal, 'columns'):
                    # DataFrame 형태
                    if 'Earnings Date' in cal.columns:
                        ed_val = cal['Earnings Date'].iloc[0]
                        ed_ts = pd.Timestamp(ed_val)
                        days_until = (ed_ts - pd.Timestamp.now()).days
                        if 0 <= days_until <= 3:
                            earnings_warn = True
                            earnings_date_str = ed_ts.strftime('%m/%d')
                        elif days_until > 0:
                            earnings_date_str = ed_ts.strftime('%m/%d')
            except Exception:
                pass
            rows.append({"Ticker":tk,"Price":round(price,2),"AI Score":ai,
                "52주 고점%":pct_ath,"신고가단계":ath_tier,"RS Raw":round(rs_raw,2),
                "PEG":round(peg,2) if peg>0 else None,"PEG 판정":peg_lbl,
                "EPS Growth%":round(eps,1),"Rev Growth%":round(rev,1),"ROE%":round(roe,1),
                "배당수익률%":div_yield,  # None = 데이터 없음(N/A 표시), 코딩원칙 2조
                "Vol Ratio":round(vol_ratio,2),
                "RSI":rsi_val,
                "ATR":atr_val,"ATR손절":atr_stop,
                "수익률20d":round(profit_ret*100,1),
                "익절단계":profit_stage,
                "평균매수가":round(_avg_bp, 2) if '_avg_bp' in dir() and _avg_bp > 0 else 0,
                "추적손절":"✅" if trailing_stop else "—",
                "Breakout":"✅" if breakout else "—","Vol Surge":"✅" if vol_surge else "—",
                "3연상":"✅" if consecutive_rise else "—",
                "MA10회복":"✅" if ma10_recovery else "—",
                "갭업":"✅" if earnings_gap_up else "—",
                "Exit Signal":"⚠️" if exit_signal else "—","Signal":signal,
                "실적예정":earnings_date_str,"실적경고":"⚠️" if earnings_warn else "—"})
        except: failed.append(tk)
    df=pd.DataFrame(rows)
    if df.empty: return df,df,failed
    df["RS Score"]=df["RS Raw"].rank(pct=True).mul(100).round(0).astype(int)
    df["RS Rank"]=df["RS Raw"].rank(ascending=False).astype(int)
    df=df.sort_values("AI Score",ascending=False).reset_index(drop=True); df.index=df.index+1
    port=df[(df["RS Score"]>=80)&(
        (df["Breakout"]=="✅")|(df.get("3연상","—")=="✅")|(df.get("MA10회복","—")=="✅")
    )&(df["Exit Signal"]=="—")&(df["PEG"].fillna(2.9)<3.0)].head(5).copy()
    if not port.empty:
        total=port["AI Score"].sum()
        port["비중%"]=(port["AI Score"]/total*100).clip(upper=30)
        port["비중%"]=(port["비중%"]/port["비중%"].sum()*100).round(1)
    return df,port,failed

# ── 전역 종목 데이터 로드 ────────────────────────────────
# V54 BUG FIX: liq_pct는 load_stocks 호출 이후 계산되므로
# 첫 실행 시 NameError → 모든 종목 failed 처리 버그 수정
# load_stocks 호출 전 기본값 0.5 설정 (나중에 실제값으로 덮어씀)
if 'liq_pct' not in vars():
    liq_pct = 0.5

# ── df_all 로딩 전략 ──────────────────────────────────────
# 최초 1회 또는 새로고침 시에만 yfinance 호출
# 체크박스/탭 전환은 session_state 캐시에서 즉시 읽음
_ck = st.session_state.cache_key
_ss_key = f"df_all_v{_ck}"   # 새로고침 시 키 변경 → 강제 재로딩

df_all         = pd.DataFrame()
df_port        = pd.DataFrame()
failed_tickers = []

if _ss_key in st.session_state and not st.session_state[_ss_key].empty:
    # ✅ 캐시 HIT: session_state에서 즉시 읽기 (체크박스 변경 등 재실행 시)
    df_all         = st.session_state[_ss_key]
    df_port        = st.session_state.get(f"df_port_v{_ck}", pd.DataFrame())
    failed_tickers = st.session_state.get(f"failed_v{_ck}", [])
else:
    # ❌ 캐시 MISS: 최초 실행 또는 새로고침 시 yfinance 호출
    try:
        with st.spinner("📡 종목 데이터 수집 중… (첫 실행 1~2분, 이후 즉시 전환)"):
            df_all, df_port, failed_tickers = load_stocks(
                tuple(TICKERS), _ck)
        if not df_all.empty and sector_data:
            _smap = {t: sec for sec, tks in SECTOR_TICKERS.items() for t in tks}
            df_all["섹터"] = df_all["Ticker"].map(lambda t: _smap.get(t, "기타"))
            def _sec_bonus(tk):
                sec = _smap.get(tk)
                if not sec or sec not in sector_data: return 0.0
                sd  = sector_data[sec]
                sc  = sd.get("sector_score", 50)
                if sc >= 70: return 8.0
                if sc >= 45: return 0.0
                return -8.0
            df_all["섹터 AI Score"] = df_all.apply(
                lambda r: min(100, max(0, r["AI Score"] + _sec_bonus(r["Ticker"]))), axis=1
            ).round(1)
            df_all = df_all.sort_values(
                "섹터 AI Score", ascending=False).reset_index(drop=True)
            df_all.index = df_all.index + 1
        # session_state에 저장 → 이후 탭 전환·체크박스 변경 시 즉시 사용
        st.session_state[f"df_all_v{_ck}"]  = df_all
        st.session_state[f"df_port_v{_ck}"] = df_port
        st.session_state[f"failed_v{_ck}"]  = failed_tickers
    except Exception as _e_load:
        pass

pe_data     = load_sp500_pe(st.session_state.cache_key)

# PE 현재값 + 역사 통계
pe_current = None; pe_mean = 16.21; pe_median = 15.07
if pe_data is not None and not pe_data.empty:
    pe_current = float(pe_data["Value"].iloc[-1])
    pe_mean    = round(float(pe_data["Value"].mean()), 2)
    pe_median  = round(float(pe_data["Value"].median()), 2)
    pe_min     = round(float(pe_data["Value"].min()), 2)
    pe_max     = round(float(pe_data["Value"].max()), 2)
else:
    pe_min = 5.31; pe_max = 123.73

# ── 유동성 점수 ──────────────────────────────────────────
def score_m2(s):
    if s is None or len(s) < 14: return 0, "데이터 없음"
    yoy = s.pct_change(12).dropna()
    if len(yoy) < 3: return 0, "데이터 부족"
    if yoy.iloc[-1] > yoy.iloc[-2] > yoy.iloc[-3]: return 3, f"2개월 연속 상향 ({yoy.iloc[-1]*100:.2f}%)"
    if yoy.iloc[-1] > yoy.iloc[-2]: return 1, f"1개월 상향 ({yoy.iloc[-1]*100:.2f}%)"
    return 0, f"하향 중 ({yoy.iloc[-1]*100:.2f}%)"
def score_rrp(s):
    if s is None or len(s) < 21: return 0, "데이터 없음"
    v = f"${s.iloc[-1]/1e3:.2f}T"
    return (2, f"감소 중 {v}") if float(s.iloc[-1])<float(s.iloc[-20]) else (0, f"증가 중 {v}")
def score_tga(s):
    if s is None or len(s) < 21: return 0, "데이터 없음"
    v = f"${s.iloc[-1]/1e3:.2f}T"
    return (2, f"감소 중 {v}") if float(s.iloc[-1])<float(s.iloc[-20]) else (0, f"증가 중 {v}")
def score_reserves(s):
    if s is None or len(s) < 5: return 0, "데이터 없음"
    last4 = s.tail(4); ok = all(last4.iloc[i]<last4.iloc[i+1] for i in range(3))
    return (2, f"4주 연속 증가 ${s.iloc[-1]/1e3:.2f}T") if ok else (0, f"증가 미충족 ${s.iloc[-1]/1e3:.2f}T")
def score_real_rate(s):
    if s is None or len(s) < 2: return 0, "데이터 없음"
    v = float(s.iloc[-1])
    return (2, f"{v:.2f}% (우호적)") if v<1.0 else ((1, f"{v:.2f}% (안정)") if v<2.0 else (0, f"{v:.2f}% (부담)"))
def score_credit(s):
    if s is None or len(s) < 21: return 0, "데이터 없음"
    v, prev = float(s.iloc[-1]), float(s.iloc[-20])
    return (2, f"{v:.2f}% 축소 (안정)") if v<3.5 and v<prev else ((1, f"{v:.2f}% 보통") if v<4.5 else (0, f"{v:.2f}% 확대 (공포)"))

SCORERS = {
    "M2":           (score_m2,       fred_data.get("M2"),           3, "💧 M2 통화량"),
    "RRP":          (score_rrp,      fred_data.get("RRP"),          2, "🏦 역레포"),
    "TGA":          (score_tga,      fred_data.get("TGA"),          2, "🏛️ TGA"),
    "Reserves":     (score_reserves, fred_data.get("Reserves"),     2, "🏧 은행 준비금"),
    "RealRate":     (score_real_rate,fred_data.get("RealRate"),     2, "📈 실질금리"),
    "CreditSpread": (score_credit,   fred_data.get("CreditSpread"), 2, "📊 크레딧 스프레드"),
}
MAX_SCORE = sum(mx for _,_,mx,_ in SCORERS.values())
total_liq = 0; score_rows = []
for key, (fn, data, mx, label) in SCORERS.items():
    sc, reason = fn(data); total_liq += sc
    pct = sc/mx if mx>0 else 0
    color = "#166534" if pct>=0.67 else ("#92400E" if pct>=0.33 else "#B91C1C")
    score_rows.append({"key":key,"label":label,"score":sc,"max":mx,
                        "reason":reason,"color":color,"has_data":data is not None})
liq_pct = total_liq/MAX_SCORE if MAX_SCORE>0 else 0

# ══════════════════════════════════════════════════════════
# V26 — 100점 역사 백분위 점수 시스템
# ══════════════════════════════════════════════════════════
def _pct_rank(series, current_val):
    """역사 데이터에서 current_val의 백분위 (0~100)"""
    if series is None or len(series) < 20: return 50.0
    return float((series < current_val).sum() / len(series) * 100)

def _indicator_score_100(key, series):
    """
    지표별 '투자 유리도' 점수 (0~100, 높을수록 투자에 좋음)
    방향: M2·준비금은 높을수록 좋음 / 나머지는 낮을수록 좋음
    """
    if series is None or len(series) < 3: return None
    cur = float(series.iloc[-1])

    # FedFunds: 절대값 기준 점수 (역사적 백분위 대신 실제 금리 수준으로 판단)
    if key == "FedFunds":
        if   cur <= 1.0: return 100.0
        elif cur <= 2.0: return 85.0
        elif cur <= 3.0: return 70.0
        elif cur <= 4.0: return 55.0
        elif cur <= 5.0: return 40.0
        elif cur <= 5.5: return 25.0
        else:            return 15.0

    if len(series) < 20: return None
    rank = _pct_rank(series, cur)           # 역사적 상위 몇 %
    if key in ("M2", "Reserves"):
        return round(rank, 1)               # 높을수록 좋음 → 그대로
    else:
        return round(100 - rank, 1)         # 낮을수록 좋음 → 반전

# 지표별 위험 기준 (이 점수 이하면 주의)
INDICATOR_DANGER = {
    "M2":           20,   # 20점 이하: 유동성 부족
    "RRP":          25,   # 25점 이하: 시장 돈 흡수 중
    "TGA":          30,   # 30점 이하: 정부 자금 묶임
    "Reserves":     25,   # 25점 이하: 은행 긴축
    "RealRate":     35,   # 35점 이하: 금리 부담 큼
    "CreditSpread": 30,   # 30점 이하: 시장 공포
}
INDICATOR_WARN = {k: v + 25 for k, v in INDICATOR_DANGER.items()}  # 주의 구간

# 각 지표 100점 계산
_liq_v2_for_score = None  # tab1 로드 전에는 fred_data 활용
IND_SCORE_100 = {}
IND_META_100 = {
    "FedFunds":     {"label":"기준금리",       "better":"↓ 낮을수록 좋음", "unit":"%",
                     "good_desc":"저금리 — 유동성 친화","bad_desc":"고금리 — 긴축 압박"},
    "M2":           {"label":"M2 통화량",     "better":"↑ 높을수록 좋음", "unit":"B$",
                     "good_desc":"시장에 돈이 충분","bad_desc":"유동성 부족 경고"},
    "RRP":          {"label":"역레포 RRP",     "better":"↓ 낮을수록 좋음", "unit":"B$",
                     "good_desc":"시장으로 돈 복귀","bad_desc":"돈이 FED로 흡수"},
    "TGA":          {"label":"재무부 TGA",     "better":"↓ 낮을수록 좋음", "unit":"B$",
                     "good_desc":"정부 자금 시장 공급","bad_desc":"정부가 돈 묶어둠"},
    "Reserves":     {"label":"은행 준비금",    "better":"↑ 높을수록 좋음", "unit":"B$",
                     "good_desc":"은행 대출 여력 충분","bad_desc":"긴축 우려"},
    "RealRate":     {"label":"실질금리",       "better":"↓ 낮을수록 좋음", "unit":"%",
                     "good_desc":"차입 비용 낮음","bad_desc":"위험자산 부담 큼"},
    "CreditSpread": {"label":"크레딧 스프레드","better":"↓ 낮을수록 좋음", "unit":"%",
                     "good_desc":"시장 안정","bad_desc":"시장 공포 신호"},
}

# V80: 역사적 이벤트 기반 레이블 (danger점, warn점)
INDICATOR_HIST_EVENTS = {
    "M2":           ("2022년 양적긴축(M2 마이너스)", "2009년 금융위기 저점"),
    "RRP":          ("2019년 레포 위기(금리 10%)",   "2022년 RRP 폭증 시작"),
    "TGA":          ("2023년 부채한도 협상 위기",    "부채한도 경고 수준"),
    "Reserves":     ("2019년 레포 위기 직전",        "경계 수준 3조$"),
    "RealRate":     ("2022년 급등(나스닥 -33%)",     "중립 수준"),
    "CreditSpread": ("2020년 코로나충격(4%돌파)",    "2008년 금융위기 수준"),
    "FedFunds":     ("2022-23년 긴축(40년 최고)",    "중립 수준 3%"),
}

for key, meta in IND_META_100.items():
    # ✅ 올바른 방법: pandas Series는 or 연산자 사용 불가 (3부 규칙)
    hist = fred_history.get(key)
    if hist is None or (isinstance(hist, pd.Series) and hist.empty):
        hist = fred_data.get(key)

    score = _indicator_score_100(key, hist)

    # V69: 현재값 — fred_data(최신, FRED_META 기준 로드) 우선
    # FedFunds 포함 모든 지표가 fred_data에 로드됨 (V68에서 FRED_META에 추가)
    cur_data = fred_data.get(key)
    if cur_data is None or (isinstance(cur_data, pd.Series) and cur_data.empty):
        cur_data = hist
    val = float(cur_data.iloc[-1]) if (
        cur_data is not None and isinstance(cur_data, pd.Series) and not cur_data.empty
    ) else None
    IND_SCORE_100[key] = {"score": score, "val": val, "meta": meta}

# 종합 유동성 100점 (가중 평균)
_WEIGHTS = {"FedFunds":0.15,"M2":0.20,"RRP":0.15,"TGA":0.10,"Reserves":0.10,"RealRate":0.15,"CreditSpread":0.15}
_valid   = {k: v for k, v in IND_SCORE_100.items() if v["score"] is not None}
if _valid:
    _wsum   = sum(_WEIGHTS.get(k, 0.1) for k in _valid)
    LIQ_SCORE_100 = round(sum(v["score"] * _WEIGHTS.get(k, 0.1) for k, v in _valid.items()) / _wsum, 1)
else:
    LIQ_SCORE_100 = 50.0

# ── 100점 기반 5단계 투자 행동 ──────────────────────────
# (기존 RISK ON/OFF 완전 대체)
LIQ_ACTION_STAGES = [
    {"range":(80,100), "stage":5, "label":"🚀 적극 매수",  "color":"#166534","bg":"#F0FDF4","border":"#86EFAC",
     "desc":"유동성 최적 환경입니다. 공격적으로 진입해도 좋습니다.",
     "size":"투자금의 80~100% 투자 가능"},
    {"range":(60, 80), "stage":4, "label":"🟢 선별 매수",  "color":"#15803D","bg":"#F0FDF4","border":"#BBF7D0",
     "desc":"유동성이 회복 중입니다. RS 상위 종목을 골라 분할 매수하세요.",
     "size":"투자금의 50~70% 투자"},
    {"range":(40, 60), "stage":3, "label":"🟡 관    망",   "color":"#92400E","bg":"#FFFBEB","border":"#FDE68A",
     "desc":"혼조 구간입니다. 새로운 진입보다 기존 보유 관리에 집중하세요.",
     "size":"투자금의 20~40%만 유지"},
    {"range":(20, 40), "stage":2, "label":"🟠 투자 보류",  "color":"#C2410C","bg":"#FFF7ED","border":"#FDBA74",
     "desc":"유동성 수축 신호입니다. 신규 매수를 자제하고 현금을 늘리세요.",
     "size":"투자금의 10% 이하"},
    {"range":( 0, 20), "stage":1, "label":"🔴 현금 보유",  "color":"#B91C1C","bg":"#FEF2F2","border":"#FECACA",
     "desc":"위기 구간입니다. 전액 현금 보유가 최선입니다.",
     "size":"현금 100% 보유"},
]

def get_liq_action(score):
    for cfg in LIQ_ACTION_STAGES:
        lo, hi = cfg["range"]
        if lo <= score <= hi:
            return cfg
    return LIQ_ACTION_STAGES[-1]

LIQ_ACTION = get_liq_action(LIQ_SCORE_100)

# 시장 상태 → 한글 보조 레이블
MKT_KR = {
    "RISK ON":  {"label":"📈 매수 적기",   "color":"#166534"},
    "NEUTRAL":  {"label":"↔️ 방향 확인 중","color":"#92400E"},
    "RISK OFF": {"label":"📉 매도/보류",   "color":"#B91C1C"},
}


m2_has_data  = fred_data.get("M2") is not None
m2_score_val = IND_SCORE_100.get("M2", {}).get("score") or 0

# liq_regime: 100점 기반으로 재정의 (기존 코드 호환 유지)
_la = LIQ_ACTION
liq_regime  = _la["label"]
liq_color   = _la["color"]
pos_guide   = _la["size"]


# ── 시장 점수 ────────────────────────────────────────────
mkt_score, mkt_avail, mkt_reasons, hard_stops = 0, 0, [], []
spy_s = mkt.get("SPY")
if spy_s is not None and len(spy_s)>=21:
    mkt_avail+=1
    if float(spy_s.iloc[-1])>float(spy_s.rolling(20).mean().iloc[-1]):
        mkt_score+=1; mkt_reasons.append(("✅","SPY > MA20 (상승 추세)"))
    else: mkt_reasons.append(("❌","SPY < MA20 (하락 추세)"))
vix_s=mkt.get("VIX"); vix_val=None
if vix_s is not None and not vix_s.empty:
    mkt_avail+=1; vix_val=float(vix_s.iloc[-1])
    if vix_val<20:   mkt_score+=1; mkt_reasons.append(("✅",f"VIX {vix_val:.1f} — 공포 없음, 안정적"))
    elif vix_val<25: mkt_reasons.append(("⚠️",f"VIX {vix_val:.1f} — 경계 구간. 신규 진입 시 비중 70% 이하 유지"))
    elif vix_val<28: mkt_reasons.append(("❌",f"VIX {vix_val:.1f} — 공포 구간. 투자 40% 상한 / 방어 자산 확대"))
    else:            mkt_reasons.append(("❌",f"VIX {vix_val:.1f} — 패닉 구간, 매수 전면 금지"))
tnx_s=mkt.get("TNX")
if tnx_s is not None and len(tnx_s)>=21:
    mkt_avail+=1; tnx_now=float(tnx_s.iloc[-1]); tnx_prev=float(tnx_s.iloc[-21])
    if tnx_now-tnx_prev<0.3: mkt_score+=1; mkt_reasons.append(("✅",f"금리 안정 ({tnx_now:.2f}%)"))
    else: mkt_reasons.append(("❌",f"금리 급등 (+{tnx_now-tnx_prev:.2f}%)"))
qqq_s=mkt.get("QQQ")
if qqq_s is not None and len(qqq_s)>=51:
    mkt_avail+=1
    if float(qqq_s.iloc[-1])>float(qqq_s.rolling(50).mean().iloc[-1]):
        mkt_score+=1; mkt_reasons.append(("✅","QQQ > MA50 — 나스닥 장기 상승 추세"))
    else: mkt_reasons.append(("❌","QQQ < MA50 — 나스닥 추세 약화"))

if vix_val and vix_val>28: hard_stops.append(f"🚫 VIX {vix_val:.1f} > 28 — 패닉, 매수 전면 금지")
if tnx_s is not None and len(tnx_s)>=21 and (float(tnx_s.iloc[-1])-float(tnx_s.iloc[-21]))>0.5:
    hard_stops.append("🚫 금리 급등 (+0.5% 이상) — 유동성 긴축")
if fred_data.get("M2") is not None:
    _yoy=fred_data["M2"].pct_change(12).dropna()
    if len(_yoy)>=3 and _yoy.iloc[-1]<_yoy.iloc[-2]<_yoy.iloc[-3]:
        hard_stops.append("🚫 M2 2개월 연속 하락 — 유동성 수축")
if fred_data.get("RRP") is not None and fred_data.get("TGA") is not None:
    _r=fred_data["RRP"]; _t=fred_data["TGA"]
    if len(_r)>=21 and len(_t)>=21 and float(_r.iloc[-1])>float(_r.iloc[-20]) and float(_t.iloc[-1])>float(_t.iloc[-20]):
        hard_stops.append("🚫 RRP+TGA 동시 증가 — 유동성 이중 흡수")
if fred_data.get("CreditSpread") is not None:
    _cs=float(fred_data["CreditSpread"].iloc[-1])
    if _cs>5.0: hard_stops.append(f"🚫 크레딧 스프레드 {_cs:.1f}% > 5%")

mkt_ratio  = mkt_score/mkt_avail if mkt_avail>0 else 0
mkt_status = ("RISK OFF" if hard_stops else
              ("RISK ON" if mkt_ratio>=0.75 else ("NEUTRAL" if mkt_ratio>=0.50 else "RISK OFF")))

# ── CNN 공포탐욕지수 자체 계산 ───────────────────────────
def calc_fear_greed():
    scores = {}
    if vix_s is not None and not vix_s.empty:
        v = float(vix_s.iloc[-1])
        scores["VIX"] = max(0, min(100, (40-v)/(40-10)*100))
    if qqq_s is not None and len(qqq_s)>=50:
        ma50 = float(qqq_s.rolling(50).mean().iloc[-1])
        cur  = float(qqq_s.iloc[-1])
        scores["Momentum"] = max(0, min(100, 50+(cur-ma50)/ma50*100*5))
    cs = fred_data.get("CreditSpread")
    if cs is not None and not cs.empty:
        scores["Credit"] = max(0, min(100, (7-float(cs.iloc[-1]))/(7-2)*100))
    rr = fred_data.get("RealRate")
    if rr is not None and not rr.empty:
        scores["RealRate"] = max(0, min(100, (3-float(rr.iloc[-1]))/(3-(-1))*100))
    return round(sum(scores.values())/len(scores), 1) if scores else 50

fg_score = calc_fear_greed()
if   fg_score >= 75: fg_label, fg_color = "극도의 탐욕", "#166534"
elif fg_score >= 55: fg_label, fg_color = "탐욕",       "#166534"
elif fg_score >= 45: fg_label, fg_color = "중립",       "#92400E"
elif fg_score >= 25: fg_label, fg_color = "공포",       "#92400E"
else:                fg_label, fg_color = "극도의 공포", "#B91C1C"

# ── 통합 최종 판정 (V26: 100점 기반 한글 5단계) ─────────
_mkt_kr   = MKT_KR.get(mkt_status, MKT_KR["NEUTRAL"])
_combined = LIQ_SCORE_100

# 하드스탑은 무조건 현금 보유
if hard_stops:
    fat,fas,fac,fab = "🔴 현금 보유","위험 신호 발동 — 전액 현금 보유 권장","#B91C1C","#FEF2F2"
elif _combined >= 80 and mkt_status == "RISK ON":
    fat,fas,fac,fab = "🟢 적극 매수","유동성·시장 모두 최적 — 분할 매수 적극 활용","#166534","#F0FDF4"
elif _combined >= 60 and mkt_status in ("RISK ON","NEUTRAL"):
    fat,fas,fac,fab = "🟢 선별 매수","RS 상위 종목 + 브레이크아웃 신호 확인 후 진입","#1D4ED8","#EFF6FF"
elif _combined >= 40:
    fat,fas,fac,fab = "🟡 관    망","신규 진입 자제 — 기존 보유 관리 집중","#92400E","#FFFBEB"
elif _combined >= 20:
    fat,fas,fac,fab = "🟠 투자 보류","유동성 수축 — 현금 비중 확대, 손절 기준 점검","#C2410C","#FFF7ED"
else:
    fat,fas,fac,fab = "🔴 현금 보유","위기 구간 — 전액 현금 보유가 최선","#B91C1C","#FEF2F2"


# ─────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────
# 수익률 커브 전체 로드 (V36 신규)
# ─────────────────────────────────────────────────────────
YIELD_SERIES = {
    "1M": ("GS1M", "1개월물"),
    "3M": ("GS3M", "3개월물"),
    "2Y": ("GS2",  "2년물"),
    "3Y": ("GS3",  "3년물"),
    "5Y": ("GS5",  "5년물"),
    "10Y":("GS10", "10년물"),
    "20Y":("GS20", "20년물"),
    "30Y":("GS30", "30년물"),
}

@st.cache_data(ttl=3600, show_spinner=False)
def load_yield_curve(api_key, _bust=0):
    """FRED에서 전체 수익률 커브 로드"""
    if is_placeholder(api_key): return {}
    result = {}
    for key, (sid, label) in YIELD_SERIES.items():
        try:
            url = (f"https://api.stlouisfed.org/fred/series/observations"
                   f"?series_id={sid}&api_key={api_key}&file_type=json"
                   f"&sort_order=desc&limit=5")
            resp = requests.get(url, timeout=15)
            if resp.status_code != 200: continue
            obs = [o for o in resp.json().get("observations",[])
                   if o["value"] not in (".", "")]
            if obs:
                result[key] = {"label": label, "value": float(obs[0]["value"]),
                               "date": obs[0]["date"]}
        except Exception:
            pass
    return result

yield_curve = load_yield_curve(FRED_API_KEY, st.session_state.cache_key)

# ─────────────────────────────────────────────────────────
# 전역 투자 유틸 함수 (V37: 탭 밖으로 이동)
# ─────────────────────────────────────────────────────────
SCALE_CONFIG = {
    "S":  {"name":"집중 모멘텀",     "emoji":"🎯", "core_ratio":1.00,"defense_ratio":0.00,"hedge_ratio":0.00},
    "M1": {"name":"모멘텀+방어",     "emoji":"⚖️", "core_ratio":0.70,"defense_ratio":0.30,"hedge_ratio":0.00},
    "M2": {"name":"코어-새틀라이트", "emoji":"🏗️", "core_ratio":0.60,"defense_ratio":0.30,"hedge_ratio":0.10},
    "L":  {"name":"기관 모방",       "emoji":"🏦", "core_ratio":0.50,"defense_ratio":0.30,"hedge_ratio":0.20},
    "XL": {"name":"멀티팩터 분산",   "emoji":"🌐", "core_ratio":0.45,"defense_ratio":0.35,"hedge_ratio":0.20},
}

def get_atr_position_size(total_capital_만원, atr_val, price, risk_pct=0.01):
    """ATR 기반 포지션 사이징 (V98)
    총자산의 risk_pct(기본 1%) 리스크를 각 종목에 동일하게 배분
    포지션크기 = (총자산 × 리스크%) / (ATR × 2)
    """
    if not atr_val or atr_val <= 0 or price <= 0:
        return None, None
    total_capital_원 = total_capital_만원 * 10000
    risk_amount_원   = total_capital_원 * risk_pct
    atr_stop_range   = atr_val * 2      # ATR × 2 = 손절 거리
    shares           = risk_amount_원 / (atr_stop_range * 1400)  # 환율 약 1400 적용
    position_value_만원 = round(shares * price * 1400 / 10000, 0)
    position_pct     = round(position_value_만원 / total_capital_만원 * 100, 1) if total_capital_만원 > 0 else 0
    return position_value_만원, position_pct


def get_invest_ratio(liq_stage, mkt_status, hard_stops, vix=None):
    """유동성 단계 + VIX 단계 → 투자 가능 비율 + GLD 헤지 비중 (V98)"""
    if hard_stops:                                   return 0.00, "🔴 매수 금지 — 현금 100%", 0.15
    vix_cap = 1.0; vix_msg = ""
    if vix is not None:
        if vix >= 28:   vix_cap = 0.00; vix_msg = f" (VIX {vix:.0f} — 매수 금지)"
        elif vix >= 25: vix_cap = 0.40; vix_msg = f" (VIX {vix:.0f} — 40% 상한)"
        elif vix >= 20: vix_cap = 0.70; vix_msg = f" (VIX {vix:.0f} — 70% 상한)"
    if vix_cap == 0.0: return 0.00, f"🔴 VIX 패닉{vix_msg} — 현금 100%", 0.20
    if liq_stage == 5 and mkt_status == "RISK ON":   base = 0.90
    elif liq_stage == 5:                             base = 0.70
    elif liq_stage == 4 and mkt_status == "RISK ON": base = 0.65
    elif liq_stage == 4:                             base = 0.50
    elif liq_stage == 3 and mkt_status == "RISK ON": base = 0.40
    elif liq_stage == 3:                             base = 0.25
    elif liq_stage == 2:                             base = 0.10
    else:                                            base = 0.00
    ratio = min(base, vix_cap)
    gld_ratio = {5:0.00, 4:0.03, 3:0.07, 2:0.15, 1:0.20}.get(liq_stage, 0.05)
    if vix and vix >= 25: gld_ratio = max(gld_ratio, 0.12)
    label_map = {
        0.90:"🚀 최적 환경", 0.70:"🟢 유동성 최고", 0.65:"🟢 회복 초기",
        0.50:"🟢 회복 중",   0.40:"🟡 혼조 구간",   0.25:"🟡 주의 구간",
        0.10:"🔴 수축 구간", 0.00:"🚨 현금 보유"
    }
    lbl = label_map.get(ratio, f"{ratio*100:.0f}% 투자")
    return ratio, f"{lbl} — {ratio*100:.0f}% 투자{vix_msg}", gld_ratio




# ─────────────────────────────────────────────────────────
# 사이드바 — 설정 (컴팩트)
# ─────────────────────────────────────────────────────────
sb = st.sidebar
sb.markdown(
    "<div style='font-family:Space Mono,monospace;font-size:13px;"
    "color:#3B5BA5;letter-spacing:2px;padding:8px 0 4px 0'>⚙ SETTINGS</div>",
    unsafe_allow_html=True)

# API 키 자동 로드 상태
_saved_fred = _get_saved("FRED_API_KEY")
_saved_bot  = _get_saved("BOT_TOKEN")
_saved_chat = _get_saved("CHAT_ID")
_kr_has     = bool(_KEYRING_OK and _kr_get("FRED_API_KEY"))
_cfg_has    = bool(_cfg_load().get("FRED_API_KEY",""))
_sec_ok     = False
try: _sec_ok = bool(st.secrets.get("FRED_API_KEY",""))
except: pass

if _kr_has:
    sb.markdown("<div style='font-size:10px;background:#F0FDF4;border:1px solid #86EFAC;"
                "border-radius:5px;padding:4px 8px;color:#166534;margin-bottom:6px'>"
                "🔐 키체인 자동 로드됨</div>", unsafe_allow_html=True)
elif _sec_ok:
    sb.markdown("<div style='font-size:10px;background:#F0FDF4;border:1px solid #86EFAC;"
                "border-radius:5px;padding:4px 8px;color:#166534;margin-bottom:6px'>"
                "✅ secrets.toml 로드됨</div>", unsafe_allow_html=True)
elif _cfg_has:
    sb.markdown("<div style='font-size:10px;background:#EFF6FF;border:1px solid #BFDBFE;"
                "border-radius:5px;padding:4px 8px;color:#1D4ED8;margin-bottom:6px'>"
                "💾 config.json 로드됨</div>", unsafe_allow_html=True)
else:
    sb.markdown("""
    <div style='font-size:10px;background:#FFFBEB;border:1px solid #FDE68A;
    border-radius:5px;padding:6px 10px;color:#92400E;margin-bottom:6px;line-height:1.6'>
    ⚠️ FRED API 키 없음<br>
    <span style='color:#6B7280'>
    ✅ 동작: 주가·RS·AI Score·종목테이블<br>
    ❌ 미동작: 유동성(M2/RRP/금리 등)<br>
    무료 발급 →
    <a href="https://fred.stlouisfed.org/docs/api/api_key.html"
       target="_blank" style="color:#1D4ED8">fred.stlouisfed.org</a>
    </span></div>
    """, unsafe_allow_html=True)

# 투자금 — 포트폴리오 탭에서 입력 (사이드바 제거 V93)
INVEST_AMOUNT_만원 = float(st.session_state.get("invest_amount", 1000))
INVEST_AMOUNT_원   = INVEST_AMOUNT_만원 * 10000
if   INVEST_AMOUNT_만원 <  10000: INVEST_SCALE = "S"
elif INVEST_AMOUNT_만원 <  30000: INVEST_SCALE = "M1"
elif INVEST_AMOUNT_만원 <  50000: INVEST_SCALE = "M2"
elif INVEST_AMOUNT_만원 < 100000: INVEST_SCALE = "L"
else:                              INVEST_SCALE = "XL"
_scale_labels = {"S":"집중 모멘텀","M1":"모멘텀+방어","M2":"코어-새틀라이트","L":"기관 모방","XL":"멀티팩터"}

INVEST_IN_REPORT = (INVEST_AMOUNT_만원 > 0)

# FRED_API_KEY 등은 아래 맨 하단 expander에서 재정의됨
# 여기서는 기본값만 유지 (중간 저장된 값)
if not FRED_API_KEY: FRED_API_KEY = _saved_fred
if not BOT_TOKEN:    BOT_TOKEN    = _saved_bot
if not CHAT_ID:      CHAT_ID      = _saved_chat

sb.markdown("<hr style='border-color:#E2E6ED;margin:10px 0'>", unsafe_allow_html=True)

# 새로고침
if sb.button("🔄 데이터 새로고침", use_container_width=True, key="sb_refresh"):
    st.session_state.cache_key += 1
    st.cache_data.clear()
    st.rerun()
sb.markdown(f"<div style='font-size:9px;color:#9CA3AF;margin-top:4px'>"
            f"🕐 {datetime.now().strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)



# ── API 키 설정 (사이드바 맨 하단) ───────────────────────


# 투자금 — 포트폴리오 탭에서 관리 (사이드바 제거)

# API KEY — 세션 토글 버튼 방식 (V93: expander 버그 우회)
if "show_api" not in st.session_state:
    st.session_state["show_api"] = not(_kr_has or _sec_ok or _cfg_has)

sb.markdown("<hr style='border-color:#E2E6ED;margin:6px 0'>", unsafe_allow_html=True)
if sb.button(
    "API 키 설정 열기" if not st.session_state["show_api"] else "API 키 설정 닫기",
    key="sb_api_toggle", use_container_width=True):
    st.session_state["show_api"] = not st.session_state["show_api"]
    st.rerun()

if st.session_state.get("show_api"):
    sb.markdown(
        "<div style='background:#F9FAFB;border:0.5px solid #E2E6ED;"
        "border-radius:7px;padding:10px 10px;margin-top:4px'>",
        unsafe_allow_html=True)
    FRED_API_KEY = sb.text_input("FRED API KEY", value=_saved_fred, type="password",
        key="sb_fred", placeholder="FRED API Key…")
    BOT_TOKEN  = sb.text_input("BOT TOKEN", value=_saved_bot, type="password",
        key="sb_bot", placeholder="Telegram Bot Token…")
    CHAT_ID    = sb.text_input("CHAT ID", value=_saved_chat,
        key="sb_chat", placeholder="Chat ID…")
    _s1, _s2 = sb.columns(2)
    if _s1.button("저장", key="sb_save", use_container_width=True):
        ok, msg = _save_all(FRED_API_KEY, BOT_TOKEN, CHAT_ID)
        (sb.success if ok else sb.error)(msg)
        if ok: st.rerun()
    if _s2.button("삭제", key="sb_del", use_container_width=True):
        ok, msg = _delete_all()
        (sb.info if ok else sb.error)(msg)
        if ok: st.rerun()
    sb.markdown("</div>", unsafe_allow_html=True)

# 값 보장
if not FRED_API_KEY: FRED_API_KEY = _saved_fred
if not BOT_TOKEN:    BOT_TOKEN    = _saved_bot
if not CHAT_ID:      CHAT_ID      = _saved_chat


# ─── 사이드바 마켓 패널 업데이트 (V92) ────────────────────
try:
    # ① 유동성 단계 카드
    _ls    = LIQ_ACTION.get("stage", 0)
    _ll    = LIQ_ACTION.get("label", "—")
    _lc    = LIQ_ACTION.get("color", "#6B7280")
    _lbg   = LIQ_ACTION.get("bg",    "#F9FAFB")
    _guide_map = {1:"현금 보유",2:"투자 보류",3:"소량 선별",4:"투자금 50~70%",5:"투자금 80~100%"}
    _lgd   = _guide_map.get(_ls, "—")
    _score = LIQ_SCORE_100 if 'LIQ_SCORE_100' in dir() else 0
    liq_stage_placeholder.markdown(
        f"<div style='background:{_lbg};border:0.5px solid {_lc}44;"
        f"border-radius:7px;padding:7px 10px'>"
        f"<div style='display:flex;justify-content:space-between;align-items:center'>"
        f"<span style='font-size:13px;font-weight:600;color:{_lc}'>{_ll}</span>"
        f"<span style='font-size:11px;color:{_lc};opacity:0.8'>{_score:.0f}점</span>"
        f"</div>"
        f"<div style='font-size:10px;color:{_lc};opacity:0.7;margin-top:2px'>{_lgd}</div>"
        f"</div>",
        unsafe_allow_html=True)
except: pass

try:
    # ② 미국 시장 패널
    def _sb_row(label, series_key, is_pct=False, decimals=2):
        s = mkt.get(series_key)
        if s is None or s.empty: return ""
        cur  = float(s.iloc[-1])
        prev = float(s.iloc[-2]) if len(s)>1 else cur
        chg  = (cur - prev) / prev * 100 if not is_pct else (cur - prev)
        arr  = "▲" if chg>0 else ("▼" if chg<0 else "―")
        col  = "#15803d" if chg>0 else ("#B91C1C" if chg<0 else "#9CA3AF")
        val_str = f"{cur:,.0f}" if cur>100 else f"{cur:.2f}"
        chg_str = f"{arr} {abs(chg):.2f}{'%' if not is_pct else ''}"
        return (f"<div style='display:flex;justify-content:space-between;"
                f"align-items:center;padding:3px 0;font-size:11px'>"
                f"<span style='color:#9CA3AF'>{label}</span>"
                f"<span style='font-family:monospace;font-weight:500;color:#0D1117'>{val_str}</span>"
                f"<span style='color:{col};font-size:10px'>{chg_str}</span></div>")

    # VIX 배지
    _vix_s = mkt.get("VIX")
    _vix_v = float(_vix_s.iloc[-1]) if _vix_s is not None and not _vix_s.empty else None
    if _vix_v:
        if   _vix_v >= 30: _vb="⚠️ 공포";    _vc="#B91C1C"; _vbg="#FEF2F2"; _vbd="#FECACA"
        elif _vix_v >= 20: _vb="⚠️ 주의";    _vc="#92400E"; _vbg="#FFFBEB"; _vbd="#FDE68A"
        else:              _vb="✅ 안정";     _vc="#15803d"; _vbg="#F0FDF4"; _vbd="#86EFAC"
        _vix_badge = (f"<span style='background:{_vbg};border:0.5px solid {_vbd};"
                      f"border-radius:3px;padding:1px 5px;font-size:9px;color:{_vc}'>{_vb}</span>")
        _vix_row = (f"<div style='display:flex;justify-content:space-between;"
                    f"align-items:center;padding:3px 0;font-size:11px'>"
                    f"<span style='color:#9CA3AF'>VIX</span>"
                    f"<span style='font-family:monospace;font-weight:500;color:#0D1117'>{_vix_v:.1f}</span>"
                    f"{_vix_badge}</div>")
    else: _vix_row = ""

    # 공포탐욕
    _fg = fg_score if 'fg_score' in dir() and fg_score else None
    if _fg:
        if   _fg <= 25: _fb="😱 극도공포"; _fc="#B91C1C"
        elif _fg <= 45: _fb="😰 공포";    _fc="#92400E"
        elif _fg <= 55: _fb="😐 중립";    _fc="#6B7280"
        elif _fg <= 75: _fb="😊 탐욕";    _fc="#15803d"
        else:           _fb="🤑 극도탐욕"; _fc="#166534"
        _fg_row = (f"<div style='display:flex;justify-content:space-between;"
                   f"align-items:center;padding:3px 0;font-size:11px'>"
                   f"<span style='color:#9CA3AF'>공포탐욕</span>"
                   f"<span style='font-family:monospace;font-weight:500;color:#0D1117'>{_fg:.0f}</span>"
                   f"<span style='font-size:10px;color:{_fc}'>{_fb}</span></div>")
    else: _fg_row = ""

    _mkt_html = (_sb_row("나스닥", "QQQ") +
                 _sb_row("S&P500", "SPY") +
                 _vix_row + _fg_row)
    mkt_panel_placeholder.markdown(_mkt_html, unsafe_allow_html=True)
except: pass

try:
    # ③ 국채금리 3종 카드 그리드
    def _yield_cell(term, key, is_pct=True):
        s = mkt.get(key)
        if s is None or s.empty:
            return (f"<div style='background:var(--color-background-secondary,#F9FAFB);"
                    f"border-radius:5px;padding:5px 6px;text-align:center'>"
                    f"<div style='font-size:9px;color:#9CA3AF'>{term}</div>"
                    f"<div style='font-size:11px;font-weight:500;color:#9CA3AF'>—</div></div>")
        cur  = float(s.iloc[-1])
        prev = float(s.iloc[-2]) if len(s)>1 else cur
        chg  = cur - prev
        col  = "#15803d" if chg>0 else ("#B91C1C" if chg<0 else "#9CA3AF")
        arr  = "▲" if chg>0 else ("▼" if chg<0 else "―")
        return (f"<div style='background:#F9FAFB;border:0.5px solid #E2E6ED;"
                f"border-radius:5px;padding:5px 6px;text-align:center'>"
                f"<div style='font-size:9px;color:#9CA3AF;margin-bottom:2px'>{term}</div>"
                f"<div style='font-size:12px;font-weight:500;color:#0D1117'>{cur:.2f}%</div>"
                f"<div style='font-size:9px;color:{col}'>{arr}{abs(chg):.2f}</div></div>")

    _yield_html = (f"<div style='display:grid;grid-template-columns:1fr 1fr 1fr;gap:4px'>"
                   f"{_yield_cell('2년', 'IRX')}"
                   f"{_yield_cell('10년','TNX')}"
                   f"{_yield_cell('30년','TYX')}"
                   f"</div>")
    yield_placeholder.markdown(_yield_html, unsafe_allow_html=True)
except: pass

try:
    # ③-b 글로벌 자산 패널 (금/BTC/원유)
    def _asset_cell(label, key, fmt="price"):
        s = mkt.get(key)
        if s is None or s.empty:
            return (f"<div style='display:flex;justify-content:space-between;"
                    f"align-items:center;padding:2px 0;font-size:11px'>"
                    f"<span style='color:#9CA3AF'>{label}</span>"
                    f"<span style='color:#9CA3AF'>—</span></div>")
        cur  = float(s.iloc[-1])
        prev = float(s.iloc[-2]) if len(s) > 1 else cur
        chg  = (cur - prev) / prev * 100 if prev != 0 else 0
        col  = "#15803d" if chg > 0 else ("#B91C1C" if chg < 0 else "#9CA3AF")
        arr  = "▲" if chg > 0 else ("▼" if chg < 0 else "―")
        if fmt == "btc":
            val_s = f"${cur:,.0f}"
        elif fmt == "oil":
            val_s = f"${cur:.1f}"
        else:  # gold
            val_s = f"${cur:,.0f}"
        return (f"<div style='display:flex;justify-content:space-between;"
                f"align-items:center;padding:2px 0;font-size:11px'>"
                f"<span style='color:#9CA3AF'>{label}</span>"
                f"<span style='font-family:monospace;font-weight:500;"
                f"color:#0D1117'>{val_s}</span>"
                f"<span style='font-size:10px;color:{col}'>"
                f"{arr}{abs(chg):.1f}%</span></div>")

    _asset_html = (
        _asset_cell("금 (Gold)",   "GOLD", "gold") +
        _asset_cell("BTC",         "BTC",  "btc")  +
        _asset_cell("WTI 원유",    "OIL",  "oil")
    )
    asset_panel_placeholder.markdown(_asset_html, unsafe_allow_html=True)
except: pass

try:
    # ③-c 국제 지수 패널
    def _idx_row(flag, label, key):
        s = mkt.get(key)
        if s is None or s.empty:
            return (f"<div style='display:flex;align-items:center;gap:4px;"
                    f"padding:2px 0;font-size:11px'>"
                    f"<span>{flag}</span>"
                    f"<span style='flex:1;color:#9CA3AF'>{label}</span>"
                    f"<span style='color:#9CA3AF'>—</span></div>")
        cur  = float(s.iloc[-1])
        prev = float(s.iloc[-2]) if len(s) > 1 else cur
        chg  = (cur - prev) / prev * 100 if prev != 0 else 0
        col  = "#15803d" if chg > 0 else ("#B91C1C" if chg < 0 else "#9CA3AF")
        arr  = "▲" if chg > 0 else ("▼" if chg < 0 else "―")
        val_s = f"{cur:,.0f}" if cur > 1000 else f"{cur:,.2f}"
        return (f"<div style='display:flex;align-items:center;gap:4px;"
                f"padding:2px 0;font-size:11px'>"
                f"<span>{flag}</span>"
                f"<span style='flex:1;color:#9CA3AF'>{label}</span>"
                f"<span style='font-family:monospace;font-size:10px;"
                f"color:#0D1117'>{val_s}</span>"
                f"<span style='font-size:10px;color:{col};margin-left:4px'>"
                f"{arr}{abs(chg):.1f}%</span></div>")

    _global_html = (
        _idx_row("🇺🇸","나스닥",  "QQQ")      +
        _idx_row("🇯🇵","닛케이",  "NIKKEI")   +
        _idx_row("🇨🇳","상하이",  "SHANGHAI") +
        _idx_row("🇭🇰","항셍",    "HANGSENG") +
        _idx_row("🇩🇪","DAX",     "DAX")      +
        _idx_row("🇬🇧","FTSE",    "FTSE")
    )
    global_panel_placeholder.markdown(_global_html, unsafe_allow_html=True)
except: pass

try:
    # ④ 한국 시장
    def _kr_row(label, key, fmt="int"):
        s = mkt.get(key)
        if s is None or s.empty: return ""
        cur  = float(s.iloc[-1])
        prev = float(s.iloc[-2]) if len(s)>1 else cur
        chg  = (cur - prev) / prev * 100
        col  = "#15803d" if chg>0 else ("#B91C1C" if chg<0 else "#9CA3AF")
        arr  = "▲" if chg>0 else ("▼" if chg<0 else "―")
        if fmt=="int":  val_s = f"{cur:,.0f}"
        elif fmt=="fx": val_s = f"{cur:,.1f}"
        else:           val_s = f"{cur:.2f}"
        return (f"<div style='display:flex;justify-content:space-between;"
                f"align-items:center;padding:3px 0;border-bottom:0.5px solid #F3F4F6;"
                f"font-size:11px'>"
                f"<span style='color:#9CA3AF'>{label}</span>"
                f"<span style='font-family:monospace;font-weight:500;color:#0D1117'>{val_s}</span>"
                f"<span style='color:{col};font-size:10px'>{arr} {abs(chg):.2f}%</span></div>")

    _kr_html = (_kr_row("KOSPI",   "KOSPI")  +
                _kr_row("KOSDAQ",  "KOSDAQ") +
                _kr_row("USD/KRW", "USDKRW", "fx"))
    if _kr_html:
        kr_panel_placeholder.markdown(_kr_html, unsafe_allow_html=True)
    else:
        kr_panel_placeholder.markdown(
            "<div style='font-size:10px;color:#9CA3AF'>한국 시장 데이터 로드 중...</div>",
            unsafe_allow_html=True)
except: pass

# ─── DATA STATUS 업데이트 (데이터 로드 완료 후) ──────────
try:
    _now_str = datetime.now().strftime('%H:%M:%S')
    _ds_html = "<div style='margin-top:2px;font-family:Space Mono,monospace'>"

    # ── FRED 지표 + 기준일 통합 (V82) ────────────────────
    _ds_html += ("<div style='font-size:9px;color:#9CA3AF;"
                 "letter-spacing:1px;margin-bottom:4px'>FRED 지표</div>")
    _fred_meta = [
        ("M2",          "M2 통화량",       "4주 지연"),
        ("RRP",         "역레포 RRP",      "익일"),
        ("TGA",         "TGA 재무부",      "익일"),
        ("Reserves",    "은행 준비금",     "주간"),
        ("RealRate",    "실질금리",        "익일"),
        ("CreditSpread","크레딧 스프레드", "익일"),
        ("FedFunds",    "기준금리",        "월간"),
    ]
    for _key, _label, _delay in _fred_meta:
        _s   = fred_data.get(_key)
        _has = _s is not None and isinstance(_s, pd.Series) and len(_s) > 0
        _icon = "✅" if _has else ("❌" if not is_placeholder(FRED_API_KEY) else "○")
        _ic   = "#166534" if _has else ("#B91C1C" if not is_placeholder(FRED_API_KEY) else "#9CA3AF")
        if _has:
            _dt = _s.index[-1]
            _dt_s = _dt.strftime('%m-%d') if hasattr(_dt,'strftime') else str(_dt)[5:10]
            _dp = f"<span style='color:#9CA3AF;font-size:9px'>{_dt_s}({_delay})</span>"
        else:
            _dp = "<span style='color:#9CA3AF;font-size:9px'>—</span>"
        _ds_html += (
            f"<div style='display:flex;align-items:center;gap:3px;"
            f"padding:1px 0;font-size:10px;color:{_ic}'>"
            f"{_icon} <span style='flex:1'>{_label}</span>{_dp}</div>"
        )

    # ── 시장 지표 ─────────────────────────────────────────
    _ds_html += ("<div style='font-size:9px;color:#9CA3AF;margin:4px 0 3px;"
                 "border-top:0.5px solid #F3F4F6;padding-top:3px'>시장 지표</div>")
    for _lbl, _key in [("QQQ","QQQ"),("SPY","SPY"),("VIX","VIX"),("10Y","TNX")]:
        _s   = mkt.get(_key)
        _has = _s is not None and isinstance(_s, pd.Series) and len(_s) > 0
        _icon = "✅" if _has else "❌"
        _ic   = "#166534" if _has else "#B91C1C"
        if _has:
            _dt = _s.index[-1]
            _dt_s = _dt.strftime('%m-%d') if hasattr(_dt,'strftime') else str(_dt)[5:10]
            _dp = f"<span style='color:#9CA3AF;font-size:9px'>{_dt_s}(15분)</span>"
        else:
            _dp = "<span style='color:#9CA3AF;font-size:9px'>—</span>"
        _ds_html += (
            f"<div style='display:flex;align-items:center;gap:3px;"
            f"padding:1px 0;font-size:10px;color:{_ic}'>"
            f"{_icon} <span style='flex:1'>{_lbl}</span>{_dp}</div>"
        )

    # ── 종목 데이터 ───────────────────────────────────────
    _ds_html += ("<div style='font-size:9px;color:#9CA3AF;margin:4px 0 3px;"
                 "border-top:0.5px solid #F3F4F6;padding-top:3px'>종목 데이터</div>")
    _ok_n = len(TICKERS) - len(failed_tickers)
    _tk_c = "#166534" if _ok_n==len(TICKERS) else "#92400E"
    _ds_html += (
        f"<div style='display:flex;align-items:center;gap:3px;"
        f"padding:1px 0;font-size:10px;color:{_tk_c}'>"
        f"{'✅' if _ok_n==len(TICKERS) else '⚠️'} "
        f"<span style='flex:1'>{_ok_n}/{len(TICKERS)} 수집</span>"
        f"<span style='color:#9CA3AF;font-size:9px'>{_now_str}</span></div>"
    )
    if failed_tickers:
        _fs = ', '.join(failed_tickers[:5]) + ('…' if len(failed_tickers)>5 else '')
        _ds_html += f"<div style='font-size:9px;color:#B91C1C;padding-left:12px'>❌ {_fs}</div>"

    # S&P500 PER
    _pe_icon = "✅" if pe_current is not None else "⚠️"
    _pe_col  = "#166534" if pe_current is not None else "#92400E"
    _pe_src  = ""
    if pe_current is not None:
        if pe_data is not None and len(pe_data)>5: _pe_src="multpl"
        elif pe_data is not None and len(pe_data)==1:
            _pv = float(pe_data["Value"].iloc[0])
            _pe_src = "yf추정" if abs(_pv-23.5)>0.01 else "기본추정"
    _ds_html += (
        f"<div style='display:flex;align-items:center;gap:3px;"
        f"padding:1px 0;font-size:10px;color:{_pe_col}'>"
        f"{_pe_icon} <span style='flex:1'>S&P500 PER</span>"
        f"<span style='color:#9CA3AF;font-size:9px'>{_pe_src}</span></div>"
    )
    _ds_html += "</div>"
    status_placeholder.markdown(_ds_html, unsafe_allow_html=True)
except Exception as _ds_err:
    pass

# ─────────────────────────────────────────────────────────
# 보고서 생성 함수
# ─────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────
# 탭 정의 (V44)
# ─────────────────────────────────────────────────────────
tab0, tab1, tab2, tab3, tab4 = st.tabs([
    'STEP1 💧 유동성',
    'STEP2 📡 섹터 강도',
    'STEP3 📊 종목 선별',
    'STEP4 💰 매수 실행',
    '📅 기타',
])

# ── V93: 지표 설명 expander 헬퍼 ─────────────────────────
def _indicator_explain(key):
    """지표 설명 — JSON 기반, 편집 모드에서 직접 수정 가능"""
    # ── 기본값 (코드 내장) ──
    _defaults = {
        "FedFunds": {
            "title": "기준금리가 오르면 왜 주가가 하락할까?",
            "up_title": "📈 기준금리 올리면 (긴축)",
            "up_flow": ["돈 빌리는 이자 비쌈","기업이 투자 줄임","소비자도 소비 줄임","→ 기업 이익 감소 → 주가 하락"],
            "dn_title": "📉 기준금리 내리면 (완화)",
            "dn_flow": ["대출 이자 저렴해짐","기업이 마음껏 투자","소비자 지갑이 열림","→ 기업 이익 증가 → 주가 상승"],
            "tip": "💡 연준이 금리를 0%로 낮춘 2020~21년에 나스닥이 2배 올랐습니다",
        },
        "M2": {
            "title": "M2가 늘면 왜 주가가 오를까?",
            "up_title": "📈 M2 증가하면",
            "up_flow": ["은행에 돈이 많아짐","대출이 쉬워짐","기업이 투자 늘림","→ 주가 상승"],
            "dn_title": "📉 M2 감소하면",
            "dn_flow": ["시장에서 돈이 빠짐","대출 어려워짐","기업 투자 줄어듦","→ 주가 하락"],
            "tip": "💡 2022년 M2가 처음으로 줄었을 때 나스닥이 -33% 하락했습니다",
        },
        "RRP": {
            "title": "역레포(RRP)가 줄면 왜 시장에 좋을까?",
            "up_title": "📉 RRP 높으면 (나쁨)",
            "up_flow": ["은행이 남는 돈을 연준에 보관 중","그 돈이 주식·채권 시장에 안 들어옴","시장 유동성 줄어듦","→ 자산 가격 정체"],
            "dn_title": "📈 RRP 줄어들면 (좋음)",
            "dn_flow": ["은행이 연준에서 돈을 빼서 시장에 투자","주식·채권 시장으로 돈 유입","매수 압력 증가","→ 자산 가격 상승"],
            "tip": "💡 2022~24년 RRP가 2.5조→0으로 줄면서 나스닥이 반등했습니다",
        },
        "TGA": {
            "title": "재무부 계좌(TGA)가 내려가면 왜 시장에 좋을까?",
            "up_title": "📉 TGA 높으면 (나쁨)",
            "up_flow": ["정부가 세금을 걷어서 쌓아둔 것","시중에서 돈이 정부 금고로 흡수됨","시장 유동성 감소","→ 자산 가격 압박"],
            "dn_title": "📈 TGA 낮으면 (좋음)",
            "dn_flow": ["정부가 지출 중","정부 돈이 시장으로 나옴","시중 유동성 증가","→ 자산 가격 상승"],
            "tip": "💡 2023년 부채한도 협상 당시 TGA가 급증해 시장이 흔들렸습니다",
        },
        "Reserves": {
            "title": "은행 준비금이 충분해야 하는 이유",
            "up_title": "📈 준비금 충분하면 (좋음)",
            "up_flow": ["은행이 여유 자금 보유","기업·가계에 대출 잘 해줌","경제 활동 활발해짐","→ 주가 상승"],
            "dn_title": "📉 준비금 부족하면 (위험)",
            "dn_flow": ["은행들이 서로 돈 빌려주기 꺼림","단기 금리가 갑자기 폭등","신용 경색 발생","→ 2019년 레포 위기 재발 위험"],
            "tip": "💡 2019년 준비금이 1.5조$까지 줄자 단기 금리가 하루 만에 10%로 폭등했습니다",
        },
        "RealRate": {
            "title": "실질금리가 오르면 왜 나스닥이 하락할까?",
            "up_title": "📉 실질금리 높으면 (나쁨)",
            "up_flow": ["채권만 들고 있어도 실질 이익 발생","굳이 위험한 주식 살 필요 없음","특히 PER 50배 이상 성장주가 타격","→ 나스닥 하락"],
            "dn_title": "📈 실질금리 낮거나 마이너스면 (좋음)",
            "dn_flow": ["채권 실질 수익이 없거나 손실","더 높은 수익 찾아 주식으로 이동","특히 고성장 기술주 선호","→ 나스닥 상승"],
            "tip": "💡 2022년 실질금리가 -1.5%→+4%로 오르자 NVDA·META가 70% 이상 하락했습니다",
        },
        "CPI": {
            "title": "CPI(물가)가 오르면 왜 주가가 하락할까?",
            "up_title": "📈 CPI 높으면 (물가 상승)",
            "up_flow": ["물가가 오른다 = 돈의 가치가 떨어진다","연준이 금리를 올려서 물가를 잡으려 함","금리 오르면 기업 대출 비용 증가","→ 기업 이익 감소 → 주가 하락"],
            "dn_title": "📉 CPI 낮으면 (물가 안정)",
            "dn_flow": ["물가가 안정됐다 = 연준이 금리 안 올려도 됨","오히려 경기 부양 위해 금리 인하 가능","대출 비용 낮아짐 → 기업 투자 늘어남","→ 기업 이익 증가 → 주가 상승"],
            "tip": "💡 연준의 목표 물가는 2%. CPI가 2%를 크게 초과하면 금리 인상 압박이 커집니다",
        },
        "BondYield": {
            "title": "미국 채권금리가 오르면 왜 나스닥이 하락할까?",
            "up_title": "📈 채권금리 오르면",
            "up_flow": ["미국 국채 이자가 많아짐","안전한데 이자도 높으니 채권으로 돈 이동","특히 전 세계 돈이 미국 채권으로 몰림","→ 주식 팔고 채권 사기 → 주가 하락"],
            "dn_title": "📉 채권금리 내리면",
            "dn_flow": ["채권 이자가 낮아 매력 없음","더 높은 수익 찾아 주식으로 이동","특히 고성장 기술주 선호 증가","→ 나스닥 자금 유입 → 주가 상승"],
            "tip": "💡 2022년 10년물 금리가 1.5%→4.5%로 오르자 나스닥이 -33% 하락했습니다",
        },
        "CreditSpread": {
            "title": "크레딧 스프레드가 벌어지면 왜 위험할까?",
            "up_title": "📉 스프레드 넓어지면 (나쁨)",
            "up_flow": ["투자자들이 '기업이 망할 수도 있다' 생각","기업 채권 아무도 안 사줌","기업이 돈 조달 어려워짐","→ 주식도 같이 하락"],
            "dn_title": "📈 스프레드 좁으면 (좋음)",
            "dn_flow": ["투자자들이 기업 부도를 걱정 안 함","기업 채권 잘 팔림","기업이 쉽게 투자 자금 조달","→ 주가 상승"],
            "tip": "💡 2008년 스프레드가 22%까지 벌어졌을 때 S&P500이 -57% 폭락했습니다",
        },
    }

    # JSON 저장된 값 우선 사용 (없으면 기본값)
    _saved = _load_explains()
    _e = {**_defaults.get(key, {}), **_saved.get(key, {})}
    if not _e: return

    # ── 편집 모드 UI ──────────────────────────────────────
    if st.session_state.get("edit_mode", False):
        st.markdown(
            f"<div style='background:#FFFBEB;border:1px solid #FDE68A;"
            f"border-radius:8px;padding:10px 14px;margin-bottom:6px'>"
            f"<b style='font-size:11px;color:#92400E'>✏️ 편집 모드 — {_e.get('title','')}</b></div>",
            unsafe_allow_html=True)

        _col_l, _col_r = st.columns(2)
        with _col_l:
            new_title    = st.text_input("제목",           value=_e.get("title",""),    key=f"ed_title_{key}")
            new_up_title = st.text_input("상승 시 제목",    value=_e.get("up_title",""), key=f"ed_up_title_{key}")
            new_up_flow  = st.text_area("상승 시 흐름\n(줄바꿈으로 구분)",
                                        value="\n".join(_e.get("up_flow",[])),
                                        height=120, key=f"ed_up_flow_{key}")
        with _col_r:
            new_tip      = st.text_input("핵심 팁",         value=_e.get("tip",""),      key=f"ed_tip_{key}")
            new_dn_title = st.text_input("하락 시 제목",    value=_e.get("dn_title",""), key=f"ed_dn_title_{key}")
            new_dn_flow  = st.text_area("하락 시 흐름\n(줄바꿈으로 구분)",
                                        value="\n".join(_e.get("dn_flow",[])),
                                        height=120, key=f"ed_dn_flow_{key}")

        if st.button(f"💾 저장 — {key}", key=f"ed_save_{key}"):
            _all = _load_explains()
            _all[key] = {
                "title":    new_title,
                "up_title": new_up_title,
                "up_flow":  [l.strip() for l in new_up_flow.split("\n") if l.strip()],
                "dn_title": new_dn_title,
                "dn_flow":  [l.strip() for l in new_dn_flow.split("\n") if l.strip()],
                "tip":      new_tip,
            }
            if _save_explains(_all):
                st.success(f"✅ {key} 저장 완료! 앱을 새로고침하면 반영됩니다.")
            else:
                st.error("❌ 저장 실패 — explanations.json 쓰기 권한 확인")
        st.markdown("---")
        # 편집 모드에서도 미리보기 표시 (아래 동일 코드로 이어짐)

    # ── 일반 표시 (HTML 표 형식) ──────────────────────────
    _up_rows = "".join(
        f"<div style='font-size:11px;color:#374151;padding:2px 0'>"
        f"<span style='color:#1D4ED8;margin-right:4px'>&#8594;</span>{fl}</div>"
        for fl in _e['up_flow'])
    _dn_rows = "".join(
        f"<div style='font-size:11px;color:#374151;padding:2px 0'>"
        f"<span style='color:#059669;margin-right:4px'>&#8594;</span>{fl}</div>"
        for fl in _e['dn_flow'])
    _html = f"""
<details style='margin:4px 0;border:0.5px solid #E2E6ED;border-radius:8px;overflow:hidden'>
<summary style='cursor:pointer;padding:7px 12px;background:#F9FAFB;
  font-size:11px;color:#374151;list-style:none;user-select:none'>
  {_e['title']}</summary>
<div style='padding:10px 14px'>
  <div style='display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:8px'>
    <div style='background:#FEF2F2;border-radius:6px;padding:10px'>
      <div style='font-size:11px;font-weight:600;color:#B91C1C;margin-bottom:6px'>{_e['up_title']}</div>
      {_up_rows}
    </div>
    <div style='background:#F0FDF4;border-radius:6px;padding:10px'>
      <div style='font-size:11px;font-weight:600;color:#15803d;margin-bottom:6px'>{_e['dn_title']}</div>
      {_dn_rows}
    </div>
  </div>
  <div style='font-size:11px;color:#6B7280;background:#F9FAFB;
    border-radius:6px;padding:8px 10px'>{_e['tip']}</div>
</div></details>
"""
    st.markdown(_html, unsafe_allow_html=True)



# ─────────────────────────────────────────────────────────
# _render_stepbar — 탭 상단 3단계 스텝 바 (전역 함수, V93j)
# ─────────────────────────────────────────────────────────
def _render_stepbar(current_step, liq_stage, n_buy):
    """상단 3단계 스텝 바"""
    _s = ["STEP1 완료 ✓" if current_step>1 else ("STEP1 진행중" if current_step==1 else "STEP1"),
          "STEP2 완료 ✓" if current_step>2 else ("STEP2 진행중" if current_step==2 else "STEP2"),
          "STEP3 완료 ✓" if current_step>3 else ("STEP3 진행중" if current_step==3 else "STEP3")]
    _c = ["#22c55e" if current_step>1 else ("#1D4ED8" if current_step==1 else "#9CA3AF"),
          "#22c55e" if current_step>2 else ("#1D4ED8" if current_step==2 else "#9CA3AF"),
          "#22c55e" if current_step>3 else ("#1D4ED8" if current_step==3 else "#9CA3AF")]
    _bg = ["#f0fdf4" if current_step>1 else ("#eff6ff" if current_step==1 else "#f9fafb"),
           "#f0fdf4" if current_step>2 else ("#eff6ff" if current_step==2 else "#f9fafb"),
           "#f0fdf4" if current_step>3 else ("#eff6ff" if current_step==3 else "#f9fafb")]
    _desc = ["시장에 돈이 있는가?", "강한 종목을 찾는다", "얼마나 살 것인가?"]
    _nums = ["✓" if current_step>i+1 else str(i+1) for i in range(3)]
    _html = "<div style='display:flex;align-items:center;gap:4px;margin-bottom:12px'>"
    for i in range(3):
        _mr = "margin-right:4px;" if i < 2 else ""
        _html += (
            f"<div style='display:flex;align-items:center;gap:7px;flex:1;"
            f"background:{_bg[i]};border:0.5px solid {_c[i]}44;"
            f"border-radius:8px;padding:8px 12px;{_mr}'>"
            f"<div style='width:22px;height:22px;border-radius:50%;background:{_c[i]};"
            f"color:white;display:flex;align-items:center;justify-content:center;"
            f"font-size:11px;font-weight:700;flex-shrink:0'>{_nums[i]}</div>"
            f"<div><div style='font-size:11px;font-weight:600;color:{_c[i]}'>{_s[i]}</div>"
            f"<div style='font-size:10px;color:{_c[i]};opacity:0.7'>{_desc[i]}</div></div>"
            f"</div>"
        )
    _html += "</div>"
    st.markdown(_html, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────
# 섹터 ETF 데이터 수집 (V93n)
# ─────────────────────────────────────────────────────────
SECTOR_ETFS = {
    "기술":      "XLK",
    "반도체":    "SOXX",
    "헬스케어":  "XLV",
    "금융":      "XLF",
    "에너지":    "XLE",
    "소비재":    "XLY",
    "유틸리티":  "XLU",
    "부동산":    "XLRE",
    "소재":      "XLB",
}

@st.cache_data(ttl=900, show_spinner=False)
def load_sector_data(_bust=0):
    res = {}
    for name, etf in SECTOR_ETFS.items():
        try:
            s = get_close(etf, "1y")
            if s is None or len(s) < 22: continue
            price   = float(s.iloc[-1])
            ret_1m  = round((price / float(s.iloc[-22]) - 1) * 100, 2) if len(s) >= 22 else 0
            ret_3m  = round((price / float(s.iloc[-63]) - 1) * 100, 2) if len(s) >= 63 else 0
            ma20    = float(s.rolling(20).mean().iloc[-1])
            ma50    = float(s.rolling(50).mean().iloc[-1]) if len(s) >= 50 else price
            # RS vs QQQ
            qqq_s   = get_close("QQQ", "1y")
            qqq_ret = (float(qqq_s.iloc[-1])/float(qqq_s.iloc[-22])-1)*100 if qqq_s is not None and len(qqq_s)>=22 else 0
            rs      = round(ret_1m - qqq_ret, 2)
            res[name] = {
                "etf": etf, "price": price,
                "ret_1m": ret_1m, "ret_3m": ret_3m,
                "above_ma20": price > ma20,
                "above_ma50": price > ma50,
                "rs_vs_qqq": rs,
                "series": s,
            }
        except: pass
    return res

sector_data = load_sector_data(_bust=st.session_state.get("cache_key",0))

# ─────────────────────────────────────────────────────────
# TAB 1 — STEP2 섹터 강도 (V93n)
# ─────────────────────────────────────────────────────────
with tab1:
    _render_stepbar(2, LIQ_ACTION.get("stage", 0), 0)
    st.markdown('<div class="sec-header">📡 섹터 강도 분석 (STEP 2)</div>',
                unsafe_allow_html=True)

    # 미션 박스
    st.markdown("""
    <div style='background:#F5F3FF;border:0.5px solid #C4B5FD;border-radius:8px;
         padding:9px 14px;margin-bottom:12px;font-size:11px;color:#374151'>
      <b style='color:#6D28D9'>✅ STEP2 에서 확인할 것</b><br>
      ① 1개월 수익률 상위 섹터 → 지금 돈이 몰리는 곳<br>
      ② MA20 위 ✅ + 수익률 양수 → 강한 섹터 조건<br>
      ③ RS(QQQ 대비) 양수 → 나스닥보다 강한 섹터<br>
      <span style='color:#9CA3AF'>강한 섹터에서 강한 종목을 선별하면 승률이 올라갑니다</span>
    </div>
    """, unsafe_allow_html=True)

    if sector_data:
        # go는 이미 import됨
        # 1M 수익률 바 차트
        _sec_df = sorted(sector_data.items(), key=lambda x: x[1]["ret_1m"], reverse=True)
        _names  = [x[0] for x in _sec_df]
        _ret1m  = [x[1]["ret_1m"] for x in _sec_df]
        _ma20   = [x[1]["above_ma20"] for x in _sec_df]
        _rs     = [x[1]["rs_vs_qqq"] for x in _sec_df]

        # 색상: MA20 위 + 양수 = 초록, MA20 위 + 음수 = 주황, MA20 아래 = 빨강
        _colors = []
        for i, (nm, d) in enumerate(_sec_df):
            if d["above_ma20"] and d["ret_1m"] > 0: _colors.append("#22c55e")
            elif d["above_ma20"]: _colors.append("#F59E0B")
            else: _colors.append("#EF4444")

        _fig_sec = go.Figure()
        _fig_sec.add_trace(go.Bar(
            x=_names, y=_ret1m,
            marker_color=_colors,
            text=[f"{v:+.1f}%" for v in _ret1m],
            textposition="outside",
            textfont=dict(size=11, color="#374151"),
            hovertemplate="<b>%{x}</b><br>1M 수익률: %{y:.1f}%<extra></extra>"
        ))
        _fig_sec.add_hline(y=0, line_color="#E5E7EB", line_width=1)
        _fig_sec.update_layout(
            template="plotly_white", paper_bgcolor="#FFFFFF", plot_bgcolor="#FAFBFC",
            height=260, margin=dict(l=4,r=4,t=28,b=4),
            title=dict(text="섹터별 1개월 수익률 vs QQQ 기준", font=dict(size=12)),
            xaxis=dict(gridcolor="#EBEDF0", tickfont=dict(size=10)),
            yaxis=dict(gridcolor="#EBEDF0", ticksuffix="%"),
            showlegend=False)
        st.plotly_chart(_fig_sec, use_container_width=True, key="sec_bar_chart")

        # 강한 섹터 / 약한 섹터
        _strong = [(nm, d) for nm, d in _sec_df if d["above_ma20"] and d["ret_1m"] > 0]
        _weak   = [(nm, d) for nm, d in _sec_df if not d["above_ma20"] or d["ret_1m"] < -2]

        # 강한/약한 섹터 (PC: 2열)
        _c1, _c2 = st.columns(2)
        with _c1:
            st.markdown(
                "<div style='background:#F0FDF4;border:0.5px solid #86EFAC;"
                "border-radius:8px;padding:10px 14px'>"
                "<div style='font-size:11px;font-weight:600;color:#15803d;"
                "margin-bottom:6px'>💪 강한 섹터</div>" +
                "".join(f"<div style='font-size:11px;color:#374151;padding:2px 0'>"
                        f"✅ <b>{nm}</b> ({d['etf']}) &nbsp;"
                        f"+{d['ret_1m']:.1f}% &nbsp; RS {d['rs_vs_qqq']:+.1f}% &nbsp; "
                        f"<span style='color:#1D4ED8'>점수 {d.get('sector_score',0):.0f}</span></div>"
                        for nm, d in _strong) +
                ("<div style='font-size:11px;color:#9CA3AF'>없음</div>" if not _strong else "") +
                "</div>", unsafe_allow_html=True)
        with _c2:
            st.markdown(
                "<div style='background:#FEF2F2;border:0.5px solid #FECACA;"
                "border-radius:8px;padding:10px 14px'>"
                "<div style='font-size:11px;font-weight:600;color:#B91C1C;"
                "margin-bottom:6px'>📉 약한 섹터</div>" +
                "".join(f"<div style='font-size:11px;color:#374151;padding:2px 0'>"
                        f"❌ <b>{nm}</b> ({d['etf']}) &nbsp;"
                        f"{d['ret_1m']:.1f}% &nbsp; "
                        f"<span style='color:#B91C1C'>점수 {d.get('sector_score',0):.0f}</span></div>"
                        for nm, d in _weak) +
                ("<div style='font-size:11px;color:#9CA3AF'>없음</div>" if not _weak else "") +
                "</div>", unsafe_allow_html=True)

        # 섹터 RS 상세 테이블
        st.markdown("<div style='margin:10px 0'></div>", unsafe_allow_html=True)
        _sec_table = []
        for nm, d in _sec_df:
            _sec_table.append({
                "섹터": nm,
                "ETF": d["etf"],
                "현재가": f"${d['price']:.1f}",
                "1M 수익률": f"{d['ret_1m']:+.1f}%",
                "3M 수익률": f"{d['ret_3m']:+.1f}%",
                "RS vs QQQ": f"{d['rs_vs_qqq']:+.1f}%",
                "MA20": "✅ 위" if d["above_ma20"] else "❌ 아래",
                "강도": "🔥 강함" if d["above_ma20"] and d["ret_1m"]>0 else ("🟡 보통" if d["above_ma20"] else "🔴 약함"),
            })
        
        _df_sec = pd.DataFrame(_sec_table)
        st.dataframe(_df_sec, use_container_width=True, hide_index=True,
                     key="sec_detail_table",
                     column_config={
                         "1M 수익률": st.column_config.TextColumn("1M %", width="small"),
                         "3M 수익률": st.column_config.TextColumn("3M %", width="small"),
                         "RS vs QQQ": st.column_config.TextColumn("RS", width="small"),
                         "MA20": st.column_config.TextColumn("MA20", width="small"),
                         "강도": st.column_config.TextColumn("강도", width="small"),
                     })

        # 다음 단계 안내
        if _strong:
            _top = _strong[0][0]
            st.markdown(
                f"<div style='background:#EFF6FF;border:0.5px solid #BFDBFE;"
                f"border-radius:8px;padding:10px 14px;margin-top:8px;font-size:11px;color:#374151'>"
                f"<b style='color:#1D4ED8'>→ STEP3으로</b> &nbsp;|&nbsp; "
                f"가장 강한 섹터: <b>{_top}</b> &nbsp;|&nbsp; "
                f"종목 선별 탭에서 이 섹터 종목을 우선 확인하세요</div>",
                unsafe_allow_html=True)
    else:
        st.info("섹터 데이터 로드 중... 잠시 후 새로고침하세요.")


# TAB 0 — 유동성
# ═══════════════════════════════════
with tab0:
    _s0 = LIQ_ACTION.get("stage", 0)
    _render_stepbar(1, _s0, 0)
    # STEP1 미션 박스
    _liq_ok = _s0 >= 3
    _pct_map = {5:"80~100%", 4:"50~70%", 3:"20~40%", 2:"0%", 1:"0%"}
    _step1_msg = "STEP1 통과 - STEP2 종목 선별로 이동하세요" if _liq_ok else "유동성 단계 부족 - 신규 매수 보류"
    _step1_ico = "ok" if _liq_ok else "warn"
    st.markdown(
        f"<div style='background:{'#F0FDF4' if _liq_ok else '#FEF2F2'};"
        f"border:0.5px solid {'#86EFAC' if _liq_ok else '#FECACA'};"
        f"border-radius:8px;padding:9px 14px;margin-bottom:12px;font-size:11px;color:#374151'>"
        f"<b style='color:{'#15803d' if _liq_ok else '#B91C1C'}'>"
        f"{'✅' if _liq_ok else '⚠️'} {_step1_msg}</b>"
        f"&nbsp;|&nbsp; 현재 {_s0}단계 &nbsp;|&nbsp;"
        f"투자금의 {_pct_map.get(_s0, '—')} 투입 가능</div>",
        unsafe_allow_html=True)
    st.markdown('<div class="sec-header">💧 글로벌 유동성 흐름 분석 (Global Liquidity OS)</div>',
                unsafe_allow_html=True)

    # FRED API 없을 때 안내
    if is_placeholder(FRED_API_KEY):
        st.markdown("""
        <div style="background:#FFF9EC;border:1px solid #F59E0B;border-radius:10px;
             padding:16px 20px;margin:8px 0">
          <div style="font-size:14px;font-weight:700;color:#78350F;margin-bottom:8px">
            ⚠️ FRED API 키가 없으면 이 탭의 데이터가 표시되지 않습니다
          </div>
          <div style="font-size:12px;color:#92400E;line-height:1.8">
            <b>지금 바로 무료로 발급받으세요 (2분 소요):</b><br>
            1. <a href="https://fred.stlouisfed.org/docs/api/api_key.html" target="_blank"
               style="color:#1D4ED8;font-weight:600">fred.stlouisfed.org</a> 접속 →
            2. 계정 생성 → 3. API 키 발급 →
            4. 왼쪽 사이드바 [🔑 API 키 설정]에 입력 후 [💾 저장]<br><br>
            <b>FRED API 없이도 동작하는 기능:</b>
            📊 종목테이블 탭 (RS·AI Score·브레이크아웃) &nbsp;|&nbsp;
            📄 보고서 탭 (기본 판단)
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════
    # V62: LAYER 1 + 5단계 바 제거 → 통합 테이블 헤더에 흡수
    # LIQ_ACTION 변수는 테이블 헤더에서 사용
    # ══════════════════════════════════════════════════════
    _la      = LIQ_ACTION
    _mkt_lbl = MKT_KR.get(mkt_status, MKT_KR["NEUTRAL"])




    # ════════════════════════════════════════════════════
    # 📋 현재 글로벌 유동성 종합 상태 — 탭 최상단 (V65)
    # ════════════════════════════════════════════════════
    def _tier5(score):
        """점수 → (dot색, 값색, 배지bg, 배지글색, bar색, 단계명)"""
        if score is None:
            return "#9CA3AF","#9CA3AF","#F3F4F6","#6B7280","#9CA3AF","N/A"
        if score >= 80:
            return "#22c55e","#16a34a","#dcfce7","#15803d","#22c55e","강한 우호"
        if score >= 65:
            return "#3b82f6","#2563eb","#dbeafe","#1d4ed8","#3b82f6","우호"
        if score >= 40:
            return "#f59e0b","#d97706","#fef9c3","#a16207","#f59e0b","중립"
        if score >= 20:
            return "#f97316","#ea580c","#ffedd5","#c2410c","#f97316","주의"
        return "#ef4444","#dc2626","#fee2e2","#b91c1c","#ef4444","위험"

    # ── 추세 연속 횟수 계산 ───────────────────────────────
    def _streak_info(series, good_direction="up"):
        """최근 데이터에서 연속 상승/하락 횟수 계산"""
        if series is None or not isinstance(series, pd.Series) or len(series) < 4:
            return "", ""
        recent = series.dropna().tail(12)
        if len(recent) < 3:
            return "", ""
        diffs = recent.diff().dropna()
        if len(diffs) == 0:
            return "→", "보합"
        last_dir = "up" if float(diffs.iloc[-1]) > 0 else ("dn" if float(diffs.iloc[-1]) < 0 else "flat")
        count = 1
        for d in reversed(list(diffs.iloc[:-1])):
            cur_dir = "up" if float(d) > 0 else ("dn" if float(d) < 0 else "flat")
            if cur_dir == last_dir:
                count += 1
            else:
                break
        unit = "개월" if len(recent) <= 12 else "주"
        if last_dir == "up":
            arrow = "↑"
            label = f"{count}{unit} 연속 상승"
        elif last_dir == "dn":
            arrow = "↓"
            label = f"{count}{unit} 연속 하락"
        else:
            arrow = "→"
            label = "보합"
        is_good = (last_dir == good_direction)
        return arrow, label, is_good

    # ── 값 포맷 헬퍼 ─────────────────────────────────────
    def _fmt_val(val, unit):
        """V70 BUG FIX: FRED B$ 지표는 이미 '십억달러' 단위로 제공됨
        M2SL=22400 → $22.4T / RRPONTSYD=312 → $312B
        이전 코드는 /1e9 또는 /1e12로 나눠 $0B 오류 발생"""
        if val is None: return "N/A"
        if unit == "B$":
            # val 단위: 십억달러(B$)
            if abs(val) >= 1000:            # 1조 이상 → T 표시
                return f"${val/1000:.2f}T"
            elif abs(val) >= 1:             # 10억 이상 → B 표시
                return f"${val:.0f}B"
            else:                           # 소수 → 소수점 표시
                return f"${val:.2f}B"
        return f"{val:.2f}{unit}"

    # ── 지표 정의 ─────────────────────────────────────────
    # (이름, FRED코드, IND키, 단위, 좋은방향, 해석함수)
    def _ff_interp(val):
        if val is None: return "데이터 없음"
        if val <= 1.5:
            return f"{val:.2f}% — 제로금리 수준. 돈 빌리는 비용 최저 → 성장주 최고 환경"
        if val <= 3.0:
            return f"{val:.2f}% — 중립금리 이하. 유동성 친화 구간 · 주식 우호"
        if val <= 4.5:
            return f"{val:.2f}% — 긴축 구간. 소비·투자 위축 시작 · 방향 주시"
        return f"{val:.2f}% — 고금리 압박. 대출 비용 증가 · 성장주 밸류에이션 하락 압력"

    def _m2_interp(val):
        if val is None: return "데이터 없음"
        try:
            _m2s = fred_data.get("M2")
            pct = None
            if _m2s is not None and len(_m2s) >= 13:
                _now = float(_m2s.iloc[-1]); _prev = float(_m2s.iloc[-13])
                pct = (_now - _prev) / _prev * 100 if _prev > 0 else None
        except: pct = None
        if pct is not None:
            if pct > 6:
                return f"전년비 +{pct:.1f}% 급증 — 과잉 유동성. 인플레이션 재점화 주의"
            if pct > 3:
                return f"전년비 +{pct:.1f}% 증가 — 시장에 돈 풀리는 중 · 주식 우호"
            if pct > 0:
                return f"전년비 +{pct:.1f}% 소폭 증가 — 보합 수준 · 방향 주시"
            if pct > -2:
                return f"전년비 {pct:.1f}% 감소 — 유동성 둔화 · 방어적 접근"
            return f"전년비 {pct:.1f}% 감소 — 2022년형 위험 신호 · 매수 자제"
        v_str = f"${val/1000:.2f}T" if val>=1000 else f"${val:.0f}B"
        return f"{v_str} — 증감률 계산 중"

    def _rrp_interp(val):
        if val is None: return "데이터 없음"
        b = val
        if b < 100:
            return f"${b:.0f}B — 거의 소진. 은행들이 연준 대신 시장에 돈 운용 · 강한 유동성"
        if b < 400:
            return f"${b:.0f}B — 감소 중. 시장으로 자금 복귀 진행 중 · 긍정적"
        if b < 1000:
            return f"${b:.0f}B — 중간 수준. 방향 확인 필요 (감소=좋음/증가=나쁨)"
        return f"${b/1000:.2f}T — 높은 수준. 금융기관이 돈을 연준에 쌓는 중 · 시장 유동성 흡수"

    def _tga_interp(val):
        if val is None: return "데이터 없음"
        b = val
        if b < 200:
            return f"${b:.0f}B — 매우 낮음. 정부가 적극 지출 중 · 시장에 돈 공급 효과"
        if b < 500:
            return f"${b:.0f}B — 적정 수준. 정상 재정 운영 구간"
        if b < 800:
            return f"${b:.0f}B — 높은 수준. 세수 흡수로 시중 유동성 감소 · 주의"
        return f"${b/1000:.2f}T — 매우 높음. 부채한도 협상 가능성 · 시장 불확실성 증가"

    def _res_interp(val):
        if val is None: return "데이터 없음"
        t = val / 1000
        if t >= 4.0:
            return f"${t:.2f}T — 풍부. 은행 대출 여력 충분 · 신용 시스템 원활"
        if t >= 3.0:
            return f"${t:.2f}T — 안정. 3조$ 안전선 상회 · 위기 없음"
        if t >= 2.0:
            return f"${t:.2f}T — 주의. 3조$ 이하 경계 진입 · 2019년 레포 위기 전 수준"
        return f"${t:.2f}T — 위험. 은행 간 자금 경색 가능 · 연준 개입 가능성"

    def _rr_interp(val):
        if val is None: return "데이터 없음"
        if val <= 0:
            return f"{val:.2f}% — 마이너스 실질금리. 2020-21년 수준 · 성장주 최고 환경"
        if val <= 1.0:
            return f"{val:.2f}% — 낮은 실질금리. NVDA·META류 고PER주 우호 · 진입 유리"
        if val <= 1.8:
            return f"{val:.2f}% — 중간 수준. 성장주에 일부 부담 · 실적 성장이 보완해야"
        if val <= 2.5:
            return f"{val:.2f}% — 2022년 수준 접근. 고PER 성장주 밸류에이션 압박 · 주의"
        return f"{val:.2f}% — 높은 실질금리. PER 50배 이상 종목 구조적 하락 위험"

    def _cs_interp(val):
        if val is None: return "데이터 없음"
        if val <= 2.5:
            return f"{val:.2f}% — 역사적 저점 수준. 시장이 위기를 전혀 안 걱정함 · 매우 우호"
        if val <= 3.5:
            return f"{val:.2f}% — 안정 구간. 기업 부도 공포 없음 · 신용 시장 정상"
        if val <= 5.0:
            return f"{val:.2f}% — 확대 중. 기업 위험 인식 증가 · 2020년 코로나 초기 수준"
        if val <= 8.0:
            return f"{val:.2f}% — 위험. 하드스탑 발동 · 매수 전면 금지. 현금 보유"
        return f"{val:.2f}% — 시스템 위기. 2008년 금융위기 수준 · 전량 청산 후 관망"

    # V66 BUG FIX: liq_v2는 이 시점에 미정의 (탭 하단에서 로드)
    # → series 컬럼을 fred_data.get()으로 교체 (line 946에서 이미 로드됨)
    # IND_SCORE_100.get("key",{}).get("val") 로 현재값 취득
    def _safe_series(key):
        """fred_data에서 series 반환, 없으면 None"""
        s = fred_data.get(key)
        if s is not None and isinstance(s, __import__('pandas').Series) and len(s) > 0:
            return s
        return None

    # 지표명: "이름|한글뜻" 형식으로 확장 (V83)
    _rows_def = [
        ("기준금리|연준이 결정하는 단기 이자율",
            "FEDFUNDS",       "FedFunds",    "%",  "dn", _ff_interp,
            IND_SCORE_100.get("FedFunds",{}).get("val"),    _safe_series("FedFunds")),
        ("M2 통화량|시장에 풀린 전체 돈의 양",
            "M2SL",           "M2",          "B$", "up", _m2_interp,
            IND_SCORE_100.get("M2",{}).get("val"),          _safe_series("M2")),
        ("역레포 RRP|금융기관이 연준에 맡겨둔 돈",
            "RRPONTSYD",      "RRP",         "B$", "dn", _rrp_interp,
            IND_SCORE_100.get("RRP",{}).get("val"),         _safe_series("RRP")),
        ("TGA 재무부|미국 정부의 당좌 계좌 잔고",
            "WDTGAL",         "TGA",         "B$", "dn", _tga_interp,
            IND_SCORE_100.get("TGA",{}).get("val"),         _safe_series("TGA")),
        ("은행 준비금|시장 신용을 움직이는 실탄",
            "WRESBAL",        "Reserves",    "B$", "up", _res_interp,
            IND_SCORE_100.get("Reserves",{}).get("val"),    _safe_series("Reserves")),
        ("실질금리|성장주 가치의 핵심 할인율",
            "DFII10",         "RealRate",    "%",  "dn", _rr_interp,
            IND_SCORE_100.get("RealRate",{}).get("val"),    _safe_series("RealRate")),
        ("크레딧 스프레드|기업 부도 공포의 온도계",
            "BAMLH0A0HYM2",  "CreditSpread","%",  "dn", _cs_interp,
            IND_SCORE_100.get("CreditSpread",{}).get("val"),_safe_series("CreditSpread")),
    ]

    # ── 6체크 종합 판단 (V93m: 6지표 기준) ──────────────────
    _m2_ok   = (IND_SCORE_100.get("M2",{}).get("score") or 0) >= 60
    _res_ok  = (IND_SCORE_100.get("Reserves",{}).get("score") or 0) >= 60
    _rrp_ok  = (IND_SCORE_100.get("RRP",{}).get("score") or 0) >= 50
    _tga_ok  = (IND_SCORE_100.get("TGA",{}).get("score") or 0) >= 50
    _rr_ok   = (IND_SCORE_100.get("RealRate",{}).get("score") or 0) >= 50
    _cs_ok   = (IND_SCORE_100.get("CreditSpread",{}).get("score") or 0) >= 60
    _yes_cnt = sum([_m2_ok, _res_ok, _rrp_ok, _tga_ok, _rr_ok, _cs_ok])

    _chk_data = [
        ("①", "M2 증가",      "돈이 풀리는 중?",      _m2_ok,  "up"),
        ("②", "은행 준비금",   "시장 실탄 충분?",      _res_ok, "up"),
        ("③", "RRP 감소",     "연준 돈 시장 유입?",   _rrp_ok, "dn"),
        ("④", "TGA 감소",     "정부 지출 중?",        _tga_ok, "dn"),
        ("⑤", "실질금리",      "금리 안정적?",        _rr_ok,  "dn"),
        ("⑥", "크레딧 스프레드","기업 부도 걱정 없음?", _cs_ok, "dn"),
    ]

    # 체크 카드 HTML
    _chk_cards = ""
    for _cn, _cl, _cd, _cv, _gd in _chk_data:
        _ci  = "✅" if _cv else "❌"
        _cbg = "#F0FDF4" if _cv else "#FEF2F2"
        _cbc = "#86EFAC" if _cv else "#FECACA"
        _ctc = "#15803d" if _cv else "#B91C1C"
        _ans = "YES" if _cv else "NO"
        _chk_cards += (
            f"<div style='flex:1;background:{_cbg};border:0.5px solid {_cbc};"
            f"border-radius:8px;padding:10px 8px;text-align:center'>"
            f"<div style='font-size:9px;color:{_ctc};opacity:0.7;margin-bottom:3px'>{_cn}</div>"
            f"<div style='font-size:18px;margin-bottom:4px'>{_ci}</div>"
            f"<div style='font-size:11px;font-weight:600;color:{_ctc};margin-bottom:3px'>{_cl}</div>"
            f"<div style='font-size:10px;color:{_ctc};opacity:0.7;margin-bottom:5px'>{_cd}</div>"
            f"<div style='font-size:12px;font-weight:700;color:{_ctc}'>{_ans}</div>"
            f"</div>"
        )

    # 종합 결과 메시지
    if _yes_cnt == 6:
        _res_bg="#F0FDF4"; _res_bc="#86EFAC"; _res_tc="#15803d"
        _res_ico="🚀"; _res_title="6개 모두 YES"
        _res_msg="하락장 걱정 말고 공격적으로 투자할 타이밍!"
    elif _yes_cnt >= 4:
        _res_bg="#EFF6FF"; _res_bc="#BFDBFE"; _res_tc="#1D4ED8"
        _res_ico="✅"; _res_title=f"{_yes_cnt}개 YES"
        _res_msg="좋은 환경입니다. 9조건 충족 종목 선별 후 분할 매수."
    elif _yes_cnt == 3:
        _res_bg="#FFFBEB"; _res_bc="#FDE68A"; _res_tc="#92400E"
        _res_ico="⚠️"; _res_title="3개 YES"
        _res_msg="혼조세. 소량만 진입하고 현금 비중을 유지하세요."
    else:
        _res_bg="#FEF2F2"; _res_bc="#FECACA"; _res_tc="#B91C1C"
        _res_ico="🔴"; _res_title=f"{_yes_cnt}개 YES"
        _res_msg="M2 정체 · 실질금리 고공행진이면 현금 비중 늘리기."

    _score_pct = int(LIQ_SCORE_100)
    _score_bg  = "#F0FDF4" if _score_pct>=65 else ("#FFFBEB" if _score_pct>=40 else "#FEF2F2")
    _score_tc  = "#15803d" if _score_pct>=65 else ("#92400E" if _score_pct>=40 else "#B91C1C")

    st.markdown(
        f"<div style='background:#FFFFFF;border:0.5px solid #E2E6ED;"
        f"border-radius:12px;padding:14px 16px;margin:8px 0'>"
        # 헤더
        f"<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:12px'>"
        f"<span style='font-size:13px;font-weight:600;color:#0D1117'>📋 유동성 종합 판단</span>"
        f"<span style='background:{_score_bg};border:0.5px solid {_score_tc}44;"
        f"border-radius:20px;padding:3px 12px;font-size:12px;font-weight:600;color:{_score_tc}'>"
        f"종합 {_score_pct}점 · {_yes_cnt}/6 체크</span>"
        f"</div>"
        # 4체크 카드
        f"<div style='display:flex;gap:6px;margin-bottom:12px'>{_chk_cards}</div>"
        # 결과 메시지
        f"<div style='background:{_res_bg};border:0.5px solid {_res_bc};"
        f"border-radius:8px;padding:10px 14px;display:flex;align-items:center;gap:10px'>"
        f"<span style='font-size:22px'>{_res_ico}</span>"
        f"<div><div style='font-size:13px;font-weight:600;color:{_res_tc}'>{_res_title}</div>"
        f"<div style='font-size:11px;color:{_res_tc};opacity:0.85;margin-top:2px'>{_res_msg}</div></div>"
        f"</div>"
        f"</div>",
        unsafe_allow_html=True)

    # ── AI 전문가 코멘트 (V93n) ────────────────────────────
    try:
        _rr_val = IND_SCORE_100.get("RealRate",{}).get("val")
        _tga_val = IND_SCORE_100.get("TGA",{}).get("val")
        _m2_score = IND_SCORE_100.get("M2",{}).get("score", 0) or 0
        _rr_score = IND_SCORE_100.get("RealRate",{}).get("score", 0) or 0
        _rrp_score = IND_SCORE_100.get("RRP",{}).get("score", 0) or 0
        _tga_score = IND_SCORE_100.get("TGA",{}).get("score", 0) or 0
        _cs_score  = IND_SCORE_100.get("CreditSpread",{}).get("score", 0) or 0

        # 상황별 동적 코멘트 생성
        _pos = []  # 긍정
        _neg = []  # 경고
        _action = ""

        if _m2_score >= 80:
            _pos.append("M2가 꾸준히 증가 중 — 시장에 돈이 공급되고 있습니다")
        if _rrp_score >= 60:
            _pos.append("RRP 거의 소진 — 연준에 묶인 돈이 시장으로 이동 완료")
        if IND_SCORE_100.get("Reserves",{}).get("score",0) >= 70:
            _pos.append("은행 준비금 충분 — 신용 경색 우려 없음")
        if _cs_score >= 60:
            _pos.append("크레딧 스프레드 안정 — 기업 부도 공포 없음")

        if _rr_val and _rr_val > 1.5:
            _neg.append(f"실질금리 {_rr_val:.2f}% — 성장주 밸류에이션 압박. 1.5% 이하 하락 시 랠리 조건")
        if _tga_score <= 20:
            _neg.append("TGA 높음 — 지금은 유동성 압박이나, 정부 지출 재개 시 시장 공급 기회")
        if _rr_val and _rr_val > 2.0:
            _neg.append("실질금리 2% 초과 — PER 30배 이상 성장주 한 번에 전액 투입 주의")

        # 종합 액션
        if _yes_cnt >= 5:
            _action = "9조건 충족 종목 선별 후 분할 매수(40%→35%→25%) 적극 권장"
        elif _yes_cnt == 4:
            _action = "9조건 충족 종목 분할 매수. 실질금리 동향 주시하며 포지션 조절"
        elif _yes_cnt == 3:
            _action = "소량 선별 진입. 손절(-8%) 반드시 설정. 현금 비중 50% 이상 유지"
        else:
            _action = "신규 매수 보류. 현금 비중 최대화. 실질금리·M2 방향 전환 대기"

        # HTML 렌더링
        _pos_html = "".join(
            f"<div style='font-size:11px;color:#374151;padding:3px 0;display:flex;gap:6px'>"
            f"<span style='color:#15803d;flex-shrink:0'>✅</span><span>{p}</span></div>"
            for p in _pos) if _pos else ""
        _neg_html = "".join(
            f"<div style='font-size:11px;color:#374151;padding:3px 0;display:flex;gap:6px'>"
            f"<span style='color:#B91C1C;flex-shrink:0'>⚠️</span><span>{n}</span></div>"
            for n in _neg) if _neg else ""

        _ai_bg = "#F0FDF4" if _yes_cnt >= 4 else ("#FFFBEB" if _yes_cnt == 3 else "#FEF2F2")
        _ai_bc = "#86EFAC" if _yes_cnt >= 4 else ("#FDE68A" if _yes_cnt == 3 else "#FECACA")

        st.markdown(
            f"<div style='background:#FFFFFF;border:0.5px solid #E2E6ED;"
            f"border-radius:12px;padding:14px 16px;margin:8px 0'>"
            f"<div style='display:flex;align-items:center;gap:8px;margin-bottom:12px'>"
            f"<span style='font-size:16px'>🤖</span>"
            f"<span style='font-size:13px;font-weight:600;color:#0D1117'>AI 유동성 분석</span>"
            f"<span style='font-size:10px;color:#9CA3AF;margin-left:auto'>"
            f"현재 지표 기반 자동 생성</span></div>"
            + (f"<div style='margin-bottom:10px'>"
               f"<div style='font-size:10px;font-weight:500;color:#15803d;"
               f"letter-spacing:1px;margin-bottom:5px'>긍정 신호</div>"
               f"{_pos_html}</div>" if _pos_html else "")
            + (f"<div style='margin-bottom:10px'>"
               f"<div style='font-size:10px;font-weight:500;color:#B91C1C;"
               f"letter-spacing:1px;margin-bottom:5px'>경고 신호</div>"
               f"{_neg_html}</div>" if _neg_html else "")
            + f"<div style='background:{_ai_bg};border:0.5px solid {_ai_bc};"
            f"border-radius:8px;padding:10px 14px'>"
            f"<div style='font-size:10px;font-weight:500;color:#374151;"
            f"letter-spacing:1px;margin-bottom:5px'>전략 판단</div>"
            f"<div style='font-size:12px;font-weight:600;color:#0D1117'>"
            f"→ {_action}</div>"
            f"</div>"
            f"</div>",
            unsafe_allow_html=True)
    except Exception as _ai_err:
        pass

    # ── FRED 확장 데이터 로드 (Core CPI, Median CPI 추가) ──
    EXTENDED_SERIES_V2 = {
        "FedFunds":   "FEDFUNDS",
        "M2":         "M2SL",
        "RRP":        "RRPONTSYD",
        "TGA":        "WDTGAL",       # V68: WTREGEN→WDTGAL (일별 데이터)
        "CPI":        "CPIAUCSL",
        "CoreCPI":    "CPILFESL",
        "T2Y":        "DGS2",      # 2년물
        "T10Y":       "DGS10",     # 10년물
        "T30Y":       "DGS30",     # 30년물
        "CreditSpread":"BAMLH0A0HYM2",
        "RealRate":   "DFII10",
    }

    @st.cache_data(ttl=600, show_spinner=False)
    def load_liq_v2(api_key, _bust=0):
        if is_placeholder(api_key):
            return {}
        result = {}
        for key, sid in EXTENDED_SERIES_V2.items():
            try:
                url = (f"https://api.stlouisfed.org/fred/series/observations"
                       f"?series_id={sid}&api_key={api_key}&file_type=json"
                       f"&sort_order=asc&observation_start=2000-01-01")
                resp = requests.get(url, timeout=15)
                if resp.status_code != 200:
                    continue
                obs  = resp.json().get("observations", [])
                data = {o["date"]: float(o["value"]) for o in obs if o["value"] not in (".", "")}
                s = pd.Series(data)
                s.index = pd.to_datetime(s.index)
                s = s.sort_index()
                if not s.empty:
                    result[key] = s
            except Exception:
                pass
        return result

    liq_v2 = load_liq_v2(FRED_API_KEY, st.session_state.cache_key)

    # 나스닥100 (V88: S&P500 → QQQ로 교체)
    qqq_s = mkt.get("QQQ")

    def _lv(key):
        """최신값 반환 — pandas Series truthiness 오류 방지
        V69: FedFunds는 fred_data 우선 (liq_v2와 값 불일치 방지)
        """
        # FedFunds: fred_data와 IND_SCORE_100 테이블 값 일치를 위해 fred_data 우선
        if key == "FedFunds":
            s = fred_data.get(key)
            if s is not None and isinstance(s, pd.Series) and not s.empty:
                return float(s.iloc[-1]), s
            # fred_data 없으면 liq_v2 fallback
        s = liq_v2.get(key)
        if s is None or (isinstance(s, pd.Series) and s.empty):
            s = fred_data.get(key)
        if s is not None and isinstance(s, pd.Series) and not s.empty:
            return float(s.iloc[-1]), s
        return None, None

    def _status(val, good_below=None, good_above=None, warn_above=None, warn_below=None):
        """🟢🟡🔴 자동 판정"""
        if val is None:
            return "⚪", "#9CA3AF", "데이터 없음"
        if good_below and val <= good_below:
            return "🟢", "#166534", "좋음"
        if good_above and val >= good_above:
            return "🟢", "#166534", "좋음"
        if warn_above and val >= warn_above:
            return "🔴", "#B91C1C", "주의"
        if warn_below and val <= warn_below:
            return "🔴", "#B91C1C", "주의"
        return "🟡", "#92400E", "보통"

    def _dir_arrow(s, n=60):
        """방향 화살표 + 변화량 계산 — 상대값 기준 (M2 절대값 단위 오류 수정)"""
        try:
            if s is None: return "→", 0.0, "보합"
            if not hasattr(s, 'iloc'): return "→", 0.0, "보합"
            if len(s) < n + 1: return "→", 0.0, "보합"
            cur  = float(s.iloc[-1])
            prev = float(s.iloc[-n])
            diff = cur - prev
            # 상대 변화율 기준 (0.05% 이상 변화 시 방향 표시)
            # 절대값 0.05 기준이면 M2(수조$) 단위에서 항상 화살표가 표시되는 버그 수정
            base = abs(prev) if prev != 0 else 1.0
            rel  = abs(diff) / base
            if diff > 0 and rel > 0.0005: return "↑", diff, "상승 중"
            if diff < 0 and rel > 0.0005: return "↓", diff, "하락 중"
            return "→", diff, "보합"
        except Exception:
            return "→", 0.0, "보합"

    # ── 점수 헬퍼 함수 (차트 아래 점수 카드용) ──────────
    FRED_SCORE_URLS = {
        "M2":           "https://fred.stlouisfed.org/graph/?g=1UTwB",
        "RRP":          "https://fred.stlouisfed.org/graph/?g=1UTxr",
        "TGA":          "https://fred.stlouisfed.org/graph/?g=1UTyR",
        "Reserves":     "https://fred.stlouisfed.org/graph/?g=1UTwL",
        "RealRate":     "https://fred.stlouisfed.org/graph/?g=1UTzt",
        "CreditSpread": "https://fred.stlouisfed.org/graph/?g=1UTAm",
    }

    def _score_color(score):
        if score is None: return "#9CA3AF"
        if score >= 60: return "#16A34A"  # 연한 초록
        if score >= 35: return "#92400E"
        return "#B91C1C"

    def _score_label(score):
        if score is None: return "⚪ 데이터 없음"
        if score >= 80: return "🟢 매우 좋음"
        if score >= 60: return "🟢 양  호"
        if score >= 45: return "🟡 보  통"
        if score >= 35: return "🟠 주  의"
        return "🔴 위  험"

    def _mini_chart(s, color, title, height=220, ref_line=None, ref_label="",
                    ref_color="#E53E3E", warn_line=None, warn_label="", warn_color="#F6AD55",
                    good_line=None, good_label="", good_color="#38A169",
                    sp500_s=None):
        """V93: sp500_s 오버레이 추가 — S&P500과의 상관관계 시각화"""
        if s is None or s.empty:
            return None
        s5 = s[s.index >= pd.Timestamp.now() - pd.DateOffset(years=5)]
        if len(s5) < 3: s5 = s

        # V69: 자동 리샘플링 — 일별/주별 데이터는 월간으로 변환해 추세를 명확히 표시
        try:
            _freq = pd.infer_freq(s5.index[:10]) if len(s5) >= 10 else None
        except Exception:
            _freq = None
        _n = len(s5)
        if _n > 180:
            # 일별 이상 (6개월치 > 180일) → 월평균으로 리샘플
            s5 = s5.resample("ME").mean().dropna()
        elif _n > 60:
            # 주별 이상 (60건 초과) → 월말값으로 리샘플
            s5 = s5.resample("ME").last().dropna()
        # 월간 이하는 그대로 (M2SL, FEDFUNDS 등)

        if len(s5) < 3: s5 = s  # 리샘플 후 너무 짧으면 원본 복원

        cur_val  = float(s5.iloc[-1])
        prev_val = float(s5.iloc[-2]) if len(s5) > 1 else cur_val
        trend_up = cur_val >= prev_val

        # 선 색상: 방향에 따라 자동
        line_color = color
        fill_rgba = hex_rgba(color, 0.08)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=s5.index, y=s5.values, mode="lines",
            line=dict(color=line_color, width=3),
            fill="tozeroy", fillcolor=fill_rgba,
            hovertemplate=f"<b>{title}</b><br>%{{x|%Y-%m}}<br>%{{y:.2f}}<extra></extra>"
        ))
        # 기준선들 — 채도 높은 색상 사용
        for _rl, _rlab, _rc, _rdash in [
            (ref_line,  ref_label,  ref_color,  "dash"),
            (warn_line, warn_label, warn_color, "dot"),
            (good_line, good_label, good_color, "dashdot"),
        ]:
            if _rl is not None:
                fig.add_hline(y=_rl, line_dash=_rdash, line_color=_rc, line_width=2)
                # 라벨을 annotation으로 별도 추가 (겹침 방지)
                fig.add_annotation(
                    x=0.01, y=_rl, xref="paper", yref="y",
                    text=f" {_rlab} ",
                    showarrow=False,
                    font=dict(size=10, color=_rc),
                    bgcolor="rgba(255,255,255,0.92)",
                    bordercolor=_rc, borderwidth=1, borderpad=2,
                    xanchor="left", yanchor="bottom"
                )
        # 끝점 라벨
        fig.add_annotation(x=s5.index[-1], y=cur_val,
            text=f"  {cur_val:.2f}",
            showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=2,
            arrowcolor=line_color, ax=55, ay=0,
            font=dict(size=11, color=line_color, family="Space Mono"),
            bgcolor="rgba(255,255,255,0.95)",
            bordercolor=line_color, borderwidth=1.5, borderpad=3)
        fig.update_layout(
            template="plotly_white", paper_bgcolor="#FFFFFF", plot_bgcolor="#FAFBFC",
            height=height, margin=dict(l=0,r=75,t=8,b=0), showlegend=False,
            xaxis=dict(gridcolor="#EBEDF0", color="#718096", tickformat="%Y",
                       linecolor="#E2E6ED", mirror=True),
            yaxis=dict(gridcolor="#EBEDF0", color="#718096",
                       linecolor="#E2E6ED", mirror=True),
            hovermode="x unified"
        )
        # S&P500 오버레이 (V93)
        if sp500_s is not None and not sp500_s.empty:
            try:
                _sp5 = sp500_s[sp500_s.index >= s5.index[0]]
                if len(_sp5) >= 5:
                    _sp_norm = _sp5 / float(_sp5.iloc[0]) * 100
                    fig.add_trace(go.Scatter(
                        x=_sp_norm.index, y=_sp_norm.values,
                        name="S&P500", mode="lines",
                        line=dict(color="#9CA3AF", width=1.5, dash="dot"),
                        opacity=0.7,
                        hovertemplate="S&P500: %{y:.1f}<extra></extra>"))
                    fig.update_layout(showlegend=True,
                        legend=dict(orientation="h", y=1.08, x=0,
                                    font=dict(size=10), bgcolor="rgba(255,255,255,0.8)"))
            except: pass
        return fig

    def _indicator_row(title, fred_code, fred_url, cur_val, status_icon, status_color,
                       desc_short, up_bad, up_good, chart_fig, unit="",
                       direction_arrow="→", direction_diff=0.0, direction_label="보합",
                       period_label="3개월 전 대비", explain_key=None,
                       good_dir="dn"):
        """V93k: 간결화 — 방향 뱃지 추가, 중복 텍스트 제거
        good_dir: 'up'=올라가야 좋음, 'dn'=내려가야 좋음"""
        diff_color = "#E53E3E" if direction_arrow == "↑" else ("#2B6CB0" if direction_arrow == "↓" else "#718096")
        diff_sign  = "+" if direction_diff > 0 else ""

        # 방향 뱃지 생성 (V93k)
        _dir_label = "올라가야 좋음 ✅" if good_dir == "up" else "내려가야 좋음 ✅"
        _dir_bg    = "#EFF6FF" if good_dir == "up" else "#F0FDF4"
        _dir_bc    = "#BFDBFE" if good_dir == "up" else "#86EFAC"
        _dir_tc    = "#1D4ED8" if good_dir == "up" else "#15803d"
        _dir_badge_html = (
            f"<span style='background:{_dir_bg};border:0.5px solid {_dir_bc};"
            f"border-radius:4px;padding:2px 7px;font-size:10px;"
            f"font-weight:500;color:{_dir_tc};margin-left:6px'>{_dir_label}</span>"
        )

        # explain 내용 미리 생성
        _exp_html = ""
        if explain_key:
            _e = {
                "FedFunds":("기준금리가 오르면 왜 주가가 하락할까?",
                    "📈 올리면 (긴축)",["돈 빌리는 이자 비쌈","기업이 투자 줄임","소비자도 소비 줄임","→ 기업 이익 감소 → 주가 하락"],
                    "📉 내리면 (완화)",["대출 이자 저렴해짐","기업이 마음껏 투자","소비자 지갑이 열림","→ 기업 이익 증가 → 주가 상승"],
                    "💡 연준이 금리를 0%로 낮춘 2020~21년에 나스닥이 2배 올랐습니다"),
                "M2":("M2가 늘면 왜 주가가 오를까?",
                    "📈 증가하면",["은행에 돈이 많아짐","대출이 쉬워짐","기업이 투자 늘림","→ 주가 상승"],
                    "📉 감소하면",["시장에서 돈이 빠짐","대출 어려워짐","기업 투자 줄어듦","→ 주가 하락"],
                    "💡 2022년 M2가 처음으로 줄었을 때 나스닥이 -33% 하락했습니다"),
                "RRP":("역레포(RRP)가 줄면 왜 시장에 좋을까?",
                    "📉 높으면 (나쁨)",["은행이 남는 돈을 연준에 보관","그 돈이 주식·채권 시장에 안 들어옴","시장 유동성 줄어듦","→ 자산 가격 정체"],
                    "📈 줄어들면 (좋음)",["은행이 연준에서 돈을 빼서 시장에 투자","주식·채권 시장으로 돈 유입","매수 압력 증가","→ 자산 가격 상승"],
                    "💡 2022~24년 RRP가 2.5조→0으로 줄면서 나스닥이 반등했습니다"),
                "TGA":("재무부 계좌(TGA)가 내려가면 왜 시장에 좋을까?",
                    "📉 높으면 (나쁨)",["정부가 세금을 걷어서 쌓아둔 것","시중에서 돈이 정부 금고로 흡수됨","시장 유동성 감소","→ 자산 가격 압박"],
                    "📈 낮으면 (좋음)",["정부가 지출 중","정부 돈이 시장으로 나옴","시중 유동성 증가","→ 자산 가격 상승"],
                    "💡 2023년 부채한도 협상 당시 TGA가 급증해 시장이 흔들렸습니다"),
                "CPI":("CPI(물가)가 오르면 왜 주가가 하락할까?",
                    "📈 CPI 높으면 (물가 상승)",["물가가 오른다 = 돈의 가치가 떨어진다","연준이 금리를 올려서 물가를 잡으려 함","금리 오르면 기업 대출 비용 증가","→ 기업 이익 감소 → 주가 하락"],
                    "📉 CPI 낮으면 (물가 안정)",["물가 안정 = 연준이 금리 안 올려도 됨","오히려 경기 부양 위해 금리 인하 가능","대출 비용 낮아짐 → 기업 투자 늘어남","→ 기업 이익 증가 → 주가 상승"],
                    "💡 연준의 목표 물가는 2%. CPI가 2%를 크게 초과하면 금리 인상 압박이 커집니다"),
                "BondYield":("채권금리가 오르면 왜 나스닥이 하락할까?",
                    "📈 채권금리 오르면",["미국 국채 이자가 많아짐","안전한데 이자도 높으니 채권으로 자금 이동","전 세계 돈이 미국 채권으로 몰림","→ 주식 팔고 채권 사기 → 주가 하락"],
                    "📉 채권금리 내리면",["채권 이자가 낮아 매력 없음","더 높은 수익 찾아 주식으로 이동","특히 고성장 기술주 선호 증가","→ 나스닥 자금 유입 → 주가 상승"],
                    "💡 2022년 10년물 금리가 1.5%→4.5%로 오르자 나스닥이 -33% 하락했습니다"),
                "Reserves":("은행 준비금이 충분해야 하는 이유",
                    "📈 충분하면 (좋음)",["은행이 여유 자금 보유","기업·가계에 대출 잘 해줌","경제 활동 활발해짐","→ 주가 상승"],
                    "📉 부족하면 (위험)",["은행들이 서로 돈 빌려주기 꺼림","단기 금리가 갑자기 폭등","신용 경색 발생","→ 2019년 레포 위기 재발 위험"],
                    "💡 2019년 준비금이 1.5조$까지 줄자 단기 금리가 하루 만에 10%로 폭등했습니다"),
                "RealRate":("실질금리가 오르면 왜 나스닥이 하락할까?",
                    "📉 높으면 (나쁨)",["채권만 들고 있어도 실질 이익 발생","굳이 위험한 주식 살 필요 없음","특히 PER 50배 이상 성장주가 타격","→ 나스닥 하락"],
                    "📈 낮거나 마이너스면 (좋음)",["채권 실질 수익이 없거나 손실","더 높은 수익 찾아 주식으로 이동","특히 고성장 기술주 선호","→ 나스닥 상승"],
                    "💡 2022년 실질금리가 -1.5%→+4%로 오르자 NVDA·META가 70% 이상 하락했습니다"),
                "CreditSpread":("크레딧 스프레드가 벌어지면 왜 위험할까?",
                    "📉 넓어지면 (나쁨)",["투자자들이 '기업이 망할 수도 있다' 생각","기업 채권 아무도 안 사줌","기업이 돈 조달 어려워짐","→ 주식도 같이 하락"],
                    "📈 좁으면 (좋음)",["투자자들이 기업 부도를 걱정 안 함","기업 채권 잘 팔림","기업이 쉽게 투자 자금 조달","→ 주가 상승"],
                    "💡 2008년 스프레드가 22%까지 벌어졌을 때 S&P500이 -57% 폭락했습니다"),
            }.get(explain_key)
            if _e:
                _etitle, _ut, _uf, _dt, _df, _tip = _e
                _u_rows = "".join(f"<div style='font-size:11px;color:#374151;padding:2px 0'>&#8594; {f}</div>" for f in _uf)
                _d_rows = "".join(f"<div style='font-size:11px;color:#374151;padding:2px 0'>&#8594; {f}</div>" for f in _df)
                _exp_html = f"""
<details style='margin-top:10px;border:0.5px solid #BFDBFE;border-radius:7px;overflow:hidden'>
  <summary style='cursor:pointer;padding:7px 10px;background:#EFF6FF;
    font-size:11px;font-weight:500;color:#1D4ED8;list-style:none'>
    &#128216; {_etitle}
  </summary>
  <div style='padding:10px 12px;background:#FFFFFF'>
    <div style='display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:8px'>
      <div style='background:#F0FDF4;border-radius:7px;padding:9px 10px'>
        <div style='font-size:11px;font-weight:600;color:#15803d;margin-bottom:5px'>{_ut}</div>
        {_u_rows}
      </div>
      <div style='background:#FEF2F2;border-radius:7px;padding:9px 10px'>
        <div style='font-size:11px;font-weight:600;color:#B91C1C;margin-bottom:5px'>{_dt}</div>
        {_d_rows}
      </div>
    </div>
    <div style='background:#F9FAFB;border-radius:5px;padding:6px 9px;font-size:11px;color:#374151'>{_tip}</div>
  </div>
</details>"""

        # ── PC: 설명(좌, 고정220px) + 차트(우, 고정220px) 2열 레이아웃 ──
        # ✅ 왼쪽 카드 min-height:220px 고정 → 지표별 높이 통일
        # ✅ _exp_html(설명) 는 카드 밖 하단에 별도 배치 → 카드 높이 영향 없음
        left_col, right_col = st.columns([1, 1.6])
        with left_col:
            st.markdown(f"""
            <div style="background:#FFFFFF;border:1px solid #E2E6ED;border-radius:10px;
                 padding:16px;min-height:220px;box-sizing:border-box;
                 display:flex;flex-direction:column;justify-content:space-between">
              <div>
                <div style="display:flex;align-items:center;gap:6px;margin-bottom:8px;flex-wrap:wrap">
                  <span style="font-size:13px;font-weight:700;color:#0D1117">{title}</span>
                  {_dir_badge_html}
                </div>
                <div style="margin-bottom:10px">
                  <a href="{fred_url}" target="_blank"
                     style="font-size:10px;color:#3B82F6;text-decoration:none;
                            background:#EFF6FF;border:0.5px solid #BFDBFE;
                            border-radius:4px;padding:2px 6px">
                    FRED: {fred_code} &#8599;</a>
                </div>
                <div style="font-family:'Space Mono',monospace;font-size:28px;
                     font-weight:700;color:{status_color};line-height:1;margin-bottom:6px">
                  {f"{cur_val:.2f}{unit}" if cur_val is not None else "N/A"}</div>
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px">
                  <span style="font-size:22px;font-weight:700;color:{diff_color}">{direction_arrow}</span>
                  <div>
                    <div style="font-size:11px;color:{diff_color};font-weight:500">
                      {direction_label} ({diff_sign}{direction_diff:.2f}{unit})</div>
                    <div style="font-size:10px;color:#9CA3AF">{period_label}</div>
                  </div>
                </div>
              </div>
              <div style="font-size:11px;color:#374151;padding:8px 0 0 0;
                   border-top:0.5px solid #F3F4F6">{desc_short}</div>
            </div>
            """, unsafe_allow_html=True)
            # 설명 펼치기 — 카드 밖 하단 (카드 높이에 영향 없음)
            if _exp_html:
                st.markdown(_exp_html, unsafe_allow_html=True)
        with right_col:
            if chart_fig is not None:
                st.plotly_chart(chart_fig, use_container_width=True, key=f"chart_ind_{fred_code}")
            else:
                st.markdown("""
                <div style="background:#F9FAFB;border:1px solid #E2E6ED;border-radius:10px;
                     height:220px;display:flex;align-items:center;justify-content:center;
                     color:#9CA3AF;font-size:13px">
                  FRED API Key를 입력하면 차트가 표시됩니다
                </div>""", unsafe_allow_html=True)

    if is_placeholder(FRED_API_KEY):
        st.markdown('<div class="warn-box">⚠️ FRED API Key 미입력 — 사이드바에서 입력하면 유동성 분석 활성화<br>'
                    '<span style="font-size:11px">무료 발급: fred.stlouisfed.org</span></div>',
                    unsafe_allow_html=True)


    # ════════════════════════════════════════════════════
    # 지표 1 — Fed 기준금리

    # ════════════════════════════════════════════════════
    # 지표 1 — Fed 기준금리
    # ════════════════════════════════════════════════════
    st.markdown("<div style='font-size:14px;font-weight:700;color:#0D1117;margin:16px 0 8px 0'>1️⃣ Fed 기준금리 (Fed Funds Rate)</div>", unsafe_allow_html=True)

    ff_val, ff_s = _lv("FedFunds")
    ff_ico, ff_c, ff_lbl = _status(ff_val, good_below=2.0, warn_above=4.5)
    ff_arrow, ff_diff, ff_dir = _dir_arrow(ff_s, 60)
    ff_color = "#E53E3E" if ff_val and ff_val > 3 else "#2B6CB0"
    # S&P500 오버레이용 시리즈 (V93)
    _sp500_overlay = mkt.get("SPY")

    fig_ff = _mini_chart(ff_s, ff_color, "Fed 기준금리",
        sp500_s=_sp500_overlay,        ref_line=2.0, ref_label="2% (2019년 인하 전 중립금리)", ref_color="#2B6CB0",
        warn_line=4.5, warn_label="4.5% (2022-23년 40년 최고금리)", warn_color="#E53E3E",
        good_line=None) if ff_s is not None else None
    _indicator_row(
        title="1️⃣ Fed 기준금리 (Fed Funds Rate)",
        fred_code="FEDFUNDS",
        fred_url="https://fred.stlouisfed.org/series/FEDFUNDS",
        cur_val=ff_val, status_icon=ff_ico, status_color=ff_c,
        desc_short="돈을 빌리는 비용",
        up_bad="대출 비싸짐 → 기업 투자 감소 → 주식 압박",
        up_good="대출 저렴 → 투자 증가 → 성장주에 우호적",
        chart_fig=fig_ff, unit="%",
        direction_arrow=ff_arrow, direction_diff=ff_diff, direction_label=ff_dir,
        period_label="3개월(60거래일) 전 대비",
        explain_key="FedFunds", good_dir="dn"
    )

    st.markdown("---")

    # ════════════════════════════════════════════════════
    # 지표 2 — M2 통화량
    # ════════════════════════════════════════════════════
    st.markdown("<div style='font-size:14px;font-weight:700;color:#0D1117;margin:8px 0'>2️⃣ M2 통화량 (M2 Money Supply)</div>", unsafe_allow_html=True)

    _m2_tmp = liq_v2.get("M2")
    m2_s2 = _m2_tmp if (_m2_tmp is not None and isinstance(_m2_tmp, pd.Series) and not _m2_tmp.empty) else fred_data.get("M2")
    m2_yoy2 = None
    if m2_s2 is not None and len(m2_s2) >= 13:
        _yy = m2_s2.pct_change(12).dropna()
        if len(_yy) > 0: m2_yoy2 = float(_yy.iloc[-1]) * 100
    m2_ico, m2_c, m2_lbl = _status(m2_yoy2, good_above=4.0, warn_below=-1.0)
    m2_arrow, m2_diff, m2_dir = _dir_arrow(m2_s2, 3)

    # M2 + S&P500 비교 차트
    fig_m2 = go.Figure()
    if m2_s2 is not None:
        m2_5y = m2_s2[m2_s2.index >= pd.Timestamp.now() - pd.DateOffset(years=5)]
        if not m2_5y.empty:
            m2_norm = m2_5y / float(m2_5y.iloc[0]) * 100
            fig_m2.add_trace(go.Scatter(x=m2_norm.index, y=m2_norm.values, mode="lines",
                name="M2", line=dict(color="#2563EB", width=3),
                fill="tozeroy", fillcolor="rgba(37,99,235,0.07)",
                hovertemplate="<b>M2</b><br>%{x|%Y-%m}<br>지수: %{y:.1f}<extra></extra>"))
    if qqq_s is not None:  # V93: SPY(S&P500) 사용
        _qqq5 = qqq_s[qqq_s.index >= pd.Timestamp.now() - pd.DateOffset(years=5)]
        if not _qqq5.empty:
            _qqq_norm = _qqq5 / float(_qqq5.iloc[0]) * 100
            # MA10, MA20 계산
            _qqq_ma10 = _qqq5.rolling(10).mean()
            _qqq_ma20 = _qqq5.rolling(20).mean()
            _qqq_ma10_norm = _qqq_ma10 / float(_qqq5.iloc[0]) * 100
            _qqq_ma20_norm = _qqq_ma20 / float(_qqq5.iloc[0]) * 100
            # 나스닥100 가격선
            fig_m2.add_trace(go.Scatter(
                x=_qqq_norm.index, y=_qqq_norm.values, mode="lines",
                name="S&P500 (SPY)", line=dict(color="#059669", width=2.5),
                hovertemplate="<b>나스닥100</b><br>%{x|%Y-%m}<br>지수: %{y:.1f}<extra></extra>"))
            # MA10 — 청산 기준선 (빨간 점선)
            fig_m2.add_trace(go.Scatter(
                x=_qqq_ma10_norm.index, y=_qqq_ma10_norm.values, mode="lines",
                name="MA10 (청산기준)", line=dict(color="#EF4444", width=1.5, dash="dot"),
                hovertemplate="MA10: %{y:.1f}<extra></extra>"))
            # MA20 — 브레이크아웃 기준선 (주황)
            fig_m2.add_trace(go.Scatter(
                x=_qqq_ma20_norm.index, y=_qqq_ma20_norm.values, mode="lines",
                name="MA20 (브레이크아웃)", line=dict(color="#F59E0B", width=1.5, dash="dash"),
                hovertemplate="MA20: %{y:.1f}<extra></extra>"))
            # 현재 MA10 이탈 여부 표시
            _cur_qqq = float(_qqq5.iloc[-1])
            _cur_ma10 = float(_qqq_ma10.dropna().iloc[-1]) if len(_qqq_ma10.dropna()) > 0 else None
            if _cur_ma10:
                _exit_now = _cur_qqq < _cur_ma10
                _exit_txt = "⚠️ MA10 이탈 — 청산 검토" if _exit_now else "✅ MA10 위 — 추세 유지"
                _exit_color = "#EF4444" if _exit_now else "#059669"
                fig_m2.add_annotation(
                    x=_qqq_norm.index[-1], y=_qqq_norm.iloc[-1],
                    text=f"  {_exit_txt}",
                    showarrow=True, arrowhead=2, arrowsize=1,
                    arrowcolor=_exit_color, ax=80, ay=-20,
                    font=dict(size=10, color=_exit_color),
                    bgcolor="rgba(255,255,255,0.95)",
                    bordercolor=_exit_color, borderwidth=1.5, borderpad=3)
    fig_m2.add_hline(y=100, line_dash="dot", line_color="#7C3AED", line_width=1.5)
    fig_m2.add_annotation(x=0.01, y=100, xref="paper", yref="y",
        text=" 기준 100 ", showarrow=False,
        font=dict(size=10, color="#7C3AED"),
        bgcolor="rgba(255,255,255,0.9)", borderwidth=0,
        xanchor="left", yanchor="bottom")
    fig_m2.update_layout(
        template="plotly_white", paper_bgcolor="#FFFFFF", plot_bgcolor="#FAFBFC",
        height=220, margin=dict(l=0,r=60,t=10,b=0),
        legend=dict(orientation="h", y=1.12, x=0, font=dict(size=10), bgcolor="rgba(255,255,255,0.8)"),
        xaxis=dict(gridcolor="#EBEDF0", color="#718096", tickformat="%Y"),
        yaxis=dict(gridcolor="#EBEDF0", color="#718096", title="지수(시작=100)"),
        hovermode="x unified")

    _indicator_row(
        title="2️⃣ M2 통화량",
        fred_code="M2SL",
        fred_url="https://fred.stlouisfed.org/series/M2SL",
        cur_val=m2_yoy2, status_icon=m2_ico, status_color=m2_c,
        desc_short="세상에 풀린 돈의 크기",
        up_bad="아이러니하게도 M2 급등은 인플레이션 → 긴축 신호",
        up_good="M2 감소 = 2022년처럼 유동성 수축 → 주식 압박",
        chart_fig=fig_m2 if m2_s2 is not None else None, unit="%/yr",
        direction_arrow=m2_arrow, direction_diff=m2_diff / 1e9 if m2_s2 is not None else 0,
        direction_label=m2_dir, period_label="전월 대비 (조달러)",
        explain_key="M2", good_dir="up"
    )

    st.markdown("---")

    # ════════════════════════════════════════════════════
    # 지표 3 & 4 — RRP + TGA (나란히)
    # ════════════════════════════════════════════════════
    # ══ 3️⃣ RRP ══════════════════════════════════════════
    st.markdown("<div style='font-size:14px;font-weight:700;color:#0D1117;margin:8px 0'>3️⃣ RRP — 역레포 (Reverse Repo)</div>", unsafe_allow_html=True)

    rrp_val, rrp_s2 = _lv("RRP")
    tga_val, tga_s2 = _lv("TGA")
    rrp_ico, rrp_c, rrp_lbl = (_status(rrp_val, good_below=300, warn_above=1000) if rrp_val else ("⚪","#9CA3AF","N/A"))
    tga_ico, tga_c, tga_lbl = (_status(tga_val, good_below=300, warn_above=700) if tga_val else ("⚪","#9CA3AF","N/A"))
    rrp_arrow, rrp_diff, rrp_dir = _dir_arrow(rrp_s2, 20)
    tga_arrow, tga_diff, tga_dir = _dir_arrow(tga_s2, 20)

    # RRP 차트 — 3년 데이터, 일별로 충분히 표시
    def _flow_chart(s, color, title, ref_line, ref_label, ref_color,
                    warn_line, warn_label, warn_color, chart_key,
                    sp500_s=None):
        """V93: sp500_s 오버레이 추가"""
        if s is None or s.empty:
            return None
        # 최근 3년
        s3 = s[s.index >= pd.Timestamp.now() - pd.DateOffset(years=3)]
        if len(s3) < 5: s3 = s

        # V69 월간 리샘플 (일별 데이터 노이즈 제거)
        if len(s3) > 180:
            s3 = s3.resample("ME").mean().dropna()
        elif len(s3) > 60:
            s3 = s3.resample("ME").last().dropna()
        if len(s3) < 3: s3 = s

        # y값: 이미 B$ 단위 → 그대로 사용
        y_vals = s3.values   # B$ 단위 (수천 단위면 T$ 표시)

        # T$ 표시 여부 결정
        y_max = float(y_vals.max()) if len(y_vals) > 0 else 0
        if y_max >= 1000:
            y_plot  = y_vals / 1000  # T$ 단위로 표시
            y_unit  = "T$"
            rl_plot = ref_line  / 1000
            wl_plot = warn_line / 1000
            cur_str = lambda v: f"${v/1000:.2f}T"
            hover_fmt = "$%{y:.2f}T"
        else:
            y_plot  = y_vals    # B$ 그대로
            y_unit  = "B$"
            rl_plot = ref_line
            wl_plot = warn_line
            cur_str = lambda v: f"${v:.0f}B"
            hover_fmt = "$%{y:.0f}B"

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=s3.index, y=y_plot,
            mode="lines", name=title,
            line=dict(color=color, width=3),
            fill="tozeroy", fillcolor=hex_rgba(color, 0.1),
            hovertemplate=f"<b>{title}</b><br>%{{x|%Y-%m}}<br>{hover_fmt}<extra></extra>"
        ))
        for _rl, _lab, _rc, _dash in [
            (rl_plot, ref_label,  ref_color,  "dash"),
            (wl_plot, warn_label, warn_color, "dot"),
        ]:
            fig.add_hline(y=_rl, line_dash=_dash, line_color=_rc, line_width=2)
            fig.add_annotation(
                x=0.01, y=_rl, xref="paper", yref="y",
                text=f" {_lab} ", showarrow=False,
                font=dict(size=10, color=_rc),
                bgcolor="rgba(255,255,255,0.92)",
                bordercolor=_rc, borderwidth=1, borderpad=2,
                xanchor="left", yanchor="bottom"
            )
        cur = float(s3.iloc[-1])
        fig.add_annotation(x=s3.index[-1], y=(cur/1000 if y_max>=1000 else cur),
            text=f"  현재 {cur_str(cur)}",
            showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=2,
            arrowcolor=color, ax=60, ay=0,
            font=dict(size=11, color=color, family="Space Mono"),
            bgcolor="rgba(255,255,255,0.95)",
            bordercolor=color, borderwidth=1.5, borderpad=3)
        fig.update_layout(
            template="plotly_white", paper_bgcolor="#FFFFFF", plot_bgcolor="#FAFBFC",
            height=220, margin=dict(l=0,r=90,t=8,b=0), showlegend=True,
            legend=dict(orientation="h", y=1.08, x=0, font=dict(size=10),
                        bgcolor="rgba(255,255,255,0.8)"),
            xaxis=dict(gridcolor="#EBEDF0", color="#718096", tickformat="%Y-%m",
                       linecolor="#E2E6ED", mirror=True),
            yaxis=dict(gridcolor="#EBEDF0", color="#718096", title=y_unit,
                       linecolor="#E2E6ED", mirror=True),
            hovermode="x unified")
        # S&P500 오버레이 (V93) — 2축 사용
        if sp500_s is not None and not sp500_s.empty:
            try:
                _sp5 = sp500_s[sp500_s.index >= s3.index[0]]
                if len(_sp5) >= 5:
                    _sp_norm = _sp5 / float(_sp5.iloc[0]) * 100
                    fig.add_trace(go.Scatter(
                        x=_sp_norm.index, y=_sp_norm.values,
                        name="S&P500", mode="lines",
                        line=dict(color="#9CA3AF", width=1.5, dash="dot"),
                        opacity=0.7, yaxis="y2",
                        hovertemplate="S&P500: %{y:.1f}<extra></extra>"))
                    fig.update_layout(
                        yaxis2=dict(
                            overlaying="y", side="right",
                            gridcolor="rgba(0,0,0,0)",
                            tickfont=dict(size=9, color="#9CA3AF"),
                            title="S&P500 (시작=100)",
                            showgrid=False))
            except: pass
        return fig

    fig_rrp = _flow_chart(rrp_s2, "#E53E3E", "RRP",
        ref_line=300, ref_label="$300B (2024년 소진 목표)", ref_color="#2B6CB0",
        warn_line=1000, warn_label="$1T (2022년 RRP 폭증 시작)", warn_color="#E53E3E",
        chart_key="chart_rrp", sp500_s=_sp500_overlay)

    rrp_disp = f"${rrp_val:.0f}B" if rrp_val else "N/A"  # V71: 이미 B$
    rrp_diff_b = rrp_diff if rrp_diff else 0  # V71: 이미 B$
    _indicator_row(
        title="3️⃣ RRP 역레포",
        fred_code="RRPONTSYD",
        fred_url="https://fred.stlouisfed.org/series/RRPONTSYD",
        cur_val=rrp_val if rrp_val else None,  # V71: 이미 B$
        status_icon=rrp_ico, status_color=rrp_c,
        desc_short="연준 금고에 묶인 돈",
        up_bad="증가 → 시장에서 돈이 연준으로 흡수됨",
        up_good="감소 → 연준 돈이 시장으로 나옴 (주식 유리)",
        chart_fig=fig_rrp, unit="B$",
        direction_arrow=rrp_arrow, direction_diff=rrp_diff_b, direction_label=rrp_dir,
        period_label="20거래일 전 대비"
,
        explain_key="RRP", good_dir="dn"
    )

    st.markdown("---")

    # ══ 4️⃣ TGA ══════════════════════════════════════════
    st.markdown("<div style='font-size:14px;font-weight:700;color:#0D1117;margin:8px 0'>4️⃣ TGA — 재무부 계좌 (Treasury General Account)</div>", unsafe_allow_html=True)


    fig_tga = _flow_chart(tga_s2, "#D97706", "TGA",
        ref_line=300, ref_label="$300B (부채한도 전 적정선)", ref_color="#2B6CB0",
        warn_line=700, warn_label="$700B (2023년 협상 고점)", warn_color="#E53E3E",
        chart_key="chart_tga", sp500_s=_sp500_overlay)

    tga_disp = f"${tga_val:.0f}B" if tga_val else "N/A"  # V71: 이미 B$
    tga_diff_b = tga_diff if tga_diff else 0  # V71: 이미 B$
    _indicator_row(
        title="4️⃣ TGA 재무부 계좌",
        fred_code="WDTGAL",
        fred_url="https://fred.stlouisfed.org/series/WDTGAL",
        cur_val=tga_val if tga_val else None,  # V71: 이미 B$
        status_icon=tga_ico, status_color=tga_c,
        desc_short="정부 돈 통장",
        up_bad="증가 → 세금 흡수, 시장 유동성 감소",
        up_good="감소 → 정부 지출 중, 시장에 돈 공급",
        chart_fig=fig_tga, unit="B$",
        direction_arrow=tga_arrow, direction_diff=tga_diff_b, direction_label=tga_dir,
        period_label="20거래일 전 대비"
,
        explain_key="TGA", good_dir="dn"
    )

    st.markdown("---")

    # ════════════════════════════════════════════════════
    # 지표 5 — CPI
    # ════════════════════════════════════════════════════
    st.markdown("<div style='font-size:14px;font-weight:700;color:#0D1117;margin:8px 0'>5️⃣ CPI 물가지수 (Consumer Price Index)</div>", unsafe_allow_html=True)

    cpi_val,  cpi_s2  = _lv("CPI")
    core_val, core_s2 = _lv("CoreCPI")
    cpi_yoy = None
    if cpi_s2 is not None and len(cpi_s2) >= 13:
        _cy = cpi_s2.pct_change(12).dropna()
        if len(_cy) > 0: cpi_yoy = float(_cy.iloc[-1]) * 100
    core_yoy = None
    if core_s2 is not None and len(core_s2) >= 13:
        _cy2 = core_s2.pct_change(12).dropna()
        if len(_cy2) > 0: core_yoy = float(_cy2.iloc[-1]) * 100
    cpi_ico, cpi_c, cpi_lbl = _status(cpi_yoy, good_below=2.5, warn_above=4.0)
    if cpi_s2 is not None and len(cpi_s2) >= 13:
        _cpi_yoy_s = cpi_s2.pct_change(12).dropna()
        cpi_arrow, cpi_diff, cpi_dir = _dir_arrow(_cpi_yoy_s, 3)
    else:
        cpi_arrow, cpi_diff, cpi_dir = "→", 0.0, "보합"

    # CPI 차트
    # fig_cpi 에 sp500 오버레이 나중에 적용
    fig_cpi = go.Figure()
    for _cs2, _cc2, _cn2 in [(cpi_s2,"#E53E3E","CPI (전체)"),(core_s2,"#D97706","Core CPI")]:
        if _cs2 is None: continue
        _cy_s2 = _cs2.pct_change(12).dropna()
        _cy_5y = _cy_s2[_cy_s2.index >= pd.Timestamp.now() - pd.DateOffset(years=5)] * 100
        if _cy_5y.empty: continue
        fig_cpi.add_trace(go.Scatter(x=_cy_5y.index, y=_cy_5y.values, mode="lines",
            name=_cn2, line=dict(color=_cc2, width=3),
            hovertemplate=f"<b>{_cn2}</b><br>%{{x|%Y-%m}}<br>%{{y:.1f}}%<extra></extra>"))
    fig_cpi.add_hline(y=2.0, line_dash="dash", line_color="#059669", line_width=2.5)
    fig_cpi.add_annotation(x=0.01, y=2.0, xref="paper", yref="y",
        text=" 연준 목표 2% ", showarrow=False,
        font=dict(size=11, color="#059669"),
        bgcolor="rgba(255,255,255,0.92)", bordercolor="#059669",
        borderwidth=1, borderpad=2, xanchor="left", yanchor="bottom")
    fig_cpi.add_hline(y=4.0, line_dash="dot", line_color="#E53E3E", line_width=2)
    fig_cpi.add_annotation(x=0.01, y=4.0, xref="paper", yref="y",
        text=" 긴축 기준 4% ", showarrow=False,
        font=dict(size=10, color="#E53E3E"),
        bgcolor="rgba(255,255,255,0.92)", bordercolor="#E53E3E",
        borderwidth=1, borderpad=2, xanchor="left", yanchor="bottom")
    fig_cpi.update_layout(
        template="plotly_white", paper_bgcolor="#FFFFFF", plot_bgcolor="#FAFBFC",
        height=220, margin=dict(l=0,r=70,t=10,b=0),
        legend=dict(orientation="h", y=1.08, x=0, font=dict(size=11), bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(gridcolor="#EBEDF0", color="#718096", tickformat="%Y"),
        yaxis=dict(gridcolor="#EBEDF0", color="#718096", title="전년비 (%)"),
        hovermode="x unified")

    # S&P500 오버레이 fig_cpi에 추가 (V93)
    if _sp500_overlay is not None and not _sp500_overlay.empty:
        try:
            _sp5c = _sp500_overlay[_sp500_overlay.index >= pd.Timestamp.now() - pd.DateOffset(years=5)]
            if len(_sp5c) >= 5:
                _sp_nc = _sp5c / float(_sp5c.iloc[0]) * 100
                fig_cpi.add_trace(go.Scatter(
                    x=_sp_nc.index, y=_sp_nc.values,
                    name="S&P500", mode="lines",
                    line=dict(color="#9CA3AF", width=1.5, dash="dot"),
                    opacity=0.7, yaxis="y2",
                    hovertemplate="S&P500: %{y:.1f}<extra></extra>"))
                fig_cpi.update_layout(
                    showlegend=True,
                    legend=dict(orientation="h", y=1.08, x=0, font=dict(size=10)),
                    yaxis2=dict(overlaying="y", side="right", showgrid=False,
                                tickfont=dict(size=9, color="#9CA3AF"), title="S&P500"))
        except: pass

    _indicator_row(
        title="5️⃣ CPI 물가지수",
        fred_code="CPIAUCSL / CPILFESL",
        fred_url="https://fred.stlouisfed.org/series/CPIAUCSL",
        cur_val=cpi_yoy, status_icon=cpi_ico, status_color=cpi_c,
        desc_short="물가 온도계 — 연준의 금리 결정을 좌우",
        up_bad="물가 상승 → 금리 인상 압력 → 유동성 긴축",
        up_good="물가 안정(2%) → 금리 인하 기대 → 주식 우호적",
        chart_fig=fig_cpi, unit="%/yr",
        direction_arrow=cpi_arrow, direction_diff=cpi_diff if cpi_diff else 0,
        direction_label=cpi_dir, period_label="전분기 대비",
        explain_key="CPI", good_dir="dn"
    )

    st.markdown("---")

    # ════════════════════════════════════════════════════
    # 지표 6 — 10년 국채금리
    # ════════════════════════════════════════════════════
    st.markdown("<div style='font-size:14px;font-weight:700;color:#0D1117;margin:8px 0'>6️⃣ 미국 국채금리 — 2Y · 10Y · 30Y 비교</div>", unsafe_allow_html=True)
    t2_val,  t2_s2  = _lv("T2Y")
    t10_val, t10_s2 = _lv("T10Y")
    t30_val, t30_s2 = _lv("T30Y")
    t10_ico, t10_c, t10_lbl = _status(t10_val, good_below=3.5, warn_above=4.5)
    t10_arrow, t10_diff, t10_dir = _dir_arrow(t10_s2, 60)

    # 장단기 스프레드 계산 (10Y - 2Y)
    spread_val = None
    if t10_val and t2_val:
        spread_val = round(t10_val - t2_val, 2)

    # 3개 금리 한 그래프
    fig_t10 = go.Figure()
    YIELD_LINES = [
        (t2_s2,  "#E53E3E", "2Y (단기금리)", "dash"),
        (t10_s2, "#2563EB", "10Y (중기금리)", "solid"),
        (t30_s2, "#059669", "30Y (장기금리)", "dot"),
    ]
    for _ys, _yc, _yn, _yd in YIELD_LINES:
        if _ys is None or _ys.empty: continue
        # 최근 5년
        _y5 = _ys[_ys.index >= pd.Timestamp.now() - pd.DateOffset(years=5)]
        if len(_y5) < 3: _y5 = _ys
        fig_t10.add_trace(go.Scatter(
            x=_y5.index, y=_y5.values,
            mode="lines", name=_yn,
            line=dict(color=_yc, width=2.5, dash=_yd),
            hovertemplate=f"<b>{_yn}</b><br>%{{x|%Y-%m-%d}}<br>%{{y:.2f}}%<extra></extra>"
        ))
        # 끝점 라벨
        _cur = float(_y5.iloc[-1])
        fig_t10.add_annotation(
            x=_y5.index[-1], y=_cur,
            text=f"  {_yn.split('(')[0].strip()} {_cur:.2f}%",
            showarrow=True, arrowhead=2, arrowsize=0.8, arrowwidth=1.5,
            arrowcolor=_yc, ax=70, ay=0,
            font=dict(size=10, color=_yc, family="Space Mono"),
            bgcolor="rgba(255,255,255,0.92)",
            bordercolor=_yc, borderwidth=1.5, borderpad=2
        )
    # 기준선
    for _rl, _rlab, _rc, _rd in [
        (3.5, "주식 유리 3.5%", "#059669", "dash"),
        (4.5, "성장주 압박 4.5%", "#E53E3E", "dot"),
    ]:
        fig_t10.add_hline(y=_rl, line_dash=_rd, line_color=_rc, line_width=2)
        fig_t10.add_annotation(
            x=0.01, y=_rl, xref="paper", yref="y",
            text=f" {_rlab} ",
            showarrow=False,
            font=dict(size=10, color=_rc),
            bgcolor="rgba(255,255,255,0.92)",
            bordercolor=_rc, borderwidth=1, borderpad=2,
            xanchor="left", yanchor="bottom"
        )
    # 장단기 역전 구간 음영
    if t2_s2 is not None and t10_s2 is not None:
        try:
            _common = t2_s2.index.intersection(t10_s2.index)
            _spread = t10_s2.loc[_common] - t2_s2.loc[_common]
            _spread5 = _spread[_spread.index >= pd.Timestamp.now() - pd.DateOffset(years=5)]
            _inv_start = None
            for _dt, _sv in _spread5.items():
                if _sv < 0 and _inv_start is None:
                    _inv_start = _dt
                elif _sv >= 0 and _inv_start is not None:
                    fig_t10.add_vrect(x0=_inv_start, x1=_dt,
                        fillcolor="rgba(229,57,62,0.07)", line_width=0)
                    _inv_start = None
            if _inv_start is not None:
                fig_t10.add_vrect(x0=_inv_start, x1=_spread5.index[-1],
                    fillcolor="rgba(229,57,62,0.07)", line_width=0)
        except Exception:
            pass

    fig_t10.update_layout(
        template="plotly_white", paper_bgcolor="#FFFFFF", plot_bgcolor="#FAFBFC",
        height=220, margin=dict(l=0, r=120, t=10, b=0),
        legend=dict(orientation="h", y=1.08, x=0,
                    font=dict(size=11), bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(gridcolor="#EBEDF0", color="#718096", tickformat="%Y-%m",
                   linecolor="#E2E6ED", mirror=True),
        yaxis=dict(gridcolor="#EBEDF0", color="#718096", title="금리 (%)",
                   linecolor="#E2E6ED", mirror=True),
        hovermode="x unified",
        showlegend=True
    )

    # 스프레드 상태 메시지
    if spread_val is not None:
        _sp_color = "#B91C1C" if spread_val < 0 else "#166534"
        _sp_msg   = f"🔴 장단기 역전 중 ({spread_val:+.2f}%) — 역사적으로 경기침체 전조" if spread_val < 0 else f"🟢 정상 ({spread_val:+.2f}%) — 장기금리 > 단기금리"
    else:
        _sp_color = "#9CA3AF"; _sp_msg = "스프레드 계산 중"

    # 현재값 카드 + 차트
    _tv_cols = st.columns([1, 1.6])
    with _tv_cols[0]:
        t2_disp  = f"{t2_val:.2f}%"  if t2_val  else "N/A"
        t10_disp = f"{t10_val:.2f}%" if t10_val else "N/A"
        t30_disp = f"{t30_val:.2f}%" if t30_val else "N/A"
        st.markdown(f"""
        <div style="background:#FFFFFF;border:1px solid #E2E6ED;border-radius:10px;padding:16px">
          <div style="font-size:14px;font-weight:700;color:#0D1117;margin-bottom:4px">
            6️⃣ 미국 국채금리</div>
          <div style="display:flex;gap:8px;margin-bottom:4px">
            <a href="https://fred.stlouisfed.org/series/DGS2" target="_blank"
               style="font-size:10px;color:#3B82F6;text-decoration:none;background:#EFF6FF;
                      border:1px solid #BFDBFE;border-radius:3px;padding:1px 5px">DGS2 ↗</a>
            <a href="https://fred.stlouisfed.org/series/DGS10" target="_blank"
               style="font-size:10px;color:#3B82F6;text-decoration:none;background:#EFF6FF;
                      border:1px solid #BFDBFE;border-radius:3px;padding:1px 5px">DGS10 ↗</a>
            <a href="https://fred.stlouisfed.org/series/DGS30" target="_blank"
               style="font-size:10px;color:#3B82F6;text-decoration:none;background:#EFF6FF;
                      border:1px solid #BFDBFE;border-radius:3px;padding:1px 5px">DGS30 ↗</a>
          </div>
          <!-- 3개 금리 현재값 -->
          <div style="display:flex;flex-direction:column;gap:6px;margin:10px 0">
            <div style="display:flex;justify-content:space-between;align-items:center;
                 background:#FEF2F2;border-radius:6px;padding:7px 10px">
              <span style="font-size:12px;color:#E53E3E;font-weight:600">● 2Y 단기</span>
              <span style="font-family:'Space Mono',monospace;font-size:16px;
                   font-weight:700;color:#E53E3E">{t2_disp}</span>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;
                 background:#EFF6FF;border-radius:6px;padding:7px 10px">
              <span style="font-size:12px;color:#2563EB;font-weight:600">● 10Y 중기</span>
              <span style="font-family:'Space Mono',monospace;font-size:16px;
                   font-weight:700;color:#2563EB">{t10_disp}</span>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;
                 background:#F0FDF4;border-radius:6px;padding:7px 10px">
              <span style="font-size:12px;color:#059669;font-weight:600">● 30Y 장기</span>
              <span style="font-family:'Space Mono',monospace;font-size:16px;
                   font-weight:700;color:#059669">{t30_disp}</span>
            </div>
          </div>
          <!-- 장단기 스프레드 -->
          <div style="background:#F9FAFB;border-radius:6px;padding:8px 10px;
               font-size:12px;color:{_sp_color};font-weight:600;margin-bottom:8px">
            10Y-2Y 스프레드: {_sp_msg}
          </div>
          <!-- 방향 -->
          <div style="display:flex;align-items:center;gap:8px">
            <span style="font-size:20px;color:{'#2B6CB0' if t10_arrow=='↓' else '#E53E3E'}">{t10_arrow}</span>
            <div>
              <div style="font-size:12px;color:{'#2B6CB0' if t10_arrow=='↓' else '#E53E3E'};font-weight:600">
                10Y {t10_dir} ({t10_diff:+.2f}%)</div>
              <div style="font-size:10px;color:#9CA3AF">3개월 전 대비</div>
            </div>
          </div>
          <div style="border-top:1px solid #F3F4F6;margin-top:10px;padding-top:10px;
               font-size:12px;color:#374151;line-height:1.7">
            <b>"세계 금융의 기준 체온계"</b><br>
            ↑ 금리 상승 → 채권으로 이동 → 성장주 압박<br>
            ↓ 금리 하락 → 주식 매력 증가 → 기술주 유리
          </div>
          <details style='margin-top:10px;border:0.5px solid #BFDBFE;border-radius:7px;overflow:hidden'>
            <summary style='cursor:pointer;padding:7px 10px;background:#EFF6FF;
              font-size:11px;font-weight:500;color:#1D4ED8;list-style:none'>
              &#128216; 채권금리가 오르면 왜 나스닥이 하락할까?
            </summary>
            <div style='padding:10px 12px;background:#FFFFFF'>
              <div style='display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:8px'>
                <div style='background:#FEF2F2;border-radius:7px;padding:9px 10px'>
                  <div style='font-size:11px;font-weight:600;color:#B91C1C;margin-bottom:5px'>
                    &#128200; 채권금리 오르면</div>
                  <div style='font-size:11px;color:#374151;padding:2px 0'>&#8594; 미국 국채 이자가 많아짐</div>
                  <div style='font-size:11px;color:#374151;padding:2px 0'>&#8594; 안전한데 이자도 높으니 채권으로 자금 이동</div>
                  <div style='font-size:11px;color:#374151;padding:2px 0'>&#8594; 전 세계 돈이 미국 채권으로 몰림</div>
                  <div style='font-size:11px;color:#374151;padding:2px 0'>&#8594; 주식 팔고 채권 사기 → 주가 하락</div>
                </div>
                <div style='background:#F0FDF4;border-radius:7px;padding:9px 10px'>
                  <div style='font-size:11px;font-weight:600;color:#15803d;margin-bottom:5px'>
                    &#128201; 채권금리 내리면</div>
                  <div style='font-size:11px;color:#374151;padding:2px 0'>&#8594; 채권 이자가 낮아 매력 없음</div>
                  <div style='font-size:11px;color:#374151;padding:2px 0'>&#8594; 더 높은 수익 찾아 주식으로 이동</div>
                  <div style='font-size:11px;color:#374151;padding:2px 0'>&#8594; 특히 고성장 기술주 선호 증가</div>
                  <div style='font-size:11px;color:#374151;padding:2px 0'>&#8594; 나스닥 자금 유입 → 주가 상승</div>
                </div>
              </div>
              <div style='background:#F9FAFB;border-radius:5px;padding:6px 9px;font-size:11px;color:#374151'>
                &#128161; 2022년 10년물 금리가 1.5%→4.5%로 오르자 나스닥이 -33% 하락했습니다
              </div>
            </div>
          </details>
        </div>""", unsafe_allow_html=True)
    with _tv_cols[1]:
        if t10_s2 is not None:
            st.plotly_chart(fig_t10, use_container_width=True, key="chart_t10")
            st.caption("빨간 음영 = 장단기 금리 역전 구간 (역사적으로 경기침체 전조)")
        else:
            st.markdown("""
            <div style="background:#F9FAFB;border:1px solid #E2E6ED;border-radius:10px;
                 height:280px;display:flex;align-items:center;justify-content:center;
                 color:#9CA3AF;font-size:13px">FRED API Key를 입력하면 차트가 표시됩니다</div>""",
                unsafe_allow_html=True)

    st.markdown("---")

    # ════════════════════════════════════════════════════
    # 지표 8·9·10 — 은행 준비금 · 실질금리 · 크레딧 스프레드
    # ✅ 바 제거 → 깔끔한 3열 요약 카드
    # ════════════════════════════════════════════════════
    st.markdown("---")
    st.markdown("<div style='font-family:Space Mono,monospace;font-size:11px;color:#3B5BA5;letter-spacing:1px;margin:8px 0'>📊 유동성 나머지 지표 — 은행준비금 · 실질금리 · 크레딧 스프레드</div>",
                unsafe_allow_html=True)

    _rem_cols = st.columns(3)
    for _rcol, _rkey, _rnum, _rlabel in [
        (_rem_cols[0], "Reserves",     "8️⃣", "은행 준비금"),
        (_rem_cols[1], "RealRate",     "9️⃣", "실질금리"),
        (_rem_cols[2], "CreditSpread", "🔟", "크레딧 스프레드"),
    ]:
        _rinfo  = IND_SCORE_100.get(_rkey, {})
        _rscore = _rinfo.get("score")
        _rval   = _rinfo.get("val")
        _rmeta  = _rinfo.get("meta", {})
        _rcolor = _score_color(_rscore)
        _rslbl  = _score_label(_rscore)
        _runit  = _rmeta.get("unit","")
        _rbetter= _rmeta.get("better","")
        _rgood  = _rmeta.get("good_desc","")
        _rbad   = _rmeta.get("bad_desc","")
        _rvstr  = (f"{_rval/1e9:.2f}T{_runit}" if (_runit=="B$" and _rval and abs(_rval)>500)
                   else (f"{_rval:.2f}{_runit}" if _rval is not None else "N/A"))
        _rsdisp = f"{_rscore:.0f}" if _rscore is not None else "—"
        _fred_u = FRED_SCORE_URLS.get(_rkey, "https://fred.stlouisfed.org")
        _bg     = "#F0FDF4" if (_rscore or 0)>=60 else ("#FFFBEB" if (_rscore or 0)>=35 else "#FEF2F2")
        _bc     = "#86EFAC" if (_rscore or 0)>=60 else ("#FDE68A" if (_rscore or 0)>=35 else "#FECACA")

        _rcol.markdown(f"""
        <div style="background:{_bg};border:1px solid {_bc};border-radius:10px;
             padding:14px 16px;margin:4px 0;min-height:110px;box-sizing:border-box">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px">
            <div>
              <div style="font-size:12px;font-weight:700;color:#374151">{_rnum} {_rlabel}</div>
              <div style="font-size:10px;color:#9CA3AF;margin-top:2px">{_rbetter}</div>
            </div>
            <div style="text-align:right">
              <span style="font-family:'Space Mono',monospace;font-size:22px;
                   font-weight:700;color:{_rcolor}">{_rsdisp}</span>
              <span style="font-size:10px;color:#9CA3AF">/100</span>
            </div>
          </div>
          <div style="display:flex;justify-content:space-between;align-items:center">
            <div style="font-size:11px;color:#374151">현재: <b>{_rvstr}</b></div>
            <div style="font-size:11px;font-weight:600;color:{_rcolor}">{_rslbl}</div>
          </div>
          <div style="font-size:10px;color:#6B7280;margin-top:6px;line-height:1.5">
            <span style="color:#16A34A">✅ {_rgood}</span><br>
            <span style="color:#B91C1C">⚠️ {_rbad}</span>
          </div>
          <div style="text-align:right;margin-top:4px">
            <a href="{_fred_u}" target="_blank"
               style="font-size:10px;color:#3B5BA5;text-decoration:none">FRED ↗</a>
          </div>
        </div>""", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════
    # V60: 현재 글로벌 유동성 종합 상태 — 통합 테이블
    # ════════════════════════════════════════════════════
    # V93: 기타 지표 explain
    _indicator_explain("Reserves")
    _indicator_explain("RealRate")
    _indicator_explain("CreditSpread")

    st.markdown("---")

    # ── 5단계 색상 팔레트 ─────────────────────────────────

# ═════════════════════════════════════════════════════════

def build_full_report():
    """초보자를 위한 역사적 위치 기반 보고서 — V51"""

    now_str  = datetime.now().strftime("%Y년 %m월 %d일 (%a)  %H:%M 기준")
    _la      = LIQ_ACTION
    _mkt_kr  = MKT_KR.get(mkt_status, MKT_KR["NEUTRAL"])
    _max_s   = {"S":40,"M1":30,"M2":25,"L":15,"XL":10}[INVEST_SCALE]
    _stage_n = _la["stage"]
    _ir, _, _gld_ratio = get_invest_ratio(_stage_n, mkt_status, hard_stops, vix=vix_val)
    _avail   = INVEST_AMOUNT_만원 * _ir
    _cash    = INVEST_AMOUNT_만원 * (1 - _ir)
    _today   = _avail * 0.40
    _day5    = _avail * 0.35
    _day10   = _avail * 0.25

    liq_txt = (_la["label"]
               .replace("🟢","").replace("🟡","").replace("🟠","")
               .replace("🔴","").replace("🚀","").strip())
    stop_txt = ("매수 금지: " + " | ".join(hard_stops)) if hard_stops else "매수 금지 조건 없음"

    def _sf(val, fmt=".2f", fallback="N/A"):
        if val is None: return fallback
        try: return format(val, fmt)
        except: return fallback

    def _fmt(key, val, unit):
        if val is None: return "N/A"
        if unit == "B$": return f"{val/1000:.2f}T$" if abs(val)>=1000 else f"{val:.0f}B$"
        if unit == "%":  return f"{val:.2f}%"
        return f"{val:.2f}"

    # ══════════════════════════════════════════════════════
    # 역사적 위치 설명 생성기
    # 원칙: 현재값 → 과거평균 → 역사 고점/저점 → 현재 위치 평가
    # ══════════════════════════════════════════════════════
    def _position(label, current, avg, high, low, unit, higher_is_good,
                  custom_interp=None):
        """숫자의 역사적 위치를 초보자 언어로 설명"""
        if current is None:
            return f"  {label}: 데이터 없음\n"

        # 현재 위치를 고점~저점 사이 %로 계산
        if high != low:
            pct = (current - low) / (high - low) * 100
        else:
            pct = 50

        # 위치 표현
        if pct >= 85:
            pos_txt = "역사적 고점에 가까운 수준"
        elif pct >= 65:
            pos_txt = "평균보다 높은 편"
        elif pct >= 35:
            pos_txt = "역사적 평균 부근"
        elif pct >= 15:
            pos_txt = "평균보다 낮은 편"
        else:
            pos_txt = "역사적 저점에 가까운 수준"

        # 투자에 유리한지 판단
        if higher_is_good:
            if pct >= 65:   eval_txt = "투자에 유리한 구간"
            elif pct >= 35: eval_txt = "중립 구간"
            else:           eval_txt = "투자에 불리한 구간"
        else:
            if pct <= 35:   eval_txt = "투자에 유리한 구간"
            elif pct <= 65: eval_txt = "중립 구간"
            else:           eval_txt = "투자에 불리한 구간"

        u = unit if unit else ""
        cur_str = f"{current:.2f}{u}" if isinstance(current, float) else f"{current}{u}"
        avg_str = f"{avg:.2f}{u}"     if isinstance(avg, float) else f"{avg}{u}"
        hi_str  = f"{high:.0f}{u}"   if isinstance(high, float) else f"{high}{u}"
        lo_str  = f"{low:.2f}{u}"    if isinstance(low, float) else f"{low}{u}"

        interp = custom_interp if custom_interp else f"{pos_txt} — {eval_txt}"

        return (
            f"  {label}: {cur_str}\n"
            f"    과거 평균 {avg_str}  /  역사 고점 {hi_str}  /  역사 저점 {lo_str}\n"
            f"    현재 위치: {interp}\n"
        )

    # ── 각 지표 데이터 ───────────────────────────────────
    try: vix_v = float(mkt.get("VIX",pd.Series([20])).iloc[-1])
    except: vix_v = None
    try:
        qs  = get_close("QQQ","1y")
        qc  = float(qs.iloc[-1])
        q200= float(qs.rolling(200).mean().iloc[-1])
        q50 = float(qs.rolling(50).mean().iloc[-1])
        q52h= float(qs.max())
        dl  = qs.diff(); gn = dl.clip(lower=0).rolling(14).mean()
        ls  = (-dl.clip(upper=0)).rolling(14).mean()
        rsi_v = float(100-100/(1+gn.iloc[-1]/ls.iloc[-1])) if ls.iloc[-1]>0 else 50
        p200= (qc/q200-1)*100
        p52h= (qc/q52h-1)*100
    except: qc=q200=q50=q52h=rsi_v=p200=p52h=0; qc=None

    fg_disp = f"{fg_score:.0f}" if fg_score else "N/A"
    fg_txt  = ("극단적 탐욕" if fg_score and fg_score>=80 else
               ("탐욕"      if fg_score and fg_score>=55 else
               ("중립"      if fg_score and fg_score>=45 else
               ("공포"      if fg_score and fg_score>=20 else "극단적 공포"))))
    pe_disp = f"{pe_current:.1f}" if pe_current else "N/A"

    rr_val  = IND_SCORE_100.get("RealRate",{}).get("val")
    m2_info = IND_SCORE_100.get("M2",{});      m2_score = m2_info.get("score",0)
    cs_info = IND_SCORE_100.get("CreditSpread",{}); cs_score = cs_info.get("score",0)

    # 금리 커브
    y2  = yield_curve.get("2Y",  {}).get("value")
    y10 = yield_curve.get("10Y", {}).get("value")
    y30 = yield_curve.get("30Y", {}).get("value")
    spread = (y10-y2) if (y10 and y2) else None
    if spread is not None:
        if spread < 0:   spread_txt = f"역전형 (10Y-2Y={spread:+.2f}%) — 경기침체 선행 신호"
        elif spread<0.3: spread_txt = f"평탄형 (10Y-2Y={spread:+.2f}%) — 불확실 구간"
        else:            spread_txt = f"정상형 (10Y-2Y={spread:+.2f}%) — 경기 확장 신호"
    else: spread_txt = "데이터 로드 중"

    # 환경 진단 핵심 근거
    pos_reasons = []; neg_reasons = []
    if m2_score >= 60:
        pos_reasons.append(f"M2 통화량 증가 중 — 시장에 돈이 들어오고 있다 ({m2_score:.0f}점)")
    if cs_score >= 60:
        pos_reasons.append(f"크레딧 스프레드 안정 — 시스템 위기 신호 없음 ({cs_score:.0f}점)")
    if p200 and p200 > 0:
        pos_reasons.append(f"QQQ MA200 위 {p200:+.1f}% — 장기 상승 추세 유지")
    if rr_val and rr_val >= 1.5:
        neg_reasons.append(f"실질금리 {rr_val:.2f}% — 성장주 밸류에이션 압박 지속")
    if rsi_v and rsi_v >= 70:
        neg_reasons.append(f"RSI {rsi_v:.0f}점 과매수 — 단기 조정 가능성 주의")
    if hard_stops:
        neg_reasons.append("하드스탑 발동 — 신규 매수 금지")

    env_pos = "\n".join(f"  긍정  {r}" for r in pos_reasons[:2]) or "  (데이터 없음)"
    env_neg = "\n".join(f"  경고  {r}" for r in neg_reasons[:2]) or "  (없음)"

    if rsi_v and rsi_v >= 75:
        entry_reason = f"RSI {rsi_v:.0f}점 과매수 — 조정 가능성 있으므로 1차 40%만 진입하고 나머지는 조정 시 활용"
    elif _ir >= 0.8:
        entry_reason = "유동성 최적 환경 — 계획 금액 전액 분할 투자"
    elif _ir == 0:
        entry_reason = "투자 불가 환경 — 하드스탑 발동 또는 위기 구간. 현금 100% 유지"
    else:
        entry_reason = f"{_stage_n}단계 선별 매수 — 가능 금액의 40%부터 시작해 조정 시 추가 매수"

    # 유동성 체크리스트 (기존 방식 유지)
    IND_CHECK = {
        "M2":{"better":"up","criterion":"2개월 연속 증가 여부"},
        "RRP":{"better":"down","criterion":"고점(2.5조$) 대비 감소율"},
        "TGA":{"better":"down","criterion":"부채한도 협상 시기 급변 주목"},
        "Reserves":{"better":"up","criterion":"3조$ 이하 하락시 경고"},
        "RealRate":{"better":"down","criterion":"2% 초과시 성장주 압박"},
        "CreditSpread":{"better":"down","criterion":"5% 초과시 매수 중단"},
    }
    liq_rows = []; ok_count = xx_count = 0
    for key in ["M2","RRP","TGA","Reserves","RealRate","CreditSpread"]:
        info  = IND_SCORE_100.get(key,{}); score=info.get("score"); val=info.get("val")
        meta  = info.get("meta",{}); chk=IND_CHECK.get(key,{})
        label = meta.get("label",key); unit=meta.get("unit","")
        if score is None: continue
        val_s = _fmt(key, val, unit); is_ok=(score>=60)
        signal = "OK" if is_ok else "XX"
        if is_ok: ok_count+=1
        else:     xx_count+=1
        cur = fred_history.get(key)
        if cur is None or (isinstance(cur,pd.Series) and cur.empty): cur=fred_data.get(key)
        if cur is not None and isinstance(cur,pd.Series) and len(cur)>=2:
            diff = float(cur.iloc[-1])-float(cur.iloc[-2])
            better=chk.get("better","up")
            dir_txt = ("증가 중 (긍정)" if diff>0 else "감소 중 (부정)") if better=="up" else \
                      ("감소 중 (긍정)" if diff<0 else "증가 중 (부정)")
        else: dir_txt=""
        liq_rows.append(
            f"  {label:<16} {score:>3.0f}점  {val_s:>10}  {signal:>4}  {dir_txt}"
        )

    liq_table = (
        f"  {'지표':<16} {'점수':>5}  {'현재값':>10}  {'신호':>4}  흐름 방향\n"
        f"  {'─'*60}\n"
        + "\n".join(liq_rows) + "\n"
        + f"  {'─'*60}\n"
        + f"  {'종합':<16} {LIQ_SCORE_100:>3.0f}점  {'':>10}  "
        + f"  {ok_count} OK / {xx_count} XX"
    )

    # 섹터
    sec_ok=[]; sec_bad=[]
    if sector_data:
        for sn,sd in sorted(sector_data.items(),key=lambda x:x[1].get("ret_1m",0),reverse=True):
            ret=sd.get("ret_1m",0); ma20=sd.get("above_ma20",False); etf=sd.get("etf","")
            if ma20 and ret>0: sec_ok.append(f"{sn} {ret:+.1f}%({etf})")
            elif not ma20:     sec_bad.append(f"{sn} {ret:+.1f}%")

    # 추천 종목
    top3_rows=[]; reason_lines=[]
    if not df_all.empty:
        sc_col="섹터 AI Score" if "섹터 AI Score" in df_all.columns else "AI Score"
        top3=df_all[
            (df_all.get("RS Score",pd.Series(dtype=int))>=70)&
            (df_all["Exit Signal"]=="—")
        ].sort_values(sc_col,ascending=False).head(3)
        for _,r in top3.iterrows():
            brk="브레이크아웃" if r.get("Breakout","—")=="✅" else "매수 신호    "
            ew=" (*실적임박)" if r.get("실적경고","—")=="⚠️" else ""
            rs=int(r.get("RS Score",0)); ai=float(r.get(sc_col,0)); pr=float(r.get("Price",0))
            top3_rows.append(f"  {r['Ticker']:<6}  RS {rs:>3}점  AI {ai:>5.1f}  ${pr:>8.2f}  {brk}{ew}")
            reason_lines.append(f"  {r['Ticker']}: RS {rs}점 — {r.get('섹터','')} 강세 섹터 내 상위 주도주")

    # ══════════════════════════════════════════════════════
    # 섹션5 — 투자금 반영 여부 (INVEST_IN_REPORT 체크박스)
    # ══════════════════════════════════════════════════════
    # 투자금 > 0 이면 항상 보고서에 반영 (V53: 체크박스 제거됨)
    _invest_flag = (INVEST_AMOUNT_만원 > 0)

    # 포트폴리오
    try:
        fx_raw=__import__('yfinance').download("KRW=X",period="5d",progress=False,auto_adjust=True)
        fx_rate=float(fx_raw["Close"].iloc[-1]) if not fx_raw.empty else 1380.0
    except: fx_rate=1380.0

    port_rows=[]; total_real=0.0
    if not df_port.empty and _avail>0:
        sc2="섹터 AI Score" if "섹터 AI Score" in df_port.columns else "AI Score"
        _tot=df_port[sc2].sum()
        for _,r in df_port.iterrows():
            w=float(r.get(sc2,0))/_tot if _tot>0 else 0
            alloc_만=_today*w; usd_pr=float(r.get("Price",0))
            shares=int((alloc_만*10000/fx_rate)/usd_pr) if usd_pr>0 else 0
            real_만=round(shares*usd_pr*fx_rate/10000,1); total_real+=real_만
            port_rows.append(f"  {r['Ticker']:<6}  {alloc_만:>8.0f}만원  {w*100:>4.0f}%  {shares:>5}주  {real_만:>8.1f}만원  @${usd_pr:.2f}")
        port_rows.append(f"  {'─'*58}")
        port_rows.append(f"  합계    {_today:>8.0f}만원              {total_real:>8.1f}만원  잔여 {_today-total_real:.0f}만원")
    elif hard_stops:
        port_rows.append(f"  투자 중단: {' | '.join(hard_stops)}")
    else:
        port_rows.append("  종목 데이터 로드 중.")

    # 위험 분석
    risks=[]; rr_val2=IND_SCORE_100.get("RealRate",{}).get("val")
    if rsi_v and rsi_v>=75:
        risks.append((f"RSI {rsi_v:.0f}점 과매수","진입 즉시 -5~8% 단기 조정 가능","분할 매수 3회 필수. 오늘은 40%만"))
    elif rsi_v and rsi_v>=65:
        risks.append((f"RSI {rsi_v:.0f}점 주의 구간","과열 초기 신호","분할 매수 준수"))
    if rr_val2 and rr_val2>=2.0:
        risks.append((f"실질금리 {rr_val2:.2f}%","성장주 구조적 압박","고PER 종목 비중 줄이기"))
    elif rr_val2 and rr_val2>=1.5:
        risks.append((f"실질금리 {rr_val2:.2f}% 주시","추가 상승 시 성장주 타격","주 1회 방향 확인"))
    if fx_rate>=1400:
        risks.append((f"환율 {fx_rate:,.0f}원/$","달러 약세 시 원화 손실 10~15%","투자 규모 결정 시 환율 감안"))
    elif fx_rate>=1350:
        risks.append((f"환율 {fx_rate:,.0f}원/$","한국 투자자 환율 리스크","수익률 계산 시 환율 시나리오 포함"))

    n=len(risks)
    if n==0: prob=(60,30,10); overall="매우 유리 — 공격적 진입 적기"
    elif n==1: prob=(40,40,20); overall="양호 — 분할 매수 원칙 준수 시 수익 가능"
    elif n==2: prob=(25,45,30); overall="주의 — 소량 분할 진입, 손절 원칙 강화"
    else:      prob=(15,40,45); overall="위험 — 현금 비중 확대 후 재진입 조건 기다릴 것"

    risk_str=""
    for i,(t,d,a) in enumerate(risks,1):
        risk_str+=f"\n  {i}. {t}\n     위험: {d}\n     대응: {a}"
    if not risks: risk_str="\n  현재 주요 위험 요소 없음 — 진입 환경 양호"

    buy_list=exit_list=warn_list=[]
    if not df_all.empty:
        buy_list =df_all[df_all["Signal"].str.contains("BUY",na=False)].head(3)["Ticker"].tolist()
        exit_list=df_all[df_all["Exit Signal"]=="⚠️"]["Ticker"].tolist()
        if "실적경고" in df_all.columns:
            warn_list=df_all[df_all["실적경고"]=="⚠️"]["Ticker"].tolist()

    # ══════════════════════════════════════════════════════
    # 역사적 위치 설명 블록 생성
    # ══════════════════════════════════════════════════════

    # 1. 유동성 종합 점수 위치
    liq_pos = _position(
        "유동성 종합점수", LIQ_SCORE_100,
        avg=55, high=100, low=0, unit="점", higher_is_good=True,
        custom_interp=(
            "역사적 평균보다 높은 편 — 시장에 돈이 들어오고 있는 상태"
            if LIQ_SCORE_100>=60 else
            "역사적 평균 부근 — 유동성이 혼조, 신중한 접근 필요"
            if LIQ_SCORE_100>=40 else
            "역사적 평균보다 낮은 편 — 돈이 시장을 떠나고 있는 상태"
        )
    )

    # 2. M2 증가율
    m2_val = IND_SCORE_100.get("M2",{}).get("val")
    m2_ser = fred_data.get("M2")
    m2_yoy = None
    if m2_ser is not None and len(m2_ser)>=13:
        try: m2_yoy = float(m2_ser.pct_change(12).dropna().iloc[-1]*100)
        except: pass
    if m2_yoy is not None:
        m2_pos = _position(
            "M2 증가율(전년비)", m2_yoy,
            avg=6.0, high=27.0, low=-5.0, unit="%", higher_is_good=True,
            custom_interp=(
                f"{m2_yoy:.1f}%는 코로나 당시 최고(+27%) 대비 낮지만 평상시 평균(+5~7%)과 비슷한 수준.\n"
                "    시장에 돈이 들어오고 있는 상태. 급격한 돈풀기는 아니지만 안정적 공급 중."
                if m2_yoy>=3 else
                f"{m2_yoy:.1f}%는 긴축 구간(0% 이하)에 근접. 시장 유동성 부족 우려."
            )
        )
    else:
        m2_pos = f"  M2 증가율: 계산 중\n    YoY 데이터 로드 필요\n"

    # 3. 실질금리
    rr_pos = ""
    if rr_val is not None:
        rr_pos = _position(
            "실질금리", rr_val,
            avg=0.8, high=4.5, low=-1.5, unit="%", higher_is_good=False,
            custom_interp=(
                f"{rr_val:.2f}%는 역사 평균(0.8%)보다 꽤 높은 편이다.\n"
                "    2020년 코로나 상승장에서는 -1%까지 내려갔었고,\n"
                "    2022년 나스닥 -33% 시기에는 4%까지 올라갔다.\n"
                "    현재는 금융위기 수준까지는 아니지만 성장주에는 부담이 있는 구간."
            )
        )

    # 4. RSI
    rsi_pos = ""
    if rsi_v:
        rsi_pos = _position(
            "QQQ RSI(14)", rsi_v,
            avg=55, high=90, low=20, unit="점", higher_is_good=False,
            custom_interp=(
                f"{rsi_v:.0f}점은 과열 기준선(70)을 넘어선 상태.\n"
                "    90점 이상이 극단적 과열 구간인데 아직 거기까진 아니다.\n"
                "    단기 조정이 와도 이상하지 않은 자리. 지금 한 번에 전부 사는 것은 위험."
                if rsi_v>=70 else
                f"{rsi_v:.0f}점은 일반적 과열 기준(70) 아래, 정상 강세 구간.\n"
                "    공포 구간(30 이하)과 과열 구간(70 이상) 사이의 중립 지대."
            )
        )

    # 5. VIX
    vix_pos = ""
    if vix_v is not None:
        vix_pos = _position(
            "VIX 공포지수", vix_v,
            avg=18, high=89, low=9, unit="", higher_is_good=False,
            custom_interp=(
                f"VIX {vix_v:.1f}은 하드스탑 기준(28)을 초과. 시장에 패닉 신호.\n"
                "    2008년 금융위기 당시 80까지 치솟았다. 현재는 위기 수준."
                if vix_v>=28 else
                f"VIX {vix_v:.1f}은 평상시 평균(17~20) 범위 안에 있다.\n"
                "    공포 구간(30)까지 여유가 있고, 시장 참가자들이 큰 위험을 느끼지 않는 상태.\n"
                "    이 수준에서 기관 투자자들은 일반적으로 매수 포지션을 늘린다."
            )
        )

    # 6. 크레딧 스프레드
    cs_val = IND_SCORE_100.get("CreditSpread",{}).get("val")
    cs_pos = ""
    if cs_val is not None:
        cs_pos = _position(
            "크레딧 스프레드", cs_val,
            avg=4.5, high=22.0, low=2.5, unit="%", higher_is_good=False,
            custom_interp=(
                f"{cs_val:.2f}%는 역사 평균(4~5%)보다 낮은 안정적 수준이다.\n"
                "    2008년 금융위기 때는 22%까지 치솟았고, 2020년 코로나 때는 10%였다.\n"
                "    현재는 기업 부도 위험을 시장이 거의 걱정하지 않는 상태.\n"
                "    하드스탑 기준인 5%까지는 여유가 있다."
            )
        )

    # 7. PE Ratio
    pe_pos = ""
    if pe_current is not None:
        # PER 수준별 해석 자동 생성
        if pe_current >= 30:
            _pe_interp = (
                f"PER {pe_current:.1f}배는 역사 평균(16.2배)보다 크게 높은 과열 구간이다.\n"
                f"    닷컴 버블(2000년) 당시 최고 38배까지 올랐다가 -80% 폭락했다.\n"
                f"    지금은 역사적으로 비싼 구간이다. AI 성장 프리미엄이 반영된 것으로 보이나,\n"
                f"    금리가 현 수준을 유지하면 밸류에이션 부담이 조정 트리거가 될 수 있다."
            )
        elif pe_current >= 22:
            _pe_interp = (
                f"PER {pe_current:.1f}배는 역사 평균(16.2배)보다 높은 편이다.\n"
                f"    닷컴 버블(38배)까지는 여유가 있지만, 역사적 중간값(15배) 대비 프리미엄이 높다.\n"
                f"    경기 확장이 지속되고 AI 수익이 실현되는 한 지탱 가능하나,\n"
                f"    금리 인상 또는 실적 둔화 시 밸류에이션 조정이 올 수 있다."
            )
        elif pe_current >= 14:
            _pe_interp = (
                f"PER {pe_current:.1f}배는 역사 평균(16.2배) 부근의 적정 수준이다.\n"
                f"    과열도 아니고 극단적 저평가도 아닌 '중립 밸류에이션' 구간.\n"
                f"    이 수준에서는 기업 이익 성장이 주가를 끌어올리는 정상적 시장이 작동한다.\n"
                f"    역사적으로 이 구간에서 진입한 투자자들은 5년 이상 보유 시 양호한 수익을 얻었다."
            )
        else:
            _pe_interp = (
                f"PER {pe_current:.1f}배는 역사 평균(16.2배)보다 낮은 저평가 구간이다.\n"
                f"    금융위기(2009년) 당시 최저 8배까지 내려간 적이 있다.\n"
                f"    현재 수준은 기업 이익 대비 주가가 싸다는 의미다.\n"
                f"    단, 낮은 PER이 '무조건 매수'는 아니다 — 이익 감소 우려가 있는지 확인 필요."
            )
        pe_pos = _position(
            "S&P500 PER", pe_current,
            avg=16.2, high=38.0, low=7.0, unit="배", higher_is_good=False,
            custom_interp=_pe_interp
        )
    else:
        # 데이터 로드 실패 시 역사 맥락 설명 제공
        pe_pos = (
            f"  S&P500 PER (주가수익비율)\n"
            f"    현재값: 로드 중 (multpl.com 연결 필요)\n\n"
            f"    [역사적 맥락]\n"
            f"    역사 평균 (1870년~현재): 약 15~16배\n"
            f"    역사 중간값:              약 14~15배\n"
            f"    닷컴버블 최고점 (2000):  38배 → 이후 나스닥 -80% 폭락\n"
            f"    금융위기 저점 (2009):    8배 → 이후 S&P500 +400% 반등\n"
            f"    코로나 회복 (2021):      38배 수준 → 이후 금리 인상으로 -20% 조정\n"
            f"    현재 (2024~2025 추정):  22~24배 (AI 기술 성장 프리미엄 반영)\n\n"
            f"    [투자 해석 원칙]\n"
            f"    25배 이상: 과열 신호 — 추가 상승 여력이 제한적, 분할 매수 필수\n"
            f"    18~25배:  보통 수준 — 금리 방향이 주가 결정\n"
            f"    14~18배:  역사 평균 — 전통적 매수 우위 구간\n"
            f"    14배 이하: 저평가 신호 — 장기 투자자에게 유리한 진입 구간\n\n"
            f"    PER만으로 타이밍을 잡기는 어렵다. 유동성+금리+이익 성장을 함께 본다.\n"
        )

    # 8. 공포탐욕지수
    fg_pos = ""
    if fg_score is not None:
        fg_pos = _position(
            "공포탐욕지수", fg_score,
            avg=50, high=100, low=0, unit="점", higher_is_good=False,
            custom_interp=(
                f"{fg_score:.0f}점은 탐욕 구간(55 이상)이다.\n"
                "    역사적으로 이 구간에서 너무 공격적으로 사면 단기 조정을 맞을 수 있다.\n"
                "    반대로 극단 공포(20 이하) 구간이 오히려 매수 기회인 경우가 많다."
                if fg_score>=55 else
                f"{fg_score:.0f}점은 중립 구간이다. 시장이 방향을 잡지 못하고 있는 상태."
                if fg_score>=35 else
                f"{fg_score:.0f}점은 공포 구간이다. 역사적으로 공포 구간이 오히려 매수 기회였다."
            )
        )

    # 9. 금리 커브 위치
    yc_pos = ""
    if y2 and y10:
        yc_pos = (
            f"  금리 커브 (2년물 vs 10년물)\n"
            f"    현재: 2년물 {y2:.2f}%  /  10년물 {y10:.2f}%  /  스프레드 {spread:+.2f}%\n"
            f"    과거 평균 스프레드: +0.5~1.5% (정상적 경기 확장 구간)\n"
            f"    2022~2023년 역전 당시: 2년물이 10년물보다 최대 1%p 높았다\n"
            f"    현재 위치: {spread_txt}\n"
            f"    역전이 해소되면서 정상화 중. 역사적으로 역전 해소 후 경기침체 가능성에 주의.\n"
        )

    # ══════════════════════════════════════════════════════
    # 보고서 최종 조합
    # ══════════════════════════════════════════════════════
    SEP  = "=" * 57
    LINE = "-" * 57

    # 섹션5: 투자금 반영 여부 조건부
    if _invest_flag:
        _s5_block = (
            f"5. 포트폴리오  [{INVEST_AMOUNT_만원:,.0f}만원 기준]  환율 {fx_rate:,.0f}원/$\n"
            f"\n"
            f"  투자 가능 금액: {INVEST_AMOUNT_만원:,.0f}만원 x {_ir*100:.0f}% = {_avail:,.0f}만원\n"
            f"  오늘 1차 진입  (40%) = {_today:,.0f}만원\n"
            f"  이유: {entry_reason}\n"
            f"\n"
            f"  종목    배분(1차)   비중   주수     실매수금액    주가\n"
            f"  {'-'*58}\n"
            + ("  없음" if not port_rows else chr(10).join(port_rows)) +
            f"\n"
            f"\n"
            f"  분할 매수 일정:\n"
            f"  1차 오늘   40% = {_today:>8,.0f}만원\n"
            f"  2차 +5일   35% = {_day5:>8,.0f}만원  (MA10 위 + RS 80이상 확인 후)\n"
            f"  3차 +10일  25% = {_day10:>8,.0f}만원  (브레이크아웃 재확인 후)\n"
            f"  잔여 현금: {_cash:,.0f}만원 → 조정 시 2·3차 매수 재원으로 보존"
        )
    else:
        _s5_block = (
            f"5. 포트폴리오\n"
            f"\n"
            f"  [ 투자금 반영 비활성화 ]\n"
            f"  사이드바의 '📊 보고서에 투자금 반영' 체크박스를 켜면\n"
            f"  투자금 기반 포트폴리오와 분할매수 일정이 이곳에 표시됩니다.\n"
            f"\n"
            f"  현재 설정 투자금: {INVEST_AMOUNT_만원:,.0f}만원  |  환율 {fx_rate:,.0f}원/$\n"
            f"  투자 가능 비율: {_ir*100:.0f}%  →  가능 금액 {_avail:,.0f}만원\n"
            f"  투자 판단: {entry_reason}"
        )

    report = f"""{SEP}
  QUANTUM INSTITUTIONAL OS  |  투자 지침서  |  V110
  {now_str}
{SEP}

1. 지금 투자해도 되는 환경인가

  판단: {liq_txt}  ({LIQ_SCORE_100:.0f}점 / {_stage_n}단계)
  {stop_txt}

  핵심 근거:
{env_pos}
{env_neg}

  시장 방향 요약:
  QQQ  ${_sf(qc, '.2f', 'N/A')}   MA200 대비 {p200:+.1f}%
  {'장기 상승 추세 유지 중. MA200 위에 있다는 것은 기관들이 아직 팔지 않는다는 신호.' if p200>0 else '장기 약세장. MA200 아래는 기관들이 매도 우위인 구간.'}

  결론:
  {entry_reason}

{LINE}

2. 지금 유동성은 어느 수준인가  (돈이 얼마나 있는가)

{liq_pos}
  체크리스트:
{liq_table}

  지금 돈의 흐름 해석:
  {"M2 증가 중. 시장에 돈이 들어오고 있다." if m2_score>=60 else "M2 정체 또는 감소. 유동성 공급 둔화."}
  {"크레딧 스프레드 안정. 시스템 위기 신호 없음." if cs_score>=60 else "크레딧 스프레드 확대. 기업 부도 우려 증가."}

{LINE}

3. 각 지표는 역사적으로 어느 위치인가

  [실질금리]
{rr_pos}
  [QQQ RSI]
{rsi_pos}
  [VIX 공포지수]
{vix_pos}
  [크레딧 스프레드]
{cs_pos}
  [S&P500 PER]
{pe_pos}
  [공포탐욕지수]
{fg_pos}
  [금리 커브]
{yc_pos}
  [M2 통화량 증가율]
{m2_pos}
{LINE}

4. RS 전략으로 어떤 종목을 사는가

  전략 원칙:
  강한 유동성 → 강한 섹터 → 그 섹터 내 RS 최상위 종목
  RS Score = QQQ 대비 초과수익률의 역사적 백분위
  RS 80이상 = 상위 20% 주도주 = 기관이 가장 많이 사는 종목
  유동성이 시장에 들어올 때 주도주가 가장 먼저 오른다.

  강한 섹터 (MA20 위 + 1개월 플러스):
  {("  ".join(sec_ok[:4])) if sec_ok else "해당 없음 — 전체 약세"}

  이 섹터들에서 RS 상위 종목:
  종목     RS점수  AI점수     현재가    신호
  {"-"*50}
{"  없음" if not top3_rows else chr(10).join(top3_rows)}

  선택 이유:
{"  없음" if not reason_lines else chr(10).join(reason_lines)}

{LINE}

{_s5_block}

{LINE}

6. 위험 요소와 대응

  현재 위험 요소:{risk_str}

  12개월 시나리오:
  낙관 {prob[0]}%  M2 증가 + 금리 인하  →  +20~35% 수익 가능
  기본 {prob[1]}%  단기 조정 후 회복    →  분할매수 시 +10~15%
  비관 {prob[2]}%  금리 상승 지속       →  -10~20% 손실 가능

  결론: {overall}

  손절:     MA10 이탈 즉시 매도. 기다리지 않는다.
  재진입:   유동성 70점 이상 + RSI 60 이하로 내려온 후
  비중:     한 종목 {_max_s}% 초과 금지. MA20 아래 섹터 진입 금지.

  매수 검토: {", ".join(buy_list) if buy_list else "해당 없음"}
  청산 검토: {", ".join(exit_list) if exit_list else "없음"}
  실적 주의: {", ".join(warn_list)+" — 발표 전 신규 매수 보류" if warn_list else "없음"}

{SEP}
  QUANTUM INSTITUTIONAL OS V106  |  교육 목적
  본 자료는 투자 권유가 아닙니다. 결과 책임은 본인에게 있습니다.
{SEP}"""

    return report.strip()






# ─────────────────────────────────────────────────────────

# ═════════════════════════════════════════════════════════
# TAB 1 — 종목테이블 (V55) — 아래 전체 코드는 TAB1_CONTENT
# ═════════════════════════════════════════════════════════
with tab2:
    _render_stepbar(3, LIQ_ACTION.get("stage", 0), 0)
    st.markdown('<div class="sec-header">📊 종목 선별 (STEP 3)</div>', unsafe_allow_html=True)


    if df_all.empty:
        st.markdown('<div class="warn-box">⚠️ 종목 데이터 없음 — 사이드바 [🔄 새로고침]을 눌러주세요.</div>', unsafe_allow_html=True)
    else:
        _sc_col    = "섹터 AI Score" if "섹터 AI Score" in df_all.columns else "AI Score"
        _liq_stage = LIQ_ACTION.get("stage", 0)

        # ── 종목 카테고리 체크박스 (멀티선택) ──────────────
        # 카테고리별 종목 정의
        _HIGH_DIV_TICKERS = {
            "JNJ","KO","PG","MCD","VZ","T","PFE","MO",
            "ABBV","CVX","XOM","PM","O","IBM","MMM",
        }
        _DIV_GROWTH_TICKERS = {
            "V","MA","JPM","HD","UNH",
            "NEE","LMT","LOW","BLK","SPGI","TGT","APD",
            "SCHD","VYM","DGRO",
        }
        _ETF_TICKERS = {
            "QQQ","SPY","IWM","SMH","XLK","XLV","XLE",
            "TQQQ","ARKK","SQQQ","GLD","TLT"
        }
        _GROWTH_TICKERS = set(DEFAULT_TICKERS) - _HIGH_DIV_TICKERS - _DIV_GROWTH_TICKERS - _ETF_TICKERS
        _DIVIDEND_TICKERS = _HIGH_DIV_TICKERS | _DIV_GROWTH_TICKERS  # 호환용

        # 체크박스 UI
        st.markdown(
            "<div style='font-size:11px;font-weight:600;color:#374151;"
            "margin-bottom:4px'>📂 종목 카테고리 선택</div>",
            unsafe_allow_html=True)
        _cb_col1, _cb_col2, _cb_col3, _cb_col4, _cb_col5 = st.columns(5)
        with _cb_col1:
            _chk_growth   = st.checkbox("📈 성장주",   value=st.session_state.get("chk_growth",   True),  key="chk_growth")
        with _cb_col2:
            _chk_highdiv  = st.checkbox("💰 고배당",   value=st.session_state.get("chk_highdiv",  False), key="chk_highdiv")
        with _cb_col3:
            _chk_divgrow  = st.checkbox("🌱 배당성장", value=st.session_state.get("chk_divgrow",  False), key="chk_divgrow")
        with _cb_col4:
            _chk_etf      = st.checkbox("📊 ETF",      value=st.session_state.get("chk_etf",      False), key="chk_etf")
        with _cb_col5:
            _chk_all      = st.checkbox("🔍 전체",     value=st.session_state.get("chk_all",      False), key="chk_all")

        # 선택된 카테고리에 따라 표시 종목 결정
        if _chk_all or not any([_chk_growth, _chk_highdiv, _chk_divgrow, _chk_etf]):
            _selected_tickers = set(DEFAULT_TICKERS)
            _mode_label = "전체 종목"
            _active_cats = {"growth","highdiv","divgrow","etf"}
        else:
            _selected_tickers = set()
            _active_cats = set()
            if _chk_growth:  _selected_tickers |= _GROWTH_TICKERS;  _active_cats.add("growth")
            if _chk_highdiv: _selected_tickers |= _HIGH_DIV_TICKERS; _active_cats.add("highdiv")
            if _chk_divgrow: _selected_tickers |= _DIV_GROWTH_TICKERS; _active_cats.add("divgrow")
            if _chk_etf:     _selected_tickers |= _ETF_TICKERS;       _active_cats.add("etf")
            _cat_labels = []
            if _chk_growth:  _cat_labels.append("📈 성장주")
            if _chk_highdiv: _cat_labels.append("💰 고배당")
            if _chk_divgrow: _cat_labels.append("🌱 배당성장")
            if _chk_etf:     _cat_labels.append("📊 ETF")
            _mode_label = " + ".join(_cat_labels)

        # 선택된 종목만 필터
        _df_all = df_all.copy()
        _df = _df_all[_df_all["Ticker"].isin(_selected_tickers)].copy()

        # 배당주 카테고리가 포함됐는지 (조건 완화 여부 결정)
        _has_div_cat = bool(_active_cats & {"highdiv","divgrow"})
        _only_div    = _active_cats <= {"highdiv","divgrow"}  # 배당 카테고리만 선택

        # 선택 카테고리 배지 표시
        st.markdown(
            f"<div style='font-size:10px;color:#6B7280;margin:2px 0 8px 0'>"
            f"표시 중: <b style='color:#374151'>{_mode_label}</b> "
            f"— {len(_df)}종목</div>",
            unsafe_allow_html=True)

        # ── 조건수 계산 (카테고리별 조건 다름) ──────────────
        _df["✅유동성"]  = _liq_stage >= 3
        _df["✅브레이크"] = (
            (_df.get("Breakout", pd.Series("—",index=_df.index)) == "✅") |
            (_df.get("3연상",    pd.Series("—",index=_df.index)) == "✅")
        )
        _df["✅거래량"]  = _df.get("Vol Surge",   pd.Series("—",index=_df.index)) == "✅"
        _df["✅RS80"]    = _df.get("RS Score",    pd.Series(0,  index=_df.index)) >= 80
        _df["✅AI70"]    = _df.get(_sc_col,       pd.Series(0,  index=_df.index)) >= 70
        _df["✅신고가"]  = _df.get("52주 고점%",  pd.Series(-99,index=_df.index)) >= -20
        _df["✅실적OK"]  = _df.get("실적경고",    pd.Series("—",index=_df.index)) != "⚠️"
        _df["✅RSI정상"] = _df.get("RSI", pd.Series(50,index=_df.index)).fillna(50) < 70

        if _only_div:
            # 배당 전용 모드: EPS 완화 + 카테고리 소속 여부로 배당 조건 판단
            # ✅ yfinance 데이터 누락과 무관하게 항상 정확히 작동
            _df["✅EPS15"]       = _df.get("EPS Growth%", pd.Series(0,index=_df.index)) >= 0
            _df["✅배당있음"]    = (
                _df["Ticker"].isin(_HIGH_DIV_TICKERS | _DIV_GROWTH_TICKERS) |
                (_df.get("배당수익률%", pd.Series(0,index=_df.index)).fillna(0) >= 0.5)
            )
            _cond_cols = ["✅유동성","✅브레이크","✅거래량","✅RS80","✅AI70",
                          "✅신고가","✅실적OK","✅EPS15","✅RSI정상","✅배당있음"]
        else:
            # 성장주 기준 (혼합 포함)
            _df["✅EPS15"]   = _df.get("EPS Growth%",  pd.Series(0,index=_df.index)) >= 15
            _cond_cols = ["✅유동성","✅브레이크","✅거래량","✅RS80","✅AI70",
                          "✅신고가","✅실적OK","✅EPS15","✅RSI정상"]

        _df["조건수"] = _df[_cond_cols].sum(axis=1).astype(int)
        _n_all = len(_df)

        # session_state에 선택 상태 저장 (STEP4 연동용)
        st.session_state["active_cats"]      = _active_cats
        st.session_state["selected_tickers"] = _selected_tickers
        st.session_state["only_div_mode"]    = _only_div

        # ── V93j: 조건 점수 옆 체크 아이콘 컬럼 ─────────────
        _sc2 = "섹터 AI Score" if "섹터 AI Score" in _df.columns else "AI Score"
        def _fmt_rs(row):
            v = int(row.get("RS Score", 0) or 0)
            return f"✅ {v}" if v >= 80 else f"❌ {v}"
        def _fmt_ai(row):
            v = float(row.get(_sc2, 0) or 0)
            return f"✅ {v:.0f}" if v >= 70 else f"❌ {v:.0f}"
        def _fmt_eps(row):
            v = float(row.get("EPS Growth%", 0) or 0)
            return f"✅ {v:.0f}%" if v >= 15 else f"❌ {v:.0f}%"
        def _fmt_rsi(row):
            v = row.get("RSI", None)
            if v is None or str(v) == "nan": return "—"
            v = float(v)
            return f"🔥 {v:.0f}" if v >= 70 else f"✅ {v:.0f}"
        def _fmt_ath(row):
            v = float(row.get("52주 고점%", 0) or 0)
            return f"✅ {v:.0f}%" if v >= -20 else f"❌ {v:.0f}%"
        def _fmt_cond(row):
            n = int(row.get("조건수", 0))
            if n >= 9: return f"🔥{n}/9"
            if n >= 7: return f"✅{n}/9"
            if n >= 5: return f"🟡{n}/9"
            return f"❌{n}/9"
        _df["RS✅"]   = _df.apply(_fmt_rs,   axis=1)
        _df["AI✅"]   = _df.apply(_fmt_ai,   axis=1)
        _df["EPS✅"]  = _df.apply(_fmt_eps,  axis=1)
        _df["RSI✅"]  = _df.apply(_fmt_rsi,  axis=1)
        _df["신고가✅"] = _df.apply(_fmt_ath, axis=1)
        _df["조건/9"] = _df.apply(_fmt_cond, axis=1)

        # ── ① 조건 배지 — 표 위에 2×4 그리드 ───────────────
        _badge_defs = [
            (f"유동성 {_liq_stage}단계", _liq_stage>=3,
             "전체 OK" if _liq_stage>=3 else "전체 NG"),
            ("브레이크아웃", None, f"{int(_df['✅브레이크'].sum())}/{_n_all}"),
            ("거래량 급증",  None, f"{int(_df['✅거래량'].sum())}/{_n_all}"),
            ("RS 80↑",      None, f"{int(_df['✅RS80'].sum())}/{_n_all}"),
            ("AI 70↑",      None, f"{int(_df['✅AI70'].sum())}/{_n_all}"),
            ("신고가 -20%↑",None, f"{int(_df['✅신고가'].sum())}/{_n_all}"),
            ("EPS 15%↑",    None, f"{int(_df['✅EPS15'].sum())}/{_n_all}"),
            ("실적 안전",    None, f"{int(_df['✅실적OK'].sum())}/{_n_all}"),
        ]
        _bh = ("<div style='display:grid;grid-template-columns:repeat(4,1fr);"
               "gap:5px;margin-bottom:8px'>")
        for _nm, _ok, _sub in _badge_defs:
            if _ok is True:    _bg="#dcfce7"; _tc="#15803d"; _bc="#86EFAC"
            elif _ok is False: _bg="#fee2e2"; _tc="#b91c1c"; _bc="#FECACA"
            else:              _bg="#eff6ff"; _tc="#1d4ed8"; _bc="#BFDBFE"
            _bh += (f"<div style='background:{_bg};border:0.5px solid {_bc};"
                    f"border-radius:7px;padding:5px 9px'>"
                    f"<div style='font-size:10px;font-weight:600;color:{_tc}'>{_nm}</div>"
                    f"<div style='font-size:12px;font-weight:500;color:{_tc};margin-top:1px'>{_sub}</div>"
                    f"</div>")
        _bh += "</div>"
        st.markdown(_bh, unsafe_allow_html=True)

        # ── ② 추천 배너 — 표 위에 ───────────────────────────
        _rec_top = _df[_df["조건수"] >= 7].sort_values(_sc_col, ascending=False).head(8)
        if not _rec_top.empty:
            _tkrs = "".join(
                f"<span style='background:{'#dcfce7' if r['조건수']==8 else '#dbeafe'};"
                f"color:{'#15803d' if r['조건수']==8 else '#1d4ed8'};"
                f"border-radius:5px;padding:2px 7px;font-size:11px;font-weight:600;"
                f"margin-right:4px'>{r['Ticker']} {r['조건수']}/8</span>"
                for _, r in _rec_top.iterrows()
            )
            st.markdown(
                f"<div style='background:#F0FDF4;border:0.5px solid #86EFAC;"
                f"border-radius:7px;padding:7px 12px;margin-bottom:6px;"
                f"display:flex;align-items:center;gap:6px;flex-wrap:wrap'>"
                f"<span style='font-size:11px;font-weight:600;color:#15803d;"
                f"white-space:nowrap'>🎯 추천 종목</span>{_tkrs}</div>",
                unsafe_allow_html=True)

        # ── ③ 정렬 + 테이블 ─────────────────────────────────
        _c1, _c2 = st.columns([3, 1])
        with _c1:
            st.markdown(
                "<span style='font-family:Space Mono,monospace;font-size:10px;"
                "color:#3B5BA5;letter-spacing:1px'>📋 종목 분석 테이블</span>"
                " <span style='font-size:10px;color:#9CA3AF'>— 조건/9 = 9가지 선별조건 충족 수</span>",
                unsafe_allow_html=True)
        with _c2:
            _sort_opt = st.selectbox(
                "정렬", ["조건수","섹터 AI Score","RS Score","배당수익률%","52주 고점%","EPS Growth%","PEG"],
                key="t1_sort", label_visibility="collapsed")

        _disp_df = (
            _df.sort_values(["조건수", _sc_col], ascending=[False,False], na_position="last")
            if _sort_opt == "조건수"
            else _df.sort_values(_sort_opt, ascending=(_sort_opt=="PEG"), na_position="last")
        )

        # PC: 컬럼 구성 고정 — 모드 무관 항상 동일한 순서
        # 배당수익률%는 항시 표시 (데이터 없으면 N/A)
        _showcols = [c for c in [
            "Ticker","섹터","조건/9",
            "RS✅","AI✅","EPS✅","RSI✅","신고가✅",
            "Breakout","Vol Surge","3연상","MA10회복","갭업",
            "Price","배당수익률%","ATR손절","PEG","Rev Growth%",
            "실적예정","실적경고"
        ] if c in _disp_df.columns]

        st.dataframe(
            _disp_df[_showcols],
            use_container_width=True,
            height=520,
            column_config={
                "조건/9":  st.column_config.TextColumn("조건/9",  width="small"),
                "RS✅":    st.column_config.TextColumn("RS",     width="small"),
                "AI✅":    st.column_config.TextColumn("AI",     width="small"),
                "EPS✅":   st.column_config.TextColumn("EPS",    width="small"),
                "RSI✅":   st.column_config.TextColumn("RSI",    width="small"),
                "신고가✅": st.column_config.TextColumn("신고가", width="small"),
                "Price":       st.column_config.NumberColumn("가격$",   format="$%.0f",width="small"),
                "신고가단계":  st.column_config.TextColumn("신고가",    width="small"),
                "52주 고점%":  st.column_config.NumberColumn("신고가%", format="%.0f%%",width="small"),
                "EPS Growth%": st.column_config.NumberColumn("EPS%",   format="%.0f%%",width="small"),
                "PEG":         st.column_config.NumberColumn("PEG",    format="%.1f", width="small"),
                "Breakout":    st.column_config.TextColumn("B/O",                      width="small"),
                "Vol Surge":   st.column_config.TextColumn("Vol↑",                     width="small"),
                "3연상":       st.column_config.TextColumn("3연상",                    width="small"),
                "MA10회복":    st.column_config.TextColumn("🔁회복",                   width="small"),
                "ATR손절":     st.column_config.NumberColumn("ATR손절",  format="$%.2f",width="small"),
                "실적경고":    st.column_config.TextColumn("실적",    width="small"),
                "실적예정":    st.column_config.TextColumn("발표일",  width="small"),
                "섹터":        st.column_config.TextColumn("섹터",    width="medium"),
                "Rev Growth%":  st.column_config.NumberColumn("매출성장%", format="%.0f%%", width="small"),
                "배당수익률%":  st.column_config.NumberColumn("배당%",    format="%.1f%%", width="small",
                                              help="최근 1년 실제 배당금 합계/현재가 기반. 데이터 없으면 N/A"),
            },
            key="t1_df"
        )

        # ── ④ 표 아래 — 경고 배너들 ─────────────────────────
        # ETF / 배당주 RS 안내
        st.markdown(
            "<div style='font-size:11px;color:#6B7280;background:#F9FAFB;"
            "border:0.5px solid #E2E6ED;border-radius:6px;padding:8px 12px;margin-bottom:8px'>"
            "💡 <b>RS 해석 주의</b> &nbsp;·&nbsp; "
            "ETF(QQQ·SMH·TQQQ 등)와 배당주(KO·JNJ·VZ 등)는 나스닥 성장주 대비 RS가 "
            "낮게 나오는 게 <b>정상</b>입니다. 배당주는 RS보다 <b>배당% · 추세 방향</b>으로 판단하세요."
            "</div>",
            unsafe_allow_html=True)
        # 7조건 없음 경고
        _cnt6 = int((_df["조건수"] >= 6).sum())
        _cnt5 = int((_df["조건수"] >= 5).sum())
        if _cnt6 == 0:
            st.markdown(
                f"<div style='background:#FFFBEB;border:0.5px solid #FDE68A;"
                f"border-radius:7px;padding:7px 12px;margin-top:6px;"
                f"font-size:11px;color:#92400E'>"
                f"⚠️ 6조건 이상 충족 종목 없음 &nbsp;|&nbsp; "
                f"5조건 이상: <b>{_cnt5}종목</b> — 조건수↓ 정렬로 확인</div>",
                unsafe_allow_html=True)

        # 청산 경고
        _exit_list = _df[_df.get("Exit Signal", pd.Series("—",index=_df.index)) == "⚠️"]["Ticker"].tolist()
        if _exit_list:
            st.markdown(
                f"<div style='background:#FEF2F2;border:0.5px solid #FECACA;"
                f"border-radius:7px;padding:7px 12px;margin-top:5px;"
                f"font-size:11px;color:#B91C1C'>"
                f"⚠️ <b>청산 검토</b>: {', '.join(_exit_list[:12])}"
                f"{'…' if len(_exit_list)>12 else ''}"
                f" — MA10 이탈. 보유 중이면 매도 검토</div>",
                unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════
# TAB 2 — 포트폴리오 (V91)
# ═════════════════════════════════════════════════════════
with tab3:
    _render_stepbar(4, LIQ_ACTION.get("stage", 0), 0)
    st.markdown('<div class="sec-header">💰 매수 실행 (STEP 4)</div>', unsafe_allow_html=True)

    # ── STEP3 선택 카테고리 안내 배지 ───────────────────────
    _s4_cats = st.session_state.get("active_cats", {"growth"})
    _cat_badge_map = {
        "growth":  ("<span style='background:#EFF6FF;color:#1D4ED8;border:0.5px solid #BFDBFE;"
                    "border-radius:4px;padding:2px 8px;font-size:11px;margin-right:4px'>"
                    "📈 성장주</span>"),
        "highdiv": ("<span style='background:#F0FDF4;color:#15803d;border:0.5px solid #86EFAC;"
                    "border-radius:4px;padding:2px 8px;font-size:11px;margin-right:4px'>"
                    "💰 고배당</span>"),
        "divgrow": ("<span style='background:#F0FDF4;color:#15803d;border:0.5px solid #86EFAC;"
                    "border-radius:4px;padding:2px 8px;font-size:11px;margin-right:4px'>"
                    "🌱 배당성장</span>"),
        "etf":     ("<span style='background:#FFFBEB;color:#92400E;border:0.5px solid #FDE68A;"
                    "border-radius:4px;padding:2px 8px;font-size:11px;margin-right:4px'>"
                    "📊 ETF</span>"),
    }
    _badges = "".join(_cat_badge_map[c] for c in ["growth","highdiv","divgrow","etf"] if c in _s4_cats)
    st.markdown(
        f"<div style='margin-bottom:10px;font-size:11px;color:#6B7280'>"
        f"STEP3 선택 카테고리: {_badges}"
        f"<span style='font-size:10px;color:#9CA3AF'>"
        f"(STEP3 탭에서 변경)</span></div>",
        unsafe_allow_html=True)

    # ── 공통 변수 준비 ─────────────────────────────────────
    _sc_col    = "섹터 AI Score" if "섹터 AI Score" in df_all.columns else "AI Score"
    _stage     = LIQ_ACTION.get("stage", 0)
    _stage_lbl = LIQ_ACTION.get("label", "—")
    _stage_col = LIQ_ACTION.get("color", "#6B7280")
    _stage_bg  = LIQ_ACTION.get("bg",    "#F9FAFB")
    _invest    = INVEST_AMOUNT_만원

    # ── STEP4 종목 필터 — STEP3 체크박스 선택과 연동 ──────
    if not df_all.empty:
        # STEP3에서 선택한 카테고리 읽기
        _s4_selected = st.session_state.get("selected_tickers", set(DEFAULT_TICKERS))
        _s4_only_div = st.session_state.get("only_div_mode", False)

        # 선택된 카테고리 종목만 필터
        _df = df_all.copy()
        if _s4_selected:
            _df = _df[_df["Ticker"].isin(_s4_selected)].copy()

        _df["✅유동성"]  = _stage >= 3
        _df["✅브레이크"] = (
            (_df.get("Breakout", pd.Series("—",index=_df.index)) == "✅") |
            (_df.get("3연상",    pd.Series("—",index=_df.index)) == "✅")
        )
        _df["✅거래량"]  = _df.get("Vol Surge",   pd.Series("—",index=_df.index)) == "✅"
        _df["✅RS80"]    = _df.get("RS Score",    pd.Series(0,  index=_df.index)) >= 80
        _df["✅AI70"]    = _df.get(_sc_col,       pd.Series(0,  index=_df.index)) >= 70
        _df["✅신고가"]  = _df.get("52주 고점%",  pd.Series(-99,index=_df.index)) >= -20
        _df["✅실적OK"]  = _df.get("실적경고",    pd.Series("—",index=_df.index)) != "⚠️"

        if _s4_only_div:
            # 배당 전용: EPS 완화 + 카테고리 소속 여부로 배당 조건 판단
            _s4_div_cat = {
                "JNJ","KO","PG","MCD","VZ","T","PFE","MO",
                "ABBV","CVX","XOM","PM","O","IBM","MMM",
                "V","MA","JPM","HD","UNH","NEE","LMT","LOW",
                "BLK","SPGI","TGT","APD","SCHD","VYM","DGRO",
            }
            _df["✅EPS15"]   = _df.get("EPS Growth%",  pd.Series(0,index=_df.index)) >= 0
            _df["✅배당있음"] = (
                _df["Ticker"].isin(_s4_div_cat) |
                (_df.get("배당수익률%", pd.Series(0,index=_df.index)).fillna(0) >= 0.5)
            )
            _df["조건수"] = _df[["✅유동성","✅브레이크","✅거래량","✅RS80",
                                 "✅AI70","✅신고가","✅실적OK","✅EPS15","✅배당있음"]].sum(axis=1).astype(int)
            _buy_min_cond = 3
        else:
            _df["✅EPS15"]   = _df.get("EPS Growth%", pd.Series(0,index=_df.index)) >= 15
            _df["조건수"] = _df[["✅유동성","✅브레이크","✅거래량","✅RS80",
                                 "✅AI70","✅신고가","✅실적OK","✅EPS15"]].sum(axis=1).astype(int)
            _buy_min_cond = 5

        _buy_df  = _df[_df["조건수"] >= _buy_min_cond].sort_values(["조건수",_sc_col],ascending=[False,False]).head(5)
        _exit_df = _df[_df.get("Exit Signal", pd.Series("—",index=_df.index))=="⚠️"]
    else:
        _buy_df = pd.DataFrame(); _exit_df = pd.DataFrame()

    # ════════════════════════════════════════════════════════
    # ════════════════════════════════════════════════════════
    # 섹션 1 — 투자금 입력 + 매수 종목 상세
    # ════════════════════════════════════════════════════════

    # ── 투자금 입력 — on_change 콜백으로 재로딩 방지 (V93) ──
    # 콜백: 투자금 변경 시 session_state만 업데이트, 전체 재로딩 없음
    def _on_invest_change():
        st.session_state["invest_amount"] = float(
            st.session_state.get("port_invest_amount", 1000))

    _pc1, = st.columns([1])
    with _pc1:
        st.markdown(
            "<div style='font-size:11px;font-weight:500;color:#374151;margin-bottom:4px'>"
            "💼 투자금 (만원)</div>",
            unsafe_allow_html=True)
        st.number_input(
            "투자금",
            min_value=0, max_value=1000000,
            value=int(st.session_state.get("invest_amount", 1000)),
            step=500, format="%d",
            key="port_invest_amount",
            label_visibility="collapsed",
            on_change=_on_invest_change,
            help="투자 예정 금액. 0이면 포트폴리오 계산 생략")
        _invest = float(st.session_state.get("invest_amount", 1000))
        INVEST_AMOUNT_만원 = _invest
        INVEST_AMOUNT_원   = _invest * 10000

    st.markdown("<div style='margin:10px 0'></div>", unsafe_allow_html=True)
    st.markdown(
        "<div style='font-family:Space Mono,monospace;font-size:11px;"
        "color:#3B5BA5;letter-spacing:1px;margin-bottom:8px'>① 매수 종목 상세</div>",
        unsafe_allow_html=True)

    if not _buy_df.empty:
        # ── 매수 종목 표 (st.dataframe — ② 청산 검토와 동일 방식) ──
        _tbl = _buy_df.copy()

        # 손절가 / 목표1 / 목표2 컬럼 추가
        def _atr_stop_val(row):
            _atr = row.get("ATR손절", None)
            _p   = float(row.get("Price", 0))
            try:
                if _atr and float(_atr) > 0:
                    return round(float(_atr), 2)
            except: pass
            return round(_p * 0.92, 2) if _p > 0 else 0.0

        _tbl["손절가$"] = _tbl.apply(_atr_stop_val, axis=1)
        _tbl["목표1$"]  = (_tbl["Price"] * 1.15).round(2)
        _tbl["목표2$"]  = (_tbl["Price"] * 1.25).round(2)

        _buy_cols = [c for c in [
            "Ticker", "섹터", "Price",
            _sc_col, "RS Score", "조건수", "EPS Growth%",
            "손절가$", "목표1$", "목표2$", "52주 고점%"
        ] if c in _tbl.columns]

        st.dataframe(
            _tbl[_buy_cols].sort_values(_sc_col, ascending=False),
            use_container_width=True,
            height=min(80 + len(_tbl) * 36, 400),
            column_config={
                _sc_col:       st.column_config.NumberColumn("AI점수", format="%.0f",   width="small"),
                "RS Score":    st.column_config.NumberColumn("RS",     format="%d",     width="small"),
                "조건수":       st.column_config.NumberColumn("조건/8", format="%d",     width="small"),
                "EPS Growth%": st.column_config.NumberColumn("EPS%",   format="%.0f%%", width="small"),
                "Price":       st.column_config.NumberColumn("현재가$", format="$%.2f",  width="small"),
                "손절가$":     st.column_config.NumberColumn("손절가$", format="$%.2f",  width="small"),
                "목표1$":      st.column_config.NumberColumn("목표1$",  format="$%.2f",  width="small"),
                "목표2$":      st.column_config.NumberColumn("목표2$",  format="$%.2f",  width="small"),
                "52주 고점%":  st.column_config.NumberColumn("신고가%", format="%.0f%%", width="small"),
            },
            key="rpt_buy_tbl"
        )
        st.markdown(
            "<div style='font-size:11px;color:#9CA3AF;margin-top:4px'>"
            "손절가: ATR×2 기준 (없으면 현재가 -8%) &nbsp;·&nbsp; "
            "목표1: +15% (50% 매도) &nbsp;·&nbsp; 목표2: +25% (25% 추가 매도)</div>",
            unsafe_allow_html=True)

        # ── QQQ 대비 수익률 비교 차트 ────────────────────────
        st.markdown("<div style='margin:14px 0 6px 0'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div style='font-family:Space Mono,monospace;font-size:11px;"
            "color:#3B5BA5;letter-spacing:1px;margin-bottom:8px'>"
            "📈 QQQ 대비 수익률 비교 (최근 3개월 · 정규화)</div>",
            unsafe_allow_html=True)

        try:
            import plotly.graph_objects as go

            # 비교 종목: 매수 추천 종목 (최대 5개) + QQQ
            _cmp_tickers = ["QQQ"] + _buy_df["Ticker"].tolist()[:5]
            _period = "3mo"

            # 색상 팔레트 — 주황·노랑·초록·파랑·남색·보라 (눈에 잘 띄는 순)
            _colors = [
                "#FF6B00",  # 주황
                "#F5C400",  # 노랑
                "#00B050",  # 초록
                "#1565C0",  # 파랑
                "#1A237E",  # 남색
                "#6A0DAD",  # 보라
            ]

            # 데이터 수집
            _price_data = {}
            for _tk in _cmp_tickers:
                try:
                    _s = get_close(_tk, _period)
                    if _s is not None and len(_s) >= 10:
                        _price_data[_tk] = _s
                except: pass

            if "QQQ" in _price_data and len(_price_data) > 1:
                # 공통 시작일 기준 정규화 (100 = 시작점)
                _common_idx = _price_data["QQQ"].index
                for _tk in list(_price_data.keys()):
                    _price_data[_tk] = _price_data[_tk].reindex(
                        _common_idx, method="ffill").dropna()

                # 공통 첫 날 기준
                _start_idx = max(s.index[0] for s in _price_data.values())
                _norm = {}
                for _tk, _s in _price_data.items():
                    _s2 = _s[_s.index >= _start_idx]
                    if len(_s2) > 0 and float(_s2.iloc[0]) > 0:
                        _norm[_tk] = (_s2 / float(_s2.iloc[0]) * 100).round(2)

                fig_cmp = go.Figure()

                # QQQ 먼저 (회색 기준선)
                if "QQQ" in _norm:
                    _qqq_last = float(_norm["QQQ"].iloc[-1])
                    _qqq_ret  = _qqq_last - 100
                    fig_cmp.add_trace(go.Scatter(
                        x=_norm["QQQ"].index,
                        y=_norm["QQQ"].values,
                        name=f"QQQ ({_qqq_ret:+.1f}%)",
                        line=dict(color="#E53E3E", width=2.5),
                        hovertemplate="%{y:.1f}<extra>QQQ</extra>"
                    ))

                # 추천 종목 오버레이
                _ci = 0
                for _tk in _cmp_tickers[1:]:
                    if _tk not in _norm: continue
                    _last = float(_norm[_tk].iloc[-1])
                    _ret  = _last - 100
                    _vs   = _ret - _qqq_ret
                    _col  = _colors[_ci % len(_colors)]
                    # QQQ 초과 여부로 선 굵기 구분
                    _lw   = 2.5 if _vs > 0 else 1.5
                    fig_cmp.add_trace(go.Scatter(
                        x=_norm[_tk].index,
                        y=_norm[_tk].values,
                        name=f"{_tk} ({_ret:+.1f}% / QQQ대비 {_vs:+.1f}%)",
                        line=dict(color=_col, width=_lw),
                        hovertemplate=f"%{{y:.1f}}<extra>{_tk}</extra>"
                    ))
                    # 끝점 라벨
                    fig_cmp.add_annotation(
                        x=_norm[_tk].index[-1],
                        y=float(_norm[_tk].iloc[-1]),
                        text=f"{_tk}<br>{_vs:+.1f}%",
                        font=dict(size=9, color=_col),
                        showarrow=False, xanchor="left",
                        xshift=4, bgcolor="rgba(255,255,255,0.8)"
                    )
                    _ci += 1

                # 기준선 (100)
                fig_cmp.add_hline(y=100, line_color="#E2E6ED", line_width=1)

                fig_cmp.update_layout(
                    template="plotly_white",
                    height=300,
                    margin=dict(l=0, r=90, t=10, b=0),
                    legend=dict(
                        orientation="h", yanchor="bottom", y=1.01,
                        xanchor="left", x=0, font=dict(size=10)),
                    xaxis=dict(showgrid=False),
                    yaxis=dict(
                        title="수익률 (시작=100)",
                        tickformat=".0f",
                        gridcolor="#EBEDF0",
                        title_font=dict(size=10)),
                    plot_bgcolor="#FFFFFF",
                    paper_bgcolor="#FAFBFC",
                    hovermode="x unified",
                )
                st.plotly_chart(fig_cmp, use_container_width=True,
                                key="step4_qqq_cmp_chart")

                # 수익률 요약 한 줄
                _sum_parts = []
                for _tk in _cmp_tickers[1:]:
                    if _tk not in _norm: continue
                    _vs = float(_norm[_tk].iloc[-1]) - _qqq_last
                    _icon = "🟢" if _vs > 0 else "🔴"
                    _sum_parts.append(
                        f"<span style='margin-right:10px'>{_icon} <b>{_tk}</b> "
                        f"QQQ대비 <b style='color:{'#15803d' if _vs>0 else '#B91C1C'}'>"
                        f"{_vs:+.1f}%</b></span>")
                if _sum_parts:
                    st.markdown(
                        "<div style='font-size:11px;color:#374151;"
                        "background:#F9FAFB;border:0.5px solid #E2E6ED;"
                        "border-radius:6px;padding:8px 12px;margin-top:4px'>"
                        + "".join(_sum_parts) + "</div>",
                        unsafe_allow_html=True)
            else:
                st.markdown(
                    "<div style='font-size:11px;color:#9CA3AF;padding:10px'>"
                    "차트 데이터 준비 중…</div>",
                    unsafe_allow_html=True)
        except Exception as _e_chart:
            st.markdown(
                f"<div style='font-size:11px;color:#9CA3AF'>차트 로드 실패</div>",
                unsafe_allow_html=True)


        # 투자금 기반 포트폴리오 (V98: ATR 사이징 + GLD 헤지 표시)
        if _invest > 0:
            st.markdown("<div style='margin:8px 0'></div>", unsafe_allow_html=True)
            try:
                fx_raw = mkt.get("USDKRW")
                if fx_raw is None or fx_raw.empty:
                    fx_raw = mkt.get("FX")
                _fx = float(fx_raw.iloc[-1]) if fx_raw is not None and not fx_raw.empty else 1380.0
            except: _fx = 1380.0
            _ir_map = {5:0.90,4:0.65,3:0.40,2:0.10,1:0.0}
            _ir = _ir_map.get(_stage, 0.5)
            _avail = _invest * _ir
            _today = _avail * 0.40
            # GLD 헤지 비중 (V98)
            _gld_map = {5:0.00, 4:0.03, 3:0.07, 2:0.15, 1:0.20}
            _gld_r = _gld_map.get(_stage, 0.05)
            if vix_val and vix_val >= 25: _gld_r = max(_gld_r, 0.12)
            _gld_amt = round(_invest * _gld_r, 0)

            _port_html = (
                f"<div style='background:#F8FAFF;border:0.5px solid #BFDBFE;"
                f"border-radius:8px;padding:12px 14px;margin-top:6px'>"
                f"<div style='font-size:11px;font-weight:600;color:#1D4ED8;margin-bottom:8px'>"
                f"💼 포트폴리오 — 투자금 {_invest:,.0f}만원 기준 (ATR 리스크 1% 룰)</div>"
                f"<div style='display:flex;gap:14px;font-size:11px;color:#6B7280;margin-bottom:6px;flex-wrap:wrap'>"
                f"<span>투자 가능: <b style='color:#0D1117'>{_avail:,.0f}만원</b> ({_ir*100:.0f}%)</span>"
                f"<span>오늘 1차: <b style='color:#0D1117'>{_today:,.0f}만원</b></span>"
                f"<span>환율: <b style='color:#0D1117'>{_fx:,.0f}원/$</b></span>"
                f"</div>"
            )
            if _gld_r > 0:
                _port_html += (
                    f"<div style='background:#FFFBEB;border:0.5px solid #FDE68A;"
                    f"border-radius:6px;padding:7px 10px;margin-bottom:8px;font-size:11px;color:#92400E'>"
                    f"🛡️ GLD 헤지 권고: <b>{_gld_amt:,.0f}만원</b> ({_gld_r*100:.0f}%) "
                    f"— 유동성 {_stage}단계 방어 자산</div>"
                )
            _n_buy = len(_buy_df)
            _weights = [40,35,25] if _n_buy>=3 else ([60,40] if _n_buy==2 else [100])
            _weights = _weights[:_n_buy]
            _total_ai = _buy_df[_sc_col].sum()

            _port_html += (
                "<div style='display:grid;grid-template-columns:"
                "60px 1fr 60px 70px 70px 70px;gap:4px;"
                "font-size:10px;color:#9CA3AF;margin-bottom:4px;"
                "padding:0 4px'>"
                "<div>종목</div><div>비중</div><div>배분</div>"
                "<div>금액(만원)</div><div>주수(주)</div><div>실매수($)</div></div>"
            )
            for i, (_, _r) in enumerate(_buy_df.iterrows()):
                _w   = (_r.get(_sc_col,50) / _total_ai * 100) if _total_ai > 0 else 100/_n_buy
                _pr  = float(_r.get("Price",0))
                _atr_v = _r.get("ATR", None)
                # V98: ATR 포지션 사이징 (1% 리스크 룰)
                _atr_amt, _atr_pct = get_atr_position_size(_invest, _atr_v, _pr)
                if _atr_amt and _atr_pct:
                    _amt = _atr_amt
                    _w   = _atr_pct
                else:
                    _amt = _avail * _w / 100
                _usd = _amt * 10000 / _fx
                _sh  = int(_usd / _pr) if _pr > 0 else 0
                _real= _sh * _pr * _fx / 10000
                _port_html += (
                    f"<div style='display:grid;grid-template-columns:"
                    f"60px 1fr 60px 70px 70px 70px;gap:4px;"
                    f"padding:5px 4px;border-top:0.5px solid #E2E6ED;"
                    f"font-size:11px;align-items:center'>"
                    f"<b style='font-family:Space Mono,monospace'>{_r['Ticker']}</b>"
                    f"<div style='background:#E0F2FE;border-radius:3px;height:6px'>"
                    f"<div style='background:#1D4ED8;width:{min(_w,100):.0f}%;height:100%;border-radius:3px'></div></div>"
                    f"<div style='color:#374151'>{_w:.0f}%</div>"
                    f"<div style='color:#374151'>{_amt:,.0f}</div>"
                    f"<div style='font-weight:600;color:#0D1117'>{_sh}주</div>"
                    f"<div style='color:#6B7280'>{_real:,.0f}</div>"
                    f"</div>"
                )
            _port_html += (
                f"<div style='font-size:10px;color:#9CA3AF;margin-top:8px;padding-top:6px;"
                f"border-top:0.5px solid #E2E6ED'>"
                f"분할 매수: 1차 오늘 40% → 2차 +5일 35% (MA10 위 확인) → 3차 +10일 25%</div>"
                f"</div>"
            )
            st.markdown(_port_html, unsafe_allow_html=True)

            # ── 섹터 집중도 경고 ──────────────────────────────
            _sectors = [_r.get("섹터","기타") for _, _r in _buy_df.iterrows()]
            _sec_count = {}
            for _s in _sectors:
                _sec_count[_s] = _sec_count.get(_s, 0) + 1
            _top_sec = max(_sec_count, key=_sec_count.get) if _sec_count else "—"
            _top_pct = _sec_count.get(_top_sec,0) / len(_sectors) * 100 if _sectors else 0
            if _top_pct >= 60:
                st.markdown(
                    f"<div style='background:#FFFBEB;border:0.5px solid #FDE68A;"
                    f"border-radius:7px;padding:9px 14px;margin-top:6px;font-size:12px;color:#92400E'>"
                    f"⚠️ <b>포트폴리오 섹터 집중 경고</b>: 추천 종목의 {_top_pct:.0f}%가 <b>{_top_sec}</b> 섹터 집중<br>"
                    f"<span style='font-size:11px'>"
                    f"동일 섹터 악재(공급과잉·규제·지정학) 시 포트폴리오 전체가 동시 하락할 수 있습니다. "
                    f"서로 다른 섹터로 1~2개 이내로 제한하는 것을 권장합니다.</span>"
                    f"</div>",
                    unsafe_allow_html=True)

            # ── FX 영향 표시 ──────────────────────────────────
            st.markdown(
                f"<div style='background:#F8FAFF;border:0.5px solid #BFDBFE;"
                f"border-radius:7px;padding:9px 14px;margin-top:6px;font-size:12px;color:#374151'>"
                f"💱 <b>환율 민감도</b> (현재 {_fx:,.0f}원/$)<br>"
                f"<div style='display:flex;gap:16px;margin-top:5px;font-size:11px'>"
                f"<span>환율 <b style='color:#B91C1C'>-5% 하락</b>(원화 강세) → 실질수익률 <b style='color:#B91C1C'>-5%p</b> 감소</span>"
                f"<span>환율 <b style='color:#15803d'>+5% 상승</b>(원화 약세) → 실질수익률 <b style='color:#15803d'>+5%p</b> 증가</span>"
                f"</div>"
                f"<div style='font-size:10px;color:#9CA3AF;margin-top:3px'>"
                f"※ 한국 투자자는 USD/KRW 환율 변동이 수익률에 직접 영향을 미칩니다</div>"
                f"</div>",
                unsafe_allow_html=True)
    else:
        st.markdown(
            "<div style='background:#FFFBEB;border:0.5px solid #FDE68A;"
            "border-radius:8px;padding:12px 16px;font-size:12px;color:#92400E'>"
            "⚠️ 현재 6조건 충족 종목 없음 — 종목테이블에서 4/8 이상 종목을 WATCH LIST로 관리하세요</div>",
            unsafe_allow_html=True)

    st.markdown("<hr style='border-color:#E2E6ED;margin:14px 0'>", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════
    # 섹션 2 — 청산 종목 상세
    # ════════════════════════════════════════════════════════
    st.markdown(
        "<div style='font-family:Space Mono,monospace;font-size:11px;"
        "color:#B91C1C;letter-spacing:1px;margin-bottom:8px'>② 청산 검토 종목 상세</div>",
        unsafe_allow_html=True)
    if not _exit_df.empty:
        _ex_cols = [c for c in ["Ticker","섹터","Price",_sc_col,"RS Score","52주 고점%","Signal"] if c in _exit_df.columns]
        st.dataframe(
            _exit_df[_ex_cols].sort_values(_sc_col, ascending=False),
            use_container_width=True,
            height=min(80+len(_exit_df)*36, 300),
            column_config={
                _sc_col:     st.column_config.NumberColumn("AI",    format="%.0f",  width="small"),
                "RS Score":  st.column_config.NumberColumn("RS",    format="%d",    width="small"),
                "52주 고점%":st.column_config.NumberColumn("신고가%",format="%.0f%%",width="small"),
                "Price":     st.column_config.NumberColumn("가격$", format="$%.0f", width="small"),
            },
            key="rpt_exit_tbl"
        )
        st.markdown(
            "<div style='font-size:11px;color:#9CA3AF;margin-top:4px'>"
            "MA10(10일 이동평균) 이탈 종목 — 단기 추세 이탈 신호. 보유 포지션 정리 검토</div>",
            unsafe_allow_html=True)
    else:
        st.markdown(
            "<div style='background:#F0FDF4;border:0.5px solid #86EFAC;"
            "border-radius:8px;padding:10px 16px;font-size:12px;color:#15803d'>"
            "✅ 청산 검토 종목 없음</div>",
            unsafe_allow_html=True)

    st.markdown("<hr style='border-color:#E2E6ED;margin:14px 0'>", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════
    # 섹션 3 — 판단 근거 요약 (원형: 유동성 카드 | 시장지표 카드)
    # ════════════════════════════════════════════════════════
    st.markdown(
        "<div style='font-family:Space Mono,monospace;font-size:11px;"
        "color:#3B5BA5;letter-spacing:1px;margin-bottom:8px'>"
        "③ 왜 이 판단인가 — 근거 요약</div>",
        unsafe_allow_html=True)

    _ev1, _ev2 = st.columns(2)
    with _ev1:
        # 유동성 핵심 지표
        _ev_rows = [
            ("M2 통화량",         "M2"),
            ("역레포 RRP",        "RRP"),
            ("TGA 재무부",        "TGA"),
            ("실질금리",          "RealRate"),
            ("크레딧 스프레드",   "CreditSpread"),
            ("기준금리",          "FedFunds"),
        ]
        _ev_html = "<div style='font-size:10px;color:#9CA3AF;margin-bottom:6px'>유동성 지표</div>"
        for _name, _key in _ev_rows:
            _info  = IND_SCORE_100.get(_key, {})
            _score = _info.get("score")
            _val   = _info.get("val")
            if _score is None: continue
            if   _score >= 65: _ic="✅"; _sc="#15803d"
            elif _score >= 40: _ic="⚠️"; _sc="#92400E"
            else:              _ic="❌"; _sc="#B91C1C"
            _unit = _info.get("meta",{}).get("unit","")
            _val_str = (f"${_val/1000:.1f}T" if _unit=="B$" and _val and _val>=1000
                        else f"${_val:.0f}B" if _unit=="B$" and _val
                        else f"{_val:.2f}%" if _unit=="%" and _val
                        else "—")
            _ev_html += (
                f"<div style='display:flex;justify-content:space-between;"
                f"align-items:center;padding:4px 0;border-bottom:0.5px solid #F3F4F6;"
                f"font-size:11px'>"
                f"<span style='color:#6B7280'>{_ic} {_name}</span>"
                f"<span style='font-family:Space Mono,monospace;color:{_sc}'>"
                f"{_val_str} &nbsp;<b>{_score:.0f}점</b></span></div>"
            )
        st.markdown(
            f"<div style='background:#F9FAFB;border:0.5px solid #E2E6ED;"
            f"border-radius:8px;padding:12px 14px'>{_ev_html}</div>",
            unsafe_allow_html=True)

    with _ev2:
        # 시장 지표 + 리스크 요인
        _mk_html = "<div style='font-size:10px;color:#9CA3AF;margin-bottom:6px'>시장 지표</div>"
        _mk_rows = []
        try:
            _vix = float(mkt.get("VIX").iloc[-1]) if mkt.get("VIX") is not None else None
            if _vix: _mk_rows.append(("VIX 공포지수", f"{_vix:.1f}",
                "#B91C1C" if _vix>25 else "#92400E" if _vix>18 else "#15803d"))
        except: pass
        try:
            _t10 = float(mkt.get("TNX").iloc[-1]) if mkt.get("TNX") is not None else None
            if _t10: _mk_rows.append(("10년물 금리", f"{_t10:.2f}%",
                "#B91C1C" if _t10>4.5 else "#92400E" if _t10>4.0 else "#15803d"))
        except: pass
        if fg_score:
            _mk_rows.append(("공포탐욕지수", f"{fg_score:.0f}점",
                "#15803d" if fg_score>60 else "#92400E" if fg_score>40 else "#B91C1C"))
        if pe_current:
            _mk_rows.append(("S&P500 PER", f"{pe_current:.1f}배",
                "#B91C1C" if pe_current>27 else "#92400E" if pe_current>22 else "#15803d"))
        _mk_rows.append(("시장 상태", MKT_KR.get(mkt_status,{}).get("label","—"),
            "#15803d" if mkt_status=="RISK ON" else "#B91C1C" if mkt_status=="RISK OFF" else "#92400E"))
        for _n, _v, _c in _mk_rows:
            _mk_html += (
                f"<div style='display:flex;justify-content:space-between;"
                f"align-items:center;padding:4px 0;border-bottom:0.5px solid #F3F4F6;"
                f"font-size:11px'>"
                f"<span style='color:#6B7280'>{_n}</span>"
                f"<span style='font-family:Space Mono,monospace;font-weight:600;color:{_c}'>{_v}</span></div>"
            )
        # 주의 요인
        _risks = []
        try:
            _rr_val = IND_SCORE_100.get("RealRate",{}).get("val")
            if _rr_val and _rr_val >= 2.0: _risks.append(f"실질금리 {_rr_val:.2f}% — 성장주 압박")
        except: pass
        try:
            _cs_val = IND_SCORE_100.get("CreditSpread",{}).get("val")
            if _cs_val and _cs_val >= 4.0: _risks.append(f"크레딧 스프레드 {_cs_val:.2f}% — 경고 수준")
        except: pass
        if hard_stops: _risks.extend(hard_stops[:2])
        if _risks:
            _mk_html += ("<div style='font-size:10px;color:#B91C1C;margin-top:8px'>"
                         "<b>⚠️ 주의 요인</b><br>"
                         + "<br>".join(f"· {r}" for r in _risks[:3]) + "</div>")
        st.markdown(
            f"<div style='background:#F9FAFB;border:0.5px solid #E2E6ED;"
            f"border-radius:8px;padding:12px 14px'>{_mk_html}</div>",
            unsafe_allow_html=True)


# ════════════════════════════════════════════════════════
# TAB 4 — 📅 기타 (FOMC·CPI 일정)
# ════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="sec-header">📅 기타</div>', unsafe_allow_html=True)

    # ── FOMC · CPI 2026 일정 ────────────────────────────
    st.markdown(
        "<div style='font-family:Space Mono,monospace;font-size:11px;"
        "color:#3B5BA5;letter-spacing:1px;margin-bottom:12px'>"
        "📆 2026 주요 경제 이벤트 일정</div>",
        unsafe_allow_html=True)

    _ev_c1, _ev_c2 = st.columns(2)

    with _ev_c1:
        st.markdown("""
        <div style='background:#FFFFFF;border:1px solid #E2E6ED;border-radius:10px;padding:16px'>
          <div style='font-size:13px;font-weight:700;color:#0D1117;margin-bottom:4px'>
            🏦 FOMC 금리 결정</div>
          <div style='font-size:10px;color:#9CA3AF;margin-bottom:12px'>
            한국 시간 새벽 3~4시 발표</div>
          <div style='display:grid;grid-template-columns:repeat(2,1fr);gap:6px'>
            <div style='background:#EFF6FF;border-radius:6px;padding:8px 10px;text-align:center'>
              <div style='font-size:10px;color:#9CA3AF'>1월</div>
              <div style='font-size:13px;font-weight:600;color:#1D4ED8'>1/28</div>
            </div>
            <div style='background:#EFF6FF;border-radius:6px;padding:8px 10px;text-align:center'>
              <div style='font-size:10px;color:#9CA3AF'>3월</div>
              <div style='font-size:13px;font-weight:600;color:#1D4ED8'>3/18</div>
            </div>
            <div style='background:#EFF6FF;border-radius:6px;padding:8px 10px;text-align:center'>
              <div style='font-size:10px;color:#9CA3AF'>5월</div>
              <div style='font-size:13px;font-weight:600;color:#1D4ED8'>5/6</div>
            </div>
            <div style='background:#EFF6FF;border-radius:6px;padding:8px 10px;text-align:center'>
              <div style='font-size:10px;color:#9CA3AF'>6월</div>
              <div style='font-size:13px;font-weight:600;color:#1D4ED8'>6/17</div>
            </div>
            <div style='background:#EFF6FF;border-radius:6px;padding:8px 10px;text-align:center'>
              <div style='font-size:10px;color:#9CA3AF'>7월</div>
              <div style='font-size:13px;font-weight:600;color:#1D4ED8'>7/29</div>
            </div>
            <div style='background:#EFF6FF;border-radius:6px;padding:8px 10px;text-align:center'>
              <div style='font-size:10px;color:#9CA3AF'>9월</div>
              <div style='font-size:13px;font-weight:600;color:#1D4ED8'>9/16</div>
            </div>
            <div style='background:#EFF6FF;border-radius:6px;padding:8px 10px;text-align:center'>
              <div style='font-size:10px;color:#9CA3AF'>10월</div>
              <div style='font-size:13px;font-weight:600;color:#1D4ED8'>10/28</div>
            </div>
            <div style='background:#EFF6FF;border-radius:6px;padding:8px 10px;text-align:center'>
              <div style='font-size:10px;color:#9CA3AF'>12월</div>
              <div style='font-size:13px;font-weight:600;color:#1D4ED8'>12/9</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    with _ev_c2:
        st.markdown("""
        <div style='background:#FFFFFF;border:1px solid #E2E6ED;border-radius:10px;padding:16px'>
          <div style='font-size:13px;font-weight:700;color:#0D1117;margin-bottom:4px'>
            📊 CPI 물가 발표</div>
          <div style='font-size:10px;color:#9CA3AF;margin-bottom:12px'>
            ⚠️ 발표 3일 전 신규 매수 자제</div>
          <div style='display:grid;grid-template-columns:repeat(3,1fr);gap:6px'>
            <div style='background:#FFF7ED;border-radius:6px;padding:8px 10px;text-align:center'>
              <div style='font-size:10px;color:#9CA3AF'>1월</div>
              <div style='font-size:13px;font-weight:600;color:#D97706'>1/14</div>
            </div>
            <div style='background:#FFF7ED;border-radius:6px;padding:8px 10px;text-align:center'>
              <div style='font-size:10px;color:#9CA3AF'>2월</div>
              <div style='font-size:13px;font-weight:600;color:#D97706'>2/11</div>
            </div>
            <div style='background:#FFF7ED;border-radius:6px;padding:8px 10px;text-align:center'>
              <div style='font-size:10px;color:#9CA3AF'>3월</div>
              <div style='font-size:13px;font-weight:600;color:#D97706'>3/11</div>
            </div>
            <div style='background:#FFF7ED;border-radius:6px;padding:8px 10px;text-align:center'>
              <div style='font-size:10px;color:#9CA3AF'>4월</div>
              <div style='font-size:13px;font-weight:600;color:#D97706'>4/10</div>
            </div>
            <div style='background:#FFF7ED;border-radius:6px;padding:8px 10px;text-align:center'>
              <div style='font-size:10px;color:#9CA3AF'>5월</div>
              <div style='font-size:13px;font-weight:600;color:#D97706'>5/12</div>
            </div>
            <div style='background:#FFF7ED;border-radius:6px;padding:8px 10px;text-align:center'>
              <div style='font-size:10px;color:#9CA3AF'>6월</div>
              <div style='font-size:13px;font-weight:600;color:#D97706'>6/10</div>
            </div>
            <div style='background:#FFF7ED;border-radius:6px;padding:8px 10px;text-align:center'>
              <div style='font-size:10px;color:#9CA3AF'>7월</div>
              <div style='font-size:13px;font-weight:600;color:#D97706'>7/14</div>
            </div>
            <div style='background:#FFF7ED;border-radius:6px;padding:8px 10px;text-align:center'>
              <div style='font-size:10px;color:#9CA3AF'>8월</div>
              <div style='font-size:13px;font-weight:600;color:#D97706'>8/12</div>
            </div>
            <div style='background:#FFF7ED;border-radius:6px;padding:8px 10px;text-align:center'>
              <div style='font-size:10px;color:#9CA3AF'>9월</div>
              <div style='font-size:13px;font-weight:600;color:#D97706'>9/9</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin:16px 0'></div>", unsafe_allow_html=True)
    st.markdown(
        "<div style='background:#FEF2F2;border:0.5px solid #FECACA;border-radius:8px;"
        "padding:12px 16px;font-size:12px;color:#B91C1C'>"
        "⚠️ <b>이벤트 매매 주의</b> — FOMC·CPI 발표 전후 변동성 급증. "
        "발표 3일 전 신규 진입 자제, 기존 포지션 손절선 재확인 권장."
        "</div>",
        unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
# ════════════════════════════════════════════════════════
    st.markdown(
        f"<div style='text-align:center;font-size:10px;color:#9CA3AF;"
        f"padding:12px 0 4px 0;border-top:1px solid #E2E6ED;margin-top:12px;line-height:2'>"
        f"<b style='color:#374151'>QUANTUM INSTITUTIONAL OS V111</b>"
        f" &nbsp;|&nbsp; APP_V111 &nbsp;|&nbsp;"
        f"{datetime.now().strftime('%Y-%m-%d %H:%M')} KST<br>"
        f"데이터 출처: FRED (미국 연방준비제도) · Yahoo Finance · multpl.com<br>"
        f"<span style='color:#B91C1C;font-weight:500'>"
        f"본 앱은 교육·정보 제공 목적이며 투자 권유가 아닙니다. "
        f"투자 결과에 대한 책임은 전적으로 본인에게 있습니다."
        f"</span></div>",
        unsafe_allow_html=True
    )
