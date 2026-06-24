import pandas as pd
import yfinance as yf
from tqdm import tqdm
import time
import os
import logging
import re  # 匯入正規表達式模組

# 設定 Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_market_suffix(ticker_code):
    """判斷該代碼應為 .TW 還是 .TWO"""
    try:
        # 使用 fast_info 取得交易所資訊
        ticker = yf.Ticker(f"{ticker_code}.TW")
        exchange = ticker.fast_info.get('exchange', '').upper()
        
        if exchange in ['TWO', 'OTC']:
            return f"{ticker_code}.TWO"
        else:
            return f"{ticker_code}.TW"
    except Exception:
        # 發生錯誤時預設為 .TW
        return f"{ticker_code}.TW"

def update_watchlist():
    """清洗並標記股票清單，使用正規表達式提取代碼"""
    input_file = 'raw_watchlist.csv'
    output_file = 'watchlist.csv'
    
    if not os.path.exists(input_file):
        logging.error(f">>> [錯誤] 找不到 {input_file}，請先執行 generate_watchlist.py")
        return

    logging.info(">>> [系統] 開始資料清洗與標記...")
    df = pd.read_csv(input_file)
    cleaned_data = []

    # 使用 tqdm 建立進度條
    for index, row in tqdm(df.iterrows(), total=len(df), desc="正在清洗資料"):
        raw_ticker = str(row['Ticker']).strip()
        
        # --- 核心修正：使用正規表達式從字串中提取 4 位數字 ---
        match = re.search(r'(\d{4})', raw_ticker)
        if not match:
            continue
        
        ticker = match.group(1)
            
        # 2. 剔除 ETF (以 00 開頭)
        if ticker.startswith('00'):
            continue
            
        # 3. 標記上市櫃 (.TW / .TWO)
        market_ticker = get_market_suffix(ticker)
        cleaned_data.append(market_ticker)
        
        # 微小的延遲
        time.sleep(0.05)

    # 存檔
    pd.DataFrame({'Ticker': cleaned_data}).to_csv(output_file, index=False)
    logging.info(f">>> [系統] 清洗完成！已產出 {output_file} (共 {len(cleaned_data)} 檔)")

if __name__ == "__main__":
    update_watchlist()