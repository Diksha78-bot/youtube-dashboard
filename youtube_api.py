from googleapiclient.discovery import build
import pandas as pd

# Initialize API
def get_service():
    api_key = "AIzaSyAC-CD0yKr8MhvBvbE6Lk7vx9CfwfjCqg8"  # Replace with your key
    return build("youtube", "v3", developerKey=api_key)

# Get Channel Info
def get_channel_info(service, channel_id):
    request = service.channels().list(
        part="snippet,statistics,contentDetails",
        id=channel_id
    )
    response = request.execute()

    if "items" not in response or len(response["items"]) == 0:
        raise Exception("Invalid Channel ID or no data found.")

    data = response["items"][0]

    return {
    "channel_name": data["snippet"].get("title", "N/A"),
    "description": data["snippet"].get("description", "No description"),
    "subscriberCount": data["statistics"].get("subscriberCount", 0),
    "viewCount": data["statistics"].get("viewCount", 0),
    "videoCount": data["statistics"].get("videoCount", 0),
    "channelLogo": data["snippet"]["thumbnails"]["default"]["url"],
    "playlistId": data["contentDetails"]["relatedPlaylists"]["uploads"]
}


# Get Video Details from Upload Playlist
def get_video_details(service, channel_id, max_videos=100):
    channel_info = get_channel_info(service, channel_id)
    playlist_id = channel_info["playlistId"]

    video_data_list = []
    next_page_token = None

    while len(video_data_list) < max_videos:
        playlist_request = service.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )
        playlist_response = playlist_request.execute()

        video_ids = [
            item["snippet"]["resourceId"]["videoId"]
            for item in playlist_response["items"]
            if "videoId" in item["snippet"]["resourceId"]
        ]

        if not video_ids:
            break

        video_request = service.videos().list(
            part="snippet,statistics",
            id=",".join(video_ids)
        )
        video_response = video_request.execute()

        for video in video_response.get("items", []):
            snippet = video.get("snippet", {})
            stats = video.get("statistics", {})

            published_at = snippet.get("publishedAt")
            published_at = pd.to_datetime(published_at) if published_at else pd.NaT

            video_data_list.append({
                "video_id": video.get("id"),
                "title": snippet.get("title", "No Title"),
                "publishedAt": published_at,
                "views": int(stats.get("viewCount", 0)),
                "likes": int(stats.get("likeCount", 0)),
                "comments": int(stats.get("commentCount", 0)),
                "thumbnail": snippet.get("thumbnails", {}).get("medium", {}).get("url", "")
            })

        next_page_token = playlist_response.get("nextPageToken")
        if not next_page_token:
            break

    return video_data_list
