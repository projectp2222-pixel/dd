import requests
from bs4 import BeautifulSoup
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
from datetime import datetime, timedelta, timezone # 시간 설정을 위해 추가됨
import sys

def scrape_to_google_sheet():
    # 1. 구글 인증 설정
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    try:
        key_json = os.environ.get("GCP_KEYS")
        if not key_json:
            print("❌ 에러: GCP_KEYS를 찾을 수 없습니다.")
            return

        key_dict = json.loads(key_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(key_dict, scope)
        client = gspread.authorize(creds)

        # 구글 시트 이름 (본인의 시트 이름과 똑같은지 확인하세요!)
        spreadsheet_name = "디램가격추출" 
        sheet = client.open(spreadsheet_name).sheet1
        print(f"✅ 구글 시트 접속 성공: {spreadsheet_name}")

    except Exception as e:
        print(f"❌ 구글 시트 인증/접속 에러: {e}")
        return

    # 2. 데이터 크롤링 및 한국 시간 설정
    url = "https://www.dramexchange.com/"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # --- [한국 시간으로 고정하는 핵심 코드] ---
        # 세계 표준시(UTC)에 9시간을 더해 한국 시간대(KST)를 만듭니다.
        kst = timezone(timedelta(hours=9))
        now = datetime.now(kst).strftime("%Y-%m-%d %H:%M") 
        # ----------------------------------------

        new_rows = []
        for tr in soup.find_all('tr'):
            cells = tr.find_all(['td', 'th'])
            row_data = [c.get_text(strip=True) for c in cells]
            
            # DDR 제품군만 추출 (Spot 데이터 제외)
            if len(row_data) >= 7 and "DDR" in row_data[0] and "Spot" not in row_data[1]:
                # 맨 앞에 한국 시간을 붙여서 한 줄을 만듭니다.
                new_rows.append([now] + row_data[:7])
                if len(new_rows) >= 7: break

        # 3. 구글 시트 맨 아래에 데이터 누적
        if new_rows:
            sheet.append_rows(new_rows)
            print(f"✅ {now} 기준, {len(new_rows)}개의 데이터를 시트에 추가했습니다!")
        else:
            print("❌ 추출된 데이터가 없습니다.")

    except Exception as e:
        print(f"❌ 크롤링 중 에러 발생: {e}")

if __name__ == "__main__":
    scrape_to_google_sheet()
