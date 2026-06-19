import json
import concurrent.futures
import pandas as pd
from tqdm import tqdm
from data_fetcher import get_daily_data
from scanner import check_criteria

def process_stock(stock_info):
    # stock_info 現在是一個字典，例如 {'code': '2330.TW', 'name': '台積電'}
    ticker = stock_info['code']
    name = stock_info['name']
    
    try:
        df = get_daily_data(ticker)
        if df is not None and not df.empty:
            passed = check_criteria(df)
            if passed:
                return {'代號': ticker, '名稱': name}
    except Exception:
        pass
    return None

def main():
    try:
        with open('stocks.json', 'r', encoding='utf-8') as f:
            stock_list = json.load(f).get('watchlist', [])
    except:
        print("無法讀取 stocks.json")
        return

    results = []

    print(f"=== 開始正式掃描 (共 {len(stock_list)} 檔) ===")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        # 這裡改為傳入整個字典
        futures = {executor.submit(process_stock, item): item['code'] for item in stock_list}
        
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(stock_list), desc="掃描中"):
            res = future.result()
            if res:
                results.append(res)

    if results:
        pd.DataFrame(results).to_csv('results.csv', index=False, encoding='utf-8-sig')
        print(f"\n=== 掃描完成！共找到 {len(results)} 檔，結果已存入 results.csv ===")
    else:
        print("\n=== 掃描完成，沒有符合條件的股票 ===")

if __name__ == "__main__":
    main()