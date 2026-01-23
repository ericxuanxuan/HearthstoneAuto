import streamlit as st
import pandas as pd
import time

# 页面配置
st.set_page_config(page_title="8人游戏结算系统", layout="centered")

# --- 满屏爆炸特效函数 ---
def trigger_feng_explosion():
    st.balloons() # 第一波气球
    # 使用 HTML 和 CSS 制作一个巨大的、带闪烁和缩放效果的文字
    explosion_html = """
        <div style="
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            z-index: 9999;
            text-align: center;
            width: 100%;
        ">
            <h1 style="
                font-size: 100px;
                color: #FF0000;
                text-shadow: 5px 5px 20px #000, 0 0 50px #FF4B4B;
                animation: shake 0.5s infinite, zoom 1s ease-out;
                font-family: 'Microsoft YaHei';
            ">
                日你个冯！！！
            </h1>
        </div>
        <style>
            @keyframes shake {
                0% { transform: translate(1px, 1px) rotate(0deg); }
                10% { transform: translate(-1px, -2px) rotate(-1deg); }
                20% { transform: translate(-3px, 0px) rotate(1deg); }
                30% { transform: translate(3px, 2px) rotate(0deg); }
                40% { transform: translate(1px, -1px) rotate(1deg); }
                50% { transform: translate(-1px, 2px) rotate(-1deg); }
            }
            @keyframes zoom {
                0% { font-size: 10px; opacity: 0; }
                100% { font-size: 100px; opacity: 1; }
            }
        </style>
    """
    st.markdown(explosion_html, unsafe_allow_html=True)

st.title("🎮 炉石战旗游戏转账结算系统 ")
st.info("规则：固定8个席位名次。第1名收钱翻倍，速8付钱翻倍，名次相同不转账。")

# --- 1. 初始化数据状态 ---
if 'rounds' not in st.session_state:
    st.session_state.rounds = []
if 'player_names' not in st.session_state:
    st.session_state.player_names = ["玩家1", "玩家2", "玩家3", "玩家4"]

# --- 2. 侧边栏：配置人数和姓名 ---
with st.sidebar:
    st.header("⚙️ 设置")
    num_players = st.number_input("参与结算人数", min_value=2, max_value=8, value=len(st.session_state.player_names))

    new_names = []
    for i in range(num_players):
        default_name = st.session_state.player_names[i] if i < len(st.session_state.player_names) else f"玩家{i + 1}"
        name = st.text_input(f"姓名 {i + 1}", value=default_name, key=f"name_{i}")
        new_names.append(name)
    st.session_state.player_names = new_names

    if st.button("🔴 清空所有数据"):
        st.session_state.rounds = []
        st.rerun()

# --- 3. 主界面：录入每轮排名 ---
st.subheader("📝 录入本轮名次 (1-8名)")
cols = st.columns(num_players)
current_round = {}

for i, col in enumerate(cols):
    name = st.session_state.player_names[i]
    rank = col.number_input(f"{name}", min_value=1, max_value=8, value=4,
                            key=f"rank_input_{i}_{len(st.session_state.rounds)}")
    current_round[name] = rank

if st.button("➕ 确认并添加本轮"):
    st.session_state.rounds.append(current_round)
    st.success(f"第 {len(st.session_state.rounds)} 轮已保存！")

# --- 4. 历史记录展示 ---
if st.session_state.rounds:
    st.write("### 📊 已录入轮次")
    df = pd.DataFrame(st.session_state.rounds)
    df.index = [f"第{i + 1}轮" for i in range(len(df))]
    st.dataframe(df, use_container_width=True)

    # --- 5. 核心结算计算 ---
    if st.button("🚀 生成最终结算账单"):
        players = st.session_state.player_names
        matrix = {p1: {p2: 0 for p2 in players if p2 != p1} for p1 in players}
        balances = {p: 0 for p in players} # 新增：用于记录总盈亏

        for r_ranks in st.session_state.rounds:
            for i in range(len(players)):
                for j in range(i + 1, len(players)):
                    p1, p2 = players[i], players[j]
                    r1, r2 = r_ranks[p1], r_ranks[p2]
                    if r1 == r2: continue

                    winner, loser = (p1, p2) if r1 < r2 else (p2, p1)
                    win_rank, lose_rank = (r1, r2) if r1 < r2 else (r2, r1)

                    base = lose_rank - win_rank
                    multiplier = 1
                    if win_rank == 1: multiplier *= 2
                    if lose_rank == 8: multiplier *= 2

                    amount = base * multiplier
                    matrix[loser][winner] += amount
                    balances[winner] += amount # 赢家加钱
                    balances[loser] -= amount  # 输家减钱

        # --- 最终显示 ---
        st.write("---")
        st.subheader("💰 最终转账方案")

        results = []
        processed = set()
        for p1 in players:
            for p2 in players:
                if p1 == p2 or (p1, p2) in processed: continue
                net = matrix[p1][p2] - matrix[p2][p1]
                if net > 0:
                    results.append(f"【{p1}】 ➡️ 【{p2}】 ： **{net}** 元")
                elif net < 0:
                    results.append(f"【{p2}】 ➡️ 【{p1}】 ： **{abs(net)}** 元")
                processed.add((p1, p2))
                processed.add((p2, p1))

        if results:
            for res in results:
                st.info(res)
        else:
            st.write("所有账目已抵消。")

        # --- 彩蛋检测逻辑 ---
        feng_wins = False
        for p, amt in balances.items():
            p_lower = p.lower()
            if ("冯" in p_lower or "feng" in p_lower or "fy" in p_lower) and amt > 0:
                feng_wins = True
                break
        
        if feng_wins:
            trigger_feng_explosion()
