import check_and_update_stocks
from scanner import run_scanner

def main():
    print("=== 系統啟動：開始執行全自動金融資料管線 ===")
    
    # 1. 第一階段：資料清洗與標準化 (Clean Data)
    # 讀取 raw_watchlist.csv，過濾 ETF、補上 .TW/.TWO 代碼，產出 watchlist.csv
    try:
        check_and_update_stocks.update_watchlist()
    except Exception as e:
        print(f"資料清洗階段發生錯誤: {e}")
        return

    # 2. 第二階段：正式掃描 (Run Scanner)
    # 讀取標準化後的 watchlist.csv 並執行技術指標篩選
    try:
        run_scanner()
    except Exception as e:
        print(f"掃描階段發生錯誤: {e}")
        return
    
    print("=== 系統結束：全自動掃描管線執行完畢 ===")

if __name__ == "__main__":
    main()