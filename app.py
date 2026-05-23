import streamlit as st
import requests

# 1. 画面レイアウトの設定
st.set_page_config(page_title="LIMEX Purge 戦略ダッシュボード", layout="wide")

st.title("🛡️ LIMEX Purge 戦略的マーケティング・商談ダッシュボード")
st.write("顧客の成形条件を入力し、TCO削減額の算出と、購買部門にそのまま提出できる『切り替え稟議書』を自動生成します。")

# 2. サイドバーの設定 (APIキー入力)
st.sidebar.header("🔑 AI連携設定")
st.sidebar.write("商談用の『稟議書自動生成』を使用するにはAPIキーが必要です。")
api_key = st.sidebar.text_input("Gemini API Key を入力してください", type="password")
model_choice = st.sidebar.selectbox("使用するAIモデル", ["gemini-1.5-pro", "gemini-1.5-flash"])

# 3. 2カラム構成でメイン画面を配置
col1, col2 = st.columns([1, 1.2])

with col1:
    st.header("📥 顧客の成形条件・現行コスト入力")
    
    current_purge_brand = st.selectbox(
        "現在使用しているパージ剤",
       
    )
    
    current_price = st.number_input("現行パージ剤の購入単価 (円/kg)", value=680, step=10)
    monthly_purge_qty = st.number_input("月間のパージ剤消費量 (kg)", value=100, step=10)
    down_time_per_change = st.number_input("1回あたりの色替え・材料替えダウンタイム (分)", value=30, step=5)
    monthly_changes = st.number_input("月間の段取り替え（色替え）回数 (回)", value=20, step=1)
    machine_loss_rate = st.number_input("成形機の時間あたり機会損失/人件費 (円/時間)", value=5000, step=500)
    lost_resin_qty = st.number_input("1回のパージ・立ち上げ時にロスする製品樹脂量 (kg)", value=15.0, step=1.0)
    lost_resin_price = st.number_input("製品用樹脂の原材料単価 (円/kg)", value=350, step=10)
    
    calc_trigger = st.button("📊 TCO削減シミュレーションを実行", use_container_width=True)

with col2:
    st.header("📈 シミュレーション結果 & 稟議書生成")
    
    if calc_trigger:
        # TCO（総コスト）計算の数理モデル
        annual_purge_qty = monthly_purge_qty * 12
        annual_purge_cost = annual_purge_qty * current_price
        
        annual_down_hours = (down_time_per_change / 60) * monthly_changes * 12
        annual_down_cost = annual_down_hours * machine_loss_rate
        
        annual_lost_resin = lost_resin_qty * monthly_changes * 12
        annual_lost_resin_cost = annual_lost_resin * lost_resin_price
        annual_waste_cost = annual_lost_resin * 50  # 産廃処理費を簡易的に50円/kgと設定
        
        # 現行の総所有コスト (TCO)
        current_tco = annual_purge_cost + annual_down_cost + annual_lost_resin_cost + annual_waste_cost
        
        # LIMEX Purgeの約32%コスト削減実績に基づく予測
        limex_tco = current_tco * 0.68  # 32%カット
        expected_saving = current_tco - limex_tco
        
        st.subheader("💡 試算されたコストメリット（年間）")
        metric_col1, metric_col2 = st.columns(2)
        metric_col1.metric(label="現在の年間総パージコスト (TCO)", value=f"¥{int(current_tco):,}")
        metric_col2.metric(label="LIMEX Purge 導入時の予測TCO", value=f"¥{int(limex_tco):,}", delta=f"-¥{int(expected_saving):,}")
        
        st.success(f"✨ 年間でおよそ **¥{int(expected_saving):,}** のコスト削減が期待できます（約32%の削減効果）。")
        
        # APIキーがある場合のみ稟議書を生成
        if api_key:
            st.write("---")
            st.subheader("📝 AI自動生成: 顧客購買部門向け『切り替え稟議提案書』")
            
            prompt = f"""
            あなたはTBM社の「LIMEX Purge」マーケティング責任者です。
            以下の成形現場データに基づき、顧客の購買部門および工場長が「即決でLIMEX Purgeへの切り替えを承認する」ための、極めてロジカルで説得力のある【パージ剤切り替え稟議提案書】を作成してください。

            【顧客の現状データ】
            - 現在使用中のパージ剤: {current_purge_brand} (単価: {current_price}円/kg, 月間消費: {monthly_purge_qty}kg)
            - 段取り替え回数: 月間 {monthly_changes} 回 (1回あたり {down_time_per_change} 分のダウンタイム発生)
            - 成形機時間当たりレート: {machine_loss_rate} 円/時間
            - 1回あたりのロス樹脂: {lost_resin_qty} kg (製品樹脂単価: {lost_resin_price} 円/kg)
            - 算出された現行年間TCO: {int(current_tco):,} 円

            【LIMEX Purge の提供価値】
            1. 炭酸カルシウムを50%以上配合した独自の物理掻き出し力により、パージ時間を大幅短縮。
            2. 低摩耗性（モース硬度3）のため、GF（ガラスファイバー）入りパージ剤と異なり、スクリュー・シリンダーを一切傷つけない高い安全性。
            3. 石油由来プラスチック使用量を50%以上削減し、工場のCO2/GHG排出量削減、Scope 3対応に直結する環境価値。
            4. 競合製品の価格高騰（例：セルパージの2026年4月の値上げなど）に対し、石灰石ベースのLIMEX Purgeは価格が極めて安定。
            5. 導入実績として約32%のトータルコスト（TCO）削減効果を実証済み。

            【稟議書の構成】
            1. 提案の趣旨（背景：サステナビリティ推進とコスト削減の同時達成）
            2. 現状のコスト構造の課題（時間ロス、材料ロス、および廃棄物コストの定量分析）
            3. LIMEX Purge選定の技術的・経済的根拠（安全性、物理掻き出し力、価格の安定性）
            4. 経済性シミュレーション結果（現行TCO：{int(current_tco):,}円 vs 導入後TCO：{int(limex_tco):,}円、年間削減額：{int(expected_saving):,}円）
            5. 導入プロセス（まずは「5kg無償サンプル」によるテストから開始し、現場負荷ゼロで移行するステップ）

            日本の製造業の購買・工場長に刺さる、丁寧かつロジカルで、厳格なビジネストーンでマークダウン形式で美しく出力してください。
            """
            
            with st.spinner("AIが説得力のある稟議書を生成中..."):
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_choice}:generateContent?key={api_key}"
                    headers = {"Content-Type": "application/json"}
                    data = {"contents": [{"parts": [{"text": prompt}]}]}
                    response = requests.post(url, json=data, headers=headers)
                    result_text = response.json()['candidates']['content']['parts']['text']
                    
                    st.markdown(result_text)
                except Exception as e:
                    st.error("API呼び出しに失敗しました。キーが正しいか確認してください。")
        else:
            st.warning("⚠️ サイドバーに『Gemini API Key』を入力すると、シミュレーション実行時に購買提出用の稟議提案書が自動生成されます。")
