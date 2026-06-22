import requests
import json

url = "https://openapivts.koreainvestment.com:29443/uapi/domestic-stock/v1/trading/order-cash"

payload = json.dumps({
  "CANO": "50194171",
  "ACNT_PRDT_CD": "01",
  "PDNO": "005930",
  "ORD_DVSN": "00",
  "ORD_QTY": "1",
  "ORD_UNPR": "55000"
})
headers = {
  'content-type': 'application/json',
  'authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6IjA2ZTJjNTI3LTFkZjItNGNkZC1iZmZlLWIzODY3ZmQxYTc4ZCIsInByZHRfY2QiOiIiLCJpc3MiOiJ1bm9ndyIsImV4cCI6MTc4MjIxMjgwMiwiaWF0IjoxNzgyMTI2NDAyLCJqdGkiOiJQU050cktyeXNjVzgwWnBnZWZ1Z0toQWEycUV6Q3JnZzJ1Z2cifQ.jYvlvofMQuezslmCikAYi_NbWYsR_lpMJyb05_ZjLloA4fHVTPcufyXcdgioOQya8mCPPtf0L5xGCaoWJPygpA',
  'appkey': 'PSNtrKryscW80ZpgefugKhAa2qEzCrgg2ugg',
  'appsecret': 'hiY1yyv9Q9teOoS7yAUBvSV+Yo/lN+J9BI7mgFOHqLVWlORzS5luobVuGRAPaNdrvpIqdU5GLpdkNGm9aclD0qc9VbQoi27nn49T0+cvO5RUhkyksmZoC4LiZ7D5GfnoPUfF+/DkDb0FHw2bwmyZLDs7kiZ7Gn26ESJtwfru5JViLNuDycg=',
  'tr_id': 'VTTC0802U'
}

response = requests.request("POST", url, headers=headers, data=payload)
data = response.json()

print(f"응답 코드: {data['rt_cd']}")
print(f"메시지: {data['msg1']}")

if data['rt_cd'] == '0':
    print(f"주문 성공! 주문번호: {data['output']['ODNO']}")
  
print(response.text)
