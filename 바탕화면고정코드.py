import requests
from bs4 import BeautifulSoup
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
from datetime import datetime
import sys

def scrape_to_google_sheet():
    # 1. 구글 인증 설정 (깃허브 비밀 금고에서 열쇠를 꺼내옵니다)
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    try:
        # 깃허브 Settings에서 등록한 'GCP_KEYS'를 가져오는 부분입니다.
        key_json = os.environ.get("GCP_KEYS")
        if not key_json:
            print("❌ 에러: GCP_KEYS를 찾을 수 없습니다. 깃허브 Secrets 설정을 확인하세요.")
            return

        key_dict = json.loads(key_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(key_dict, scope)
        client = gspread.authorize(creds)

        # ---------------------------------------------------------
        # 2. 구글 시트 열기 (중요: 본인이 만든 구글 시트 이름을 적으세요!)
        spreadsheet_name = "DRAM_Data_Sheet"  # <--- 여기에 구글 시트 제목을 똑같이 적으세요!
        # ---------------------------------------------------------
        
        sheet = client.open(spreadsheet_name).sheet1
        print(f"✅ 구글 시트 접속 성공: {spreadsheet_name}")

    except Exception as e:
        print(f"❌ 구글 시트 인증/접속 에러: {e}")
        return

    # 3. 데이터 크롤링 (우리가 쓰던 로직 그대로입니다)
    url = "https://www.dramexchange.com/"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        new_rows = []

        for tr in soup.find_all('tr'):
            cells = tr.find_all(['td', 'th'])
            row_data = [c.get_text(strip=True) for c in cells]
            if len(row_data) >= 7 and "DDR" in row_data[0] and "Spot" not in row_data[1]:
                # [시간, 품목명, 가격들...] 순서로 한 줄의 데이터를 만듭니다.
                new_rows.append([now] + row_data[:7])
                if len(new_rows) >= 7: break

        # 4. 구글 시트 맨 아래에 데이터 추가
        if new_rows:
            # append_rows는 기존 데이터 아래에 새로운 줄들을 이어 붙입니다.
            sheet.append_rows(new_rows)
            print(f"✅ {len(new_rows)}개의 데이터를 구글 시트에 누적했습니다!")
        else:
            print("❌ 추출된 데이터가 없습니다.")

    except Exception as e:
        print(f"❌ 크롤링 중 에러 발생: {e}")

if __name__ == "__main__":
    scrape_to_google_sheet()

    

