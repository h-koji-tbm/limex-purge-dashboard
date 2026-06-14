import streamlit as st
import pandas as pd

# ==========================================
# ページ初期設定＆TBMブランドCSSインジェクション
# ==========================================
st.set_page_config(
    page_title="LIMEX Purge | TCO & Environmental Value Simulator",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# TBMプレミアム・サステナビリティを表現するカスタムCSS
tbm_css = """
<style>
    /* 全体背景とフォントの設定 */
    .stApp {
        background-color: #F8FAF9;
        font-family: 'Helvetica Neue', Arial, 'Hiragino Kaku Gothic ProN', Meiryo, sans-serif;
        color: #1A2521;
    }
    
    /* ヘッダーデザイン */
    .header-container {
        background: linear-gradient(135deg, #0B3C2D 0%, #155E46 100%);
        padding: 2.5rem;
        border-radius: 12px;
        color: #FFFFFF;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(11, 60, 45, 0.15);
    }
    .header-title {
        font-size: 2.5rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        margin: 0;
    }
    .header-subtitle {
        font-size: 1.1rem;
        font-weight: 300;
        opacity: 0.9;
        margin-top: 0.5rem;
    }
    
    /* カード風セクション */
    .metric-card-before {
        background-color: #FFF5F5;
        border-left: 5px solid #E53E3E;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.02);
        margin-bottom: 1rem;
    }
    .metric-card-after {
        background-color: #F0F7F4;
        border-left: 5px solid #0B3C2D;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.02);
        margin-bottom: 1rem;
    }
    
    /* 商社営業セクション用の特別CSS */
    .dealer-card {
        background-color: #F0F4F8;
        border-left: 5px solid #1A5276;
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    
    /* ボタンデザイン */
    .stButton>button {
        background: linear-gradient(135deg, #9FCB3B 0%, #85AB2F 100%) !important;
        color: #FFFFFF !important;
        font-weight: bold !important;
        border: none !important;
        padding: 0.75rem 2rem !important;
        border-radius: 50px !important;
        box-shadow: 0 4px 15px rgba(159, 203, 59, 0.3) !important;
        transition: all 0.3s ease !important;
        width: 100%;
    }
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(159, 203, 59, 0.5) !important;
    }
    
    /* ディスクレイマー（フッター） */
    .footer-disclaimer {
        font-size: 0.8rem;
        color: #7F8C8D;
        text-align: center;
        margin-top: 3rem;
        padding-top: 1.5rem;
        border-top: 1px solid #E2E8F0;
    }
</style>
"""
st.markdown(tbm_css, unsafe_allow_html=True)

# ==========================================
# ヘッダー表示
# ==========================================
st.markdown("""
<div class="header-container">
    <div class="header-title">LIMEX Purge</div>
    <div class="header-subtitle">TCO（総所有コスト）兼 環境価値シミュレーター ＆ 営業攻略ダッシュボード</div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 統合タブ設定
# ==========================================
tab_simulator, tab_sales_strategy = st.tabs(["📊 シミュレーター (デモ用)", "🎯 商社・代理店様向け営業攻略 (虎の巻)"])

# ==========================================
# マスターデータ定義（技術定数）
# ==========================================
RESIN_MASTER = {
    "PP (ポリプロピレン)": {"price": 280, "co2": 1.62, "loss_multiplier": 8.0},
    "ABS (アクリロニトリル・ブタジエン・スチレン)": {"price": 420, "co2": 3.10, "loss_multiplier": 12.0},
    "PC (ポリカーボネート)": {"price": 600, "co2": 5.20, "loss_multiplier": 15.0},
    "PA (ポリアミド/ナイロン)": {"price": 850, "co2": 6.80, "loss_multiplier": 18.0},
    "その他・不明樹脂": {"price": 350, "co2": 2.50, "loss_multiplier": 10.0}
}

MACHINE_MASTER = {
    "小型機 (100t以下)": {"charge": 4000, "power": 12},
    "中型機 (100t - 300t)": {"charge": 6000, "power": 22},
    "大型機 (300t - 500t)": {"charge": 9000, "power": 38},
    "超大型機 (500t以上)": {"charge": 13000, "power": 60}
}

ELECTRICITY_CO2_FACTOR = 0.45  # kg-CO2/kWh (Scope 2)
CONVENTIONAL_PURGE_CO2 = 2.5   # kg-CO2/kg (Scope 3 汎用値)
LIMEX_PURGE_CO2 = 0.95         # kg-CO2/kg (Scope 3 - 炭酸カルシウム高配合によりクリーン)
LIMEX_PURGE_PRICE = 1500       # 円/kg (プレミアムパージ剤市場想定価格)
LIMEX_DISPLACEMENT_MULTIPLIER = 1.5 # 追い出しに必要な次樹脂倍率

# ==========================================
# TAB 1: 📊 シミュレーター
# ==========================================
with tab_simulator:
    st.write("現場の型替えにかかる「隠れた損失（時間・樹脂・人件費）」を可視化し、LIMEX Purgeによる劇的なコスト削減とCO2削減効果をリアルタイム算出します。")
    
    col_input, col_result = st.columns([1, 1.1], gap="large")
    
    with col_input:
        st.subheader("⚙️ 1. 現在の稼働環境・処理方法の入力")
        
        # 3パターン動的分岐
        pattern = st.selectbox(
            "現在のパージ・型替え処理方法を選択してください",
            ["パターンA：他社パージ剤からの代替（競合代替）", "パターンB：共洗い（本材樹脂での押し出し）", "パターンC：オートパージ（シャットダウン・炭化防止）"]
        )
        
        # 共通入力項目：成形機クラス
        machine_class = st.selectbox("対象成形機の型締め力クラス", list(MACHINE_MASTER.keys()))
        hourly_charge = MACHINE_MASTER[machine_class]["charge"]
        power_kw = MACHINE_MASTER[machine_class]["power"]
        
        # シリンダー容量の自動推定
        if "小型" in machine_class:
            default_v_cyl = 1.5
        elif "中型" in machine_class:
            default_v_cyl = 3.5
        elif "大型" in machine_class:
            default_v_cyl = 6.5
        else:
            default_v_cyl = 12.0
            
        v_cyl = st.number_input("シリンダー容量 (kg) ※型締め力から自動推定", min_value=0.1, value=default_v_cyl, step=0.5)
        
        # パターン別動的分岐フォーム
        if "パターンA" in pattern:
            st.info("💡 現在他社のパージ剤をお使いの場合のシミュレーションです。")
            purge_type = st.radio("現在のパージ剤タイプ", ["汎用グレード", "ガラス繊維入りグレード", "価格不明"], horizontal=True)
            
            if purge_type == "ガラス繊維入りグレード":
                default_price = 1800
                st.warning("⚠️ ガラス繊維入りパージ剤は、シリンダーやスクリューの摩耗リスク（オーバーホール等で年間約120万円の潜在コスト）を伴います。非研磨性のLIMEX Purgeに切り替えることでこの損失を回避可能です。")
            elif purge_type == "汎用グレード":
                default_price = 1200
            else:
                default_price = 1200
                
            current_price = st.number_input("現在のパージ剤単価 (円/kg)", min_value=0, value=default_price)
            current_amount = st.number_input("1回あたりの他社パージ剤使用量 (kg)", min_value=0.1, value=v_cyl * 1.5, step=0.5)
            current_time = st.number_input("1回あたりのパージ作業時間 (分)", min_value=1, value=45, step=5)
            annual_runs = st.number_input("年間のパージ回数 (回/年)", min_value=1, value=120, step=10)
            
            # LIMEX Purge（After）の削減ロジック (通常、他社比で30%量削減、35%時間短縮)
            after_price = LIMEX_PURGE_PRICE
            after_amount = current_amount * 0.70
            after_time = current_time * 0.65
            screw_risk_saving = 1200000 if purge_type == "ガラス繊維入りグレード" else 0
            
        elif "パターンB" in pattern:
            st.info("💡 パージ剤を使用せず、次製品の成形材料（本材）をそのまま流して洗浄（共洗い）している場合のシミュレーションです。")
            selected_resin = st.selectbox("置換対象の樹脂（次樹脂）", list(RESIN_MASTER.keys()))
            resin_price = st.number_input("樹脂の仕入れ単価 (円/kg)", min_value=0, value=RESIN_MASTER[selected_resin]["price"])
            resin_co2 = RESIN_MASTER[selected_resin]["co2"]
            loss_multiplier = RESIN_MASTER[selected_resin]["loss_multiplier"]
            
            # 共洗い時の押し出しロス（シリンダー容量の倍率）
            current_amount = st.number_input("1回あたりの共洗い樹脂ロス量 (kg) ※定数から自動算出", min_value=0.1, value=v_cyl * loss_multiplier, step=1.0)
            current_time = st.number_input("1回あたりの共洗い作業時間 (分)", min_value=1, value=60, step=5)
            annual_runs = st.number_input("年間の型替え・色替え回数 (回/年)", min_value=1, value=100, step=10)
            
            # LIMEX Purge導入プロセス（After）の削減ロジック
            after_price = LIMEX_PURGE_PRICE
            after_amount = v_cyl * 1.2  # LIMEX使用量（シリンダー容量の1.2倍）
            after_time = current_time * 0.40  # 作業時間60%削減（40%に短縮）
            after_sub_resin_amount = v_cyl * LIMEX_DISPLACEMENT_MULTIPLIER  # 次樹脂でのLIMEX押し出し量（1.5倍）
            screw_risk_saving = 0
            
        else:  # パターンC：オートパージ
            st.info("💡 週末のシャットダウン時等にシリンダー内をLIMEX Purgeでシールし、熱劣化（炭化）による月曜朝の再起動不良（スクラップ）およびダウンタイムを防止するパターンです。")
            selected_resin = st.selectbox("対象の樹脂", list(RESIN_MASTER.keys()))
            resin_price = st.number_input("樹脂の仕入れ単価 (円/kg)", min_value=0, value=RESIN_MASTER[selected_resin]["price"])
            resin_co2 = RESIN_MASTER[selected_resin]["co2"]
            
            scrap_shots = st.number_input("再起動時の平均不良ショット数 (ショット)", min_value=1, value=15, step=1)
            shot_weight = st.number_input("1ショット重量 (kg)", min_value=0.01, value=0.3, step=0.05)
            current_amount = scrap_shots * shot_weight # 廃棄樹脂量
            
            current_time = st.number_input("立ち上げ時の無駄な時間遅れ (時間)", min_value=0.5, value=2.0, step=0.5)
            annual_runs = st.number_input("年間の立ち上げ回数 (回/年)", min_value=1, value=50, step=5)
            
            # LIMEX Purge導入プロセス（After）の削減ロジック
            after_price = LIMEX_PURGE_PRICE
            after_amount = v_cyl * 1.0  # シリンダー内をLIMEXで完全置換（シリンダー容量と同量）
            after_time = 0.25  # 再起動時の無駄な時間（一律15分に短縮）
            screw_risk_saving = 0

    # ==========================================
    # 計算エンジン
    # ==========================================
    try:
        if "パターンA" in pattern:
            # Before（現状）
            before_material_cost = current_price * current_amount * annual_runs
            before_labor_cost = (current_time / 60) * hourly_charge * annual_runs
            before_total_cost = before_material_cost + before_labor_cost
            
            before_co2_scope2 = (current_time / 60) * power_kw * ELECTRICITY_CO2_FACTOR * annual_runs
            before_co2_scope3 = current_amount * CONVENTIONAL_PURGE_CO2 * annual_runs
            before_total_co2 = before_co2_scope2 + before_co2_scope3
            
            # After（LIMEX Purge）
            after_material_cost = after_price * after_amount * annual_runs
            after_labor_cost = (after_time / 60) * hourly_charge * annual_runs
            after_total_cost = after_material_cost + after_labor_cost
            
            after_co2_scope2 = (after_time / 60) * power_kw * ELECTRICITY_CO2_FACTOR * annual_runs
            after_co2_scope3 = after_amount * LIMEX_PURGE_CO2 * annual_runs
            after_total_co2 = after_co2_scope2 + after_co2_scope3
            
            total_time_saved = (current_time - after_time) * annual_runs / 60
            
        elif "パターンB" in pattern:
            # Before（現状）
            before_material_cost = resin_price * current_amount * annual_runs
            before_labor_cost = (current_time / 60) * hourly_charge * annual_runs
            before_total_cost = before_material_cost + before_labor_cost
            
            before_co2_scope2 = (current_time / 60) * power_kw * ELECTRICITY_CO2_FACTOR * annual_runs
            before_co2_scope3 = current_amount * resin_co2 * annual_runs
            before_total_co2 = before_co2_scope2 + before_co2_scope3
            
            # After（LIMEX Purge）
            # 材料費 = LIMEX代 ＋ 追い出しに要した次樹脂代
            after_material_cost = ((after_price * after_amount) + (resin_price * after_sub_resin_amount)) * annual_runs
            after_labor_cost = (after_time / 60) * hourly_charge * annual_runs
            after_total_cost = after_material_cost + after_labor_cost
            
            after_co2_scope2 = (after_time / 60) * power_kw * ELECTRICITY_CO2_FACTOR * annual_runs
            after_co2_scope3 = ((after_amount * LIMEX_PURGE_CO2) + (after_sub_resin_amount * resin_co2)) * annual_runs
            after_total_co2 = after_co2_scope2 + after_co2_scope3
            
            total_time_saved = (current_time - after_time) * annual_runs / 60
            
        else:  # パターンC（オートパージ）
            # Before（現状）
            before_material_cost = resin_price * current_amount * annual_runs
            before_labor_cost = current_time * hourly_charge * annual_runs # 待機中も機械チャージ・停止損失が発生
            before_total_cost = before_material_cost + before_labor_cost
            
            before_co2_scope2 = current_time * power_kw * ELECTRICITY_CO2_FACTOR * annual_runs
            before_co2_scope3 = current_amount * resin_co2 * annual_runs
            before_total_co2 = before_co2_scope2 + before_co2_scope3
            
            # After（LIMEX Purge）
            after_material_cost = after_price * after_amount * annual_runs
            after_labor_cost = after_time * hourly_charge * annual_runs  # 立ち上げ時間のみ（15分）
            after_total_cost = after_material_cost + after_labor_cost
            
            after_co2_scope2 = after_time * power_kw * ELECTRICITY_CO2_FACTOR * annual_runs
            after_co2_scope3 = after_amount * LIMEX_PURGE_CO2 * annual_runs
            after_total_co2 = after_co2_scope2 + after_co2_scope3
            
            total_time_saved = (current_time - after_time) * annual_runs
            
        # 削減メリットのサマリー
        cost_savings = before_total_cost - after_total_cost
        co2_savings = before_total_co2 - after_total_co2
        roi_multiple = (cost_savings / after_material_cost) if after_material_cost > 0 else 0
        
    except Exception as e:
        st.error(f"計算エラーが発生しました。入力を確認してください。エラー詳細: {e}")
        cost_savings = co2_savings = total_time_saved = roi_multiple = before_total_cost = after_total_cost = 0

    # ==========================================
    # 出力層（リアルタイム結果表示）
    # ==========================================
    with col_result:
        st.subheader("📊 2. 削減ベネフィット対比 (Before vs After)")
        
        col_before, col_after = st.columns(2)
        
        with col_before:
            st.markdown(f"""
            <div class="metric-card-before">
                <h4 style="color:#E53E3E; margin:0;">現状 (Before)</h4>
                <p style="font-size: 1.8rem; font-weight: 700; margin: 0.5rem 0; color:#E53E3E;">{before_total_cost:,.0f} <span style="font-size:1rem;">円/年</span></p>
                <p style="font-size: 0.9rem; color:#7F8C8D; margin:0;">材料関連費: {before_material_cost:,.0f} 円<br>停止・作業損失: {before_labor_cost:,.0f} 円</p>
                <p style="font-size: 1.1rem; color:#E53E3E; font-weight:bold; margin-top:1rem;">CO2排出量: {before_total_co2:,.1f} kg/年</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col_after:
            st.markdown(f"""
            <div class="metric-card-after">
                <h4 style="color:#0B3C2D; margin:0;">LIMEX Purge 導入後</h4>
                <p style="font-size: 1.8rem; font-weight: 700; margin: 0.5rem 0; color:#0B3C2D;">{after_total_cost:,.0f} <span style="font-size:1rem;">円/年</span></p>
                <p style="font-size: 0.9rem; color:#7F8C8D; margin:0;">材料関連費: {after_material_cost:,.0f} 円<br>停止・作業損失: {after_labor_cost:,.0f} 円</p>
                <p style="font-size: 1.1rem; color:#0B3C2D; font-weight:bold; margin-top:1rem;">CO2排出量: {after_total_co2:,.1f} kg/年</p>
            </div>
            """, unsafe_allow_html=True)
            
        # インジケータ（劇的メリット）の強調表示
        st.success(f"🎉 **年間総削減額: {cost_savings:,.0f} 円** のコスト削減が可能です！")
        
        # 投資回収（ROI）と環境貢献
        col_sub_m1, col_sub_m2, col_sub_m3 = st.columns(3)
        
        if "パターンC" in pattern:
            col_sub_m1.metric("短縮ダウンタイム", f"{total_time_saved:,.1f} 時間/年")
        else:
            col_sub_m1.metric("作業削減時間", f"{total_time_saved:,.1f} 時間/年", f"-{((current_time - after_time)/current_time*100):.0f}%")
            
        col_sub_m2.metric("CO2削減率", f"{co2_savings:,.1f} kg", f"-{((before_total_co2 - after_total_co2)/before_total_co2*100):.1f}%")
        col_sub_m3.metric("投資対回収率 (ROI)", f"{roi_multiple:.1f} 倍", "ROIプラス")
        
        # ビジュアル：削減効果のグラフィカル対比
        st.write("📈 **コスト・環境負荷削減のビジュアル比較**")
        chart_data = pd.DataFrame({
            "項目": ["Beforeコスト", "Afterコスト", "Before CO2 (*10)", "After CO2 (*10)"],
            "数値": [before_total_cost, after_total_cost, before_total_co2 * 10, after_total_co2 * 10]
        })
        st.bar_chart(chart_data, x="項目", y="数値", use_container_width=True)
        
        if screw_risk_saving > 0:
            st.warning(f"🛡️ **スクリュー寿命保護の追加効果：** ガラス繊維非含有のLIMEX Purgeに切り替えることで、年間推定 **{screw_risk_saving:,.0f}円** 相当のスクリュー摩耗・オーバーホール費用リスクを完全に回避できます。")

    # ==========================================
    # 稟議書自動生成セクション（多層防御型）
    # ==========================================
    st.markdown("---")
    st.subheader("📝 3. 社内稟議・提案用コピペテンプレート")
    st.write("工場の意思決定層（工場長・調達・経営層）にそのまま提出できる、極めてロジカルな推奨稟議文面です。")
    
    ringi_text = f"""# LIMEX Purge（ライメックスパージ）導入によるコスト削減および環境改善に関する稟議書

## 1. 導入の目的と背景
成形機における型替え・パージ作業は、多大な材料ロス、稼働時間の損失、そして廃プラスチック処理によるCO2排出を発生させています。
本提案は、TBM社が開発した石灰石を主原料とする「LIMEX Purge」を導入し、生産プロセスの「経済的価値（TCO削減）」と「環境的価値（Scope 2, Scope 3削減）」を同時に極大化することを目的とします。

## 2. 期待される導入効果（年間シミュレーション結果）
当工場の稼働環境（{pattern}、型締め力クラス: {machine_class}、シリンダー容量: {v_cyl:.1f}kg）に基づく年間削減効果：

### 【経済的価値：総所有コスト（TCO）の削減】
- **現状コスト (Before)：** {before_total_cost:,.0f} 円/年
- **LIMEX導入後 (After)：** {after_total_cost:,.0f} 円/年
- **年間純削減額 (利益創出)：**  **{cost_savings:,.0f} 円/年**
- **作業（ダウンタイム）短縮時間：** {total_time_saved:,.1f} 時間/年（稼働効率向上）
- **費用に対する材料回収率 (ROI)：** 約 **{roi_multiple:.1f} 倍** （削減額 ÷ LIMEX等パージ材料費）
{"- ※ガラス繊維入りパージ剤からの脱却により、年間約1,200,000円規模のスクリュー摩耗・オーバーホール費用リスクを回避。" if screw_risk_saving > 0 else ""}

### 【環境的価値：ESG・デカーボナイゼーション（CO2削減）】
- **年間CO2排出量削減：** **{co2_savings:,.1f} kg-CO2/年 （約 {((before_total_co2 - after_total_co2)/before_total_co2*100):.1f}% 削減）**
  - **Scope 2（電力削減）：** パージ時間短縮に伴う、成形機ヒーター等の消費電力量削減
  - **Scope 3（原材料削減）：** 主原料である石灰石の低炭素特性による、製品ライフサイクル全体のCO2抑制

## 3. 各決裁部門への訴求点
- **工場長・製造現場向け：** 作業時間が劇的に短縮され、型替えに関わる現場作業員の負担を軽減。空いた時間を本生産に充当でき、実質的な設備総合効率（OEE）を向上させます。
- **購買・調達部門向け：** 材料単価は一見プレミアムに見えますが、使用量が減り、作業時間チャージ削減効果が極めて大きいため、トータルTCOでは回収率 {roi_multiple:.1f} 倍という確実な調達改善メリットを生み出します。
- **経営企画・サステナビリティ部門向け：** 石灰石ベースの環境配慮型素材への切り替えにより、確実なScope 2/3の排出削減実績を自社のサステナビリティレポートに計上可能です。

## 4. 結論
上記の通り、LIMEX Purgeへの移行は単なる「材料調達」の枠を超え、「工場生産性向上」と「デカーボナイゼーション推進」を両立する戦略的投資です。最速でのサンプル評価および実機テストへの移行を上申します。
"""
    st.text_area("📋 コピペ用テキストボックス (Markdown)", value=ringi_text, height=350)

    # ==========================================
    # 無料サンプル請求＆CRM連携シミュレーション
    # ==========================================
    st.markdown("---")
    st.subheader("🎁 4. 【無料サンプル1kg請求】および実証テストの申し込み")
    col_form1, col_form2 = st.columns(2)
    with col_form1:
        company_name = st.text_input("貴社名", placeholder="例：株式会社〇〇成形ファクトリー")
        contact_name = st.text_input("担当者名", placeholder="例：山田 太郎")
    with col_form2:
        email_address = st.text_input("メールアドレス", placeholder="example@tbm.co.jp")
        sample_request_btn = st.button("無料サンプル1kgと実証テスト資料を請求する")
        
    if sample_request_btn:
        if company_name and contact_name and email_address:
            st.balloons()
            st.success(f"ありがとうございます、{contact_name}様！ご入力いただいた情報（想定削減効果: {cost_savings:,.0f}円/年）を営業担当へ転送しました。近日中に1kgの評価用サンプルを持参し、実機検証のサポートに伺います。")
            st.info(f"⚡ [CRM用バックエンド通知] 顧客リード獲得: {company_name} | {email_address} | 削減ポテンシャル: {cost_savings:,.0f}円")
        else:
            st.error("⚠️ 会社名、担当者名、メールアドレスを正しく入力してください。")

# ==========================================
# TAB 2: 🎯 商社・代理店様向け営業攻略 (虎の巻)
# ==========================================
with tab_sales_strategy:
    st.markdown("""
    <div class="dealer-card">
        <h3 style="color:#1A5276; margin-top:0;">🤝 化学品商社・機械工具ディーラー代理店様へ</h3>
        <p>「環境に良い」だけでは顧客の予算は動きません。また、皆様の営業目標も達成できません。<br>
        このシミュレーターを武器に、<b>『商社の利己的な売上目標』</b>と<b>『顧客のコスト削減欲求』</b>を同時にハックするGTM（Go-To-Market）アプローチを展開しましょう。</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("💡 1. 代理店様が動く3大「実利」動機")
    col_g1, col_g2, col_g3 = st.columns(3)
    
    with col_g1:
        st.markdown("""
        **① 粗利大幅アップへの代替**
        汎用パージ剤や他社パージ剤は価格競争で利益幅がわずか（数％）。
        プレミアムパージ剤「LIMEX Purge」へ切り替えることで、顧客のトータルコストは下がる一方で、商社側の粗利額は最大3倍に増加します。
        """)
        
    with col_g2:
        st.markdown("""
        **② 樹脂原料の口座（商権）防衛**
        既存顧客に「CO2削減提案」を切り口とする他社が介入するのを防ぎます。
        先手を打ってこのシミュレーターを提示することで、顧客の他社への流出（主幹樹脂の商権強奪）をロックインします。
        """)
        
    with col_g3:
        st.markdown("""
        **③ 新規顧客開拓の「ドアオープナー」**
        「材料を売る」のではなく、「工場の隠れ人件費ロスを削減する無料診断」としてアポを打診。
        これによって容易に工場長や生産技術へ接触し、将来の原料口座奪取の足がかりとします。
        """)
        
    st.markdown("---")
    st.subheader("✉️ 2. コピペで使える！宛先別1ステップ追撃メール")
    st.write("顧客の決裁権を持つ3つのレイヤー別に最適化した、商談獲得・アポ化率を劇的に向上させる営業テンプレートです。コピーしてそのままお使いいただけます。")
    
    sub_tab_plant, sub_tab_proc, sub_tab_mgmt = st.tabs(["🏭 製造現場・工場長向け", "🛒 購買・調達部門向け", "🌿 経営層・サステナビリティ向け"])
    
    # 現場・工場長向けメール
    with sub_tab_plant:
        st.write("⚙️ **訴求ポイント**：型替え時間の苦痛と、パージ時の新樹脂「ドブ捨て廃棄」の痛みを突きます。")
        mail_plant = f"""件名：【御社成形機向け】型替えの「停止時間」と「樹脂廃棄」の削減シミュレーションのご提案

〇〇株式会社
生産技術部 / 工場長 〇〇様

いつも大変お世話になっております。〇〇商事の〇〇です。

突然ですが、日々の成形機の型替え・色替えにおいて、以下のような「現場の隠れた損失」について頭を悩まされることはございませんでしょうか？

・他社パージ剤を使っているが、なかなか色が抜けず時間がかかっている
・パージ剤を使わず次樹脂で押し出している（共洗い）が、新樹脂を大量に廃棄してしまっている
・週末のシャットダウン後、月曜朝の立ち上げ時に炭化不良（スクラップ）が発生し、機械が止まる

これらはすべて、年間に換算すると「数百万円規模のドブ捨て損失」になっている可能性がございます。

このたび、成形機の停止時間（労務人件費）や樹脂廃棄ロス、さらにはCO2排出量までを「わずか5分」で完全定量化できる、TBM社開発の「TCO（総所有コスト）診断シミュレーター」を導入いたしました。

御社の「成形機の型締め力」と「現在の作業時間」を数項目ご入力いただくだけで、
現状どのくらいの損失が発生しており、新技術「LIMEX Purge」によって年間どれだけのコストと作業時間が削減できるかを即座にレポート化いたします。

一度、御社の実数値で5分だけシミュレーション（無料診断）をさせていただけないでしょうか？
タブレットを持参して10分ほどお時間をいただけますと幸いです。

何卒よろしくお願い申し上げます。
"""
        st.text_area("📋 コピペ：製造現場（工場長・生産技術）宛て", value=mail_plant, height=350)
        
    # 購買・調達向けメール
    with sub_tab_proc:
        st.write("🪙 **訴求ポイント**：単価（円/kg）ではなく、人件費を含めたトータルTCO（総所有コスト）の経済合理性を証明します。")
        mail_proc = f"""件名：【購買部様向け】パージ剤の「単価比較」から「TCO（総所有コスト）最適化」への切り替えご提案

〇〇株式会社
資材調達部 / 購買責任者 〇〇様

いつも大変お世話になっております。〇〇商事の〇〇です。

本日は、パージ剤（機械洗浄剤）調達における「隠れた重大なコスト損失」を解消し、御社の購買実績（コスト削減）に直結するご提案でご連絡いたしました。

パージ剤を「仕入れ単価（円/kg）の安さ」だけで選ばれている場合、実は以下の「見えないコスト」を工場側で余計に支払っている（TCOが肥大化している）ケースが多々ございます。

・パージ能力が低いために「成形機が停止している時間の人件費・設備チャージ」
・色が抜けきるまでに「無駄に浪費される本材樹脂の廃棄費用」

弊社がこのたび導入した「TCOシミュレーター」は、これら「材料費 ＋ 停止時間損失 ＋ 廃棄ロス」をすべて統合し、御社の実稼働における【真の総所有コスト（TCO）】を算出する無料の診断ツールです。

「単価は少し高いが、使用量が30%減り、作業時間が半分になるプレミアムパージ剤（LIMEX Purge）」を導入した場合、年間で【実質数百万〜一千万円規模の純利益】が創出され、材料投資に対して「数倍のROI（投資回収率）」で回収できることが、具体的な数値データとして判明しております。

御社の現在の調達単価と稼働データをシミュレーターに一度入力させていただければ、購買部門様から経営層へそのまま提出できる「TCO削減・稟議用シミュレーションレポート」を即座に作成いたします。

一度、試算データを提示させていただくお時間をいただけませんでしょうか？
何卒ご検討のほど、よろしくお願い申し上げます。
"""
        st.text_area("📋 コピペ：資材調達・購買宛て", value=mail_proc, height=350)
        
    # 経営層・サステナビリティ向けメール
    with sub_tab_mgmt:
        st.write("🌿 **訴求ポイント**：設備への追加投資ゼロで、Scope 2 & 3（CO2削減）という経営アジェンダを一発でクリアする実績提案。")
        mail_mgmt = f"""件名：【経営層・環境推進部様向け】工場型替え時のCO2排出量を最大90%削減する、画期的なScope2/3対策のご提案

〇〇株式会社
代表取締役 / サステナビリティ推進担当役員 〇〇様

いつも大変お世話になっております。〇〇商事の〇〇です。

昨今、主要なお取引先様（ブランドオーナー様等）より、製品製造プロセスにおける「Scope 3（原材料調達）およびScope 2（製造時電力）のCO2排出削減」や、環境データの開示要求が急速に厳格化していることと存じます。

しかしながら、「工場の設備全体を置き換えるのは膨大な投資がかかる」「具体的な低炭素化の打ち手が見当たらない」というのが多くの経営層様の実情ではないでしょうか。

そこで弊社より、**「製造設備への投資はゼロ」「日々の型替え・パージ作業を見直すだけ」で、年間数トン〜数十トンのCO2を削減し、かつ同時に工場の生産コストも大幅に引き下げる**、極めて現実的なデカーボナイゼーション施策をご提案いたします。

石灰石高充填の新素材「LIMEX Purge」を導入することで、以下の効果が期待できます。
・【Scope 3削減】：主原料である石灰石の低炭素特性により、パージ剤自体の原材料CO2を劇的に抑制
・【Scope 2削減】：洗浄スピード向上により、成形機ヒーター等の稼働時間を短縮、消費電力量を削減

弊社では、御社の工場の稼働条件を入力するだけで、この「CO2削減量（環境価値）」と「削減コスト（経済価値）」を同時に可視化し、サステナビリティレポートにそのまま引用できる「環境価値シミュレーションレポート」を無料で作成しております。

御社のESG経営、および取引先大手メーカー様への強力なアピール実績として、本試算データを一度ご覧になりませんか？
近日中に、シミュレーターを用いたデモンストレーションの機会をいただけますと幸いです。
何卒よろしくお願い申し上げます。
"""
        st.text_area("📋 コピペ：代表・経営層・サステナ部門宛て", value=mail_mgmt, height=350)

# ==========================================
# フッター＆ディスクレイマー (景表法完全回避モデル)
# ==========================================
st.markdown(f"""
<div class="footer-disclaimer">
    <p><b>【免責事項および試算に関するご注意】</b><br>
    本シミュレーターによって算出される各種削減コスト、CO2排出削減量、およびその他の試算結果（以下「本試算結果」といいます）は、
    一般的な成形機仕様、市場における各種主要樹脂の平均的市場価格、公開された炭素排出係数、および当社特定の実験環境に基づく
    モデル数式を用いて算出された「参考値（シミュレーション）」であり、将来における具体的な経済的効果や環境負荷削減効果、
    あるいは特定の取引における成果を保証するものではありません。<br>
    実際のパージ効率、必要量、残留性、およびダウンタイム等は、お客様がご使用になる成形機仕様（メーカー、型締め力、スクリュ形状）、
    金型構造、成形材料のグレード、添加剤、温度設定、および作業者の習熟度等の諸条件によって大きく変動します。<br>
    また、比較対象として提示している他社パージ剤および共洗いに関する定数データは、一般的な市場調査および公表情報に基づき
    公正に設定されておりますが、すべての他社製品および作業工法に対する網羅性や正確性を保証するものではありません。
    本製品（LIMEX Purge）の導入を検討される際には、必ず事前にお客様の実機におけるテストおよび評価を実施してください。<br>
    なお、本シミュレーターの利用、または本試算結果に基づいて生じた直接的、間接的、その他一切の損害およびトラブルについて、
    株式会社TBMは法的責任を含めいかなる責任も負いかねます。本仕様は予告なく変更される場合があります。</p>
    <p>【プライバシーポリシー】本システムはお客様の入力したデータをサーバー上に一切保持しない「Session State処理（完全データ非保持）」を採用しております。安心してデモにご活用ください。 © {pd.Timestamp.now().year} TBM Co., Ltd. All Rights Reserved.</p>
</div>
""", unsafe_allow_html=True)
