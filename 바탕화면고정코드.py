import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from datetime import datetime

def scrape_dram_to_desktop():
    url = "https://www.dramexchange.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
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
            
            if len(row_data) >= 7 and "DDR" in row_data[0]:
                if "Spot" not in row_data[1] and "Memory" not in row_data[2]:
                    extracted_rows.append(row_data[:7])

        if not extracted_rows:
            return

        df = pd.DataFrame(extracted_rows[:7], columns=columns)

        # --- [수정된 부분: 바탕화면 경로 고정] ---
        now = datetime.now()
        
        # 1. 사용자의 윈도우 바탕화면 경로를 자동으로 찾아냅니다.
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        
        # 2. 바탕화면에 'DRAM_Prices'라는 메인 폴더, 그 안에 '2026-01' 같은 월별 폴더를 설정합니다.
        folder_name = now.strftime("%Y-%m")
        target_folder = os.path.join(desktop_path, "DRAM_Prices", folder_name)
        
        # 3. 폴더가 없으면 새로 만듭니다.
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)

        # 4. 파일명을 정하고 최종 경로를 합칩니다.
        timestamp = now.strftime("%Y-%m-%d_%H-%M") 
        file_name = f"{timestamp}_DRAM_Price.xlsx"
        file_path = os.path.join(target_folder, file_name)
        
        # 5. 엑셀 저장
        df.to_excel(file_path, index=False)
        print(f"✅ 바탕화면 저장 완료: {file_path}")

    except Exception as e:
        # 에러 발생 시 바탕화면에 로그를 남겨서 바로 볼 수 있게 합니다.
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        with open(os.path.join(desktop, "dram_error_log.txt"), "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now()}] 에러 발생: {str(e)}\n")

if __name__ == "__main__":
    scrape_dram_to_desktop()
    