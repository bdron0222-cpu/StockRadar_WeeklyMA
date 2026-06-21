import yfinance as yf

def get_daily_data(ticker):
    """
    下載股票資料，並自動處理上市(.TW)與上櫃(.TWO)的後綴差異。
    """
    try:
        # 1. 第一次嘗試：使用原始代號下載
        df = yf.download(ticker, period="2y", interval="1d", progress=False)
        
        # 2. 判斷機制：如果下載結果是空的，且原始代號是以 .TW 結尾，嘗試自動轉為 .TWO 下載
        if df.empty and ticker.endswith('.TW'):
            fallback_ticker = ticker.replace('.TW', '.TWO')
            # 進行補救嘗試
            df = yf.download(fallback_ticker, period="2y", interval="1d", progress=False)
            
        # 3. 最終檢查：如果還是空的，代表真的抓不到資料
        if df.empty:
            return None
            
        # 4. 核心清理：統一處理 Yahoo 的 MultiIndex 格式
        if isinstance(df.columns, tuple) or hasattr(df.columns, 'get_level_values'):
            if hasattr(df.columns, 'get_level_values'):
                df.columns = df.columns.get_level_values(0)
            df.columns = [c.capitalize() for c in df.columns]
        
        return df

    except Exception as e:
        # 發生任何例外錯誤時，直接回傳 None，確保主程式不會崩潰
        return None