import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import json
from gamification_engine import GamificationEngine
from ai_components import AIComponents
from live_interaction import LiveInteractionManager

# Set page configuration
st.set_page_config(
    page_title="Event & Webinar Engagement Booster", 
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern gradient theme and cards (no logic changes)
st.markdown("""
<style>
    :root {
        --gradient-start: #6a11cb;
        --gradient-end: #2575fc;
        --bg-light: #f6f7fb;
        --card-bg: #ffffff;
        --text-main: #0f172a;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--gradient-start) 0%, var(--gradient-end) 100%) !important;
        color: #ffffff !important;
        padding-top: 25px;
        padding-right: 10px;
    }
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    /* Sidebar radio as tile-like menu */
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] {
        gap: 0px !important;
    }
    /* Hide the radio group label (e.g., "Choose a section:") only in sidebar */
    [data-testid="stSidebar"] .stRadio [data-testid="stWidgetLabel"] {
        display: none !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] > label,
    [data-testid="stSidebar"] div[role="radiogroup"] > div[role="radio"] {
        display: flex;
        align-items: center;
        gap: 12px;
        background: rgba(255,255,255,0.10);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        padding: 14px 18px;
        margin: 8px 0;
        border-radius: 12px;
        overflow: hidden;
        position: relative;
        cursor: pointer;
        transition: background 0.3s ease, box-shadow 0.3s ease, transform 0.25s ease;
        font-weight: 600;
        color: #ffffff;
        font-size: 15px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.20);
        border: 1px solid rgba(255,255,255,0.22);
        border-left: 4px solid transparent;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] > label:hover,
    [data-testid="stSidebar"] div[role="radiogroup"] > div[role="radio"]:hover {
        background: rgba(255,255,255,0.25);
        box-shadow: 0 0 12px rgba(255,255,255,0.40), 0 8px 18px rgba(0,0,0,0.28);
        transform: translateX(4px);
    }
    /* Selected/active option */
    [data-testid="stSidebar"] div[role="radiogroup"] > label[aria-checked="true"],
    [data-testid="stSidebar"] div[role="radiogroup"] > div[role="radio"][aria-checked="true"],
    [data-testid="stSidebar"] div[role="radiogroup"] > label[selected="true"],
    [data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {
        background: #ffffff !important;
        color: #6a11cb !important;
        font-weight: 800;
        box-shadow: 0 4px 15px rgba(0,0,0,0.35);
        border-color: rgba(106,17,203,0.35);
        box-shadow: inset 6px 0 0 #ff9800, 0 4px 15px rgba(0,0,0,0.35);
    }
    /* Propagate selected color to inner elements for reliability */
    [data-testid="stSidebar"] div[role="radiogroup"] > label[aria-checked="true"] *,
    [data-testid="stSidebar"] div[role="radiogroup"] > div[role="radio"][aria-checked="true"] *,
    [data-testid="stSidebar"] div[role="radiogroup"] > label[selected="true"] *,
    [data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) * {
        color: #6a11cb !important;
    }
    /* Hide the default radio circle (various DOM variants) */
    [data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child,
    [data-testid="stSidebar"] div[role="radiogroup"] > div[role="radio"] > div:first-child {
        display: none !important;
    }
    /* Hide native radio inputs for a cleaner tile look */
    [data-testid="stSidebar"] div[role="radiogroup"] input[type="radio"] {
        display: none;
    }

    /* Category headings using pseudo-elements (indexes map to your menu order) */
    [data-testid="stSidebar"] div[role="radiogroup"] > label:nth-of-type(1)::before,
    [data-testid="stSidebar"] div[role="radiogroup"] > div[role="radio"]:nth-of-type(1)::before {
        content: 'Overview';
        display: block;
        margin: 18px 4px 6px 4px;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: rgba(106,229,255,0.95);
    }
    [data-testid="stSidebar"] div[role="radiogroup"] > label:nth-of-type(2)::before,
    [data-testid="stSidebar"] div[role="radiogroup"] > div[role="radio"]:nth-of-type(2)::before {
        content: 'Engagement';
        display: block;
        margin: 18px 4px 6px 4px;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: rgba(106,229,255,0.95);
    }
    [data-testid="stSidebar"] div[role="radiogroup"] > label:nth-of-type(6)::before,
    [data-testid="stSidebar"] div[role="radiogroup"] > div[role="radio"]:nth-of-type(6)::before {
        content: 'Analytics';
        display: block;
        margin: 18px 4px 6px 4px;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: rgba(106,229,255,0.95);
    }

    /* App background */
    .stApp {
        background: linear-gradient(180deg, #f8f9fb 0%, #eef1f8 100%);
    }

    /* Gradient header bar */
    .main-header {
        font-size: 2rem;
        background: linear-gradient(90deg, var(--gradient-start), var(--gradient-end));
        color: #ffffff !important;
        text-align: center;
        padding: 18px 24px;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 22px rgba(37, 117, 252, 0.25);
    }

    /* Metric widgets as cards */
    div[data-testid="stMetric"] {
        background: var(--card-bg);
        border-radius: 16px;
        padding: 16px 14px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.08);
        border: 1px solid rgba(106,17,203,0.10);
        margin-bottom: 10px;
    }
    div[data-testid="stMetricLabel"] > div {
        color: #475569 !important;
        font-weight: 600;
    }
    div[data-testid="stMetricValue"] > div {
        background: linear-gradient(90deg, var(--gradient-start), var(--gradient-end));
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        font-weight: 800;
    }

    /* Generic card */
    .metric-card {
        padding: 20px;
        border-radius: 16px;
        background: var(--card-bg);
        box-shadow: 0 10px 24px rgba(0,0,0,0.08);
        border: 1px solid rgba(106,17,203,0.12);
        margin: 10px 0;
        text-align: left;
    }
    .metric-title {
        font-size: 16px;
        font-weight: 700;
        color: #334155;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 28px;
        font-weight: 800;
        background: linear-gradient(90deg, var(--gradient-start), var(--gradient-end));
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
    }

    /* Themed cards used across the app */
    .reminder-card, .success-card, .warning-card {
        padding: 16px 18px;
        border-radius: 14px;
        color: var(--text-main);
        margin: 10px 0;
        box-shadow: 0 8px 20px rgba(0,0,0,0.08);
        border: 1px solid rgba(0,0,0,0.05);
    }
    .reminder-card {
        background: linear-gradient(145deg, #e9f0ff 0%, #f1f4ff 100%);
        border-left: 6px solid #4c6fff;
    }
    .success-card {
        background: linear-gradient(145deg, #d4edda 0%, #e9f8ef 100%);
        border-left: 6px solid #2ecc71;
    }
    .warning-card {
        background: linear-gradient(145deg, #fff3cd 0%, #fff7df 100%);
        border-left: 6px solid #f1c40f;
    }

    /* Buttons */
    div.stButton > button {
        background: linear-gradient(90deg, var(--gradient-start), var(--gradient-end));
        color: #ffffff;
        border: none;
        border-radius: 12px;
        padding: 0.5rem 1rem;
        box-shadow: 0 8px 18px rgba(37,117,252,0.35);
    }
    div.stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 10px 22px rgba(37,117,252,0.45);
    }

    /* Tabs */
    [data-testid="stTabs"] button[role="tab"] {
        border-radius: 12px 12px 0 0;
        padding: 8px 14px;
        font-weight: 600;
    }

    /* DataFrame & Plotly containers */
    div[data-testid="stDataFrame"] {
        background: var(--card-bg);
        border-radius: 12px;
        padding: 8px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.06);
        border: 1px solid rgba(106,17,203,0.08);
    }
    div[data-testid="stPlotlyChart"] {
        background: var(--card-bg);
        border-radius: 14px;
        padding: 10px;
        box-shadow: 0 10px 24px rgba(0,0,0,0.06);
        border: 1px solid rgba(106,17,203,0.08);
    }

    /* Layout tweaks */
    .block-container {
        padding-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("attendees.csv")
        return df
    except FileNotFoundError:
        st.error("❌ attendees.csv file not found. Please make sure the file exists in the project directory.")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.stop()

# Helper: attendee names with 'Taniya' prioritized first
def get_attendee_names_priority(priority="Taniya"):
    names = df["Name"].tolist() if not df.empty else []
    if priority in names:
        return [priority] + [n for n in names if n != priority]
    return names

# Title
st.markdown('<h1 class="main-header">🎤 Event & Webinar Engagement Booster</h1>', unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.title("🧭 Navigation")
menu = st.sidebar.radio(
    "Choose a section:",
    ["📊 Dashboard", "🎮 Pre-Event Gamification", "⚡ Live Event Control", "📧 Pre-Event Reminders", "🙏 Post-Event Follow-ups", "💡 Insights & Analytics", "🔍 Search & Filter"]
)

# Dashboard
if menu == "📊 Dashboard":
    st.header("📊 Event Dashboard Overview")
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_attendees = len(df)
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg,#6a11cb 0%,#2575fc 100%); color: white;">
            <div class="metric-title" style="color: rgba(255,255,255,0.9);">👥 Total Registered</div>
            <div class="metric-value" style="background:none !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff;">{total_attendees}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        attended_count = len(df[df['Attended'] == 'Yes'])
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg,#16a34a 0%, #22c55e 100%); color: white;">
            <div class="metric-title" style="color: rgba(255,255,255,0.92);">✅ Attended</div>
            <div class="metric-value" style="background:none !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff;">{attended_count}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        attendance_rate = (attended_count / total_attendees * 100) if total_attendees > 0 else 0
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg,#f59e0b 0%, #fbbf24 100%); color: #1f2937;">
            <div class="metric-title" style="color: rgba(31,41,55,0.95);">📈 Attendance Rate</div>
            <div class="metric-value" style="background:none !important; color:#111827 !important; -webkit-text-fill-color:#111827;">{attendance_rate:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        total_events = df['Registered_Event'].nunique()
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg,#06b6d4 0%, #3b82f6 100%); color: white;">
            <div class="metric-title" style="color: rgba(255,255,255,0.92);">🎯 Total Events</div>
            <div class="metric-value" style="background:none !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff;">{total_events}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Event Registration Summary
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Event Registration Summary")
        event_summary = df.groupby("Registered_Event").agg({
            'Name': 'count',
            'Attended': lambda x: (x == 'Yes').sum()
        }).rename(columns={'Name': 'Registered', 'Attended': 'Attended'})
        event_summary['Attendance_Rate'] = (event_summary['Attended'] / event_summary['Registered'] * 100).round(1)
        st.dataframe(event_summary, use_container_width=True)
    
    with col2:
        st.subheader("📊 Attendance Distribution")
        fig = px.pie(
            values=df['Attended'].value_counts().values,
            names=df['Attended'].value_counts().index,
            title="Overall Attendance Distribution",
            color_discrete_map={'Yes': '#28a745', 'No': '#dc3545'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Event-wise Attendance Chart
    st.subheader("📈 Event-wise Attendance Analysis")
    event_data = df.groupby(['Registered_Event', 'Attended']).size().unstack(fill_value=0)
    
    fig = px.bar(
        x=event_data.index,
        y=[event_data.get('Yes', 0), event_data.get('No', 0)],
        title="Attendance by Event",
        labels={'x': 'Events', 'y': 'Number of Attendees'},
        color_discrete_map={'Yes': '#28a745', 'No': '#dc3545'}
    )
    fig.update_layout(barmode='stack')
    st.plotly_chart(fig, use_container_width=True)

# Pre-Event Gamification
elif menu == "🎮 Pre-Event Gamification":
    st.header("🎮 Pre-Event Gamification & Engagement")

    # Instantiate engines
    engine = GamificationEngine()
    ai = AIComponents()

    # Helpers scoped to this section
    def load_events():
        try:
            events_df = pd.read_csv("events.csv")
            events_df["StartDateTime"] = pd.to_datetime(events_df["StartDateTime"])
            return events_df
        except Exception:
            return pd.DataFrame(columns=["Event", "StartDateTime"])

    def load_user_activities():
        data = {}
        try:
            with open("user_activities.json", "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}
        # Ensure every attendee has a record
        for _, r in df.iterrows():
            name = r["Name"]
            if name not in data:
                data[name] = {
                    "interests": r.get("Interests", ""),
                    "days_before_registration": 10,
                    "activities": {}
                }
        return data

    def save_user_activities(data):
        with open("user_activities.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    events_df = load_events()
    activities = load_user_activities()

    # Build interest options
    interest_set = set()
    for interests in df["Interests"]:
        for t in interests.split(";"):
            t = t.strip()
            if t:
                interest_set.add(t)
    interest_options = sorted(list(interest_set))

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "⏳ Countdown & Teasers", "🧠 Mini-Quiz & Poll", "🏆 Leaderboard & Badges", "🤝 Networking", "🤖 AI Targeting"
    ])

    # Tab 1: Countdown & Teasers
    with tab1:
        st.subheader("⏳ Countdown & Teasers")
        colA, colB = st.columns(2)
        with colA:
            attendee_name = st.selectbox("Select attendee:", get_attendee_names_priority(), key="teaser_attendee")
            attendee_row = df[df["Name"] == attendee_name].iloc[0]
        with colB:
            available_events = events_df["Event"].tolist() if not events_df.empty else []
            default_event = attendee_row["Registered_Event"] if attendee_row["Registered_Event"] in available_events else (available_events[0] if available_events else None)
            selected_event = st.selectbox("Select event:", available_events if available_events else ["No events configured"], index=available_events.index(default_event) if available_events and default_event in available_events else 0)

        if events_df.empty:
            st.warning("No events found. Please ensure `events.csv` exists with columns `Event, StartDateTime`.")
        else:
            start_dt = events_df.loc[events_df["Event"] == selected_event, "StartDateTime"].iloc[0]
            now_dt = datetime.now()
            delta = start_dt - now_dt
            days = max(delta.days, 0)
            hours = max((delta.seconds // 3600) % 24, 0)
            minutes = max((delta.seconds // 60) % 60, 0)
            c1, c2, c3 = st.columns(3)
            c1.metric("Days", days)
            c2.metric("Hours", hours)
            c3.metric("Minutes", minutes)

        # Personalized teaser / fun fact
        teaser = engine.generate_personalized_teaser({"interests": attendee_row["Interests"]}, {"event": selected_event})
        st.info(f"Teaser for {attendee_name}: {teaser}")

        st.divider()
        st.subheader("🗳️ Quick Pre-Event Poll")
        poll_q = "Which part are you most excited about?"
        poll_opts = ["Keynote", "Hands-on demo", "Q&A", "Case studies"]
        poll_choice = st.radio(poll_q, poll_opts, key=f"pre_poll_{attendee_name}")
        if st.button("Submit Poll Response", key=f"submit_pre_poll_{attendee_name}"):
            # Track participation for attendee
            user_act = activities.get(attendee_name, {}).get("activities", {})
            user_act["poll_participation"] = user_act.get("poll_participation", 0) + 1
            activities[attendee_name]["activities"] = user_act
            save_user_activities(activities)
            st.success("Poll response recorded and points updated!")

    # Tab 2: Mini-Quiz
    with tab2:
        st.subheader("🧠 Mini-Quiz")
        quiz_attendee = st.selectbox("Select attendee:", get_attendee_names_priority(), key="quiz_attendee")
        # Topic defaults to attendee's first interest
        default_topic = df[df["Name"] == quiz_attendee]["Interests"].iloc[0].split(";")[0]
        quiz_topic = st.selectbox("Select quiz topic:", interest_options or [default_topic], index=(interest_options.index(default_topic) if default_topic in interest_options else 0))
        quiz_difficulty = st.selectbox("Difficulty:", ["easy", "medium", "hard"], index=1)

        questions = engine.generate_quiz_questions(quiz_topic, difficulty=quiz_difficulty)[:3]
        with st.form(key=f"quiz_form_{quiz_attendee}"):
            selections = []
            for i, q in enumerate(questions):
                st.write(f"Q{i+1}. {q['question']}")
                choice = st.radio("", q["options"], key=f"q_{quiz_attendee}_{i}")
                selections.append(q["options"].index(choice))
                st.write("")
            submitted = st.form_submit_button("Submit Quiz")
        if submitted:
            correct = 0
            for i, q in enumerate(questions):
                if selections[i] == q["correct"]:
                    correct += 1
            score_ratio = correct / max(len(questions), 1)
            # Update activities
            ua = activities.get(quiz_attendee, {}).get("activities", {})
            prev_attempts = ua.get("pre_event_quiz", 0)
            prev_avg = ua.get("quiz_scores", 0)
            new_avg = round(((prev_avg * prev_attempts) + score_ratio) / (prev_attempts + 1), 2)
            ua["pre_event_quiz"] = prev_attempts + 1
            ua["quiz_scores"] = new_avg
            activities[quiz_attendee]["activities"] = ua
            save_user_activities(activities)
            st.success(f"You scored {correct}/{len(questions)}. Points awarded!")

    # Tab 3: Leaderboard & Badges
    with tab3:
        st.subheader("🏆 Leaderboard & Badges")
        users_data = {}
        for name, data in activities.items():
            users_data[name] = {
                "interests": data.get("interests", ""),
                "days_before_registration": data.get("days_before_registration", 10),
                "activities": data.get("activities", {})
            }
        leaderboard = engine.create_leaderboard(users_data)
        if leaderboard:
            # Prepare display
            lb_df = pd.DataFrame([{
                "Name": item["name"],
                "Points": item["points"],
                "Badges": ", ".join(engine.badges[b]["name"] for b in item["badges"]) if item.get("badges") else "-"
            } for item in leaderboard])
            st.dataframe(lb_df, use_container_width=True)
        else:
            st.info("No leaderboard data yet. Complete quizzes or polls to earn points.")

        st.divider()
        st.subheader("🔓 Unlockable Content")
        unlock_attendee = st.selectbox("Select attendee:", get_attendee_names_priority(), key="unlock_attendee")
        ua2 = activities.get(unlock_attendee, {}).get("activities", {})
        user_points = engine.calculate_user_points({"activities": ua2})
        threshold = 50
        if user_points >= threshold:
            st.success("Unlocked: Exclusive Pre-Event Guide (sample)")
            st.download_button("📥 Download Guide", "Congratulations! Here's your exclusive pre-event guide.", file_name=f"guide_{unlock_attendee}.txt")
        else:
            st.warning(f"Earn {threshold - user_points} more points to unlock exclusive content.")

    # Tab 4: Networking
    with tab4:
        st.subheader("🤝 Pre-event Networking Suggestions")
        net_attendee = st.selectbox("Select attendee:", get_attendee_names_priority(), key="network_attendee")
        user_interests = df[df["Name"] == net_attendee]["Interests"].iloc[0]
        all_users = {name: {"interests": data.get("interests", "")} for name, data in activities.items() if name != net_attendee}
        suggestions = engine.suggest_connections(user_interests, all_users)
        if suggestions:
            for s in suggestions:
                st.write(f"- {s['name']} | Common: {', '.join(s['common_interests'])} | Match: {round(s['match_score']*100)}%")
        else:
            st.info("No strong matches found yet.")

    # Tab 5: AI Targeting
    with tab5:
        st.subheader("🤖 Predict Likely Engaging Attendees")
        rows = []
        for _, row in df.iterrows():
            name = row["Name"]
            acts = activities.get(name, {}).get("activities", {})
            feats = {
                "days_since_registration": 10,
                "previous_events_attended": acts.get("event_attendance", 0),
                "quiz_completion_rate": min(1.0, acts.get("pre_event_quiz", 0) / 5) if acts else 0,
                "social_shares": acts.get("social_share", 0),
                "interests": row.get("Interests", "")
            }
            score = ai.predict_engagement(feats)
            rows.append({"Name": name, "Predicted_Engagement": round(score, 2)})
        if rows:
            pe_df = pd.DataFrame(rows).sort_values("Predicted_Engagement", ascending=False)
            st.dataframe(pe_df, use_container_width=True)

            st.subheader("🎯 Personalized Teasers & Challenges (Top 5)")
            top5 = pe_df.head(5)["Name"].tolist()
            for nm in top5:
                interests = df[df["Name"] == nm]["Interests"].iloc[0]
                teaser_msg = engine.generate_personalized_teaser({"interests": interests}, {})
                challenge = "Complete a mini-quiz today (+15 pts) • Share this event on social (+10 pts)"
                st.write(f"- {nm}: {teaser_msg} | Challenge: {challenge}")
        else:
            st.info("No attendees available for prediction.")

# Live Event Control
elif menu == "⚡ Live Event Control":
    st.header("⚡ Live Event Control")

    # Initialize manager in session state
    if "live_mgr" not in st.session_state:
        st.session_state.live_mgr = LiveInteractionManager()
    mgr: LiveInteractionManager = st.session_state.live_mgr
    ai_live = AIComponents()

    polls_tab, qa_tab, engagement_tab, chat_tab, insights_tab = st.tabs([
        "🗳️ Polls", "❓ Q&A", "🔥 Engagement", "💬 Chat", "📊 Insights"
    ])

    # Polls
    with polls_tab:
        st.subheader("Create Poll")
        q = st.text_input("Question", key="poll_q")
        opts_text = st.text_area("Options (one per line)", key="poll_opts")
        if st.button("Create Poll", key="create_poll"):
            options = [o.strip() for o in (opts_text or "").splitlines() if o.strip()]
            if q and len(options) >= 2:
                pid = mgr.create_poll(q, options, poll_type='multiple_choice')
                st.success(f"Poll created: {pid}")
            else:
                st.warning("Please enter a question and at least two options.")

        if mgr.active_polls:
            st.subheader("Vote & Results")
            poll_ids = list(mgr.active_polls.keys())
            selected_pid = st.selectbox("Select poll:", poll_ids, key="active_poll_sel")
            poll = mgr.active_polls[selected_pid]
            st.write(f"Q: {poll['question']}")
            voter = st.selectbox("Participant:", get_attendee_names_priority(), key="poll_voter")
            voter_segment = df[df['Name'] == voter]['Interests'].iloc[0].split(';')[0]
            choice = st.radio("Choose an option", poll['options'], key=f"vote_choice_{selected_pid}")
            if st.button("Submit Response", key=f"vote_submit_{selected_pid}"):
                if mgr.submit_poll_response(selected_pid, choice, user_segment=voter_segment):
                    mgr.track_engagement_event(voter, 'poll_response', {'user_segment': voter_segment})
                    st.success("Vote recorded")
            results = mgr.get_poll_results(selected_pid, show_segments=True)
            if results:
                res_df = pd.DataFrame({
                    'Option': list(results['responses'].keys()),
                    'Votes': list(results['responses'].values())
                })
                fig = px.bar(res_df, x='Option', y='Votes', title='Poll Results')
                st.plotly_chart(fig, use_container_width=True)
                if 'segments' in results and results['segments']:
                    st.subheader("Segmented Results")
                    st.json(results['segments'])
        else:
            st.info("No active polls yet.")

    # Q&A
    with qa_tab:
        st.subheader("Ask a Question")
        asker = st.selectbox("Attendee:", get_attendee_names_priority(), key="qa_asker")
        question = st.text_input("Your question", key="qa_question")
        priority = st.selectbox("Priority:", ["low", "normal", "high"], index=1, key="qa_priority")
        if st.button("Submit Question", key="qa_submit"):
            seg = df[df['Name'] == asker]['Interests'].iloc[0].split(';')[0]
            qa_id = mgr.add_qa_question(question, asker, user_segment=seg, priority=priority)
            mgr.track_engagement_event(asker, 'question', {'user_segment': seg})
            st.success(f"Added to Q&A as {qa_id}")

        st.subheader("Queue")
        sort_by = st.selectbox("Sort by:", ["votes", "time", "priority"], key="qa_sort")
        queue = mgr.get_qa_queue(sort_by=sort_by)
        for item in queue:
            st.markdown(f"**{item['user_name']}**: {item['question']} | Votes: {item['votes']} | Status: {item['status']}")
            c1, c2, c3 = st.columns(3)
            if c1.button("👍 Upvote", key=f"qa_up_{item['id']}"):
                mgr.vote_qa_question(item['id'])
                st.experimental_rerun()
            if c2.button("🤖 AI Answer", key=f"qa_ai_{item['id']}"):
                resp = ai_live.generate_smart_qa_response(item['question'])
                mgr.answer_qa_question(item['id'], resp['response'])
                st.info(f"AI: {resp['response']} (confidence {resp['confidence']})")
                if resp['needs_human']:
                    st.warning("Flagged for human follow-up")
            if c3.button("Mark Answered", key=f"qa_ans_{item['id']}"):
                mgr.answer_qa_question(item['id'], item.get('answer') or 'Answered live')
            if item.get('answer'):
                st.success(f"Answer: {item['answer']}")

    # Engagement
    with engagement_tab:
        st.subheader("Real-time Engagement")
        eng_user = st.selectbox("User:", get_attendee_names_priority(), key="eng_user")
        event_type = st.selectbox("Event type:", ['click', 'poll_response', 'question', 'chat', 'reaction', 'share'], key="eng_type")
        if st.button("Record Event", key="eng_record"):
            seg = df[df['Name'] == eng_user]['Interests'].iloc[0].split(';')[0]
            mgr.track_engagement_event(eng_user, event_type, {'user_segment': seg})
            st.success("Event recorded")
        score = mgr.calculate_engagement_score()
        st.metric("Engagement Score (last 5 min)", round(score, 2))
        heat = mgr.generate_engagement_heatmap()
        if heat:
            heat_df = pd.DataFrame(heat)
            fig = px.bar(heat_df, x='time_slot', y='total_events', title='Engagement Over Time')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No engagement data yet.")

    # Chat
    with chat_tab:
        st.subheader("Live Chat")
        chat_user = st.selectbox("User:", get_attendee_names_priority(), key="chat_user")
        msg = st.text_input("Message", key="chat_msg")
        if st.button("Send", key="chat_send"):
            seg = df[df['Name'] == chat_user]['Interests'].iloc[0].split(';')[0]
            mid = mgr.add_chat_message(chat_user, msg, user_segment=seg)
            st.success(f"Message sent ({mid})")
        messages = mgr.get_chat_messages(limit=30)
        for m in messages:
            st.markdown(f"**{m['user_name']}** [{m['timestamp'].strftime('%H:%M:%S')}]: {m['message']}")
            c1, c2, c3 = st.columns(3)
            if c1.button("👍", key=f"react_up_{m['id']}"):
                mgr.add_reaction_to_message(m['id'], '👍', chat_user)
            if c2.button("❤️", key=f"react_heart_{m['id']}"):
                mgr.add_reaction_to_message(m['id'], '❤️', chat_user)
            if c3.button("😂", key=f"react_lol_{m['id']}"):
                mgr.add_reaction_to_message(m['id'], '😂', chat_user)

    # Insights
    with insights_tab:
        st.subheader("Live Insights")
        ins = mgr.get_live_insights()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Engagement Score", round(ins.get('current_engagement_score', 0), 2))
        c2.metric("Active Polls", ins.get('total_active_polls', 0))
        c3.metric("Total Questions", ins.get('total_questions', 0))
        c4.metric("Pending Questions", ins.get('pending_questions', 0))
        c5, c6 = st.columns(2)
        c5.metric("Unique Participants", ins.get('unique_participants', 0))
        c6.write(f"Trend: {ins.get('engagement_trend', 'stable')}")
        if ins.get('top_question'):
            st.info(f"Top Q: {ins['top_question']['question']} (votes {ins['top_question']['votes']})")
        if ins.get('most_active_segment'):
            seg, cnt = ins['most_active_segment']
            st.success(f"Most Active Segment: {seg} ({cnt} events)")
        st.download_button(
            "📦 Export Session Data",
            data=json.dumps(mgr.export_session_data(), default=str, indent=2),
            file_name="live_session_data.json"
        )

# Pre-Event Reminders
elif menu == "📧 Pre-Event Reminders":
    st.header("📧 Personalized Pre-Event Reminders")
    
    st.info("💡 **Tip:** These are personalized reminder templates based on attendee interests and registered events.")
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        selected_event = st.selectbox("Filter by Event:", ["All Events"] + list(df['Registered_Event'].unique()))
    with col2:
        reminder_type = st.selectbox("Reminder Type:", ["Standard", "Personalized", "Last Chance"])
    
    # Generate reminders
    filtered_df = df if selected_event == "All Events" else df[df['Registered_Event'] == selected_event]
    
    for _, row in filtered_df.iterrows():
        with st.container():
            st.markdown(f"""
            <div class="reminder-card">
                <h4>📧 To: {row['Name']} ({row['Email']})</h4>
                <p><strong>Event:</strong> {row['Registered_Event']}</p>
                <p><strong>Interests:</strong> {row['Interests']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if reminder_type == "Standard":
                st.info(f"""
                **Subject:** Don't miss your upcoming event: {row['Registered_Event']} 🎯
                
                Hi {row['Name']} 👋
                
                This is a friendly reminder about your upcoming event **{row['Registered_Event']}** tomorrow!
                
                We're excited to see you there. Don't forget to bring your enthusiasm! 🚀
                
                Best regards,
                Event Team
                """)
            elif reminder_type == "Personalized":
                interests_list = row['Interests'].split(';')
                st.success(f"""
                **Subject:** Your {row['Registered_Event']} event is tomorrow - Perfect for your {interests_list[0]} interests! 🎯
                
                Hi {row['Name']} 👋
                
                We noticed you're interested in **{row['Interests']}** - that's perfect! 
                
                Tomorrow's **{row['Registered_Event']}** will dive deep into topics you love. 
                
                See you there! 🚀
                
                Best regards,
                Event Team
                """)
            else:  # Last Chance
                st.warning(f"""
                **Subject:** ⏰ Last chance to join {row['Registered_Event']} - Starting in 2 hours!
                
                Hi {row['Name']} 👋
                
                **{row['Registered_Event']}** starts in just 2 hours!
                
                Don't miss out on this amazing opportunity. Join us now! ⚡
                
                Quick access link: [Join Event] 🔗
                
                Best regards,
                Event Team
                """)
            
            # Download button for each reminder
            reminder_content = f"To: {row['Name']} ({row['Email']})\nEvent: {row['Registered_Event']}\nInterests: {row['Interests']}\n\nReminder sent successfully!"
            st.download_button(
                f"📥 Download Reminder for {row['Name']}", 
                reminder_content, 
                f"reminder_{row['Name'].replace(' ', '_')}.txt",
                key=f"reminder_{row['Name']}"
            )
            
            st.divider()

# Post-Event Follow-ups
elif menu == "🙏 Post-Event Follow-ups":
    st.header("🙏 Post-Event Follow-up Messages")
    
    st.info("💡 **Tip:** Automated follow-up messages based on attendance status.")
    
    # Helpers
    def _load_user_activities_po():
        try:
            with open("user_activities.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    engine_po = GamificationEngine()
    ai_po = AIComponents()
    activities_po = _load_user_activities_po()
    
    # Tabs for different follow-up types
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["✅ Attendees", "❌ No-shows", "📊 All Participants", "🎯 Next Steps", "🚨 Churn Alerts", "📣 Social Sharing"])
    
    with tab1:
        st.subheader("Thank You Messages for Attendees")
        attendees = df[df['Attended'] == 'Yes']
        
        for _, row in attendees.iterrows():
            st.markdown(f"""
            <div class="success-card">
                <h4>✅ {row['Name']} - Attended {row['Registered_Event']}</h4>
            </div>
            """, unsafe_allow_html=True)
            
            st.success(f"""
            **Subject:** Thank you for attending {row['Registered_Event']}! 🎉
            
            Hi {row['Name']} 👋
            
            Thank you for attending **{row['Registered_Event']}**! We hope you found it valuable.
            
            📎 **Resources for you:**
            - Event slides and presentation materials
            - Recording link (available for 30 days)
            - Additional resources related to {row['Interests']}
            - Certificate of attendance
            
            🔔 **What's next?**
            Based on your interests in {row['Interests']}, you might like our upcoming events!
            
            Stay connected! 🚀
            
            Best regards,
            Event Team
            """)
            st.divider()
    
    with tab2:
        st.subheader("Re-engagement Messages for No-shows")
        no_shows = df[df['Attended'] == 'No']
        
        for _, row in no_shows.iterrows():
            st.markdown(f"""
            <div class="warning-card">
                <h4>❌ {row['Name']} - Missed {row['Registered_Event']}</h4>
            </div>
            """, unsafe_allow_html=True)
            
            st.warning(f"""
            **Subject:** We missed you at {row['Registered_Event']} - Here's what you missed! 📚
            
            Hi {row['Name']} 👋
            
            We noticed you couldn't make it to **{row['Registered_Event']}**. No worries - we've got you covered!
            
            📎 **What you missed:**
            - Key takeaways and highlights
            - Full event recording
            - Presentation slides
            - Q&A session summary
            
            🎯 **Special offer:**
            Since you're interested in {row['Interests']}, we'd love to offer you priority access to our next related event!
            
            Hope to see you next time! 🚀
            
            Best regards,
            Event Team
            """)
            st.divider()
    
    with tab3:
        st.subheader("📊 Follow-up Summary")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("✅ Thank You Messages", len(df[df['Attended'] == 'Yes']))
        with col2:
            st.metric("🔄 Re-engagement Messages", len(df[df['Attended'] == 'No']))
        
        # Bulk download option
        all_followups = ""
        for _, row in df.iterrows():
            status = "Attended" if row['Attended'] == 'Yes' else "No-show"
            all_followups += f"Name: {row['Name']}\nEmail: {row['Email']}\nEvent: {row['Registered_Event']}\nStatus: {status}\n\n"
        
        st.download_button(
            "📥 Download All Follow-ups",
            all_followups,
            "all_followups.txt"
        )

    # Next-Step Suggestions
    with tab4:
        st.subheader("🎯 Next-Step Suggestions")
        # Simple content catalog
        available_content = [
            {"title": "Advanced AI Workshop", "description": "Deep dive into ML and AI ops for builders"},
            {"title": "Cloud Cost Optimization", "description": "Practical steps to reduce cloud bills"},
            {"title": "SaaS Growth Playbook", "description": "Tactics for product-led growth"},
            {"title": "DevOps Bootcamp", "description": "CI/CD pipelines, GitOps, infra as code"},
            {"title": "Design Systems 101", "description": "Build consistent UI at scale"},
            {"title": "Blockchain for PMs", "description": "Product thinking for web3"}
        ]
        sel_att = st.selectbox("Select attendee:", get_attendee_names_priority(), key="ns_att")
        interests = df[df["Name"] == sel_att]["Interests"].iloc[0]
        recs = ai_po.recommend_content(interests, available_content)
        if recs:
            for r in recs:
                st.write(f"- {r['content']['title']} (match: {', '.join(r['match_reasons'])})")
        else:
            st.info("No strong recommendations found.")

    # Predictive Churn Alerts
    with tab5:
        st.subheader("🚨 Predictive Churn Alerts")
        rows = []
        for _, r in df.iterrows():
            name = r["Name"]
            acts = activities_po.get(name, {}).get("activities", {})
            points = engine_po.calculate_user_points({"activities": acts})
            engagement_score = min(points / 100.0, 1.0)
            attendance_rate = 1.0 if r.get("Attended", "No") == "Yes" else 0.0
            days_since_last_activity = 3 if (acts.get("pre_event_quiz", 0) > 0 or acts.get("poll_participation", 0) > 0) else 21
            risk = ai_po.predict_churn_risk({
                "days_since_last_activity": days_since_last_activity,
                "attendance_rate": attendance_rate,
                "engagement_score": engagement_score
            })
            rows.append({
                "Name": name,
                "Risk Level": risk["risk_level"],
                "Risk Score": round(risk["risk_score"], 2),
                "Top Action": risk["recommendations"][0] if risk.get("recommendations") else "-"
            })
        if rows:
            import pandas as _pd
            churn_df = _pd.DataFrame(rows).sort_values(["Risk Level", "Risk Score"], ascending=[False, False])
            st.dataframe(churn_df, use_container_width=True)
        else:
            st.info("No attendees available.")

    # Social Sharing Module
    with tab6:
        st.subheader("📣 Social Sharing")
        share_att = st.selectbox("Select attendee:", get_attendee_names_priority(), key="share_att")
        share_event = df[df["Name"] == share_att]["Registered_Event"].iloc[0]
        share_interest = df[df["Name"] == share_att]["Interests"].iloc[0].split(';')[0]
        quote = f"Loved today's {share_event}! The {share_interest} insights were 🔥 #webinar #learning"
        highlight = f"Top takeaway from {share_event}: Personalization drives outcomes."
        st.text_area("Shareable Post", quote, height=80)
        st.text_area("Highlight", highlight, height=80, key="hl_text")
        cert_text = f"Certificate of Participation\nThis certifies that {share_att} participated in {share_event}."
        st.download_button("📥 Download Certificate (text)", cert_text, file_name=f"certificate_{share_att}.txt")

# Insights & Analytics
elif menu == "💡 Insights & Analytics":
    st.header("💡 Attendee Insights & Analytics")
    
    # Interest Analysis
    st.subheader("🎯 Interest Categories Analysis")
    
    # Extract all interests
    all_interests = []
    for interests in df["Interests"]:
        all_interests.extend(interests.split(";"))
    
    interest_counts = pd.Series(all_interests).value_counts()
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(
            x=interest_counts.values,
            y=interest_counts.index,
            orientation='h',
            title="Popular Interest Categories",
            labels={'x': 'Number of Attendees', 'y': 'Interest Categories'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.pie(
            values=interest_counts.values,
            names=interest_counts.index,
            title="Interest Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Event Performance Analysis
    st.subheader("📈 Event Performance Metrics")
    
    event_performance = df.groupby('Registered_Event').agg({
        'Name': 'count',
        'Attended': lambda x: (x == 'Yes').sum()
    }).rename(columns={'Name': 'Total_Registered', 'Attended': 'Total_Attended'})
    
    event_performance['Attendance_Rate'] = (event_performance['Total_Attended'] / event_performance['Total_Registered'] * 100).round(2)
    event_performance['No_Shows'] = event_performance['Total_Registered'] - event_performance['Total_Attended']
    
    st.dataframe(event_performance, use_container_width=True)
    
    # Attendance Rate by Event
    fig = px.bar(
        x=event_performance.index,
        y=event_performance['Attendance_Rate'],
        title="Attendance Rate by Event (%)",
        labels={'x': 'Events', 'y': 'Attendance Rate (%)'},
        color=event_performance['Attendance_Rate'],
        color_continuous_scale='RdYlGn'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Recommendations
    st.subheader("🎯 Recommendations")
    
    best_event = event_performance['Attendance_Rate'].idxmax()
    worst_event = event_performance['Attendance_Rate'].idxmin()
    most_popular_interest = interest_counts.index[0]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.success(f"""
        **🏆 Best Performing Event**
        
        {best_event}
        
        Attendance Rate: {event_performance.loc[best_event, 'Attendance_Rate']:.1f}%
        """)
    
    with col2:
        st.warning(f"""
        **📉 Needs Improvement**
        
        {worst_event}
        
        Attendance Rate: {event_performance.loc[worst_event, 'Attendance_Rate']:.1f}%
        """)
    
    with col3:
        st.info(f"""
        **🎯 Most Popular Interest**
        
        {most_popular_interest}
        
        {interest_counts[most_popular_interest]} attendees interested
        """)

    st.divider()
    st.subheader("💵 ROI Prediction")
    ai_ins = AIComponents()
    # Inputs
    if not event_performance.empty:
        sel_event = st.selectbox("Event for ROI:", event_performance.index.tolist(), key="roi_event")
        default_costs = int(event_performance.loc[sel_event, 'Total_Registered'] * 10)
        conv_rate = st.slider("Assumed conversion rate", 0.0, 0.3, 0.05, 0.01)
        costs = st.number_input("Estimated costs ($)", min_value=0, value=default_costs, step=50)
        # Build engagement score from activities
        try:
            with open("user_activities.json", "r", encoding="utf-8") as f:
                acts_all = json.load(f)
        except Exception:
            acts_all = {}
        ev_attendees = df[df['Registered_Event'] == sel_event]['Name'].tolist()
        if ev_attendees:
            from gamification_engine import GamificationEngine as _GE
            _eng = _GE()
            pts = []
            for nm in ev_attendees:
                pts.append(_eng.calculate_user_points({"activities": acts_all.get(nm, {}).get("activities", {})}))
            avg_eng = (sum(min(p/100.0, 1.0) for p in pts) / len(ev_attendees)) if ev_attendees else 0
        else:
            avg_eng = 0
        edata = {
            'total_registrations': int(event_performance.loc[sel_event, 'Total_Registered']),
            'attendance_rate': float(event_performance.loc[sel_event, 'Attendance_Rate'])/100.0,
            'avg_engagement_score': float(avg_eng),
            'conversion_rate': float(conv_rate),
            'event_costs': int(costs)
        }
        roi = ai_ins.calculate_roi_prediction(edata)
        c1, c2, c3 = st.columns(3)
        c1.metric("Estimated Revenue", f"${int(roi['estimated_revenue'])}")
        c2.metric("Estimated Costs", f"${int(roi['estimated_costs'])}")
        c3.metric("ROI %", f"{roi['roi_percentage']:.1f}%")

    st.divider()
    st.subheader("🧩 AI Clustering (Attendees)")
    # Build attendee feature data from activities
    try:
        with open("user_activities.json", "r", encoding="utf-8") as f:
            acts_all2 = json.load(f)
    except Exception:
        acts_all2 = {}
    from gamification_engine import GamificationEngine as _GE2
    _eng2 = _GE2()
    attendee_data = {}
    for _, r in df.iterrows():
        name = r['Name']
        acts = acts_all2.get(name, {}).get('activities', {})
        points = _eng2.calculate_user_points({"activities": acts})
        attendee_data[name] = {
            'events_attended': 1 if r['Attended'] == 'Yes' else 0,
            'engagement_score': min(points/100.0, 1.0),
            'interests': r.get('Interests', ''),
            'social_shares': acts.get('social_share', 0),
            'quiz_scores': acts.get('quiz_scores', 0)
        }
    clusters = ai_ins.cluster_attendees(attendee_data)
    if clusters.get('clusters'):
        for cname, members in clusters['clusters'].items():
            st.write(f"**{cname}**: {', '.join(members)}")
    else:
        st.info("Not enough data to form clusters yet.")

# Search & Filter
elif menu == "🔍 Search & Filter":
    st.header("🔍 Search & Filter Attendees")
    
    # Search functionality
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_name = st.text_input("🔍 Search by Name:")
    with col2:
        filter_event = st.selectbox("Filter by Event:", ["All"] + list(df['Registered_Event'].unique()))
    with col3:
        filter_attendance = st.selectbox("Filter by Attendance:", ["All", "Yes", "No"])
    
    # Apply filters
    filtered_df = df.copy()
    
    if search_name:
        filtered_df = filtered_df[filtered_df['Name'].str.contains(search_name, case=False, na=False)]
    
    if filter_event != "All":
        filtered_df = filtered_df[filtered_df['Registered_Event'] == filter_event]
    
    if filter_attendance != "All":
        filtered_df = filtered_df[filtered_df['Attended'] == filter_attendance]
    
    # Display results
    st.subheader(f"📋 Search Results ({len(filtered_df)} found)")
    
    if not filtered_df.empty:
        # Display as cards
        for _, row in filtered_df.iterrows():
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                
                with col1:
                    st.write(f"**👤 {row['Name']}**")
                    st.write(f"📧 {row['Email']}")
                
                with col2:
                    st.write(f"🎯 **Event:** {row['Registered_Event']}")
                    st.write(f"💡 **Interests:** {row['Interests']}")
                
                with col3:
                    status_color = "🟢" if row['Attended'] == 'Yes' else "🔴"
                    st.write(f"**Attendance:** {status_color} {row['Attended']}")
                
                with col4:
                    if st.button(f"📧 Contact", key=f"contact_{row['Name']}"):
                        st.success(f"Opening email client for {row['Name']}")
                
                st.divider()
        
        # Export filtered results
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            "📥 Export Filtered Results",
            csv,
            "filtered_attendees.csv",
            "text/csv"
        )
    else:
        st.warning("No attendees found matching your search criteria.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>🎤 Event & Webinar Engagement Booster | Built with Streamlit</p>
    <p>💡 Boost your event engagement with personalized communications!</p>
</div>
""", unsafe_allow_html=True)