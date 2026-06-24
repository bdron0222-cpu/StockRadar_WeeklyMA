import requests
import pandas as pd
import io
import re

def fetch_market_list():
    print(">>> [系統] 正在抓取全市場資料 (精準標記上市/上櫃)...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    # 直接在清單中指定後綴，Mode 2 是上市，Mode 4 是上櫃
    targets = [
        {"url": "https://isin.twse.com.tw/isin/C_public.jsp?strMode=2", "suffix": ".TW"},
        {"url": "https://isin.twse.com.tw/isin/C_public.jsp?strMode=4", "suffix": ".TWO"}
    ]
    
    all_tickers = []
    
    for target in targets:
        url = target['url']
        suffix = target['suffix']
        print(f">>> 正在讀取: {url} ({suffix})")
        
        try:
            r = requests.get(url, headers=headers)
            dfs = pd.read_html(io.StringIO(r.text))
            df = dfs[0]
            
            for val in df[0]:
                if isinstance(val, str):
                    # 使用正規表達式切開代碼 (處理全形與半形空白)
                    parts = re.split(r'\s+', val.strip())
                    if len(parts) >= 1:
                        code = parts[0]
                        # 篩選：4位數、純數字、非 00 開頭
                        if len(code) == 4 and code.isdigit() and not code.startswith('00'):
                            all_tickers.append(f"{code}{suffix}")
                            
        except Exception as e:
            print(f">>> [錯誤] 解析網址 {url} 失敗: {e}")

    # 存檔
    pd.DataFrame({'Ticker': all_tickers}).to_csv('raw_watchlist.csv', index=False)
    print(f">>> [系統] 成功！共抓取 {len(all_tickers)} 檔股票 (已包含 .TW 與 .TWO)。")

if __name__ == "__main__":
    fetch_market_list()