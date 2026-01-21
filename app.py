import streamlit as st
import pandas as pd
import pickle
import requests
from datetime import datetime, timedelta
import folium
from streamlit_folium import st_folium

# --- 47都道府県マスタデータ ---
PREF_MASTER = {
    1: {"name": "北海道", "jma_id": "016000", "lat": 43.0642, "lon": 141.3469},
    2: {"name": "青森", "jma_id": "020000", "lat": 40.8244, "lon": 140.7400},
    3: {"name": "岩手", "jma_id": "030000", "lat": 39.7036, "lon": 141.1525},
    4: {"name": "宮城", "jma_id": "040000", "lat": 38.2682, "lon": 140.8694},
    5: {"name": "秋田", "jma_id": "050000", "lat": 39.7186, "lon": 140.1024},
    6: {"name": "山形", "jma_id": "060000", "lat": 38.2554, "lon": 140.3396},
    7: {"name": "福島", "jma_id": "070000", "lat": 37.7503, "lon": 140.4675},
    8: {"name": "茨城", "jma_id": "080000", "lat": 36.3418, "lon": 140.4468},
    9: {"name": "栃木", "jma_id": "090000", "lat": 36.5651, "lon": 139.8836},
    10: {"name": "群馬", "jma_id": "100000", "lat": 36.3912, "lon": 139.0608},
    11: {"name": "埼玉", "jma_id": "110000", "lat": 35.8570, "lon": 139.6489},
    12: {"name": "千葉", "jma_id": "120000", "lat": 35.6051, "lon": 140.1233},
    13: {"name": "東京", "jma_id": "130000", "lat": 35.6895, "lon": 139.6917},
    14: {"name": "神奈川", "jma_id": "140000", "lat": 35.4478, "lon": 139.6425},
    15: {"name": "新潟", "jma_id": "150000", "lat": 37.9120, "lon": 139.0489},
    16: {"name": "富山", "jma_id": "160000", "lat": 36.6953, "lon": 137.2113},
    17: {"name": "石川", "jma_id": "170000", "lat": 36.5947, "lon": 136.6256},
    18: {"name": "福井", "jma_id": "180000", "lat": 36.0652, "lon": 136.2216},
    19: {"name": "山梨", "jma_id": "190000", "lat": 35.6639, "lon": 138.5683},
    20: {"name": "長野", "jma_id": "200000", "lat": 36.6485, "lon": 138.1942},
    21: {"name": "岐阜", "jma_id": "210000", "lat": 35.3912, "lon": 136.7223},
    22: {"name": "静岡", "jma_id": "220000", "lat": 34.9769, "lon": 138.3831},
    23: {"name": "愛知", "jma_id": "230000", "lat": 35.1802, "lon": 136.9066},
    24: {"name": "三重", "jma_id": "240000", "lat": 34.7303, "lon": 136.5086},
    25: {"name": "滋賀", "jma_id": "250000", "lat": 35.0045, "lon": 135.8686},
    26: {"name": "京都", "jma_id": "260000", "lat": 35.0212, "lon": 135.7556},
    27: {"name": "大阪", "jma_id": "270000", "lat": 34.6937, "lon": 135.5023},
    28: {"name": "兵庫", "jma_id": "280000", "lat": 34.6913, "lon": 135.1830},
    29: {"name": "奈良", "jma_id": "290000", "lat": 34.6853, "lon": 135.8327},
    30: {"name": "和歌山", "jma_id": "300000", "lat": 34.2260, "lon": 135.1675},
    31: {"name": "鳥取", "jma_id": "310000", "lat": 35.5036, "lon": 134.2383},
    32: {"name": "島根", "jma_id": "320000", "lat": 35.4722, "lon": 133.0506},
    33: {"name": "岡山", "jma_id": "330000", "lat": 34.6618, "lon": 133.9344},
    34: {"name": "広島", "jma_id": "340000", "lat": 34.3963, "lon": 132.4594},
    35: {"name": "山口", "jma_id": "350000", "lat": 34.1858, "lon": 131.4706},
    36: {"name": "徳島", "jma_id": "360000", "lat": 34.0658, "lon": 134.5594},
    37: {"name": "香川", "jma_id": "370000", "lat": 34.3401, "lon": 134.0434},
    38: {"name": "愛媛", "jma_id": "380000", "lat": 33.8416, "lon": 132.7657},
    39: {"name": "高知", "jma_id": "390000", "lat": 33.5597, "lon": 133.5311},
    40: {"name": "福岡", "jma_id": "400000", "lat": 33.6064, "lon": 130.4181},
    41: {"name": "佐賀", "jma_id": "410000", "lat": 33.2635, "lon": 130.3008},
    42: {"name": "長崎", "jma_id": "420000", "lat": 32.7500, "lon": 129.8773},
    43: {"name": "熊本", "jma_id": "430000", "lat": 32.7898, "lon": 130.7417},
    44: {"name": "大分", "jma_id": "440000", "lat": 33.2381, "lon": 131.6125},
    45: {"name": "宮崎", "jma_id": "450000", "lat": 31.9111, "lon": 131.4239},
    46: {"name": "鹿児島", "jma_id": "460100", "lat": 31.5602, "lon": 130.5580},
    47: {"name": "沖縄", "jma_id": "471000", "lat": 26.2124, "lon": 127.6809},
}

st.set_page_config(page_title="熱中症予測AIアラート", page_icon="🌡️", layout="centered")

st.title("🌡️ 1週間後の熱中症搬送数予測")
st.write("AIが最新の気象予報に基づき、1週間後の熱中症リスクを判定します。")

with st.sidebar:
    st.header("⚙️ 設定")
    api_key = st.text_input("OpenWeatherMap API Key", type="password")
    st.info("APIキーを入力して予測を開始してください。")

@st.cache_resource
def load_model():
    with open('heatstroke_prediction_model.pkl', 'rb') as f:
        return pickle.load(f)

def get_predictions(owm_key, model):
    target_date = datetime.now() + timedelta(days=7)
    results = []
    progress_bar = st.progress(0)
    total = len(PREF_MASTER)
    
    for i, (code, info) in enumerate(PREF_MASTER.items()):
        try:
            # 1. 湿度取得 (OWM)
            owm_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={info['lat']}&lon={info['lon']}&appid={owm_key}&units=metric"
            owm_res = requests.get(owm_url).json()
            humidity = owm_res['list'][-1]['main']['humidity']

            # 2. 気温取得 (気象庁)
            jma_url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{info['jma_id']}.json"
            jma_res = requests.get(jma_url).json()
            temps = jma_res[1]['timeSeries'][1]['areas'][0]
            max_t = float(temps['tempsMax'][-1]) if temps['tempsMax'][-1] != "" else 25.0
            min_t = float(temps['tempsMin'][-1]) if temps['tempsMin'][-1] != "" else 18.0
            avg_t = (max_t + min_t) / 2

            # 3. DI計算
            di = 0.81 * avg_t + 0.01 * humidity * (0.99 * avg_t - 14.3) + 46.3

            # 4. 予測
            input_df = pd.DataFrame([{
                '平均気温(℃)': avg_t, '平均湿度(％)': humidity, '最高気温(℃)': max_t, 
                '最低気温(℃)': min_t, 'DI': di, 'month': target_date.month, 
                'dayofweek': target_date.weekday(), 'pref_code': code
            }])
            
            pred = model.predict(input_df)[0]
            if max_t < 20: pred = 0 # 冬場対策
            
            results.append({
                "都道府県": info['name'], "予測人数": round(pred, 1),
                "最高気温": max_t, "湿度": humidity, "不快指数": round(di, 1)
            })
        except:
            continue
        progress_bar.progress((i + 1) / total)
    
    return pd.DataFrame(results)

# メイン処理
if api_key:
    try:
        model = load_model()
        if st.button("🚀 予測を開始する"):
            df_res = get_predictions(api_key, model)
            
            if not df_res.empty:
                st.success(f"✅ {(datetime.now() + timedelta(days=7)).strftime('%Y/%m/%d')} の予測が完了しました。")
                
                # --- アップデート：重点警戒アラート ---
                top_pref = df_res.sort_values("予測人数", ascending=False).iloc[0]
                st.subheader("📢 最重点警戒エリア")
                if top_pref['予測人数'] >= 50:
                    st.error(f"【厳重警戒】{top_pref['都道府県']}で非常に高いリスクが予測されています。")
                elif top_pref['予測人数'] >= 20:
                    st.warning(f"【注意】{top_pref['都道府県']}で搬送者が増加する見込みです。")
                else:
                    st.info(f"現在、大規模な搬送リスクが予測されている地域はありません。")

                # --- アップデート：メトリックスカード ---
                st.write("---")
                st.subheader("🏆 予測ワースト3")
                top3 = df_res.sort_values("予測人数", ascending=False).head(3)
                cols = st.columns(3)
                for i, row in enumerate(top3.itertuples()):
                    delta_text = "要警戒" if row.予測人数 > 20 else "平常"
                    cols[i].metric(
                        label=f"Rank {i+1}: {row.都道府県}", 
                        value=f"{row.予測人数} 人",
                        delta=delta_text,
                        delta_color="inverse" if row.予測人数 > 20 else "normal"
                    )
                st.write("---")
                
                st.subheader("🗺️ 全国リスクマップ")
                
                # 日本の中心（付近）を基準に地図を作成
                m = folium.Map(location=[36.0, 137.1], zoom_start=5)
                
                for _, row in df_res.iterrows():
                    # 都道府県名から座標を取得（PREF_MASTERを逆引き、またはdf_resに座標を含めるよう修正が必要）
                    # 今回は簡略化のため、PREF_MASTERから直接取得する流れで解説
                    pref_info = next((v for k, v in PREF_MASTER.items() if v['name'] == row['都道府県']), None)
                    
                    if pref_info:
                        # 予測人数に応じた円の半径（最低5、人数に応じて大きく）
                        radius = 5 + (row['予測人数'] * 2) 
                        
                        # 色の設定
                        color = 'red' if row['予測人数'] >= 20 else 'orange' if row['予測人数'] >= 5 else 'green'
                        
                        folium.CircleMarker(
                            location=[pref_info['lat'], pref_info['lon']],
                            radius=radius,
                            popup=f"{row['都道府県']}: {row['予測人数']}人",
                            color=color,
                            fill=True,
                            fill_color=color,
                            fill_opacity=0.6
                        ).add_to(m)
                
                # 地図を表示
                st_folium(m, width=700, height=500)
                # --- アップデート：装飾付きデータテーブル ---
                st.write("---")
                st.subheader("📊 全国予測一覧")
                
                def color_risk(val):
                    if isinstance(val, (float, int)):
                        if val >= 50: return 'background-color: #ffcccc'
                        if val >= 20: return 'background-color: #fff3cd'
                    return ''

                st.dataframe(
                    df_res.sort_values("予測人数", ascending=False).style.applymap(color_risk, subset=['予測人数']),
                    use_container_width=True
                )
            else:
                st.warning("データが取得できませんでした。")
    except FileNotFoundError:
        st.error("モデルファイルが見つかりません。")
else:
    st.warning("左側のサイドバーにOpenWeatherMapのAPIキーを入力してください。")
