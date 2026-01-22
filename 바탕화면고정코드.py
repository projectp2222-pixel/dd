import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from datetime import datetime

def scrape_dram_github():
    url = "https://www.dramexchange.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        columns = ["Item", "Daily High", "Daily Low", "Session High", "Session Low", "Session Average", "Session Change"]
        extracted_rows = []
        
        for tr in soup.find_all('tr'):
            cells = tr.find_all(['td', 'th'])
            row_data = [c.get_text(strip=True) for c in cells]
            
            # DDR 제품군 데이터만 추출
            if len(row_data) >= 7 and "DDR" in row_data[0]:
                if "Spot" not in row_data[1]:
                    extracted_rows.append(row_data[:7])

        if not extracted_rows:
            print("❌ 데이터를 찾지 못했습니다.")
            return

        # 상위 7개 항목 데이터프레임 생성
        df = pd.DataFrame(extracted_rows[:7], columns=columns)

        # --- [경로 설정 핵심 부분] ---
        # 1. 현재 파이썬 파일이 실행되는 '폴더'의 절대 경로를 잡습니다.
        base_path = os.getcwd() 
        
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d_%H-%M") 
        file_name = f"{timestamp}_DRAM_Price.xlsx"
        
        # 2. 파일 저장 경로를 절대 경로로 합칩니다.
        file_path = os.path.join(base_path, file_name)
        
        # 3. 엑셀 저장 (경로를 명시적으로 지정)
        df.to_excel(file_path, index=False)
        
        print(f"✅ 저장 완료! 파일 위치: {file_path}")
        print(df) # 로그에서도 데이터를 볼 수 있게 출력합니다.

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        # 오류가 나면 깃허브 액션도 실패로 표시되게 강제 종료합니다.
        import sys
        sys.exit(1)

if __name__ == "__main__":
    scrape_dram_github()

    
