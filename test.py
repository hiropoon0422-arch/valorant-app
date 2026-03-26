import os
import sys

# ==========================================
# 0. 文字化け（ASCIIエラー）防止の魔法
# ==========================================
os.environ["PYTHONIOENCODING"] = "utf-8"
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

import streamlit as st
from google import genai
from google.genai import types

# ==========================================
# 1. 初期設定（Secrets管理）
# ==========================================
try:
    GOOGLE_API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    GOOGLE_API_KEY = "あなたのAPIキー" # テスト用

client = genai.Client(
    api_key=GOOGLE_API_KEY,
    http_options={'api_version': 'v1beta'}
)

st.set_page_config(page_title="VALORANT Tactical Room", page_icon="🕵️‍♂️")
st.title("🎖️ VALORANT Tactical Room")

# ==========================================
# 2. UIセクション
# ==========================================
with st.sidebar:
    st.markdown("### ⚙️ オペレーション設定")
    side = st.radio("開始時のサイド", ["防衛スタート", "攻撃スタート"])
    agent = st.text_input("使用エージェント", value="ネオン")

st.markdown("### 🔍 戦術データの提供")
st.info("Tracker.ggなどの戦績テキスト（K/D、ACSなど）をコピーして貼り付けてください。")
match_data = st.text_area(
    "戦績データ",
    placeholder="ここにテキストをコピペ...",
    height=150
)

st.markdown("### 📝 フィールドレポート（任意）")
user_reflection = st.text_area(
    "現場の報告があれば書け。なければ空欄で構わん。",
    placeholder="（例：Bサイトの守りがキツかった、エントリーでデスしすぎた等）",
    height=100
)

# ==========================================
# 3. 解析実行
# ==========================================
if "report" not in st.session_state:
    st.session_state.report = ""

if st.button("ブリーフィングを開始する"):
    if not match_data:
        st.warning("解析対象のデータがなければ、俺にも何も言えん。データを貼れ。")
    else:
        with st.spinner("データのみで状況を推測中だ..."):
            try:
                reflection_context = user_reflection if user_reflection else "（報告なし：データから客観的に推測せよ）"
                
                prompt_text = f"""
                # 役割
                VALORANTのベテラン指揮官、ブリムストーン。渋く冷静なトーン（熱量5）。

                # 解析対象
                - エージェント: {agent}
                - 開始サイド: {side}
                - 提供データ: {match_data}
                - プレイヤーからの報告: {reflection_context}

                # ブリーフィングの指針
                1. 報告がない場合は、提供された数値データ（ACS, K/D, HS%, FB数など）のみから、戦場での立ち回りを逆算しろ。
                2. 勝利していても、さらに高みへ行くための「微かな綻び」を見つけ出せ。
                3. サイド（{side}）とエージェント（{agent}）の特性を考慮した、現実的なアドバイスを行え。

                # 出力の構成
                - **【戦況の総括】**
                - **【戦術的な分岐点】**
                - **【次戦への備え】**

                # 出力ルール
                - 締めは「次は自分の力で戦況を変えてみせろ。報告は以上だ。さあ、射撃場へ戻れ！」
                """

                # API呼び出し（リスト形式にして確実にテキストとして渡す）
                response = client.models.generate_content(
                    model="gemini-3-flash-preview", 
                    contents=[prompt_text],
                    config=types.GenerateContentConfig(
                        temperature=0.5, 
                    )
                )
                
                st.session_state.report = response.text

            except Exception as e:
                st.error(f"解析トラブル： {e}")

# 保存されているレポートがあれば常に表示する
if st.session_state.report:
    st.markdown("---")
    st.header("📝 偵察報告書")
    st.write(st.session_state.report)
