from scanner import check_criteria
from data_fetcher import get_daily_data
import pandas as pd

def test_strategy(ticker):
    print(f"--- 正在檢查個股: {ticker} ---")
    df = get_daily_data(ticker)
    
    if df is not None and not df.empty:
        # 手動計算均線與成交量
        df['ma5'] = df['Close'].rolling(window=5).mean()
        df['ma43'] = df['Close'].rolling(window=43).mean()
        df['ma87'] = df['Close'].rolling(window=87).mean()
        df['ma284'] = df['Close'].rolling(window=284).mean()
        
        latest = df.iloc[-1]
        
        # 【關鍵檢查】：印出所有的判斷條件
        print(f"最新收盤價: {float(latest['Close']):.2f}")
        print(f"今日成交量 (股): {float(latest['Volume']):,.0f}")
        print(f"成交量達標 (>=300萬): {float(latest['Volume']) >= 3000000}")
        print(f"多頭排列成立: {(latest['ma43'] > latest['ma87']) and (latest['ma87'] > latest['ma284'])}")
        print(f"回檔條件成立: {(latest['Close'] < latest['ma43']) and (latest['Close'] < latest['ma5'])}")
        
        result = check_criteria(df)
        print(f"最終篩選結果: {'✅ 符合' if result else '❌ 不符合'}")
    else:
        print("❌ 無法取得資料")

if __name__ == "__main__":
    # 分別測試你覺得有問題的這兩檔
    test_strategy("1203.TW")
    test_strategy("2231.TW")