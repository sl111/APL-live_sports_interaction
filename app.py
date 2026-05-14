import streamlit as st
import time
import pandas as pd
import re
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

# 🌍 Global Shared State (Synchronizes all fans in real-time)
@st.cache_resource
def get_global_state():
    return {
        "hype_score": 0,
        "poll_votes": {},
        "leaderboard": {}, # {Name: Score}
        "match_id": ""
    }

global_state = get_global_state()

# 📊 Initialize State (Local & Global)
if "scores" not in st.session_state: st.session_state.scores = []
if "user_prediction" not in st.session_state: st.session_state.user_prediction = None
if "fan_name" not in st.session_state: st.session_state.fan_name = ""

# Reset global state if match changes
current_match_id = f"{insights.get('team1')}_{insights.get('team2')}_{insights.get('date')}"
if global_state["match_id"] != current_match_id:
    global_state["match_id"] = current_match_id
    global_state["hype_score"] = 0
    global_state["poll_votes"] = {}
    global_state["leaderboard"] = {}
    from memory.commentary_memory import clear_history
    clear_history()
    st.session_state.scores = []

def cricket_overs_to_decimal(overs_str):
    try:
        parts = str(overs_str).split(".")
        if len(parts) == 2:
            return int(parts[0]) + (int(parts[1]) / 6.0)
        return float(parts[0])
    except: return 0.1

def parse_score_details(score_str):
    try:
        # Extract runs/wickets
        runs = int(score_str.split("/")[0])
        wickets = int(score_str.split("/")[1].split(" ")[0]) if "/" in score_str else 0
        
        # Look for overs in common formats: (1.3/20) or (1.3 ov) or just 1.3
        over_match = re.search(r'\((\d+\.\d+)', score_str)
        if over_match:
            o_raw = over_match.group(1)
        else:
            # Fallback for simpler strings
            o_raw = "0.1"
            
        return runs, wickets, cricket_overs_to_decimal(o_raw)
    except: return 0, 0, 0.1

# 📊 GLOBAL DATA TRACKER (Runs every refresh)
try:
    s1, s2 = insights.get('score1', ''), insights.get('score2', '')
    active_s = s2 if "(" in s2 else s1
    r_val, w_val, o_val = parse_score_details(active_s)
    
    # Only track if we have valid overs to prevent '40000' projection
    if o_val > 0.1:
        # Prevent duplicates in momentum
        if not st.session_state.scores or st.session_state.scores[-1]["Overs"] != o_val:
            st.session_state.scores.append({"Overs": o_val, "Runs": r_val})
except: pass

def format_event(text):
    if "out" in text.lower() or "wicket" in text.lower(): return f'<span class="wicket">🔴 {text}</span>'
    elif "6" in text: return f'<span class="run6">💎 {text}</span>'
    elif "4" in text: return f'<span class="run4">✨ {text}</span>'
    elif "2" in text: return f'<span class="run2">🔵 {text}</span>'
    elif "1" in text: return f'<span class="run1">🟢 {text}</span>'
    else: return text

# 🎙️ AI Commentary & Prediction Engine (Optimized)
# We only call the AI if the match state has changed to prevent lag on button clicks
current_ball = insights.get("last_event", "")
if "commentary" not in st.session_state or st.session_state.get("last_ball") != current_ball:
    with st.spinner("🤖 AI analyzing match..."):
        state = insights.get("state", "pre")
        history = get_history()
        
        # Limit post-match to 3 unique lines
        if state == "post" and len(history) >= 3:
            commentary = history[-1] if history else "Match Finished."
        else:
            commentary = generate_commentary(insights)
            if "Error" not in commentary:
                add_commentary(commentary)
        
        prediction = predict_winner(insights)
        
        # Save to session state so button clicks don't re-trigger AI
        st.session_state.commentary = commentary
        st.session_state.prediction = prediction
        st.session_state.last_ball = current_ball
else:
    commentary = st.session_state.commentary
    prediction = st.session_state.prediction

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
        st.markdown('<h4 style="color: #fbbf24;">📈 Match Momentum</h4>', unsafe_allow_html=True)
        if len(st.session_state.scores) > 0:
            df = pd.DataFrame(st.session_state.scores)
            st.line_chart(df.set_index("Overs")["Runs"])
        else:
            st.info("Momentum chart is warming up (starts after 1 over).")

    with tab2:
        st.markdown('<h3 style="color: #fbbf24; text-align: center;">🏆 Match Projection</h3>', unsafe_allow_html=True)
        try:
            s1, s2 = insights.get('score1', ''), insights.get('score2', '')
            active_score = s2 if "(" in s2 else s1
            active_team = insights.get('team2_short', 'T2') if "(" in s2 else insights.get('team1_short', 'T1')
            r, w, o = parse_score_details(active_score)
            
            # CRR Check (Prevent crazy numbers)
            crr = r / o if o > 0.2 else 0
            projected = int(crr * 20) if o > 0.2 else 0
            
            # Win probability logic
            win_p = 50
            if "target" in active_score: # Run Chase
                target_match = re.search(r'target (\d+)', active_score)
                target = int(target_match.group(1)) if target_match else 180
                needed = target - r
                win_p = 100 if needed <= 0 else 85 if needed <= 15 else 45
            else: # 1st Innings
                if projected > 190: win_p = 75
                elif projected > 160: win_p = 55
                elif projected < 140: win_p = 35

            st.markdown(f"""
            <div class="card" style="text-align: center;">
                <h1 style="color: #fbbf24; font-size: 56px; margin: 0;">{win_p}%</h1>
                <p style="color: #f8fafc; font-weight: 600;">{active_team.upper()} WIN CHANCE</p>
                <div style="background: rgba(255,255,255,0.05); border-radius: 20px; height: 12px; width: 100%;">
                    <div style="background: #fbbf24; width: {win_p}%; height: 100%; border-radius: 20px;"></div>
                </div>
                <div style="display: flex; justify-content: center; gap: 20px; margin-top: 20px;">
                    <div><p style="color: #94a3b8; font-size: 11px;">PROJECTED</p><p style="color: #fbbf24; font-size: 18px; font-weight: bold;">{projected}</p></div>
                    <div><p style="color: #94a3b8; font-size: 11px;">RUN RATE</p><p style="color: #fbbf24; font-size: 18px; font-weight: bold;">{crr:.2f}</p></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        except: st.info("Analyzing opening overs...")

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
        st.markdown('<h3 style="color: #fbbf24;">🔥 Pressure Index</h3>', unsafe_allow_html=True)
        try:
            s1, s2 = insights.get('score1', ''), insights.get('score2', '')
            active_score = s2 if "(" in s2 else s1
            active_team = insights.get('team2_short', 'T2') if "(" in s2 else insights.get('team1_short', 'T1')
            r, w, o = parse_score_details(active_score)
            crr = r / o
            
            # Correct Pressure Logic: Factor in Wickets and Run Rate gaps
            pressure = min(100, max(5, (8.5 - crr) * 12 + (w * 15)))
            
            st.metric(f"{active_team} Pressure", f"{pressure:.1f}%", delta=f"{crr:.2f} CRR", delta_color="inverse")
            st.progress(pressure/100)
            st.caption(f"AI Note: {active_team} pressure increases as run rate drops or wickets fall.")
        except: st.info("Analyzing match pressure...")

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
    # GROUP 0: FAN IDENTITY
    with st.container(border=True):
        st.markdown('<h4 style="margin-bottom: 5px; color: #fbbf24;">👤 Fan Identity</h4>', unsafe_allow_html=True)
        name = st.text_input("Enter your Fan Name:", value=st.session_state.fan_name, placeholder="e.g. CricketKing", label_visibility="collapsed")
        if name != st.session_state.fan_name:
            st.session_state.fan_name = name
            st.rerun()

    # GROUP 1: 🏆 TOP 3 FANS (Elite Placement)
    with st.container(border=True):
        st.markdown('<h4 style="margin-bottom: 5px; color: #fbbf24; text-align: center;">🏆 Hall of Fame</h4>', unsafe_allow_html=True)
        if global_state["leaderboard"]:
            sorted_fans = sorted(global_state["leaderboard"].items(), key=lambda x: x[1], reverse=True)[:3]
            for i, (fname, fscore) in enumerate(sorted_fans):
                medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉"
                st.markdown(f'<div style="display: flex; justify-content: space-between; font-size: 14px; color: #f8fafc; border-bottom: 1px solid rgba(255,255,255,0.05); padding: 8px 0;"><span>{medal} {fname}</span><span style="color: #fbbf24; font-weight: bold;">{fscore} pts</span></div>', unsafe_allow_html=True)
        else:
            st.markdown('<p style="font-size: 11px; color: #94a3b8; font-style: italic; text-align: center;">No activity yet. Boost the hype!</p>', unsafe_allow_html=True)

    # GROUP 2: HEADER
    with st.container(border=True):
        st.markdown('<h2 style="color: #fbbf24; margin: 0; text-align: center;">🔥 FAN ZONE</h2>', unsafe_allow_html=True)
        st.markdown('<p style="color: #f8fafc; font-size: 13px; font-weight: bold; margin: 0; text-align: center;">Live interactions & AI challenges</p>', unsafe_allow_html=True)

    # GROUP 2: HYPE METER
    with st.container(border=True):
        st.markdown('<h4 style="margin-bottom: 5px; color: #fbbf24; text-align: center;">⚡ Hype Meter</h4>', unsafe_allow_html=True)
        st.markdown('<p style="font-size: 11px; color: #f8fafc; font-weight: 600; margin-bottom: 10px; text-align: center;">Boost the match hype score!</p>', unsafe_allow_html=True)
        st.markdown(f'<h2 style="color: #ffffff; margin: 0; text-align: center; text-shadow: 0 0 10px rgba(251, 191, 36, 0.4);">{global_state["hype_score"]}</h2>', unsafe_allow_html=True)
        h_col1, h_col2, h_col3 = st.columns(3)
        def add_hype(pts):
            global_state["hype_score"] += pts
            if st.session_state.fan_name:
                global_state["leaderboard"][st.session_state.fan_name] = global_state["leaderboard"].get(st.session_state.fan_name, 0) + pts
            st.rerun()

        if h_col1.button("🔥", key="btn_fire"): add_hype(5)
        if h_col2.button("👏", key="btn_clap"): add_hype(2)
        if h_col3.button("😱", key="btn_shock"): add_hype(3)

    # GROUP 3: LIVE POLL (Only show when match is live)
    if state == "in":
        with st.container(border=True):
            st.markdown('<h4 style="color: #fbbf24; margin-bottom: 5px;">🗳️ Next Wicket Guess?</h4>', unsafe_allow_html=True)
            st.markdown('<p style="color: #f8fafc; font-size: 11px; font-weight: 600;">Predict which team loses the next wicket.</p>', unsafe_allow_html=True)
            p_opt = st.radio("Who goes next?", [insights['team1'], insights['team2']], key="poll_radio", horizontal=True)
            if st.button("Vote Now", key="vote_btn", use_container_width=True):
                global_state["poll_votes"][p_opt] = global_state["poll_votes"].get(p_opt, 0) + 1
                st.toast(f"Voted for {p_opt}!")
                st.rerun()
            
            t1_v = global_state["poll_votes"].get(insights['team1'], 0)
            t2_v = global_state["poll_votes"].get(insights['team2'], 0)
            total = t1_v + t2_v
            st.progress(t1_v / total if total > 0 else 0.5)
            st.markdown(f'<p style="font-size: 11px; font-weight: bold; margin-top: 5px;">Fan Sentiment: {insights["team1"]} ({t1_v}) vs {insights["team2"]} ({t2_v})</p>', unsafe_allow_html=True)
    elif state == "pre":
        with st.container(border=True):
            st.markdown('<h4 style="color: #fbbf24; margin-bottom: 5px;">🗳️ Match Prediction</h4>', unsafe_allow_html=True)
            st.markdown('<p style="color: #f8fafc; font-size: 11px; font-weight: 600;">Who will win today?</p>', unsafe_allow_html=True)
            p_opt = st.radio("Pick a winner", [insights['team1'], insights['team2']], key="pre_poll_radio", horizontal=True)
            if st.button("Vote Now", key="pre_vote_btn", use_container_width=True):
                global_state["poll_votes"][p_opt] = global_state["poll_votes"].get(p_opt, 0) + 1
                st.toast(f"Voted for {p_opt}!")
                st.rerun()

    # GROUP 4: PREDICTIONS & AI
    with st.container(border=True):
        st.markdown('<h4 style="margin-bottom: 5px; color: #fbbf24;">🎯 Beat the AI</h4>', unsafe_allow_html=True)
        st.markdown('<p style="font-size: 11px; color: #f8fafc; font-weight: 600; margin-bottom: 10px;">Enter your predicted final score!</p>', unsafe_allow_html=True)
        user_pred = st.number_input("Your Prediction:", min_value=0, max_value=500, value=180, key="pred_in")
        if st.button("Submit Prediction", key="sub_btn", use_container_width=True):
            st.session_state.user_prediction = user_pred; st.success(f"Recorded: {user_pred}!")

        # Unified AI Win Prob & Pressure Index
        try:
            # Check which score has the 'target'
            s1, s2 = insights.get("score1", ""), insights.get("score2", "")
            target_score = s1 if "target" in s1 else s2 if "target" in s2 else None
            active_score = s2 if "target" in s2 else s1 # The team currently chasing
            
            if target_score and "(" in active_score:
                # Calculate Win Prob
                target = int(target_score.split("target")[1].strip().replace(")", ""))
                runs = int(active_score.split("/")[0])
                needed = target - runs
                win_prob = 100 if needed <= 0 else 85 if needed <= 10 else 55 if needed <= 40 else 30
                
                # Calculate Pressure
                overs_val = float(active_score.split("(")[1].split(" ")[0])
                rrr = needed / (20.0 - overs_val) if overs_val < 20 else 0
                pressure = min(100, rrr * 8)

                st.markdown(f"""
                <div style="margin-top: 15px; border-top: 1px solid rgba(255, 255, 255, 0.1); padding-top: 10px;">
                    <h4 style="margin-bottom: 5px; color: #fbbf24;">🤖 AI Win Probability</h4>
                    <p style="font-size: 10px; color: #f8fafc; font-weight: 600; margin-bottom: 10px;">Pressure: {pressure:.1f}%% | Req. Rate: {rrr:.2f}</p>
                    <div style="display: flex; justify-content: space-between; font-size: 11px; color: #ffffff; font-weight: bold;"><span>{insights['team2_short']}</span><span>{win_prob}%%</span></div>
                    <div style="background-color: rgba(255, 255, 255, 0.05); border-radius: 10px; height: 6px; overflow: hidden;"><div style="background-color: #fbbf24; width: {win_prob}%%; height: 100%; box-shadow: 0 0 10px rgba(251, 191, 36, 0.5);"></div></div>
                </div>""", unsafe_allow_html=True)
            else:
                st.info("AI Win Probability will activate as the chase intensifies.")
        except: pass

# 🔄 Auto Refresh Logic
if auto_refresh:
    time.sleep(15)
    st.rerun()