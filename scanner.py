import pandas as pd
import numpy as np

# --- 參數設定區 (未來想調參數只要改這裡) ---
MA_FAST, MA_MID, MA_SLOW, MA_LONG = 5, 43, 87, 284
VOL_MA_WINDOW = 5
VOL_THRESHOLD = 1000000  # 1000 張 = 1,000,000 股

def check_criteria(df):
    # 1. 資料清理：確保欄位為數值並處理異常
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.columns = [c.capitalize() for c in df.columns]
    
    # 防禦：如果基本欄位缺失或資料過少，直接回傳 False
    if 'Close' not in df.columns or 'Volume' not in df.columns or len(df) < MA_LONG + 10:
        return False
    
    # 轉換為數值，非數值者轉為 NaN
    df = df.copy()
    df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
    df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce')
    
    # 處理 NaN：移除完全沒有數據的行，但保留中間少量缺漏，避免直接 Drop 影響時間序列連續性
    # 如果最新的收盤價是 NaN，這檔股票直接不符合篩選
    if pd.isna(df['Close'].iloc[-1]):
        return False

    # 2. 計算指標
    df['ma5'] = df['Close'].rolling(window=MA_FAST).mean()
    df['ma43'] = df['Close'].rolling(window=MA_MID).mean()
    df['ma87'] = df['Close'].rolling(window=MA_SLOW).mean()
    df['ma284'] = df['Close'].rolling(window=MA_LONG).mean()
    
    # 優化：5 日均量
    df['vol_ma5'] = df['Volume'].rolling(window=VOL_MA_WINDOW).mean()
    
    # 3. 防禦性檢查：確認計算出的均線是否有 NaN (避免剛掛牌的股票)
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    
    # 若最新數據計算不出均線，代表資料不足，直接淘汰
    if pd.isna(latest[['ma5', 'ma43', 'ma87', 'ma284', 'vol_ma5']]).any():
        return False

    # --- 策略邏輯 ---
    
    # A. 多頭排列
    is_bullish = (latest['ma43'] > latest['ma87']) and (latest['ma87'] > latest['ma284'])
    
    # B. 均線趨勢向上 (檢查斜率)
    is_uptrend = (latest['ma43'] > prev['ma43']) and \
                 (latest['ma87'] > prev['ma87']) and \
                 (latest['ma284'] > prev['ma284'])
    
    # C. 短期回檔
    is_pullback = (latest['Close'] < latest['ma43']) and (latest['Close'] < latest['ma5'])
    
    # D. 成交量篩選 (使用 5 日均量)
    is_volume_ok = latest['vol_ma5'] >= VOL_THRESHOLD
    
    return is_bullish and is_uptrend and is_pullback and is_volume_ok