import json
import pandas as pd
import requests
import io

def generate_stocks_json():
    urls = [
        "https://isin.twse.com.tw/isin/C_public.jsp?strMode=2", # 上市
        "https://isin.twse.com.tw/isin/C_public.jsp?strMode=4"  # 上櫃
    ]
    
    all_watchlist = []
    
    print("正在下載上市與上櫃股票清單，請稍候...")
    
    for url in urls:
        response = requests.get(url)
        response.encoding = 'big5'
        
        dfs = pd.read_html(io.StringIO(response.text))
        target_df = None
        for df in dfs:
            if "有價證券代號及名稱" in df.iloc[0].values:
                target_df = df
                break
        
        if target_df is None:
            continue
            
        target_df.columns = target_df.iloc[0]
        target_df = target_df[1:]
        
        # 遍歷資料，提取代號與名稱
        for _, row in target_df.iterrows():
            code_name = str(row['有價證券代號及名稱'])
            parts = code_name.split()
            if len(parts) >= 2:
                code, name = parts[0], parts[1]
                # 過濾規則
                if code.isdigit() and len(code) == 4 and not code.startswith(('00', '02', '01', '9')):
                    all_watchlist.append({"code": f"{code}.TW", "name": name})
    
    # 去除重複 (根據 code 去重)
    unique_watchlist = {item['code']: item['name'] for item in all_watchlist}
    final_list = [{"code": code, "name": name} for code, name in unique_watchlist.items()]
    
    with open("stocks.json", "w", encoding="utf-8") as f:
        json.dump({"watchlist": final_list}, f, ensure_ascii=False, indent=4)
        
    print(f"成功！已產生 stocks.json，共 {len(final_list)} 檔股票。")

if __name__ == "__main__":
    generate_stocks_json()