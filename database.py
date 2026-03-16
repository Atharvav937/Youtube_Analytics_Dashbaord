import sqlite3

DB_PATH = "youtube_data.db"


def _conn():
    """Return a new connection (thread-safe)."""
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def create_tables():
    con = _conn()
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS channel (
            channel_id   TEXT PRIMARY KEY,
            channel_name TEXT,
            subscribers  INTEGER,
            total_views  INTEGER,
            total_videos INTEGER
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS video (
            video_id        TEXT PRIMARY KEY,
            channel_id      TEXT,
            title           TEXT,
            views           INTEGER,
            likes           INTEGER,
            comments        INTEGER,
            published_date  TEXT,
            engagement_rate REAL,
            FOREIGN KEY(channel_id) REFERENCES channel(channel_id)
        )
    """)
    con.commit()
    con.close()


def insert_channel(channel_id, data):
    con = _conn()
    con.execute("""
        INSERT OR REPLACE INTO channel VALUES (?, ?, ?, ?, ?)
    """, (
        channel_id,
        data["channel_name"],
        int(data["subscribers"]),
        int(data["total_views"]),
        int(data["total_videos"])
    ))
    con.commit()
    con.close()


def insert_videos(channel_id, df):
    con = _conn()
    cur = con.cursor()
    for _, row in df.iterrows():
        cur.execute("""
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
    con.commit()
    con.close()


def get_all_channels():
    con = _conn()
    rows = con.execute("SELECT channel_id, channel_name FROM channel").fetchall()
    con.close()
    return rows


def get_videos_by_channel(channel_id):
    con = _conn()
    rows = con.execute("""
        SELECT video_id, channel_id, title, views, likes, comments,
               published_date, engagement_rate
        FROM video
        WHERE channel_id = ?
        ORDER BY published_date DESC
    """, (channel_id,)).fetchall()
    con.close()
    return rows
