import os
import json
import time
from generate_watchlist import generate_stocks_json # 引用你原本寫好的生成邏輯
from generate_watchlist import generate_stocks_json # 引用你原本寫好的生成邏輯

# 檢查檔案是否超過 90 天未更新
# 檢查檔案是否超過 90 天未更新
def should_update(file_path):
    if not os.path.exists(file_path): return True
    last_mod = os.path.getmtime(file_path)
    days_passed = (time.time() - last_mod) / (60 * 60 * 24)
    return days_passed > 90

if __name__ == "__main__":
    # 如果不存在 stocks.json 或超過 90 天，就執行更新
    # 如果不存在 stocks.json 或超過 90 天，就執行更新
    if should_update('stocks.json'):
        print("股票清單需更新，執行中...")
        generate_stocks_json() # 直接呼叫你原本寫好的生成函數
        print("股票清單需更新，執行中...")
        generate_stocks_json() # 直接呼叫你原本寫好的生成函數
    else:
        print("股票清單尚無需更新。")