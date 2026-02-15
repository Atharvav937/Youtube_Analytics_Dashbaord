import streamlit as st
import pandas as pd
import plotly.express as px
from youtube_api import get_channel_details, get_video_details
from database import (
    create_tables,
    insert_channel,
    insert_videos,
    get_all_channels,
    get_videos_by_channel
)

st.set_page_config(page_title="YouTube Analytics Dashboard", layout="wide")

st.title("📊 YouTube Analytics Dashboard")

create_tables()

# ------------------ FETCH FROM API ------------------

channel_id = st.text_input("Enter YouTube Channel ID")

if st.button("Fetch Channel Data"):

    if channel_id:

        with st.spinner("Fetching data from YouTube API..."):

            channel_data = get_channel_details(channel_id)

            if channel_data:

                st.success("Channel Found ✅")

                st.subheader(f"📺 {channel_data['channel_name']}")

                col1, col2, col3 = st.columns(3)

                col1.metric("Subscribers", f"{int(channel_data['subscribers']):,}")
                col2.metric("Total Views", f"{int(channel_data['total_views']):,}")
                col3.metric("Total Videos", f"{int(channel_data['total_videos']):,}")

                st.divider()

                videos = get_video_details(channel_id)

                if videos:

                    df = pd.DataFrame(videos)

                    # ---- PREPROCESSING ----
                    df["views"] = pd.to_numeric(df["views"], errors="coerce").fillna(0).astype(int)
                    df["likes"] = pd.to_numeric(df["likes"], errors="coerce").fillna(0).astype(int)
                    df["comments"] = pd.to_numeric(df["comments"], errors="coerce").fillna(0).astype(int)
                    df["published_date"] = pd.to_datetime(df["published_date"], errors="coerce")

                    df["engagement_rate"] = (
                        (df["likes"] + df["comments"]) / df["views"]
                    ).replace([float("inf")], 0).fillna(0)

                    df["engagement_rate"] = (df["engagement_rate"] * 100).round(2)

                    # ---- STORE IN DATABASE ----
                    insert_channel(channel_id, channel_data)
                    insert_videos(channel_id, df)

                    st.success("Data Stored in Database ✅")

                    # ---- DISPLAY ----
                    st.subheader("📋 Video Details")
                    st.dataframe(df, use_container_width=True)

                else:
                    st.warning("No videos found")

            else:
                st.error("Invalid Channel ID ❌")

    else:
        st.warning("Please enter a Channel ID")


# ------------------ VIEW STORED CHANNELS ------------------

st.divider()
st.subheader("📂 View Stored Channels")

stored_channels = get_all_channels()

if stored_channels:

    channel_options = {
        f"{name} ({cid})": cid for cid, name in stored_channels
    }

    selected_label = st.selectbox(
        "Select Stored Channel",
        list(channel_options.keys())
    )

    selected_channel_id = channel_options[selected_label]

    if st.button("Load Selected Channel Data"):

        records = get_videos_by_channel(selected_channel_id)

        if records:
            columns = [
                "video_id",
                "channel_id",
                "title",
                "views",
                "likes",
                "comments",
                "published_date",
                "engagement_rate"
            ]

            db_df = pd.DataFrame(records, columns=columns)
            db_df["published_date"] = pd.to_datetime(db_df["published_date"])

            st.success("Loaded from Database ✅")
            st.dataframe(db_df, use_container_width=True)

        else:
            st.warning("No videos found for this channel.")

else:
    st.info("No channels stored in database yet.")
