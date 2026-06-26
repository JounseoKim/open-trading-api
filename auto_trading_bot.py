import requests
import json
import time
from datetime import datetime, timezone, timedelta

# ==========================================
# 1. 기본 설정
# ==========================================
APP_KEY    = "PSNtrKryscW80ZpgefugKhAa2qEzCrgg2ugg"
APP_SECRET = "hiY1yyv9Q9teOoS7yAUBvSV+Yo/lN+J9BI7mgFOHqLVWlORzS5luobVuGRAPaNdrvpIqdU5GLpdkNGm9aclD0qc9VbQoi27nn49T0+cvO5RUhkyksmZoC4LiZ7D5GfnoPUfF+/DkDb0FHw2bwmyZLDs7kiZ7Gn26ESJtwfru5JViLNuDycg="
ACCESS_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6ImIwZjZkNGQwLTQxZDEtNDVkZC1hNmYzLTc5ZmNlY2EzNDk4MCIsInByZHRfY2QiOiIiLCJpc3MiOiJ1bm9ndyIsImV4cCI6MTc4MjUxNDAwOSwiaWF0IjoxNzgyNDI3NjA5LCJqdGkiOiJQU050cktyeXNjVzgwWnBnZWZ1Z0toQWEycUV6Q3JnZzJ1Z2cifQ.uN1xGGpqG5gcQVHPqTxM5_id6C3Yf52XHJzl-xsxiftoiObgJel7s3N3xL1Y28esg2hmlOBeUrLzw32MBh72ew"

CANO       = "50194171"          # 계좌번호 앞 8자리
BASE_URL   = "https://openapivts.koreainvestment.com:29443"  # 모의투자 서버
KST        = timezone(timedelta(hours=9))

# ==========================================
# 2. 유틸리티: 로그 출력
# ==========================================
def log(msg: str):
    now = datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {msg}")

def make_headers(tr_id: str, is_post: bool = False) -> dict:
    """공통 헤더 생성"""
    h = {
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "appkey":        APP_KEY,
        "appsecret":     APP_SECRET,
        "tr_id":         tr_id,
    }
    if is_post:
        h["content-type"] = "application/json"
    return h

# ==========================================
# 3. 현재가 조회
# ==========================================
def get_current_price(symbol: str) -> int:
    """주어진 종목의 현재가(원)를 반환합니다."""
    url = (
        f"{BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-price"
        f"?FID_COND_MRKT_DIV_CODE=J&FID_INPUT_ISCD={symbol}"
    )
    res = requests.get(url, headers=make_headers("FHKST01010100"))
    data = res.json()
    if data.get("rt_cd") != "0":
        raise RuntimeError(f"현재가 조회 실패: {data.get('msg1')}")
    return int(data["output"]["stck_prpr"])

# ==========================================
# 4. 주식 잔고 조회
# ==========================================
def get_balance() -> list[dict]:
    """
    현재 계좌에 보유한 주식 잔고를 조회합니다.
    반환값: [{"종목코드", "종목명", "보유수량", "평균단가", "현재가", "평가손익", "수익률(%)"}]
    """
    url = f"{BASE_URL}/uapi/domestic-stock/v1/trading/inquire-balance"
    params = {
        "CANO":            CANO,
        "ACNT_PRDT_CD":    "01",
        "AFHR_FLPR_YN":    "N",
        "OFL_YN":          "",
        "INQR_DVSN":       "02",
        "UNPR_DVSN":       "01",
        "FUND_STTL_ICLD_YN": "N",
        "FNCG_AMT_AUTO_RDPT_YN": "N",
        "PRCS_DVSN":       "00",
        "CTX_AREA_FK100":  "",
        "CTX_AREA_NK100":  "",
    }
    res = requests.get(url, headers=make_headers("VTTC8434R"), params=params)
    data = res.json()

    if data.get("rt_cd") != "0":
        raise RuntimeError(f"잔고 조회 실패: {data.get('msg1')}")

    holdings = []
    for item in data.get("output1", []):
        qty = int(item.get("hldg_qty", "0"))
        if qty == 0:
            continue
        avg_price  = int(float(item.get("pchs_avg_pric", "0")))
        cur_price  = int(item.get("prpr", "0"))
        eval_pnl   = int(item.get("evlu_pfls_amt", "0"))
        pnl_rate   = float(item.get("evlu_pfls_rt", "0"))
        holdings.append({
            "종목코드": item.get("pdno"),
            "종목명":   item.get("prdt_name"),
            "보유수량": qty,
            "평균단가": avg_price,
            "현재가":   cur_price,
            "평가손익": eval_pnl,
            "수익률(%)": round(pnl_rate, 2),
        })

    # 예수금(주문가능금액)도 함께 반환
    output2 = data.get("output2", [{}])
    available_cash = int(output2[0].get("dnca_tot_amt", "0")) if output2 else 0
    return holdings, available_cash

def print_balance():
    """잔고를 사람이 읽기 편한 형태로 출력합니다."""
    holdings, cash = get_balance()
    print("\n" + "=" * 60)
    print("📊 현재 보유 주식 잔고")
    print("=" * 60)
    if not holdings:
        print("  보유 중인 주식이 없습니다.")
    for h in holdings:
        sign = "+" if h["평가손익"] >= 0 else ""
        print(
            f"  [{h['종목코드']}] {h['종목명']}"
            f"  |  {h['보유수량']}주"
            f"  |  평균단가 {h['평균단가']:,}원"
            f"  |  현재가 {h['현재가']:,}원"
            f"  |  평가손익 {sign}{h['평가손익']:,}원 ({sign}{h['수익률(%)']}%)"
        )
    print(f"\n  💰 주문가능 예수금: {cash:,}원")
    print("=" * 60 + "\n")
    return holdings, cash

# ==========================================
# 5. 지정가 매수 주문
# ==========================================
def buy_limit_order(symbol: str, price: int, qty: int) -> dict:
    """
    지정가 매수 주문을 냅니다.
    - symbol: 종목코드 (예: "005930")
    - price:  지정 매수가 (원)
    - qty:    주문 수량 (주)
    """
    url = f"{BASE_URL}/uapi/domestic-stock/v1/trading/order-cash"
    payload = {
        "CANO":        CANO,
        "ACN_PRDT_CD": "01",
        "PDNO":        symbol,
        "ORD_DVSN":    "00",          # 00: 지정가
        "ORD_QTY":     str(qty),
        "ORD_UNPR":    str(price),
    }
    res = requests.post(
        url,
        headers=make_headers("VTTC0802U", is_post=True),
        data=json.dumps(payload),
    )
    data = res.json()

    print("\n" + "=" * 60)
    print(f"🛒 지정가 매수 주문 결과 [{symbol}]")
    print("-" * 60)
    
    if data.get("rt_cd") == "0":
        output = data.get("output", {})
        odno = output.get("ODNO", "확인불가")
        ord_tmd = output.get("ORD_TMD", "")
        
        if len(ord_tmd) == 6:
            formatted_time = f"{ord_tmd[:2]}:{ord_tmd[2:4]}:{ord_tmd[4:]}"
        else:
            formatted_time = ord_tmd
            
        print(f" ✅ 성공: {data.get('msg1')}")
        print(f"  ┠ 주문번호: {odno}")
        print(f"  ┖ 주문시각: {formatted_time}")
    else:
        print(f" ❌ 실패: {data.get('msg1')}")
        print(f"  ┠ 에러코드: {data.get('msg_cd')}")
        print(f"  ┖ 상세사유: 주문을 다시 확인해주세요.")
        
    print("=" * 60 + "\n")

    return data

# ==========================================
# 6. 지정가 매도 주문
# ==========================================
def sell_limit_order(symbol: str, price: int, qty: int) -> dict:
    """
    지정가 매도 주문을 냅니다.
    - symbol: 종목코드
    - price:  지정 매도가 (원)
    - qty:    주문 수량 (주)
    """
    url = f"{BASE_URL}/uapi/domestic-stock/v1/trading/order-cash"
    payload = {
        "CANO":        CANO,
        "ACN_PRDT_CD": "01",
        "PDNO":        symbol,
        "ORD_DVSN":    "00",          # 00: 지정가
        "ORD_QTY":     str(qty),
        "ORD_UNPR":    str(price),
    }
    res = requests.post(
        url,
        headers=make_headers("VTTC0801U", is_post=True),   # 매도 tr_id
        data=json.dumps(payload),
    )
    data = res.json()

    print("\n" + "=" * 60)
    print(f"📉 지정가 매도 주문 결과 [{symbol}]")
    print("-" * 60)
    
    if data.get("rt_cd") == "0":
        output = data.get("output", {})
        odno = output.get("ODNO", "확인불가")
        ord_tmd = output.get("ORD_TMD", "")
        
        if len(ord_tmd) == 6:
            formatted_time = f"{ord_tmd[:2]}:{ord_tmd[2:4]}:{ord_tmd[4:]}"
        else:
            formatted_time = ord_tmd
            
        print(f" ✅ 성공: {data.get('msg1')}")
        print(f"  ┠ 주문번호: {odno}")
        print(f"  ┖ 주문시각: {formatted_time}")
    else:
        print(f" ❌ 실패: {data.get('msg1')}")
        print(f"  ┠ 에러코드: {data.get('msg_cd')}")
        print(f"  ┖ 상세사유: 주문을 다시 확인해주세요.")
        
    print("=" * 60 + "\n")

    return data


# ==========================================
# 7. 거래 시간 확인
# ==========================================
def is_market_open() -> bool:
    """KST 기준 장 운영 시간(09:00 ~ 15:30)인지 확인합니다."""
    now = datetime.now(KST)
    if now.weekday() >= 5:          # 토(5), 일(6) 제외
        return False
    market_open  = now.replace(hour=9,  minute=0,  second=0, microsecond=0)
    market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)
    return market_open <= now <= market_close

# ==========================================
# 8. 자동매매 봇 (매수 + 매도 통합)
# ==========================================
def run_auto_trader(
    symbol:       str,
    buy_target:   int,
    sell_target:  int,
    qty:          int   = 1,
    poll_sec:     int   = 2,
    max_hold_min: int   = 60,
):
    """
    지정가 자동매매 봇.

    동작 흐름:
      1) 현재가 ≤ buy_target  → 지정가 매수 주문
      2) 매수 체결 확인 후
         현재가 ≥ sell_target → 지정가 매도 주문
      3) max_hold_min 분이 지나도 매도 미체결 → 미체결 주문 취소
      4) 매도 완료 시 결과 요약 출력 후 종료

    Parameters
    ----------
    symbol       : 종목코드 (예: "005930")
    buy_target   : 지정 매수가 (원)
    sell_target  : 지정 매도가 (원)
    qty          : 주문 수량 (기본값 1주)
    poll_sec     : 가격 조회 주기 (초, 기본값 2)
    max_hold_min : 매수 후 최대 보유 시간 (분, 기본값 60분)
    """
    print("\n" + "=" * 60)
    print(f"🤖 자동매매 봇 시작")
    print(f"   종목코드  : {symbol}")
    print(f"   매수 목표가: {buy_target:,}원")
    print(f"   매도 목표가: {sell_target:,}원")
    print(f"   주문 수량 : {qty}주")
    print("=" * 60)

    # ── 초기 잔고 확인 ──────────────────────────────────────
    print_balance()

    bought_order_no  = None   # 매수 주문번호
    sold_order_no    = None   # 매도 주문번호
    buy_time         = None   # 매수 체결 시각

    phase = "WAITING_BUY"     # 상태 머신: WAITING_BUY → WAITING_SELL → DONE

    try:
        while phase != "DONE":
            # ── 장 마감 체크 ────────────────────────────────
            if not is_market_open():
                log("⏸  장 운영 시간이 아닙니다. 대기 중…")
                time.sleep(30)
                continue

            try:
                current_price = get_current_price(symbol)
            except Exception as e:
                log(f"⚠️  현재가 조회 오류: {e}")
                time.sleep(poll_sec)
                continue

            # ── [단계 1] 매수 대기 ──────────────────────────
            if phase == "WAITING_BUY":
                log(f"📈 현재가 {current_price:,}원  |  매수 목표가 {buy_target:,}원")

                if current_price <= buy_target:
                    log("🚨 매수 조건 충족! 지정가 매수 주문을 제출합니다…")
                    result = buy_limit_order(symbol, buy_target, qty)

                    if result.get("rt_cd") == "0":
                        bought_order_no = result["output"]["ODNO"]
                        buy_time = datetime.now(KST)
                        log(f"✅ 매수 주문 성공 (주문번호: {bought_order_no})")
                        phase = "WAITING_SELL"
                    else:
                        log(f"❌ 매수 주문 실패: {result.get('msg1')}")

            # ── [단계 2] 매도 대기 ──────────────────────────
            elif phase == "WAITING_SELL":
                hold_minutes = (datetime.now(KST) - buy_time).seconds // 60
                log(
                    f"📉 현재가 {current_price:,}원  |  매도 목표가 {sell_target:,}원"
                    f"  |  보유 {hold_minutes}분 경과"
                )

                # 강제 청산: 최대 보유 시간 초과 시 현재가 매도
                if hold_minutes >= max_hold_min:
                    log(f"⏰ 최대 보유 시간({max_hold_min}분) 초과 → 현재가로 강제 매도합니다.")
                    sell_price = current_price
                else:
                    sell_price = sell_target if current_price >= sell_target else None

                if sell_price:
                    log(f"🚨 매도 조건 충족! 지정가 {sell_price:,}원 매도 주문을 제출합니다…")
                    result = sell_limit_order(symbol, sell_price, qty)

                    if result.get("rt_cd") == "0":
                        sold_order_no = result["output"]["ODNO"]
                        log(f"✅ 매도 주문 성공 (주문번호: {sold_order_no})")
                        phase = "DONE"
                    else:
                        log(f"❌ 매도 주문 실패: {result.get('msg1')}")

            time.sleep(poll_sec)

    except KeyboardInterrupt:
        log("🛑 사용자가 프로그램을 중단했습니다.")

        
    # ── 최종 잔고 확인 ───────────────────────────────────────
    log("📊 최종 잔고를 확인합니다…")
    try:
        print_balance()
    except Exception as e:
        log(f"⚠️  최종 잔고 조회 오류: {e}")

    log("🏁 자동매매 봇 종료.")
