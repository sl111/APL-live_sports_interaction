import streamlit as st
import time
import pandas as pd
from data.fetch_data import get_match_data
from agents.insight_agent import analyze_match
from agents.commentary_agent import generate_commentary
from agents.prediction_agent import predict_winner
from memory.commentary_memory import add_commentary, get_history

# 🏏 Page config
st.set_page_config(page_title="AI Cricket Live", layout="wide")

# 📡 Data Engine (Ensures insights are available for Dynamic CSS)
data = get_match_data()
insights = analyze_match(data)

if "error" in insights:
    st.error(f"📡 Match Data Issue: {insights['error']}")
    st.info("Wait a moment for the API to refresh or check your connection.")
    st.stop()

# 🎨 Premium Styling & Spacing Fixes
st.markdown("""
<style>
    /* Adjust top spacing */
    .block-container {
        padding-top: 3.5rem !important;
        padding-bottom: 2rem !important;
    }
    
    /* 🟢 Badge styles */
    .badge {
        display: inline-block;
        padding: 4px 10px;
        color: white;
        border-radius: 15px;
        font-weight: bold;
        font-size: 12px;
    }

    .live-badge { background-color: #22c55e; animation: blink 1s infinite; }
    .finished-badge { background-color: #6b7280; }
    .scheduled-badge { background-color: #3b82f6; }

    @keyframes blink { 0%% {opacity: 1;} 50%% {opacity: 0.3;} 100%% {opacity: 1;} }

    /* 📦 Card style */
    .card {
        background-color: #111827;
        padding: 12px;
        border-radius: 10px;
        margin-bottom: 8px;
        color: white;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.4);
    }

    /* 🎨 Event colors */
    .run1 { color: #facc15; font-weight: bold; }
    .run2 { color: #3b82f6; font-weight: bold; }
    .run4 { color: #a855f7; font-weight: bold; }
    .run6 { color: #22c55e; font-weight: bold; }
    .wicket { color: #ef4444; font-weight: bold; }

    /* Remove gap above headers */
    h1, h2, h3 { margin-top: 0px !important; padding-top: 0px !important; }

    /* Limit commentary to keep dashboard compact */
    .commentary-text {
        display: -webkit-box;
        -webkit-line-clamp: 4;
        -webkit-box-orient: vertical;  
        overflow: hidden;
    }

    /* 🎨 DYNAMIC FAN ZONE THEME */
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: %(fan_bg)s !important;
        border: 3px solid %(fan_border)s !important;
        border-radius: 15px !important;
        padding: 15px !important;
        transition: all 0.5s ease;
    }

    div[data-testid="stHorizontalBlock"] > div:nth-child(2) div[data-testid="stVerticalBlockBorderWrapper"] * {
        color: %(fan_text)s !important;
        font-weight: bold !important;
    }

    /* Fix labels for inputs */
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) label,
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) p,
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) span {
        color: %(fan_text)s !important;
    }
</style>
""" % {
    "fan_bg": "#ef4444" if insights.get('batting_team') == insights.get('team1') else "#3b0764" if insights.get('batting_team') == insights.get('team2') else "rgba(251, 191, 36, 0.6)",
    "fan_border": "#991b1b" if insights.get('batting_team') == insights.get('team1') else "#fbbf24" if insights.get('batting_team') == insights.get('team2') else "rgba(251, 191, 36, 0.9)",
    "fan_text": "#ffffff" if insights.get('batting_team') in [insights.get('team1'), insights.get('team2')] else "#000000"
}, unsafe_allow_html=True)

# 📊 Initialize State
if "scores" not in st.session_state: st.session_state.scores = []
if "hype_score" not in st.session_state: st.session_state.hype_score = 0
if "poll_votes" not in st.session_state: st.session_state.poll_votes = {}
if "user_prediction" not in st.session_state: st.session_state.user_prediction = None

def format_event(text):
    if "out" in text.lower() or "wicket" in text.lower(): return f'<span class="wicket">🔴 {text}</span>'
    elif "6" in text: return f'<span class="run6">🟡 {text}</span>'
    elif "4" in text: return f'<span class="run4">🟣 {text}</span>'
    elif "2" in text: return f'<span class="run2">🔵 {text}</span>'
    elif "1" in text: return f'<span class="run1">🟢 {text}</span>'
    else: return text

# 🎙️ AI Commentary Engine (Limit post-match to 3 unique lines)
state = insights.get("state", "pre")
history = get_history()
finished_commentary_count = sum(1 for c in history if "won" in c.lower() or "final" in c.lower() or state == "post")

if state == "post" and len(history) >= 3:
    # If match is finished and we already have 3 highlights, just use the last one
    commentary = history[-1] if history else "Match Finished."
else:
    commentary = generate_commentary(insights)
    if "Error" not in commentary:
        add_commentary(commentary)

prediction = predict_winner(insights)

# Update Graph Data (Builds during LIVE match)
try:
    # Try to extract current batting team score
    # Usually insights['score1'] or insights['score2'] contains the active score
    current_score = insights["score2"] if "Yet to bat" not in insights["score2"] else insights["score1"]
    
    if "/" in current_score and "(" in current_score:
        runs = int(current_score.split("/")[0])
        overs_part = current_score.split("(")[1].split(" ")[0]
        
        over_parts = overs_part.split(".")
        over_float = float(over_parts[0]) + (float(over_parts[1]) / 6 if len(over_parts) > 1 else 0)
        
        # Only add if it's a new over/score update
        if not st.session_state.scores or st.session_state.scores[-1] != (over_float, runs):
            st.session_state.scores.append((over_float, runs))
except Exception as e:
    # Silent fail for graph data, but we could log it for debugging
    pass

# 🖥️ UI Header
state = insights.get("state", "pre")
badge_class = "live-badge" if state == "in" else "finished-badge" if state == "post" else "scheduled-badge"
badge_text = "🟢 LIVE" if state == "in" else "🏁 FINISHED" if state == "post" else "📅 NOT STARTED"

# Header Columns (Title/Badges on left, Refresh on right)
h_left, h_right = st.columns([0.8, 0.2])

with h_left:
    info_text = ""
    if state == "post":
        winner_logo = insights.get("team1_logo") if insights.get("winner_name") == insights.get("team1") else insights.get("team2_logo")
        logo_html = f'<img src="{winner_logo}" width="25" style="margin-right: 5px; vertical-align: middle;">' if winner_logo else ""
        info_text = f"<div style='background: rgba(34, 197, 94, 0.2); padding: 5px 15px; border-radius: 20px; border: 1px solid #22c55e; margin-left: 10px; display: flex; align-items: center;'>{logo_html}<span style='color: #4ade80; font-weight: bold;'>{insights.get('winner_name', 'Match')} Won!</span></div>"
    elif state == "pre":
        from datetime import datetime
        try:
            dt = datetime.strptime(insights['date'], "%Y-%m-%dT%H:%MZ")
            info_text = f"<span style='color: #9ca3af; font-size: 14px; margin-left: 10px;'>Starts: {dt.strftime('%b %d, %H:%M UTC')}</span>"
        except: pass

    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px; flex-wrap: wrap;">
        <h1 style="margin: 0; font-size: 28px;">🏏 AI Cricket Live</h1>
        <span class="badge {badge_class}">{badge_text}</span>
        {info_text}
    </div>
    """, unsafe_allow_html=True)

with h_right:
    auto_refresh = st.toggle("🔄 Auto Refresh", value=True, help="Auto-update dashboard every 15s")

# 📐 Layout Split
left_col, right_col = st.columns([0.65, 0.35])

with left_col:
    # 🏟️ Match & Score
    m_col1, m_col2 = st.columns(2)
    with m_col1:
        status_label = "🏁 Result" if state == "post" else "📌 Status"
        st.markdown(f"""
        <div class="card">
            <h3>🏟️ Match</h3>
            <div style="display: flex; align-items: center; gap: 10px;">
                <img src="{insights['team1_logo']}" width="30">
                <span style="font-size: 18px; font-weight: bold;">{insights['team1']}</span>
            </div>
            <div style="margin: 5px 0; font-style: italic; color: #9ca3af;">vs</div>
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                <img src="{insights['team2_logo']}" width="30">
                <span style="font-size: 18px; font-weight: bold;">{insights['team2']}</span>
            </div>
            <p style="color: #9ca3af; font-size: 13px; border-top: 1px solid #374151; padding-top: 5px;">{status_label}: {insights['status']}</p>
        </div>
        """, unsafe_allow_html=True)
    with m_col2:
        st.markdown(f"""
        <div class="card">
            <h3>📊 Current Score</h3>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <img src="{insights['team1_logo']}" width="20">
                    <span>{insights['team1']}</span>
                </div>
                <b>{insights['score1']}</b>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <img src="{insights['team2_logo']}" width="20">
                    <span>{insights['team2']}</span>
                </div>
                <b>{insights['score2']}</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 🎙️ Commentary
    st.markdown(f"""<div class="card" style="border-left: 4px solid #3b82f6;"><h3>🎙️ AI Commentary</h3><p class="commentary-text" style="font-style: italic; color: #d1d5db;">"{format_event(commentary)}"</p></div>""", unsafe_allow_html=True)

    # 📈 Performance Insights
    st.markdown("### 📊 Performance Insights")
    
    # Check if we have trend data
    has_data = len(st.session_state.scores) > 0
    
    # 4 Powerful Interactive Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🚀 Momentum", "⚖️ Win Prob", "🏏 Scoring Mix", "📉 Pressure"])
    
    with tab1:
        st.caption("Match Momentum: Runs progression over time.")
        if len(st.session_state.scores) > 1:
            df = pd.DataFrame(st.session_state.scores, columns=["Overs", "Runs"])
            st.line_chart(df.set_index("Overs"), height=200)
        else:
            st.info("Momentum chart builds as more overs are bowled.")

    with tab2:
        st.caption("🏆 **Match Favorite**: Current chance of victory.")
        try:
            score_text = insights["score1"]; target = int(score_text.split("target")[1].strip().replace(")", ""))
            runs = int(score_text.split("/")[0]); needed = target - runs
            win_p = 100 if needed <= 0 else 80 if needed <= 10 else 55 if needed <= 30 else 30
            
            # Using a Gauge-like progress bar instead of a confusing 2D chart
            st.markdown(f"""
            <div style="text-align: center; padding: 20px 0;">
                <h1 style="color: #22c55e; font-size: 48px; margin: 0;">{win_p}%</h1>
                <p style="color: #9ca3af; margin-bottom: 20px;">Winning Chance for {insights['team1_short']}</p>
                <div style="background-color: #374151; border-radius: 10px; height: 15px; width: 100%;">
                    <div style="background-color: #22c55e; width: {win_p}%; height: 100%; border-radius: 10px; transition: width 1s ease-in-out;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.info(f"The AI predicts {insights['team1_short']} has the edge based on current run rate vs required target.")
        except: st.info("Win chance will appear once the target is set.")

    with tab3:
        st.caption("🏏 **Match Stats**: Direct comparison of Runs and Wickets.")
        try:
            r1 = int(insights['score1'].split("/")[0])
            w1 = int(insights['score1'].split("/")[1].split(" ")[0])
            r2 = int(insights['score2'].split("/")[0])
            w2 = int(insights['score2'].split("/")[1].split(" ")[0])
            
            # Show as a clean comparison table instead of a scaled chart
            stats_df = pd.DataFrame({
                "Team": [insights['team1_short'], insights['team2_short']],
                "Runs Scored": [r1, r2],
                "Wickets Lost": [w1, w2]
            })
            st.table(stats_df.set_index("Team"))
            st.caption("Unlike the chart above, these are raw counts. No scaling applied.")
        except: st.info("Match stats will appear once the game is underway.")

    with tab4:
        st.caption("Pressure Index: Calculated based on Required Run Rate.")
        try:
            overs_val = float(insights["score2"].split("(")[1].split(" ")[0]) if "(" in insights["score2"] else 20.0
            needed = int(insights["score1"].split("target")[1].strip().replace(")", "")) - int(insights["score1"].split("/")[0])
            rrr = needed / (20.0 - overs_val) if overs_val < 20 else 0
            pressure = min(100, rrr * 8)
            st.metric("Current Pressure", f"{pressure:.1f}%", delta=f"{rrr:.2f} RRR", delta_color="inverse")
            st.progress(pressure/100)
            st.caption("Higher pressure means a wicket is more likely in the next over!")
        except: st.info("Pressure index available during the run chase.")

    # 🕒 Timeline
    st.markdown("### 🕒 Latest 3 Highlights")
    history = get_history()
    if history:
        timeline_html = '<div class="card">'
        for c in reversed(history):
            timeline_html += f'<div class="commentary-text" style="border-bottom: 1px solid #374151; padding: 6px 0; font-size: 12px;">• {format_event(c)}</div>'
        timeline_html += '</div>'
        st.markdown(timeline_html, unsafe_allow_html=True)

with right_col:
    # GROUP 1: HEADER
    with st.container(border=True):
        st.markdown('<h2 style="color: #000000; margin: 0; text-align: center;">🔥 FAN ZONE</h2>', unsafe_allow_html=True)
        st.markdown('<p style="color: #000000; font-size: 13px; font-weight: bold; margin: 0; text-align: center;">Live interactions & AI challenges</p>', unsafe_allow_html=True)

    # GROUP 2: HYPE METER
    with st.container(border=True):
        st.markdown('<h4 style="margin-bottom: 5px; color: #000000; text-align: center;">⚡ Hype Meter</h4>', unsafe_allow_html=True)
        st.markdown('<p style="font-size: 11px; color: #000000; font-weight: bold; margin-bottom: 10px; text-align: center;">Boost the match hype score!</p>', unsafe_allow_html=True)
        st.markdown(f'<h2 style="color: #000000; margin: 0; text-align: center;">{st.session_state.hype_score}</h2>', unsafe_allow_html=True)
        h_col1, h_col2, h_col3 = st.columns(3)
        if h_col1.button("🔥", key="btn_fire"): st.session_state.hype_score += 5; st.rerun()
        if h_col2.button("👏", key="btn_clap"): st.session_state.hype_score += 2; st.rerun()
        if h_col3.button("😱", key="btn_shock"): st.session_state.hype_score += 3; st.rerun()

    # GROUP 3: LIVE POLL
    with st.container(border=True):
        st.markdown('<h4 style="color: #000000; margin-bottom: 5px;">🗳️ Next Wicket Guess?</h4>', unsafe_allow_html=True)
        st.markdown('<p style="color: #000000; font-size: 11px; font-weight: bold;">Predict which team loses the next wicket.</p>', unsafe_allow_html=True)
        p_opt = st.radio("Who goes next?", [insights['team1'], insights['team2']], key="poll_radio", horizontal=True)
        if st.button("Vote Now", key="vote_btn", use_container_width=True):
            st.session_state.poll_votes[p_opt] = st.session_state.poll_votes.get(p_opt, 0) + 1
            st.toast(f"Voted for {p_opt}!")
            st.rerun()
        
        t1_v = st.session_state.poll_votes.get(insights['team1'], 0)
        t2_v = st.session_state.poll_votes.get(insights['team2'], 0)
        total = t1_v + t2_v
        st.progress(t1_v / total if total > 0 else 0.5)
        st.markdown(f'<p style="font-size: 11px; font-weight: bold; margin-top: 5px;">Fan Sentiment: {insights["team1"]} ({t1_v}) vs {insights["team2"]} ({t2_v})</p>', unsafe_allow_html=True)

    # GROUP 4: PREDICTIONS & AI
    with st.container(border=True):
        st.markdown('<h4 style="margin-bottom: 5px; color: #00000;">🎯 Beat the AI</h4>', unsafe_allow_html=True)
        st.markdown('<p style="font-size: 11px; color: #000000; font-weight: bold; margin-bottom: 10px;">Enter your predicted final score!</p>', unsafe_allow_html=True)
        user_pred = st.number_input("Your Prediction:", min_value=0, max_value=500, value=180, key="pred_in")
        if st.button("Submit Prediction", key="sub_btn", use_container_width=True):
            st.session_state.user_prediction = user_pred; st.success(f"Recorded: {user_pred}!")

        # Unified AI Win Prob
        try:
            score_text = insights["score1"]; target = int(score_text.split("target")[1].strip().replace(")", ""))
            runs = int(score_text.split("/")[0]); needed = target - runs
            win_prob = 100 if needed <= 0 else 80 if needed <= 10 else 55 if needed <= 30 else 30
            st.markdown(f"""
            <div style="margin-top: 15px; border-top: 1px solid rgba(251, 191, 36, 0.4); padding-top: 10px;">
                <h4 style="margin-bottom: 5px; color: #000000;">🤖 AI Win Probability</h4>
                <p style="font-size: 10px; color: #000000; font-weight: bold; margin-bottom: 10px;">Real-time victory chance</p>
                <div style="display: flex; justify-content: space-between; font-size: 11px; color: #000000; font-weight: bold;"><span>{insights['team1_short']}</span><span>{win_prob}%</span></div>
                <div style="background-color: rgba(0,0,0,0.1); border-radius: 10px; height: 6px; overflow: hidden;"><div style="background-color: #fbbf24; width: {win_prob}%; height: 100%;"></div></div>
            </div>""", unsafe_allow_html=True)
        except: pass

# 🔄 Auto Refresh Logic
if auto_refresh:
    time.sleep(15)
    st.rerun()