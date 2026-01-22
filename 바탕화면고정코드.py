import requests
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
from datetime import datetime, timedelta, timezone
import sys

def scrape_to_new_sheet():
    # 1. 구글 인증 및 시트 접속
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    try:
        key_json = os.environ.get("GCP_KEYS")
        key_dict = json.loads(key_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(key_dict, scope)
        client = gspread.authorize(creds)

        # 구글 시트 파일 열기 (본인의 시트 이름 확인!)
        spreadsheet_name = "디램가격추출" 
        spreadsheet = client.open(spreadsheet_name)

        # 한국 시간 설정
        kst = timezone(timedelta(hours=9))
        now_time = datetime.now(kst)
        sheet_name = now_time.strftime("%m-%d %H:%M") # 시트 이름 (예: 01-23 13:00)
        
        # 2. 새로운 시트 생성
        # 동일한 이름의 시트가 있으면 에러가 날 수 있어 기존 시트를 찾거나 새로 만듭니다.
        try:
            new_sheet = spreadsheet.add_worksheet(title=sheet_name, rows="100", cols="20")
            print(f"✅ 새 시트 생성: {sheet_name}")
        except:
            new_sheet = spreadsheet.get_worksheet_by_title(sheet_name)
            print(f"⚠️ 기존 시트 사용: {sheet_name}")

    except Exception as e:
        print(f"❌ 접속/시트 생성 에러: {e}")
        return

    # 3. 데이터 크롤링
    url = "https://www.dramexchange.com/"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 이미지와 똑같은 제목(헤더) 설정
        header = ["Item", "Daily High", "Daily Low", "Session High", "Session Low", "Session Average", "Session Change"]
        new_rows = [header] # 첫 번째 줄에 제목 추가

        for tr in soup.find_all('tr'):
            cells = tr.find_all(['td', 'th'])
            row_data = [c.get_text(strip=True) for c in cells]
            
            # DDR 제품군만 추출
            if len(row_data) >= 7 and "DDR" in row_data[0] and "Spot" not in row_data[1]:
                processed_row = [row_data[0]] # Item 이름
                
                # 숫자 데이터 처리 (Daily High ~ Session Average)
                for val in row_data[1:6]:
                    try:
                        processed_row.append(float(val.replace(',', '')))
                    except:
                        processed_row.append(val)
                
                processed_row.append(row_data[6]) # Session Change (%)
                new_rows.append(processed_row)
                
                if len(new_rows) > 7: break # 제목 포함 8줄(데이터 7줄)

        # 4. 새 시트에 데이터 입력 및 서식 지정
        if len(new_rows) > 1:
            new_sheet.update('A1', new_rows, value_input_option='USER_ENTERED')
            
            # 제목행(1행) 강조 (선택 사항: 볼드체 등은 API로 복잡해서 데이터만 깔끔히 넣습니다)
            print(f"✅ {sheet_name} 시트에 데이터 입력을 완료했습니다!")
        else:
            print("❌ 추출된 데이터가 없습니다.")

    except Exception as e:
        print(f"❌ 실행 중 에러 발생: {e}")

if __name__ == "__main__":
    scrape_to_new_sheet()
