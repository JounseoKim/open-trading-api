import requests
import json
import time
from datetime import datetime

# ==========================================
# 1. 기본 설정
# ==========================================
APP_KEY = "PSNtrKryscW80ZpgefugKhAa2qEzCrgg2ugg"
APP_SECRET = "hiY1yyv9Q9teOoS7yAUBvSV+Yo/lN+J9BI7mgFOHqLVWlORzS5luobVuGRAPaNdrvpIqdU5GLpdkNGm9aclD0qc9VbQoi27nn49T0+cvO5RUhkyksmZoC4LiZ7D5GfnoPUfF+/DkDb0FHw2bwmyZLDs7kiZ7Gn26ESJtwfru5JViLNuDycg="
ACCESS_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6IjA2ZTJjNTI3LTFkZjItNGNkZC1iZmZlLWIzODY3ZmQxYTc4ZCIsInByZHRfY2QiOiIiLCJpc3MiOiJ1bm9ndyIsImV4cCI6MTc4MjIxMjgwMiwiaWF0IjoxNzgyMTI2NDAyLCJqdGkiOiJQU050cktyeXNjVzgwWnBnZWZ1Z0toQWEycUV6Q3JnZzJ1Z2cifQ.jYvlvofMQuezslmCikAYi_NbWYsR_lpMJyb05_ZjLloA4fHVTPcufyXcdgioOQya8mCPPtf0L5xGCaoWJPygpA"
CANO = "50194171"
SYMBOL = "005930"  # 삼성전자 종목코드
TARGET_PRICE = 350000  # 매수 목표가

# ==========================================
# 2. 현재가 조회 함수
# ==========================================
def get_current_price():
    url = "https://openapivts.koreainvestment.com:29443/uapi/domestic-stock/v1/quotations/inquire-price?FID_COND_MRKT_DIV_CODE=J&FID_INPUT_ISCD=" + SYMBOL
    headers = {
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "tr_id": "FHKST01010100"
    }
    res = requests.get(url, headers=headers)
    data = res.json()
    return int(data['output']['stck_prpr'])

# ==========================================
# 3. 시장가 매수 주문 함수
# ==========================================
def buy_market_order():
    url = "https://openapivts.koreainvestment.com:29443/uapi/domestic-stock/v1/trading/order-cash"
    headers = {
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "tr_id": "VTTC0802U",
        "content-type": "application/json"
    }
    payload = json.dumps({
        "CANO": CANO,
        "ACN_PRDT_CD": "01",
        "PDNO": SYMBOL,
        "ORD_DVSN": "01",  # 01: 시장가
        "ORD_QTY": "1",    # 주문 수량 1주
        "ORD_UNPR": "0"    # 시장가 주문이므로 가격은 0
    })
    res = requests.post(url, headers=headers, data=payload)
    return res.json()

# ==========================================
# 4. 메인 자동매매 무한 루프 실행
# ==========================================
print("=== 🚀 자동매매 봇 가동을 시작합니다 ===")

while True:
    try:
        # 현재 시간과 주가 확인
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        current_price = get_current_price()
        print(f"[{now}] 삼성전자 현재가: {current_price}원 (목표가: {TARGET_PRICE}원)")

        # 매수 조건 판단
        if current_price <= TARGET_PRICE:
            print(">>> 🚨 목표가 도달! 매수 주문을 실행합니다.")
            result = buy_market_order()
            
            if result['rt_cd'] == '0':
                print(f">>> ✅ 매수 주문 성공! (주문번호: {result['output']['ODNO']})")
            else:
                print(f">>> ❌ 매수 주문 실패: {result['msg1']}")
            
            # 주문을 넣었으면 중복 구매를 막기 위해 무한 루프 탈출
            break 
        
        # 1초 대기 (증권사 서버 차단 방지)
        time.sleep(1)
        
    except Exception as e:
        print(f"시스템 에러 발생: {e}")
        time.sleep(1)
