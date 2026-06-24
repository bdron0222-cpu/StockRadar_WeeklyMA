import pandas as pd
import yfinance as yf
import concurrent.futures
import logging
from tqdm import tqdm
from config import STRATEGY  # 匯入你的設定檔

# 設定日誌等級
logging.getLogger("yfinance").setLevel(logging.ERROR)

def normalize_ticker(ticker):
    """自動補上後綴，確保資料格式正確"""
    s_ticker = str(ticker).strip()
    if s_ticker.endswith('.TW') or s_ticker.endswith('.TWO'):
        return s_ticker
    return f"{s_ticker}.TW"

def check_criteria(df):
    """根據設定檔的參數進行技術指標篩選"""
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.columns = [c.capitalize() for c in df.columns]
    
    # 讀取設定檔參數
    ma_fast = STRATEGY["MA_FAST"]
    ma_mid = STRATEGY["MA_MID"]
    ma_slow = STRATEGY["MA_SLOW"]
    ma_long = STRATEGY["MA_LONG"]
    vol_threshold = STRATEGY["VOL_THRESHOLD"]

    # 檢查資料長度是否足夠計算最長均線
    if 'Close' not in df.columns or 'Volume' not in df.columns or len(df) < ma_long + 10:
        return None
    
    df = df.copy()
    df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
    df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce')
    
    # 計算均線
    df['ma_f'] = df['Close'].rolling(window=ma_fast).mean()
    df['ma_m'] = df['Close'].rolling(window=ma_mid).mean()
    df['ma_s'] = df['Close'].rolling(window=ma_slow).mean()
    df['ma_l'] = df['Close'].rolling(window=ma_long).mean()
    
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    
    # 檢查是否有 NaN
    if pd.isna(latest[['ma_f', 'ma_m', 'ma_s', 'ma_l']]).any():
        return None

    # --- 策略邏輯 ---
    # 1. 長線多頭排列
    is_bullish = (latest['ma_m'] > latest['ma_s']) and (latest['ma_s'] > latest['ma_l'])
    # 2. 均線趨勢向上
    is_uptrend = (latest['ma_m'] > prev['ma_m']) and (latest['ma_s'] > prev['ma_s']) and (latest['ma_l'] > prev['ma_l'])
    # 3. 短期回檔訊號
    is_pullback = (latest['Close'] < latest['ma_m']) and (latest['Close'] < latest['ma_f'])
    # 4. 成交量篩選
    is_volume_ok = latest['Volume'] >= vol_threshold
    
    if is_bullish and is_uptrend and is_pullback and is_volume_ok:
        return {
            "Close": round(float(latest['Close']), 2),
            "成交量(張)": int(latest['Volume'] / 1000)
        }
    return None

def process_ticker(ticker):
    clean_ticker = normalize_ticker(ticker)
    try:
        # 使用 auto_adjust=True 修正除權息影響
        df = yf.download(clean_ticker, period="2y", interval="1d", progress=False, auto_adjust=True)
        if df.empty or len(df) < STRATEGY["MA_LONG"]:
            return None
        
        metrics = check_criteria(df)
        if metrics:
            return {"Ticker": clean_ticker, **metrics}
    except Exception as e:
        logging.error(f"下載 {clean_ticker} 失敗: {e}")
    return None

def run_scanner():
    try:
        watchlist = pd.read_csv('watchlist.csv')
        tickers = watchlist['Ticker'].tolist()
    except Exception as e:
        print(f"錯誤：無法讀取 watchlist.csv: {e}")
        return

    if not tickers:
        logging.warning("watchlist.csv 為空，停止掃描。")
        return

    print(f"開始掃描 {len(tickers)} 檔股票...")
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(process_ticker, t): t for t in tickers}
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(tickers), desc="掃描進度"):
            res = future.result()
            if res:
                results.append(res)

    if results:
        pd.DataFrame(results).to_csv('results.csv', index=False, encoding='utf-8-sig')
        print(f"掃描完成！共找到 {len(results)} 檔，結果已存入 results.csv")
    else:
        print("掃描完成，未找到符合條件的標的。")

if __name__ == "__main__":
    run_scanner()