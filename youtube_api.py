from googleapiclient.discovery import build

API_KEY = "AIzaSyA7Dg-4bG1UuFG2S-6_Y4RXpTrt6JoDd64"   # Replace with new key

youtube = build("youtube", "v3", developerKey=API_KEY)


# ----------------------------------------------------
# Get Channel Details (Safe Version)
# ----------------------------------------------------
def get_channel_details(channel_id):
    try:
        request = youtube.channels().list(
            part="snippet,statistics",
            id=channel_id
        )
        response = request.execute()

        print("API RESPONSE:", response)

        if "items" in response and len(response["items"]) > 0:
            data = response["items"][0]
            return {
                "channel_name": data["snippet"]["title"],
                "subscribers": data["statistics"].get("subscriberCount", 0),
                "total_views": data["statistics"].get("viewCount", 0),
                "total_videos": data["statistics"].get("videoCount", 0)
            }
        else:
            return None

    except Exception as e:
        print("ERROR:", e)
        return None

# ----------------------------------------------------
# Get Video Details (Safe Version)
# ----------------------------------------------------
def get_video_details(channel_id):
    try:
        # Step 1: Get Upload Playlist ID
        request = youtube.channels().list(
            part="contentDetails",
            id=channel_id
        )
        response = request.execute()

        if "items" not in response or len(response["items"]) == 0:
            return None

        uploads_playlist_id = response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

        # Step 2: Get Video IDs
        video_ids = []
        next_page_token = None

        while True:
            request = youtube.playlistItems().list(
                part="snippet",
                playlistId=uploads_playlist_id,
                maxResults=50,
                pageToken=next_page_token
            )
            response = request.execute()

            if "items" not in response:
                break

            for item in response["items"]:
                video_ids.append(item["snippet"]["resourceId"]["videoId"])

            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break

        # Step 3: Get Video Statistics
        video_data = []

        for i in range(0, len(video_ids), 50):
            request = youtube.videos().list(
                part="snippet,statistics",
                id=",".join(video_ids[i:i+50])
            )
            response = request.execute()

            if "items" not in response:
                continue

            for item in response["items"]:
                video_data.append({
                    "video_id": item["id"],
                    "title": item["snippet"]["title"],
                    "views": item["statistics"].get("viewCount", 0),
                    "likes": item["statistics"].get("likeCount", 0),
                    "comments": item["statistics"].get("commentCount", 0),
                    "published_date": item["snippet"]["publishedAt"][:10]
                })

        return video_data

    except Exception as e:
        print("Video API Error:", e)
        return None
