# --- app.py ---
import streamlit as st
import pandas as pd
import plotly.express as px
from channel_videos import get_uploads_playlist_id, get_video_data

# --- API Key ---
API_KEY = st.secrets["API_KEY"]
 # Replace with your valid API key

# --- Streamlit App ---
st.set_page_config(page_title="📊 YouTube Channel Dashboard", layout="wide")

st.title("📺 YouTube Channel Dashboard")
st.write("Analyze video performance with thumbnails, views, and keyword filter.")

# --- Sidebar Input ---
st.sidebar.header("🔧 Channel Settings")
channel_id = st.sidebar.text_input("Enter YouTube Channel ID", placeholder="e.g. UC_x5XG1OV2P6uZZ5FSM9Ttw")

if st.sidebar.button("🎯 Use Example Channel"):
    channel_id = "UC_x5XG1OV2P6uZZ5FSM9Ttw"

if channel_id:
    playlist_id = get_uploads_playlist_id(API_KEY, channel_id)
    if playlist_id:
        df = get_video_data(API_KEY, playlist_id, max_results=50)

        if df.empty:
            st.warning("No videos found or access denied.")
        else:
            # -- Keyword Filter --
            keyword = st.text_input("🔍 Search in Titles", "").lower()
            if keyword:
                df = df[df["title"].str.lower().str.contains(keyword)]

            # -- Thumbnails Section --
            st.subheader("🎞️ Latest Videos")
            for i, row in df.iterrows():
                with st.container():
                    cols = st.columns([1, 3])
                    cols[0].image(row["thumbnail"], width=150)
                    cols[1].markdown(f"**{row['title']}**")
                    cols[1].markdown(f"📅 *{row['published_at'][:10]}* | 👁️ {int(row['views']):,} views")
                    cols[1].markdown(f"[🔗 Watch on YouTube](https://youtu.be/{row['video_id']})")

            # -- Views Over Time --
            st.subheader("📈 Views Over Time")
            df["published_at"] = pd.to_datetime(df["published_at"])
            df = df.sort_values("published_at")

            fig = px.line(
                df.sort_values("published_at"),
                x="published_at",
                y="views",
                title="Views Trend",
                markers=True
            )
            st.write("✅ Plotly graph will appear below if data exists.")
            st.write(df[["published_at", "views"]].head())

            st.plotly_chart(fig, use_container_width=True)


            # -- Data Table --
            st.subheader("📋 Video Table")
            st.dataframe(df[["title", "views", "published_at"]])
    else:
        st.error("❌ Error: Playlist not found. Check the Channel ID.")
else:
    st.info("👈 Enter a Channel ID to get started.")
