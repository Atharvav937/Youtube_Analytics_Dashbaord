import sqlite3

# Create database connection
conn = sqlite3.connect("youtube_data.db", check_same_thread=False)
cursor = conn.cursor()


def create_tables():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS channel (
            channel_id TEXT PRIMARY KEY,
            channel_name TEXT,
            subscribers INTEGER,
            total_views INTEGER,
            total_videos INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS video (
            video_id TEXT PRIMARY KEY,
            channel_id TEXT,
            title TEXT,
            views INTEGER,
            likes INTEGER,
            comments INTEGER,
            published_date TEXT,
            engagement_rate REAL,
            FOREIGN KEY(channel_id) REFERENCES channel(channel_id)
        )
    """)

    conn.commit()


def insert_channel(channel_id, data):
    cursor.execute("""
        INSERT OR REPLACE INTO channel VALUES (?, ?, ?, ?, ?)
    """, (
        channel_id,
        data["channel_name"],
        int(data["subscribers"]),
        int(data["total_views"]),
        int(data["total_videos"])
    ))
    conn.commit()


def insert_videos(channel_id, df):
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT OR REPLACE INTO video VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row["video_id"],
            channel_id,
            row["title"],
            int(row["views"]),
            int(row["likes"]),
            int(row["comments"]),
            str(row["published_date"]),
            float(row["engagement_rate"])
        ))
    conn.commit()


# 🔥 NEW FUNCTIONS FOR VIEW STORED CHANNELS

def get_all_channels():
    cursor.execute("SELECT channel_id, channel_name FROM channel")
    return cursor.fetchall()


def get_videos_by_channel(channel_id):
    cursor.execute("""
        SELECT video_id, channel_id, title, views, likes, comments, published_date, engagement_rate
        FROM video
        WHERE channel_id = ?
    """, (channel_id,))
    return cursor.fetchall()
