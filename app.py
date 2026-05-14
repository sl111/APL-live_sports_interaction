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

# 🎨 Premium IPL Broadcast Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');

    /* Global Theme Overrides */
    .stApp {
        background: radial-gradient(circle at top right, #1e293b, #0f172a) !important;
        font-family: 'Outfit', sans-serif !important;
        color: #f8fafc !important; /* Force all text to off-white */
    }

    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 95%% !important;
    }

    /* 💎 Glassmorphism Cards */
    .card, [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(30, 41, 59, 0.6) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        padding: 20px !important;
        border-radius: 16px !important;
        margin-bottom: 15px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3) !important;
        color: #f8fafc !important;
    }

    /* 🟡 Broadcast Typography */
    h1, h2, h3, h4, [data-testid="stMetricLabel"] {
        color: #fbbf24 !important; /* Bright IPL Gold */
        font-weight: 700 !important;
        text-transform: uppercase !important;
    }

    /* Force all labels, paragraphs and spans to be visible */
    p, span, label, .commentary-text {
        color: #e2e8f0 !important; /* High-contrast light grey/white */
    }

    /* 🟢 Live & Status Badges */
    .badge {
        display: inline-flex;
        align-items: center;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .live-badge { 
        background: rgba(220, 38, 38, 0.3); 
        color: #ffffff !important; 
        border: 1px solid rgba(220, 38, 38, 0.6);
        animation: pulse 2s infinite; 
    }
    @keyframes pulse {
        0%% { box-shadow: 0 0 0 0 rgba(220, 38, 38, 0.4); }
        70%% { box-shadow: 0 0 0 10px rgba(220, 38, 38, 0); }
        100%% { box-shadow: 0 0 0 0 rgba(220, 38, 38, 0); }
    }

    /* 🎨 Event Color System */
    .run1 { color: #cbd5e1; font-weight: bold; }
    .run2 { color: #38bdf8; font-weight: bold; }
    .run4 { color: #fcd34d; font-weight: bold; text-shadow: 0 0 8px rgba(251, 191, 36, 0.6); }
    .run6 { color: #4ade80; font-weight: bold; text-shadow: 0 0 8px rgba(74, 222, 128, 0.6); }
    .wicket { color: #fca5a5; font-weight: bold; text-transform: uppercase; }

    /* 🏏 DYNAMIC TEAM THEME (Glow Borders) */
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) [data-testid="stVerticalBlockBorderWrapper"] {
        border: 2px solid %(glow_color)s !important;
        box-shadow: 0 0 20px %(glow_alpha)s !important;
    }

    /* Streamlit Widget Polishing (Inputs/Buttons) */
    div[data-testid="stMetricValue"] { color: #fbbf24 !important; font-size: 2.2rem !important; }
    .stProgress > div > div > div > div { background-color: #fbbf24 !important; }
    
    /* 🟡 HIGH VISIBILITY BUTTONS (Fix for invisible buttons) */
    .stButton > button {
        background-color: #fbbf24 !important;
        color: #0f172a !important;
        font-weight: 700 !important;
        border: 1px solid #fbbf24 !important;
        border-radius: 12px !important;
        width: 100%% !important;
        padding: 10px !important;
        transition: all 0.3s ease-in-out !important;
        opacity: 1 !important; /* Ensure they are never transparent */
        visibility: visible !important;
    }

    .stButton > button:hover {
        background-color: #fcd34d !important;
        box-shadow: 0 0 15px rgba(251, 191, 36, 0.5) !important;
        transform: translateY(-1px) !important;
    }

    /* Fix for radio buttons and inputs */
    [data-testid="stWidgetLabel"] p { color: #fbbf24 !important; font-weight: 700 !important; }
    [data-testid="stMarkdownContainer"] p { color: #f8fafc !important; }
    
</style>
""" % {
    "glow_color": "#f87171" if insights.get('batting_team') == insights.get('team1') else "#c084fc" if insights.get('batting_team') == insights.get('team2') else "#fbbf24",
    "glow_alpha": "rgba(239, 68, 68, 0.3)" if insights.get('batting_team') == insights.get('team1') else "rgba(168, 85, 247, 0.3)" if insights.get('batting_team') == insights.get('team2') else "rgba(251, 191, 36, 0.2)"
}, unsafe_allow_html=True)

# 📊 Initialize State
if "scores" not in st.session_state: st.session_state.scores = []
if "hype_score" not in st.session_state: st.session_state.hype_score = 0
if "poll_votes" not in st.session_state: st.session_state.poll_votes = {}
if "user_prediction" not in st.session_state: st.session_state.user_prediction = None

# 🔄 Match Tracking (Clear history if match changes)
current_match_id = f"{insights.get('team1')}_{insights.get('team2')}_{insights.get('date')}"
if "match_id" not in st.session_state:
    st.session_state.match_id = current_match_id
elif st.session_state.match_id != current_match_id:
    from memory.commentary_memory import clear_history
    clear_history()
    st.session_state.scores = []
    st.session_state.hype_score = 0
    st.session_state.poll_votes = {}
    st.session_state.match_id = current_match_id

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
        from datetime import datetime, timedelta
        try:
            dt_utc = datetime.strptime(insights['date'], "%Y-%m-%dT%H:%MZ")
            dt_ist = dt_utc + timedelta(hours=5, minutes=30)
            info_text = f"<span style='color: #9ca3af; font-size: 14px; margin-left: 10px;'>Starts: {dt_ist.strftime('%b %d, %I:%M %p')} IST</span>"
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
        st.caption("🏆 **Match Favorite**: Current chance of victory or projection.")
        try:
            if "target" in insights["score1"]:
                score_text = insights["score1"]
                target = int(score_text.split("target")[1].strip().replace(")", ""))
                runs = int(score_text.split("/")[0])
                needed = target - runs
                win_p = 100 if needed <= 0 else 80 if needed <= 10 else 55 if needed <= 30 else 30
                
                st.markdown(f"""
                <div style="text-align: center; padding: 20px 0;">
                    <h1 style="color: #22c55e; font-size: 48px; margin: 0;">{win_p}%</h1>
                    <p style="color: #9ca3af; margin-bottom: 20px;">Winning Chance for {insights['team1_short']}</p>
                    <div style="background-color: #374151; border-radius: 10px; height: 15px; width: 100%;">
                        <div style="background-color: #22c55e; width: {win_p}%; height: 100%; border-radius: 10px; transition: width 1s ease-in-out;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("Win probability will appear during the run chase.")
                if state == "in":
                    st.success(prediction) # Shows projected score
        except: 
            st.info("Waiting for more match data to calculate odds.")

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
            if "target" in insights["score1"] and "(" in insights["score2"]:
                overs_val = float(insights["score2"].split("(")[1].split(" ")[0])
                target = int(insights["score1"].split("target")[1].strip().replace(")", ""))
                runs = int(insights["score1"].split("/")[0])
                needed = target - runs
                rrr = needed / (20.0 - overs_val) if overs_val < 20 else 0
                pressure = min(100, rrr * 8)
                st.metric("Current Pressure", f"{pressure:.1f}%", delta=f"{rrr:.2f} RRR", delta_color="inverse")
                st.progress(pressure/100)
                st.caption("Higher pressure means a wicket is more likely in the next over!")
            else:
                st.info("Pressure index is most accurate during the run chase.")
        except: 
            st.info("Pressure index unavailable for current match state.")

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
        st.markdown('<h4 style="margin-bottom: 5px; color: #fbbf24; text-align: center;">⚡ Hype Meter</h4>', unsafe_allow_html=True)
        st.markdown('<p style="font-size: 11px; color: #f8fafc; font-weight: 600; margin-bottom: 10px; text-align: center;">Boost the match hype score!</p>', unsafe_allow_html=True)
        st.markdown(f'<h2 style="color: #ffffff; margin: 0; text-align: center; text-shadow: 0 0 10px rgba(251, 191, 36, 0.4);">{st.session_state.hype_score}</h2>', unsafe_allow_html=True)
        h_col1, h_col2, h_col3 = st.columns(3)
        if h_col1.button("🔥", key="btn_fire"): st.session_state.hype_score += 5; st.rerun()
        if h_col2.button("👏", key="btn_clap"): st.session_state.hype_score += 2; st.rerun()
        if h_col3.button("😱", key="btn_shock"): st.session_state.hype_score += 3; st.rerun()

    # GROUP 3: LIVE POLL (Only show when match is live)
    if state == "in":
        with st.container(border=True):
            st.markdown('<h4 style="color: #fbbf24; margin-bottom: 5px;">🗳️ Next Wicket Guess?</h4>', unsafe_allow_html=True)
            st.markdown('<p style="color: #f8fafc; font-size: 11px; font-weight: 600;">Predict which team loses the next wicket.</p>', unsafe_allow_html=True)
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
    elif state == "pre":
        with st.container(border=True):
            st.markdown('<h4 style="color: #fbbf24; margin-bottom: 5px;">🗳️ Match Prediction</h4>', unsafe_allow_html=True)
            st.markdown('<p style="color: #f8fafc; font-size: 11px; font-weight: 600;">Who will win today?</p>', unsafe_allow_html=True)
            p_opt = st.radio("Pick a winner", [insights['team1'], insights['team2']], key="pre_poll_radio", horizontal=True)
            if st.button("Vote Now", key="pre_vote_btn", use_container_width=True):
                st.session_state.poll_votes[p_opt] = st.session_state.poll_votes.get(p_opt, 0) + 1
                st.toast(f"Voted for {p_opt}!")
                st.rerun()

    # GROUP 4: PREDICTIONS & AI
    with st.container(border=True):
        st.markdown('<h4 style="margin-bottom: 5px; color: #fbbf24;">🎯 Beat the AI</h4>', unsafe_allow_html=True)
        st.markdown('<p style="font-size: 11px; color: #f8fafc; font-weight: 600; margin-bottom: 10px;">Enter your predicted final score!</p>', unsafe_allow_html=True)
        user_pred = st.number_input("Your Prediction:", min_value=0, max_value=500, value=180, key="pred_in")
        if st.button("Submit Prediction", key="sub_btn", use_container_width=True):
            st.session_state.user_prediction = user_pred; st.success(f"Recorded: {user_pred}!")

        # Unified AI Win Prob
        try:
            score_text = insights["score1"]; target = int(score_text.split("target")[1].strip().replace(")", ""))
            runs = int(score_text.split("/")[0]); needed = target - runs
            win_prob = 100 if needed <= 0 else 80 if needed <= 10 else 55 if needed <= 30 else 30
            st.markdown(f"""
            <div style="margin-top: 15px; border-top: 1px solid rgba(255, 255, 255, 0.1); padding-top: 10px;">
                <h4 style="margin-bottom: 5px; color: #fbbf24;">🤖 AI Win Probability</h4>
                <p style="font-size: 10px; color: #f8fafc; font-weight: 600; margin-bottom: 10px;">Real-time victory chance</p>
                <div style="display: flex; justify-content: space-between; font-size: 11px; color: #ffffff; font-weight: bold;"><span>{insights['team1_short']}</span><span>{win_prob}%</span></div>
                <div style="background-color: rgba(255, 255, 255, 0.05); border-radius: 10px; height: 6px; overflow: hidden;"><div style="background-color: #fbbf24; width: {win_prob}%; height: 100%; box-shadow: 0 0 10px rgba(251, 191, 36, 0.5);"></div></div>
            </div>""", unsafe_allow_html=True)
        except: pass

# 🔄 Auto Refresh Logic
if auto_refresh:
    time.sleep(15)
    st.rerun()