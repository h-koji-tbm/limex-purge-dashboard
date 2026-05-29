import streamlit as st
import pandas as pd
import numpy as np

# ページ設定
st.set_page_config(
    page_title="LIMEX Purge コスト＆脱炭素シミュレーター",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# データベース (紹介資料 Slide 16, Slide 36, Slide 38)
# ==========================================
MACHINE_DEFAULTS = {
    "小型 (80ton級)": {"purge": 0.35, "waste": 2.0, "time": 45},
    "中小型 (125ton級)": {"purge": 0.5, "waste": 3.0, "time": 50},
    "中大型 (550ton級)": {"purge": 2.5, "waste": 10.0, "time": 60},
    "大型 (800ton級)": {"purge": 5.0, "waste": 15.0, "time": 80},
    "超大型 (1250ton級)": {"purge": 7.0, "waste": 20.0, "time": 100}
}

ENV_FACTORS = {
    "他社AS樹脂系 (アスアクリア等)": {"plastic": 1.00, "ghg": 8.34},
    "他社スチレン系": {"plastic": 0.75, "ghg": 6.88},
    "他社エチレン系": {"plastic": 1.00, "ghg": 7.41},
    "他社無機/AS系": {"plastic": 0.50, "ghg": 6.50},
    "LIMEX Purge G": {"plastic": 0.33, "ghg": 4.35},
    "LIMEX Purge HT2": {"plastic": 0.34, "ghg": 4.08}
}

# ==========================================
# サイドバー入力領域
# ==========================================
st.sidebar.header("⚙️ 稼働条件の設定")

machine_class = st.sidebar.selectbox(
    "1. 成形機のサイズを選択",
    list(MACHINE_DEFAULTS.keys()),
    index=2
)

# 選択されたサイズから初期値を取得
defaults = MACHINE_DEFAULTS[machine_class]

machines = st.sidebar.slider("稼働している成形機の台数 (台)", 1, 100, 5)
cycles_per_month = st.sidebar.slider("1台あたりの月間色替え回数 (回/月)", 1, 100, 20)

st.sidebar.markdown("---")
st.sidebar.subheader("💸 コスト・単価設定")

st.sidebar.warning("⚠️ 原油・ナフサ高騰により、他社製石油系パージ剤は急激な価格高騰リスクに晒されています。")

comp_purge_type = st.sidebar.selectbox(
    "比較対象の現行パージ剤タイプ",
    ["他社AS樹脂系 (アスアクリア等)", "他社スチレン系", "他社エチレン系", "他社無機/AS系"]
)

comp_price = st.sidebar.number_input("現行パージ剤の単価 (円/kg)", value=1500, step=50)
limex_price = st.sidebar.number_input("LIMEX Purge 想定単価 (円/kg)", value=1000, step=50)
raw_resin_price = st.sidebar.number_input("成形用原料樹脂の平均単価 (円/kg)", value=350, step=10)
machine_charge = st.sidebar.number_input("マシンチャージ・人件費 (円/時間)", value=8000, step=500)

st.sidebar.markdown("---")
st.sidebar.subheader("⏱️ 現場実測値の微調整")
current_time = st.sidebar.number_input("1回あたりの現行段取り時間 (分)", value=defaults["time"], step=5)
current_purge_usage = st.sidebar.number_input("1回あたりの現行パージ剤使用量 (kg)", value=defaults["purge"], step=0.1)
current_resin_waste = st.sidebar.number_input("1回あたりの現行ロス樹脂量 (kg)", value=defaults["waste"], step=0.5)

# ==========================================
# 計算ロジック
# ==========================================
total_cycles = machines * cycles_per_month * 12

# 現状コスト
curr_time_cost = (current_time / 60) * machine_charge
curr_purge_cost = current_purge_usage * comp_price
curr_resin_cost = current_resin_waste * raw_resin_price
curr_cycle_total = curr_time_cost + curr_purge_cost + curr_resin_cost
curr_annual_cost = total_cycles * curr_cycle_total

# LIMEX Purge導入後 (作業時間30%減、使用量20%減、ロス樹脂30%減)
limex_time = current_time * 0.7
limex_time_cost = (limex_time / 60) * machine_charge
limex_purge_usage = current_purge_usage * 0.8
limex_purge_cost = limex_purge_usage * limex_price
limex_resin_waste = current_resin_waste * 0.7
limex_resin_cost = limex_resin_waste * raw_resin_price
limex_cycle_total = limex_time_cost + limex_purge_cost + limex_resin_cost
limex_annual_cost = total_cycles * limex_cycle_total

annual_savings = curr_annual_cost - limex_annual_cost

# 環境価値計算
curr_total_purge_kg = current_purge_usage * total_cycles
limex_total_purge_kg = limex_purge_usage * total_cycles

curr_env = ENV_FACTORS[comp_purge_type]
limex_env = ENV_FACTORS["LIMEX Purge G"]

curr_co2 = curr_total_purge_kg * curr_env["ghg"]
limex_co2 = limex_total_purge_kg * limex_env["ghg"]
co2_savings = max(0.0, curr_co2 - limex_co2)

curr_plat = curr_total_purge_kg * curr_env["plastic"]
limex_plat = limex_total_purge_kg * limex_env["plastic"]
plat_savings = max(0.0, curr_plat - limex_plat)

saved_time_hours = ((current_time - limex_time) * total_cycles) / 60

# ==========================================
# メイン画面の描画
# ==========================================
st.title("🌱 LIMEX Purge 価格安定＆脱炭素シミュレーター")
st.markdown("""
直近の中東情勢によるナフサ価格の高騰に直面する成形メーカー様へ。
国内で100%自給可能な石灰石を50%以上含む **LIMEX Purge** は、原油高の影響を受けない安定した価格構造と、
石油プラスチック・CO2排出量の大幅削減を両立します。自社の条件を入力して、今すぐ削減効果を測定してください。
""")

st.markdown("---")

# 4つの主要メトリクス表示
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(
        label="💰 年間コスト削減見込み",
        value=f"¥{int(annual_savings):,}",
        delta=f"削減率: {((curr_annual_cost - limex_annual_cost)/curr_annual_cost*100):.1f}%"
    )
with col2:
    st.metric(
        label="📉 GHG (CO₂) 年間削減量",
        value=f"{int(co2_savings):,} kg-CO2e",
        delta=f"削減率: {((curr_co2 - limex_co2)/curr_co2*100):.1f}%"
    )
with col3:
    st.metric(
        label="🛢️ 石油系プラ 年間削減量",
        value=f"{int(plat_savings):,} kg",
        delta=f"削減率: {((curr_plat - limex_plat)/curr_plat*100):.1f}%"
    )
with col4:
    st.metric(
        label="⏳ 段取り替えの年間削減時間",
        value=f"{int(saved_time_hours):,} 時間",
        delta="現場のダウンタイム削減"
    )

st.markdown("---")

# タブ機能
tab1, tab2, tab3 = st.tabs(["📊 コスト・環境分析グラフ", "📋 詳細計算明細", "💡 技術データ＆導入事例"])

with tab1:
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("💰 年間トータルコストの比較")
        # Streamlit純正のインタラクティブな縦棒グラフ（文字化けが絶対に起きない）
        cost_df = pd.DataFrame(
            [curr_annual_cost, limex_annual_cost],
            index=["現状 (他社石油系)", "LIMEX Purge 導入後"],
            columns=["年間トータルコスト (円)"]
        )
        st.bar_chart(cost_df, height=350, use_container_width=True)
        
    with col_chart2:
        st.subheader("🌱 環境貢献比較 (現状 vs LIMEX)")
        # 複数カラムの比較グラフ
        env_df = pd.DataFrame(
            {
                "現状 (他社石油系)": [curr_co2, curr_plat],
                "LIMEX Purge 導入後": [limex_co2, limex_plat]
            },
            index=["GHG排出量 (kg-CO2e)", "石油プラ使用量 (kg)"]
        )
        st.bar_chart(env_df, height=350, use_container_width=True)

with tab2:
    st.subheader("📋 項目別 年間コストシミュレーション明細")
    
    detail_data = {
        "項目": ["段取り人件費・稼働ロス (時間コスト)", "パージ剤購入コスト", "材料ロス樹脂コスト", "合計コスト (年間)"],
        "現状 (他社石油系)": [
            f"¥{int(total_cycles * curr_time_cost):,}",
            f"¥{int(total_cycles * curr_purge_cost):,}",
            f"¥{int(total_cycles * curr_resin_cost):,}",
            f"¥{int(curr_annual_cost):,}"
        ],
        "LIMEX Purge 導入後": [
            f"¥{int(total_cycles * limex_time_cost):,}",
            f"¥{int(total_cycles * limex_purge_cost):,}",
            f"¥{int(total_cycles * limex_resin_cost):,}",
            f"¥{int(limex_annual_cost):,}"
        ],
        "差額 (年間削減効果)": [
            f"¥{int(total_cycles * (curr_time_cost - limex_time_cost)):,}",
            f"¥{int(total_cycles * (curr_purge_cost - limex_purge_cost)):,}",
            f"¥{int(total_cycles * (curr_resin_cost - limex_resin_cost)):,}",
            f"¥{int(annual_savings):,}"
        ]
    }
    
    st.table(pd.DataFrame(detail_data))

with tab3:
    st.subheader("💡 設備保護・作業効率化に関する技術的ファクト")
    
    col_tech1, col_env_tbl = st.columns(2)
    
    with col_tech1:
        with st.expander("🛠️ スクリューを絶対に傷つけない理由 (モース硬度比較)"):
            st.markdown("""
            他社パージ剤に含まれるガラス繊維（モース硬度7）と異なり、LIMEXに高配合されている
            **炭酸カルシウム（石灰石）は人の爪と同等に柔らかいモース硬度3**です。
            
            *   **スクリュー/シリンダー摩耗への影響度：**
                *   ガラス入り材料：5 (摩耗リスク大)
                *   タルク入り材料：3〜4
                *   **炭酸カルシウム（石灰石）材料：2〜3 (極めて安全)**
            
            過去5年間、TBM自社工場および射出・押出機メーカーからの摩耗障害事例の報告はありません。
            """)
            
        with st.expander("⏱️ 金曜日に機内充填して「週末シャットダウン」が可能"):
            st.markdown("""
            金曜日の稼働停止（立ち下げ）時にシリンダー内にLIMEX Purgeを充填したままヒーターを切り、
            月曜日の朝にそのまま温度を上げて立ち上げることが可能です（100t射出機、200℃実証済み）。
            
            *   **結果：** 熱分解や樹脂焼け・炭化物の発生は一切見られず、月曜朝の生産用PP樹脂への置換が非常にスムーズに完了します。
            """)
            
        with st.expander("🚗 Tier1企業をはじめとする豊富な良好導入事例"):
            st.markdown("""
            *   **自動車部品 (ピラー/700t):** 現行パージ剤（B社製）と比較して洗浄能力が高く、量産開始直後の捨て打ち廃棄数を半減（不良ロス削減＆コストダウン）。
            *   **自動車部品 (ドアロック/450t):** スクリュー表面 of 炭化物のこびり付きを低減し、コストダウンを両立。
            *   **家電製品 (空調ファン/350t):** 洗浄力が高く、現行品（A社製）の半分以下の使用量でパージが完了。
            """)

    with col_env_tbl:
        st.markdown("**🌱 パージ剤1kgあたりの環境負荷データ比較 (LCAデータ)**")
        lca_df = pd.DataFrame({
            "パージ剤の種類": ["他社スチレン系", "他社AS樹脂系", "他社エチレン系", "LIMEX Purge G"],
            "プラスチック使用量 (kg/kg)": ["0.75", "1.00", "1.00", "0.33"],
            "GHG排出量 (kg-CO2e)": ["6.88", "8.34", "7.41", "4.35"]
        })
        st.dataframe(lca_df, use_container_width=True)
        st.caption("※2026年1月 株式会社TBM算定データ。LCIデータベースIDEA version 3.2参照。")

st.markdown("---")
st.subheader("📞 テスト用「無料サンプルキット」のお申し込み")
st.markdown("シミュレーターで算出された効果を現場で実際にお試しください。対応グレード（G / HT / S / F）の選定・診断も合わせて実施します。")

col_form1, col_form2 = st.columns(2)
with col_form1:
    company_name = st.text_input("会社名")
    user_name = st.text_input("お名前")
with col_form2:
    email = st.text_input("メールアドレス")
    grade_selection = st.selectbox("最も試してみたい対応グレード", ["高洗浄：LIMEX Purge G (汎用樹脂向け)", "高洗浄：LIMEX Purge HT (エンプラ樹脂向け)", "低残留：LIMEX Purge S (開発中バランスタイプ)", "フィルム用：LIMEX Purge F (インフレ・Tダイ)"])

if st.button("シミュレーション結果を添付して無料サンプルを請求する"):
    if company_name and user_name and email:
        st.success("ありがとうございます！お申込みを受け付けました。1営業日以内に担当者（h-koji@tb-m.com）より折り返しご連絡いたします。")
    else:
        st.error("お手数ですが、会社名・お名前・メールアドレスをご入力ください。")
