import streamlit as st
import pandas as pd
import os
import datetime

# 設定網頁版面配置
st.set_page_config(page_title="StockRadar WeeklyMA", layout="wide")

st.title("📈 StockRadar WeeklyMA 選股雷達")

# 設定檔案路徑
DATA_FILE = os.path.join(os.path.dirname(__file__), "results.csv")

# 檢查資料是否存在
if not os.path.exists(DATA_FILE):
    st.error(f"找不到 results.csv！請確認 main.py 是否已執行成功。")
else:
    # 讀取篩選結果 (不使用 cache，確保每次讀取都是最新的檔案狀態)
    df = pd.read_csv(DATA_FILE, encoding='utf-8-sig')
    
    # 獲取檔案最後修改時間
    mtime = os.path.getmtime(DATA_FILE)
    last_updated = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')

    # --- 儀表板上方資訊列 ---
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        st.metric("潛力股總數", f"{len(df)} 檔")
    with col2:
        st.caption(f"🕒 資料庫更新時間: {last_updated}")
    with col3:
        # 增加強制重新整理按鈕，解決快取延遲問題
        if st.button('🔄 強制重新整理'):
            st.rerun()

    # --- 策略說明區塊 ---
    with st.expander("🔍 當前篩選策略說明 (點擊展開)"):
        st.markdown("""
        本系統自動掃描全市場，篩選出符合以下所有條件的潛力股：
        1. **長線多頭排列**：MA43 > MA87 > MA284 (代表中長期趨勢向上)
        2. **均線趨勢向上**：MA43, MA87, MA284 本身斜率為正 (今日數值 > 昨日數值)
        3. **短期回檔訊號**：股價 < MA43 且 股價 < MA5 (正在修正回測)
        4. **成交量篩選**：單日成交量 >= 1,000,000 股 (即 1,000 張以上)
        """)

    # --- 顯示互動式表格 ---
    st.dataframe(df, use_container_width=True, hide_index=True)

    # --- 產生下載按鈕 ---
    csv = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
    st.download_button(
        label="📥 下載 CSV 結果",
        data=csv,
        file_name='weekly_ma_results.csv',
        mime='text/csv',
    )
