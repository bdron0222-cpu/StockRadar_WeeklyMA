import os
import json
import time
from datetime import datetime

# 檢查檔案最後修改時間，如果超過 90 天就重新抓取
def should_update(file_path):
    if not os.path.exists(file_path): return True
    last_mod = os.path.getmtime(file_path)
    days_passed = (time.time() - last_mod) / (60 * 60 * 24)
    return days_passed > 90

if __name__ == "__main__":
    if should_update('stocks.json'):
        print("距離上次更新超過 90 天，開始更新股票清單...")
        # 這裡放入你獲取最新股票清單的邏輯
        # ... (例如從證交所下載並儲存) ...
        # 最後存成 stocks.json
    else:
        print("清單無需更新。")