import streamlit as st
import pandas as pd

# 页面配置
st.set_page_config(page_title="8人游戏结算系统", layout="centered")

# --- 满屏文字特效函数 (右侧精简版) ---
def trigger_feng_explosion():
    # 锚点设在极右侧 (right: 2%)，字号使用较小的 vw 单位
    elements = [
        {"top": "50%", "right": "2%", "size": "14vw", "delay": "0s"},
        {"top": "35%", "right": "4%", "size": "9vw", "delay": "0.5s"},
        {"top": "65%", "right": "3%", "size": "10vw", "delay": "1s"},
        {"top": "42%", "right": "6%", "size": "7vw", "delay": "1.5s"},
        {"top": "58%", "right": "2%", "size": "11vw", "delay": "2s"},
        {"top": "25%", "right": "5%", "size": "6vw", "delay": "0.3s"},
        {"top": "75%", "right": "4%", "size": "8vw", "delay": "0.8s"},
        {"top": "15%", "right": "5%", "size": "5vw", "delay": "0.1s"},
    ]
    
    html_content = ""
    for i, el in enumerate(elements):
        html_content += f"""
        <div style="
            position: fixed;
            top: {el['top']};
            right: {el['right']};
            transform: translateY(-50%);
            z-index: {10000 + i};
            pointer-events: none;
            animation: pop-and-shake-right 3s infinite {el['delay']};
            opacity: 0;
            text-align: right;
        ">
            <h1 style="
                font-size: {el['size']};
                color: #FF0000;
                text-shadow: 1px 1px 5px #000, -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000;
                font-family: 'Microsoft YaHei', 'SimHei', sans-serif;
                white-space: nowrap;
                margin: 0;
                font-weight: 900;
            ">
                日你个冯！！！
            </h1>
        </div>
        """

    full_html = f"""
        {html_content}
        <style>
            @keyframes pop-and-shake-right {{
                0% {{ transform: translateY(-50%) scale(0); opacity: 0; }}
                10% {{ transform: translateY(-50%) scale(1); opacity: 1; }}
                20% {{ transform: translateY(-49%) rotate(1deg); opacity: 1; }}
                30% {{ transform: translateY(-51%) rotate(-1deg); opacity: 1; }}
                50% {{ transform: translateY(-50%) scale(1); opacity: 1; }}
                90% {{ transform: translateY(-50%) scale(0.9); opacity: 1; }}
                100% {{ transform: translateY(-50%) scale(0); opacity: 0; }}
            }}
        </style>
    """
    st.markdown(full_html, unsafe_allow_html=True)

st.title("🎮 炉石战旗游戏转账结算系统")
st.info("规则：固定8个席位名次。第1名收钱翻倍，速8付钱翻倍，名次相同不转账。")

# --- 1. 初始化数据状态 ---
if 'rounds' not in st.session_state:
    st.session_state.rounds = []
if 'player_names' not in st.session_state:
    st.session_state.player_names = ["玩家1", "玩家2", "玩家3", "玩家4"]

# --- 2. 侧边栏：配置 ---
with st.sidebar:
    st.header("⚙️ 设置")
    num_players = st.number_input("参与结算人数", min_value=2, max_value=8, value=len(st.session_state.player_names))

    new_names = []
    for i in range(num_players):
        default_name = st.session_state.player_names[i] if i < len(st.session_state.player_names) else f"玩家{i + 1}"
        name = st.text_input(f"姓名 {i + 1}", value=default_name, key=f"name_{i}")
        new_names.append(name)
    st.session_state.player_names = new_names

    st.write("---")
    if st.button("🗑️ 删除最后一轮"):
        if st.session_state.rounds:
            st.session_state.rounds.pop()
            st.rerun()
            
    if st.button("🔴 清空所有数据"):
        st.session_state.rounds = []
        st.rerun()

# --- 3. 主界面：录入 ---
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

# --- 4. 历史展示 ---
if st.session_state.rounds:
    st.write("---")
    st.write("### 📊 已录入轮次")
    df = pd.DataFrame(st.session_state.rounds)
    df.index = [f"第{i + 1}轮" for i in range(len(df))]
    st.dataframe(df, use_container_width=True)

    # --- 5. 核心结算逻辑 ---
    if st.button("🚀 生成结算报告 (含优化方案)"):
        players = st.session_state.player_names
        matrix = {p1: {p2: 0 for p2 in players if p2 != p1} for p1 in players}
        balances = {p: 0 for p in players}

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
                    balances[winner] += amount
                    balances[loser] -= amount

        st.divider()
        st.subheader("🔍 第一部分：两两结算明细")
        detail_results = []
        processed = set()
        for p1 in players:
            for p2 in players:
                if p1 == p2 or (p1, p2) in processed: continue
                net = matrix[p1][p2] - matrix[p2][p1]
                if net > 0:
                    detail_results.append(f"• **{p1}** ➡️ **{p2}** ： `{net}` 元")
                elif net < 0:
                    detail_results.append(f"• **{p2}** ➡️ **{p1}** ： `{abs(net)}` 元")
                processed.add((p1, p2))
                processed.add((p2, p1))
        
        if detail_results:
            for res in detail_results: st.write(res)
        else: st.write("无账目往来")

        st.divider()
        st.subheader("✅ 第二部分：最简转账方案 (推荐)")
        debtors = [[p, amt] for p, amt in balances.items() if amt < 0]
        creditors = [[p, amt] for p, amt in balances.items() if amt > 0]

        optimized_results = []
        d_idx, c_idx = 0, 0
        while d_idx < len(debtors) and c_idx < len(creditors):
            d_name, d_amt = debtors[d_idx][0], abs(debtors[d_idx][1])
            c_name, c_amt = creditors[c_idx][0], creditors[c_idx][1]
            transfer = min(d_amt, c_amt)
            if transfer > 0.01:
                optimized_results.append(f"🔴 **{d_name}** ➡️ 转给 🟢 **{c_name}** ： **{round(transfer, 2)}** 元")
            debtors[d_idx][1] += transfer
            creditors[c_idx][1] -= transfer
            if abs(debtors[d_idx][1]) < 0.01: d_idx += 1
            if abs(creditors[c_idx][1]) < 0.01: c_idx += 1

        if optimized_results:
            for res in optimized_results: st.info(res)
        else: st.write("账目已平")

        with st.expander("查看全员最终输赢总额"):
            for p, amt in balances.items():
                if amt > 0: st.success(f"**{p}**：最终赢了 `{amt}` 元")
                elif amt < 0: st.error(f"**{p}**：最终输了 `{abs(amt)}` 元")
                else: st.write(f"**{p}**：不输不赢")

        # --- 彩蛋检测 ---
        feng_wins = False
        for p, amt in balances.items():
            p_lower = p.lower()
            if any(key in p_lower for key in ["冯", "feng", "fy"]) and amt > 0:
                feng_wins = True
                break
        
        if feng_wins:
            trigger_feng_explosion()
