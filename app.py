import streamlit as st
import pandas as pd
import os

# 設定網頁版面配置
st.set_page_config(page_title="StockRadar WeeklyMA", layout="wide")

st.title("📈 StockRadar WeeklyMA 選股雷達")

# 新增：選股策略說明區塊 (可摺疊，保持頁面簡潔)
with st.expander("🔍 當前篩選策略說明 (點擊展開查看細節)"):
    st.markdown("""
    本系統自動掃描全市場，篩選出符合以下所有條件的潛力股：
    1. **長線多頭排列**：MA43 > MA87 > MA284 (代表中長期趨勢向上)
    2. **均線趨勢向上**：MA43, MA87, MA284 本身斜率為正 (今日數值 > 昨日數值)
    3. **短期回檔訊號**：股價 < MA43 且 股價 < MA5 (正在修正回測)
    4. **成交量篩選**：單日成交量 >= 1,000,000 股 (即 1,000 張以上)
    """)

# 設定檔案路徑
DATA_FILE = os.path.join(os.path.dirname(__file__), "results.csv")

if not os.path.exists(DATA_FILE):
    st.error(f"找不到 results.csv！請先執行 main.py 進行掃描。")
else:
    # 讀取篩選結果
    df = pd.read_csv(DATA_FILE, encoding='utf-8-sig')
    
    st.write(f"目前共篩選出 {len(df)} 檔潛力股")
    
    # 顯示互動式表格
    st.dataframe(df, use_container_width=True, hide_index=True)

    # 產生下載按鈕
    csv = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
    st.download_button(
        label="📥 下載 CSV 結果",
        data=csv,
        file_name='weekly_ma_results.csv',
        mime='text/csv',
    )