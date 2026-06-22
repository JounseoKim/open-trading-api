import requests
import json

url = "https://openapivts.koreainvestment.com:29443/uapi/domestic-stock/v1/quotations/inquire-price?fid_cond_mrkt_div_code=J&fid_input_iscd=005930"

payload = ""
headers = {
  'content-type': 'application/json',
  'authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6IjA2ZTJjNTI3LTFkZjItNGNkZC1iZmZlLWIzODY3ZmQxYTc4ZCIsInByZHRfY2QiOiIiLCJpc3MiOiJ1bm9ndyIsImV4cCI6MTc4MjIxMjgwMiwiaWF0IjoxNzgyMTI2NDAyLCJqdGkiOiJQU050cktyeXNjVzgwWnBnZWZ1Z0toQWEycUV6Q3JnZzJ1Z2cifQ.jYvlvofMQuezslmCikAYi_NbWYsR_lpMJyb05_ZjLloA4fHVTPcufyXcdgioOQya8mCPPtf0L5xGCaoWJPygpA',
  'appkey': 'PSNtrKryscW80ZpgefugKhAa2qEzCrgg2ugg',
  'appsecret': 'hiY1yyv9Q9teOoS7yAUBvSV+Yo/lN+J9BI7mgFOHqLVWlORzS5luobVuGRAPaNdrvpIqdU5GLpdkNGm9aclD0qc9VbQoi27nn49T0+cvO5RUhkyksmZoC4LiZ7D5GfnoPUfF+/DkDb0FHw2bwmyZLDs7kiZ7Gn26ESJtwfru5JViLNuDycg=',
  'tr_id': 'FHKST01010100'
}

response = requests.request("GET", url, headers=headers, data=payload)

data = response.json()

current_price = data['output']['stck_prpr']
print(f"조회된 삼성전자의 현재가는 {current_price}원 입니다.")
