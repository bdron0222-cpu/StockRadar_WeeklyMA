import yfinance as yf

def get_daily_data(ticker):
    try:
        # 下載資料
        df = yf.download(ticker, period="2y", interval="1d", progress=False)
        
        # 如果下載後是空的，直接回傳 None
        if df.empty:
            return None
            
        # --- 核心清理：統一處理 Yahoo 的 MultiIndex 格式 ---
        # 如果欄位包含 MultiIndex，強制降維並將欄位轉為首字大寫
        if isinstance(df.columns, tuple) or hasattr(df.columns, 'get_level_values'):
             # 處理 MultiIndex，只取第一層
            if hasattr(df.columns, 'get_level_values'):
                df.columns = df.columns.get_level_values(0)
            df.columns = [c.capitalize() for c in df.columns]
        
        return df
    except Exception as e:
        print(f"DEBUG: {ticker} 下載錯誤: {e}")
        return None