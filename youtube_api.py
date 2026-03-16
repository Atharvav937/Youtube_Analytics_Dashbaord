from googleapiclient.discovery import build

# ⚠️  Replace with your valid YouTube Data API v3 key
API_KEY = "YOUR_YOUTUBE_API_KEY"

youtube = build("youtube", "v3", developerKey=API_KEY)


def get_channel_details(channel_id: str) -> dict | None:
    """Return channel-level stats or None on failure."""
    try:
        response = youtube.channels().list(
            part="snippet,statistics",
            id=channel_id
        ).execute()

        items = response.get("items", [])
        if not items:
            return None

        data = items[0]
        stats = data["statistics"]
        return {
            "channel_name": data["snippet"]["title"],
            "subscribers":  stats.get("subscriberCount", 0),
            "total_views":  stats.get("viewCount", 0),
            "total_videos": stats.get("videoCount", 0),
        }
    except Exception as e:
        print(f"[channel_details] ERROR: {e}")
        return None


def get_video_details(channel_id: str) -> list[dict] | None:
    """Return a list of video dicts for the channel, or None on failure."""
    try:
        # 1. Get the uploads playlist ID
        response = youtube.channels().list(
            part="contentDetails",
            id=channel_id
        ).execute()

        items = response.get("items", [])
        if not items:
            return None

        uploads_id = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]

        # 2. Paginate through the playlist to collect all video IDs
        video_ids = []
        next_page_token = None
        while True:
            pl_response = youtube.playlistItems().list(
                part="snippet",
                playlistId=uploads_id,
                maxResults=50,
                pageToken=next_page_token
            ).execute()

            for item in pl_response.get("items", []):
                video_ids.append(item["snippet"]["resourceId"]["videoId"])

            next_page_token = pl_response.get("nextPageToken")
            if not next_page_token:
                break

        # 3. Fetch stats in batches of 50
        video_data = []
        for i in range(0, len(video_ids), 50):
            batch = ",".join(video_ids[i:i + 50])
            v_response = youtube.videos().list(
                part="snippet,statistics",
                id=batch
            ).execute()

            for item in v_response.get("items", []):
                snippet = item["snippet"]
                stats   = item["statistics"]
                video_data.append({
                    "video_id":      item["id"],
                    "title":         snippet["title"],
                    "views":         stats.get("viewCount",   0),
                    "likes":         stats.get("likeCount",   0),
                    "comments":      stats.get("commentCount", 0),
                    "published_date": snippet["publishedAt"][:10],
                })

        return video_data if video_data else None

    except Exception as e:
        print(f"[video_details] ERROR: {e}")
        return None
