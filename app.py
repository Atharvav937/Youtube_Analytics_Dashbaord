import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from database import (
    create_tables,
    insert_channel,
    insert_videos,
    get_all_channels,
    get_videos_by_channel
)
from youtube_api import get_channel_details, get_video_details

# ─────────────────────────────────────────────
#  PAGE CONFIG & GLOBAL STYLES
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="YouTube Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

/* ── Light background ── */
.stApp {
    background: #f5f6fa;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #e8eaf0 !important;
    box-shadow: 2px 0 12px rgba(0,0,0,0.04);
}
[data-testid="stSidebar"] * {
    color: #2d3142 !important;
}
[data-testid="stSidebar"] hr {
    border-color: #e8eaf0 !important;
}

/* ── Metric Cards ── */
[data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 1.9rem !important;
    font-weight: 700 !important;
    color: #1a1d2e !important;
}
[data-testid="stMetricLabel"] {
    font-size: 0.75rem !important;
    color: #8a94b0 !important;
    text-transform: uppercase;
    letter-spacing: 0.09em;
}
[data-testid="metric-container"] {
    background: #ffffff;
    border: 1px solid #e8eaf0;
    border-radius: 14px;
    padding: 20px 24px !important;
    box-shadow: 0 2px 10px rgba(0,0,0,0.04);
}
[data-testid="stMetricDelta"] svg { display: none; }

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #ff0033, #e0002b) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 0.03em;
    padding: 0.5rem 1.6rem !important;
    box-shadow: 0 4px 14px rgba(255,0,51,0.25) !important;
    transition: all 0.2s;
}
.stButton > button:hover {
    opacity: 0.88 !important;
    box-shadow: 0 6px 18px rgba(255,0,51,0.35) !important;
}

/* ── Text Input ── */
.stTextInput > div > div > input {
    background: #ffffff !important;
    border: 1.5px solid #e0e3ed !important;
    border-radius: 8px !important;
    color: #1a1d2e !important;
    font-family: 'JetBrains Mono', monospace !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.stTextInput > div > div > input:focus {
    border-color: #ff0033 !important;
}

/* ── Selectbox ── */
.stSelectbox > div > div {
    background: #ffffff !important;
    border: 1.5px solid #e0e3ed !important;
    border-radius: 8px !important;
    color: #1a1d2e !important;
}

/* ── Number input ── */
.stNumberInput > div > div > input {
    background: #ffffff !important;
    border: 1.5px solid #e0e3ed !important;
    border-radius: 8px !important;
    color: #1a1d2e !important;
}

/* ── Dataframe ── */
.stDataFrame {
    border-radius: 12px !important;
    overflow: hidden !important;
    border: 1px solid #e8eaf0 !important;
    box-shadow: 0 2px 10px rgba(0,0,0,0.04) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #eef0f7;
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    color: #6b7a99 !important;
    font-weight: 500;
}
.stTabs [aria-selected="true"] {
    background: #ff0033 !important;
    color: white !important;
}

/* ── Radio in sidebar ── */
[data-testid="stSidebar"] .stRadio label {
    color: #4a5068 !important;
    font-size: 0.9rem;
    padding: 6px 10px;
    border-radius: 7px;
    transition: background 0.15s;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background: #f5f6fa !important;
}

/* ── Section Headers ── */
.section-header {
    font-size: 1rem;
    font-weight: 700;
    color: #1a1d2e;
    letter-spacing: 0.02em;
    margin: 1.5rem 0 0.8rem;
    padding-bottom: 0.4rem;
    border-bottom: 2px solid #f0f1f7;
}

/* ── Hero Banner ── */
.hero-banner {
    background: linear-gradient(135deg, #fff5f6 0%, #fff0f3 50%, #f5f6fa 100%);
    border: 1.5px solid #ffd6dc;
    border-radius: 18px;
    padding: 32px 36px;
    margin-bottom: 24px;
}
.hero-title {
    font-size: 2rem;
    font-weight: 800;
    color: #1a1d2e;
    margin: 0 0 6px;
    letter-spacing: -0.02em;
}
.hero-subtitle {
    color: #6b7a99;
    font-size: 0.95rem;
    margin: 0;
}
.yt-badge {
    display: inline-block;
    background: #ff0033;
    color: white;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 3px 10px;
    border-radius: 4px;
    margin-bottom: 10px;
}

/* ── Insight pill ── */
.insight-pill {
    display: inline-block;
    background: #fff0f3;
    border: 1px solid #ffd6dc;
    border-radius: 20px;
    padding: 5px 14px;
    font-size: 0.82rem;
    color: #4a5068;
    margin: 3px 3px;
}
.insight-pill span { color: #ff0033; font-weight: 700; }

/* ── General text ── */
h1, h2, h3 { color: #1a1d2e !important; }
p, li { color: #4a5068; }

/* Divider */
hr { border-color: #e8eaf0 !important; }

/* ── Spinner ── */
.stSpinner > div { border-top-color: #ff0033 !important; }

/* ── Alerts ── */
.stSuccess { background: #f0fff4 !important; border-color: #68d391 !important; }
.stWarning { background: #fffbeb !important; }
.stError   { background: #fff5f5 !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  PLOTLY THEME
# ─────────────────────────────────────────────
PLOTLY_THEME = dict(
    paper_bgcolor="#ffffff",
    plot_bgcolor="#ffffff",
    font=dict(family="Plus Jakarta Sans", color="#4a5068", size=12),
    xaxis=dict(gridcolor="#f0f1f7", zerolinecolor="#e8eaf0", linecolor="#e8eaf0"),
    yaxis=dict(gridcolor="#f0f1f7", zerolinecolor="#e8eaf0", linecolor="#e8eaf0"),
    colorway=["#ff0033", "#ff6b6b", "#ff9e9e", "#ffc7c7"],
    margin=dict(l=10, r=10, t=40, b=10),
)

YT_COLORS = ["#ff0033", "#ff4d6d", "#ff8099", "#ff99a8", "#ffb3bf"]

def apply_theme(fig, title=""):
    fig.update_layout(**PLOTLY_THEME, title=dict(text=title, font=dict(size=14, color="#1a1d2e"), x=0))
    return fig

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def fmt_num(n):
    if n >= 1_000_000_000:
        return f"{n/1_000_000_000:.2f}B"
    if n >= 1_000_000:
        return f"{n/1_000_000:.2f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)

def load_channel_df(channel_id):
    records = get_videos_by_channel(channel_id)
    if not records:
        return pd.DataFrame()
    cols = ["video_id","channel_id","title","views","likes","comments","published_date","engagement_rate"]
    df = pd.DataFrame(records, columns=cols)
    df["published_date"] = pd.to_datetime(df["published_date"])
    df["views"] = pd.to_numeric(df["views"], errors="coerce").fillna(0).astype(int)
    df["likes"] = pd.to_numeric(df["likes"], errors="coerce").fillna(0).astype(int)
    df["comments"] = pd.to_numeric(df["comments"], errors="coerce").fillna(0).astype(int)
    df["engagement_rate"] = pd.to_numeric(df["engagement_rate"], errors="coerce").fillna(0)
    df["year"] = df["published_date"].dt.year
    df["month"] = df["published_date"].dt.to_period("M").astype(str)
    return df

# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
create_tables()

with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 10px 0 20px;'>
        <div style='font-size:2.2rem;'>▶️</div>
        <div style='font-size:1.1rem; font-weight:700; color:#1a1d2e; letter-spacing:-0.01em;'>YT Analytics</div>
        <div style='font-size:0.75rem; color:#6b7a99;'>Infosys Springboard Project</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    page = st.radio(
        "Navigate",
        ["🏠 Overview", "📥 Fetch Channel", "📊 Channel Analytics", "🔍 Video Explorer", "⚖️ Compare Channels"],
        label_visibility="collapsed"
    )
    st.markdown("---")

    # Quick channel switcher
    stored_channels = get_all_channels()
    if stored_channels:
        st.markdown("<div style='font-size:0.78rem;color:#6b7a99;text-transform:uppercase;letter-spacing:.08em;margin-bottom:6px;'>Stored Channels</div>", unsafe_allow_html=True)
        for cid, cname in stored_channels:
            st.markdown(f"<div style='font-size:0.85rem;color:#4a5068;padding:4px 0;'>📺 {cname}</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  PAGE: OVERVIEW
# ─────────────────────────────────────────────
if page == "🏠 Overview":
    st.markdown("""
    <div class="hero-banner">
        <div class="yt-badge">YouTube Analytics</div>
        <div class="hero-title">📊 Channel Intelligence Hub</div>
        <div class="hero-subtitle">Fetch, store, and analyze YouTube channels — engagement metrics, video trends, and audience insights all in one place.</div>
    </div>
    """, unsafe_allow_html=True)

    stored_channels = get_all_channels()

    if not stored_channels:
        st.info("👆 No channels yet. Head to **📥 Fetch Channel** to get started.")
    else:
        # Platform-wide stats
        all_dfs = []
        channel_meta = []
        for cid, cname in stored_channels:
            df = load_channel_df(cid)
            if not df.empty:
                all_dfs.append(df)
                channel_meta.append((cid, cname, df))

        total_videos = sum(len(d) for d in all_dfs)
        total_views = sum(d["views"].sum() for d in all_dfs)
        avg_eng = sum(d["engagement_rate"].mean() for d in all_dfs) / len(all_dfs) if all_dfs else 0

        st.markdown("<div class='section-header'>Platform Overview</div>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Channels Tracked", len(stored_channels))
        c2.metric("Total Videos", fmt_num(total_videos))
        c3.metric("Total Views", fmt_num(total_views))
        c4.metric("Avg Engagement", f"{avg_eng:.2f}%")

        st.markdown("<div class='section-header'>Channel Leaderboard</div>", unsafe_allow_html=True)
        for cid, cname, df in channel_meta:
            with st.container():
                a, b, c, d = st.columns([3, 2, 2, 2])
                a.markdown(f"**{cname}**")
                b.markdown(f"👁️ {fmt_num(df['views'].sum())}")
                c.markdown(f"👍 {fmt_num(df['likes'].sum())}")
                d.markdown(f"📈 {df['engagement_rate'].mean():.2f}% avg")
            st.divider()

        # Combined views over time
        if all_dfs:
            st.markdown("<div class='section-header'>Views Over Time — All Channels</div>", unsafe_allow_html=True)
            combined = pd.concat(all_dfs)
            monthly = combined.groupby(["month", "channel_id"])["views"].sum().reset_index()
            # get channel name
            ch_map = {cid: cname for cid, cname in stored_channels}
            monthly["channel"] = monthly["channel_id"].map(ch_map)
            fig = px.line(monthly, x="month", y="views", color="channel",
                          color_discrete_sequence=YT_COLORS)
            apply_theme(fig, "Monthly Views Comparison")
            fig.update_traces(line_width=2)
            st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────
#  PAGE: FETCH CHANNEL
# ─────────────────────────────────────────────
elif page == "📥 Fetch Channel":
    st.markdown("<h2 style='color:#1a1d2e;font-weight:700;'>📥 Fetch YouTube Channel</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#6b7a99;'>Enter a YouTube Channel ID to pull channel data and all video metrics via the YouTube Data API.</p>", unsafe_allow_html=True)

    channel_id = st.text_input("YouTube Channel ID", placeholder="e.g. UCBJycsmduvYEL83R_U4JriQ")

    if st.button("🚀 Fetch & Store Data"):
        if not channel_id.strip():
            st.warning("Please enter a Channel ID.")
        else:
            with st.spinner("Connecting to YouTube API..."):
                channel_data = get_channel_details(channel_id.strip())

            if not channel_data:
                st.error("❌ Channel not found. Please check the Channel ID.")
            else:
                st.success(f"✅ Found: **{channel_data['channel_name']}**")
                c1, c2, c3 = st.columns(3)
                c1.metric("Subscribers", fmt_num(int(channel_data["subscribers"])))
                c2.metric("Total Views", fmt_num(int(channel_data["total_views"])))
                c3.metric("Total Videos", fmt_num(int(channel_data["total_videos"])))

                with st.spinner("Fetching all videos..."):
                    videos = get_video_details(channel_id.strip())

                if videos:
                    df = pd.DataFrame(videos)
                    df["views"] = pd.to_numeric(df["views"], errors="coerce").fillna(0).astype(int)
                    df["likes"] = pd.to_numeric(df["likes"], errors="coerce").fillna(0).astype(int)
                    df["comments"] = pd.to_numeric(df["comments"], errors="coerce").fillna(0).astype(int)
                    df["published_date"] = pd.to_datetime(df["published_date"], errors="coerce")
                    df["engagement_rate"] = (
                        (df["likes"] + df["comments"]) / df["views"].replace(0, 1)
                    ).fillna(0)
                    df["engagement_rate"] = (df["engagement_rate"] * 100).round(2)

                    insert_channel(channel_id.strip(), channel_data)
                    insert_videos(channel_id.strip(), df)

                    st.success(f"✅ {len(df)} videos stored in database!")
                    st.dataframe(df[["title","views","likes","comments","engagement_rate","published_date"]],
                                 use_container_width=True)
                else:
                    st.warning("No videos returned for this channel.")

    st.markdown("---")
    st.markdown("<div class='section-header'>Quick Guide — How to find a Channel ID</div>", unsafe_allow_html=True)
    st.markdown("""
    1. Go to the YouTube channel page  
    2. Click **About** → **Share** → **Copy channel ID**  
    3. Or check the URL: `youtube.com/channel/`**UCxxxxxx**
    """)

# ─────────────────────────────────────────────
#  PAGE: CHANNEL ANALYTICS
# ─────────────────────────────────────────────
elif page == "📊 Channel Analytics":
    st.markdown("<h2 style='color:#1a1d2e;font-weight:700;'>📊 Channel Analytics</h2>", unsafe_allow_html=True)

    stored_channels = get_all_channels()
    if not stored_channels:
        st.info("No channels stored yet. Go to **📥 Fetch Channel** first.")
        st.stop()

    ch_options = {f"{name}": cid for cid, name in stored_channels}
    selected_name = st.selectbox("Select Channel", list(ch_options.keys()))
    selected_cid = ch_options[selected_name]

    df = load_channel_df(selected_cid)
    if df.empty:
        st.warning("No video data found for this channel.")
        st.stop()

    # ── KPI Row ──
    st.markdown("<div class='section-header'>Key Metrics</div>", unsafe_allow_html=True)
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total Videos", fmt_num(len(df)))
    k2.metric("Total Views", fmt_num(df["views"].sum()))
    k3.metric("Total Likes", fmt_num(df["likes"].sum()))
    k4.metric("Total Comments", fmt_num(df["comments"].sum()))
    k5.metric("Avg Engagement", f"{df['engagement_rate'].mean():.2f}%")

    # ── Date Filter ──
    st.markdown("<div class='section-header'>Filter by Date Range</div>", unsafe_allow_html=True)
    min_date = df["published_date"].min().date()
    max_date = df["published_date"].max().date()
    col_a, col_b = st.columns(2)
    start_date = col_a.date_input("From", min_date, min_value=min_date, max_value=max_date)
    end_date = col_b.date_input("To", max_date, min_value=min_date, max_value=max_date)
    df = df[(df["published_date"].dt.date >= start_date) & (df["published_date"].dt.date <= end_date)]

    # ── Tabs ──
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Trends", "🏆 Top Videos", "📉 Engagement", "📅 Posting Habits"])

    # TAB 1: Trends
    with tab1:
        monthly = df.groupby("month").agg(
            views=("views", "sum"),
            likes=("likes", "sum"),
            comments=("comments", "sum"),
            videos=("video_id", "count")
        ).reset_index()

        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=monthly["month"], y=monthly["views"],
                                   name="Views", line=dict(color="#ff0033", width=2.5),
                                   fill="tozeroy", fillcolor="rgba(255,0,51,0.08)"))
        apply_theme(fig1, "Monthly Views")
        st.plotly_chart(fig1, use_container_width=True)

        c1, c2 = st.columns(2)
        with c1:
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(x=monthly["month"], y=monthly["likes"],
                                   name="Likes", marker_color="#ff0033"))
            apply_theme(fig2, "Monthly Likes")
            st.plotly_chart(fig2, use_container_width=True)
        with c2:
            fig3 = go.Figure()
            fig3.add_trace(go.Bar(x=monthly["month"], y=monthly["videos"],
                                   name="Videos Posted", marker_color="#ff4d6d"))
            apply_theme(fig3, "Videos Published per Month")
            st.plotly_chart(fig3, use_container_width=True)

    # TAB 2: Top Videos
    with tab2:
        n = st.slider("Show top N videos", 5, 50, 10)
        top = df.nlargest(n, "views")[["title","views","likes","comments","engagement_rate","published_date"]]

        fig_top = px.bar(top, x="views", y="title", orientation="h",
                          color="engagement_rate", color_continuous_scale=["#fff0f3","#ff0033"],
                          hover_data=["likes","comments"])
        apply_theme(fig_top, f"Top {n} Videos by Views")
        fig_top.update_layout(yaxis=dict(autorange="reversed"), height=max(350, n*38),
                               coloraxis_colorbar=dict(title="Eng %", tickfont=dict(color="#6b7a99")))
        st.plotly_chart(fig_top, use_container_width=True)

        st.dataframe(top.reset_index(drop=True), use_container_width=True)

    # TAB 3: Engagement
    with tab3:
        c1, c2 = st.columns(2)
        with c1:
            # Engagement distribution
            bins = [0, 1, 3, 5, 100]
            labels = ["< 1%", "1–3%", "3–5%", "> 5%"]
            df["eng_bucket"] = pd.cut(df["engagement_rate"], bins=bins, labels=labels)
            dist = df["eng_bucket"].value_counts().reset_index()
            dist.columns = ["bucket", "count"]
            fig_pie = px.pie(dist, values="count", names="bucket",
                             color_discrete_sequence=YT_COLORS, hole=0.5)
            apply_theme(fig_pie, "Engagement Distribution")
            fig_pie.update_traces(textfont_color="#ffffff")
            st.plotly_chart(fig_pie, use_container_width=True)

        with c2:
            # Views vs Engagement scatter
            fig_sc = px.scatter(df, x="views", y="engagement_rate",
                                hover_data=["title"], color="engagement_rate",
                                color_continuous_scale=["#fff0f3","#ff0033"])
            apply_theme(fig_sc, "Views vs Engagement Rate")
            fig_sc.update_traces(marker=dict(size=6, opacity=0.7))
            st.plotly_chart(fig_sc, use_container_width=True)

        # Likes vs Comments
        fig_lc = px.scatter(df, x="likes", y="comments", size="views",
                             hover_data=["title"], color_discrete_sequence=["#ff0033"],
                             size_max=30)
        apply_theme(fig_lc, "Likes vs Comments (bubble = views)")
        st.plotly_chart(fig_lc, use_container_width=True)

        # Monthly avg engagement line
        monthly_eng = df.groupby("month")["engagement_rate"].mean().reset_index()
        fig_eng = go.Figure()
        fig_eng.add_trace(go.Scatter(x=monthly_eng["month"], y=monthly_eng["engagement_rate"],
                                      mode="lines+markers", name="Avg Engagement",
                                      line=dict(color="#ff0033", width=2),
                                      marker=dict(size=5)))
        apply_theme(fig_eng, "Average Engagement Rate Over Time (%)")
        st.plotly_chart(fig_eng, use_container_width=True)

    # TAB 4: Posting Habits
    with tab4:
        df["weekday"] = df["published_date"].dt.day_name()
        df["hour"] = df["published_date"].dt.hour
        df["quarter"] = df["published_date"].dt.quarter.astype(str)

        c1, c2 = st.columns(2)
        with c1:
            wday_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
            wday = df["weekday"].value_counts().reindex(wday_order).reset_index()
            wday.columns = ["day","count"]
            fig_wd = px.bar(wday, x="day", y="count", color="count",
                             color_continuous_scale=["#fff0f3","#ff0033"])
            apply_theme(fig_wd, "Videos by Day of Week")
            st.plotly_chart(fig_wd, use_container_width=True)

        with c2:
            yearly = df.groupby("year").agg(videos=("video_id","count"), views=("views","sum")).reset_index()
            fig_yr = px.bar(yearly, x="year", y="videos", color="views",
                             color_continuous_scale=["#fff0f3","#ff0033"])
            apply_theme(fig_yr, "Videos Published per Year")
            st.plotly_chart(fig_yr, use_container_width=True)

        # Quarterly posting frequency
        q_dist = df.groupby(["year","quarter"])["video_id"].count().reset_index()
        q_dist.columns = ["year","quarter","count"]
        q_dist["period"] = q_dist["year"].astype(str) + " Q" + q_dist["quarter"]
        fig_q = px.bar(q_dist, x="period", y="count", color_discrete_sequence=["#ff0033"])
        apply_theme(fig_q, "Quarterly Upload Frequency")
        st.plotly_chart(fig_q, use_container_width=True)

        # Insights
        best_day = df["weekday"].value_counts().idxmax()
        best_month = df.groupby("month")["views"].sum().idxmax()
        st.markdown(f"""
        <div style='margin-top:12px;'>
            <div class='insight-pill'>📅 Best upload day: <span>{best_day}</span></div>
            <div class='insight-pill'>🏆 Best month by views: <span>{best_month}</span></div>
            <div class='insight-pill'>📦 Avg videos/month: <span>{len(df)/max(df['month'].nunique(),1):.1f}</span></div>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  PAGE: VIDEO EXPLORER
# ─────────────────────────────────────────────
elif page == "🔍 Video Explorer":
    st.markdown("<h2 style='color:#1a1d2e;font-weight:700;'>🔍 Video Explorer</h2>", unsafe_allow_html=True)

    stored_channels = get_all_channels()
    if not stored_channels:
        st.info("No channels stored yet.")
        st.stop()

    ch_options = {f"{name}": cid for cid, name in stored_channels}
    selected_name = st.selectbox("Select Channel", list(ch_options.keys()))
    selected_cid = ch_options[selected_name]
    df = load_channel_df(selected_cid)

    if df.empty:
        st.warning("No data found.")
        st.stop()

    # Search + filters
    col1, col2, col3 = st.columns([3, 2, 2])
    search = col1.text_input("🔎 Search by title", placeholder="keyword...")
    sort_col = col2.selectbox("Sort by", ["views","likes","comments","engagement_rate","published_date"])
    sort_asc = col3.selectbox("Order", ["Descending","Ascending"]) == "Ascending"

    # View/Engagement filters
    fc1, fc2 = st.columns(2)
    min_views = fc1.number_input("Min Views", value=0, step=1000)
    min_eng = fc2.number_input("Min Engagement %", value=0.0, step=0.5)

    filtered = df.copy()
    if search:
        filtered = filtered[filtered["title"].str.contains(search, case=False, na=False)]
    filtered = filtered[filtered["views"] >= min_views]
    filtered = filtered[filtered["engagement_rate"] >= min_eng]
    filtered = filtered.sort_values(sort_col, ascending=sort_asc)

    st.markdown(f"<div style='color:#6b7a99;font-size:0.85rem;margin:8px 0;'>Showing {len(filtered):,} of {len(df):,} videos</div>", unsafe_allow_html=True)

    display = filtered[["title","views","likes","comments","engagement_rate","published_date"]].reset_index(drop=True)
    st.dataframe(display, use_container_width=True, height=500)

    # Download
    csv = display.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download CSV", csv, f"{selected_name}_videos.csv", "text/csv")

    # Quick stats on filtered set
    if not filtered.empty:
        st.markdown("<div class='section-header'>Filtered Set Stats</div>", unsafe_allow_html=True)
        s1, s2, s3, s4 = st.columns(4)
        s1.metric("Videos", len(filtered))
        s2.metric("Total Views", fmt_num(filtered["views"].sum()))
        s3.metric("Avg Engagement", f"{filtered['engagement_rate'].mean():.2f}%")
        s4.metric("Max Views", fmt_num(filtered["views"].max()))

# ─────────────────────────────────────────────
#  PAGE: COMPARE CHANNELS
# ─────────────────────────────────────────────
elif page == "⚖️ Compare Channels":
    st.markdown("<h2 style='color:#1a1d2e;font-weight:700;'>⚖️ Compare Channels</h2>", unsafe_allow_html=True)

    stored_channels = get_all_channels()
    if len(stored_channels) < 2:
        st.info("You need at least 2 stored channels to compare. Fetch more channels first.")
        st.stop()

    ch_options = {name: cid for cid, name in stored_channels}
    col1, col2 = st.columns(2)
    ch_a_name = col1.selectbox("Channel A", list(ch_options.keys()), index=0)
    ch_b_name = col2.selectbox("Channel B", list(ch_options.keys()), index=1)

    if ch_a_name == ch_b_name:
        st.warning("Please select two different channels.")
        st.stop()

    df_a = load_channel_df(ch_options[ch_a_name])
    df_b = load_channel_df(ch_options[ch_b_name])

    if df_a.empty or df_b.empty:
        st.warning("One of the channels has no video data.")
        st.stop()

    # Head-to-head KPIs
    st.markdown("<div class='section-header'>Head-to-Head Comparison</div>", unsafe_allow_html=True)

    metrics = {
        "Total Videos": (len(df_a), len(df_b)),
        "Total Views": (df_a["views"].sum(), df_b["views"].sum()),
        "Total Likes": (df_a["likes"].sum(), df_b["likes"].sum()),
        "Total Comments": (df_a["comments"].sum(), df_b["comments"].sum()),
        "Avg Engagement %": (df_a["engagement_rate"].mean(), df_b["engagement_rate"].mean()),
        "Max Single Video Views": (df_a["views"].max(), df_b["views"].max()),
    }

    header = st.columns([3,2,2])
    header[0].markdown("<div style='color:#6b7a99;font-size:0.8rem;text-transform:uppercase;'>Metric</div>", unsafe_allow_html=True)
    header[1].markdown(f"<div style='color:#ff0033;font-weight:700;'>{ch_a_name}</div>", unsafe_allow_html=True)
    header[2].markdown(f"<div style='color:#ff4d6d;font-weight:700;'>{ch_b_name}</div>", unsafe_allow_html=True)
    st.divider()

    for metric, (val_a, val_b) in metrics.items():
        row = st.columns([3,2,2])
        row[0].markdown(f"<div style='color:#6b7a99;'>{metric}</div>", unsafe_allow_html=True)
        is_pct = "%" in metric
        fmt = (lambda v: f"{v:.2f}%") if is_pct else fmt_num
        winner_a = val_a >= val_b
        row[1].markdown(f"<div style='color:{'#16a34a' if winner_a else '#1a1d2e'};font-weight:600;font-family:Plus Jakarta Sans,sans-serif;'>{fmt(val_a)}</div>", unsafe_allow_html=True)
        row[2].markdown(f"<div style='color:{'#16a34a' if not winner_a else '#1a1d2e'};font-weight:600;font-family:Plus Jakarta Sans,sans-serif;'>{fmt(val_b)}</div>", unsafe_allow_html=True)
        st.divider()

    # ── CHART 1: Views Over Time — clearly distinct colors ──
    st.markdown("<div class='section-header'>📈 Monthly Views Over Time</div>", unsafe_allow_html=True)
    m_a = df_a.groupby("month")["views"].sum().reset_index()
    m_b = df_b.groupby("month")["views"].sum().reset_index()

    fig_comp = go.Figure()
    fig_comp.add_trace(go.Scatter(
        x=m_a["month"], y=m_a["views"], name=ch_a_name,
        line=dict(color="#e63946", width=3),
        fill="tozeroy", fillcolor="rgba(230,57,70,0.08)"
    ))
    fig_comp.add_trace(go.Scatter(
        x=m_b["month"], y=m_b["views"], name=ch_b_name,
        line=dict(color="#1d6ae5", width=3),
        fill="tozeroy", fillcolor="rgba(29,106,229,0.08)"
    ))
    apply_theme(fig_comp, "")
    fig_comp.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    font=dict(size=13), bgcolor="rgba(0,0,0,0)"),
        hovermode="x unified",
        height=380,
        yaxis_title="Total Views",
        xaxis_title="Month"
    )
    st.plotly_chart(fig_comp, use_container_width=True)

    # ── CHART 2 & 3 side by side ──
    c1, c2 = st.columns(2)

    # CHART 2: Avg Engagement bar chart (replaces confusing box plot)
    with c1:
        st.markdown("<div class='section-header'>📊 Engagement Rate Breakdown</div>", unsafe_allow_html=True)

        # Bucket videos into engagement tiers and count per channel
        def eng_buckets(df):
            bins   = [0, 1, 3, 5, 100]
            labels = ["Low\n(<1%)", "Medium\n(1–3%)", "High\n(3–5%)", "Viral\n(>5%)"]
            df = df.copy()
            df["bucket"] = pd.cut(df["engagement_rate"], bins=bins, labels=labels)
            return df["bucket"].value_counts().reindex(labels).fillna(0).reset_index()

        buck_a = eng_buckets(df_a)
        buck_b = eng_buckets(df_b)
        buck_a.columns = ["bucket", "count"]
        buck_b.columns = ["bucket", "count"]

        fig_eng = go.Figure()
        fig_eng.add_trace(go.Bar(
            x=buck_a["bucket"], y=buck_a["count"],
            name=ch_a_name, marker_color="#e63946",
            text=buck_a["count"].astype(int), textposition="outside"
        ))
        fig_eng.add_trace(go.Bar(
            x=buck_b["bucket"], y=buck_b["count"],
            name=ch_b_name, marker_color="#1d6ae5",
            text=buck_b["count"].astype(int), textposition="outside"
        ))
        apply_theme(fig_eng, "")
        fig_eng.update_layout(
            barmode="group",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                        font=dict(size=12), bgcolor="rgba(0,0,0,0)"),
            yaxis_title="Number of Videos",
            xaxis_title="Engagement Tier",
            height=380,
            bargap=0.25,
            bargroupgap=0.1
        )
        st.plotly_chart(fig_eng, use_container_width=True)

    # CHART 3: Side-by-side metric comparison bar chart (replaces radar)
    with c2:
        st.markdown("<div class='section-header'>🏆 Metric Comparison (Avg per Video)</div>", unsafe_allow_html=True)

        metrics_labels = ["Avg Views", "Avg Likes", "Avg Comments", "Avg Eng %", "Total Videos"]
        vals_a = [
            int(df_a["views"].mean()),
            int(df_a["likes"].mean()),
            int(df_a["comments"].mean()),
            round(df_a["engagement_rate"].mean(), 2),
            len(df_a)
        ]
        vals_b = [
            int(df_b["views"].mean()),
            int(df_b["likes"].mean()),
            int(df_b["comments"].mean()),
            round(df_b["engagement_rate"].mean(), 2),
            len(df_b)
        ]

        # Normalize each metric to 0–100 so all bars are readable on same axis
        norm_a, norm_b = [], []
        raw_labels_a, raw_labels_b = [], []
        for va, vb, lbl in zip(vals_a, vals_b, metrics_labels):
            mx = max(va, vb, 1)
            norm_a.append(round(va / mx * 100, 1))
            norm_b.append(round(vb / mx * 100, 1))
            raw_labels_a.append(fmt_num(va) if "%" not in lbl else f"{va}%")
            raw_labels_b.append(fmt_num(vb) if "%" not in lbl else f"{vb}%")

        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            y=metrics_labels, x=norm_a, name=ch_a_name,
            orientation="h", marker_color="#e63946",
            text=raw_labels_a, textposition="inside",
            textfont=dict(color="white", size=11)
        ))
        fig_bar.add_trace(go.Bar(
            y=metrics_labels, x=norm_b, name=ch_b_name,
            orientation="h", marker_color="#1d6ae5",
            text=raw_labels_b, textposition="inside",
            textfont=dict(color="white", size=11)
        ))
        apply_theme(fig_bar, "")
        fig_bar.update_layout(
            barmode="group",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                        font=dict(size=12), bgcolor="rgba(0,0,0,0)"),
            xaxis_title="Score (normalized to 100)",
            xaxis=dict(range=[0, 115], gridcolor="#f0f1f7"),
            height=380,
            bargap=0.3,
            bargroupgap=0.08
        )
        st.plotly_chart(fig_bar, use_container_width=True)

# ── Footer ──
st.markdown("""
<div style='text-align:center;padding:32px 0 16px;color:#3a4255;font-size:0.78rem;'>
    YouTube Analytics Dashboard · Infosys Springboard Internship Project · Built with Streamlit & Plotly
</div>
""", unsafe_allow_html=True)
