import requests
import pandas as pd

def get_uploads_playlist_id(api_key, channel_id):
    url = f"https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id={channel_id}&key={api_key}"
    res = requests.get(url).json()
    try:
        return res["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    except:
        return None

def get_video_data(api_key, playlist_id, max_results=50):
    url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId={playlist_id}&maxResults={max_results}&key={api_key}"
    res = requests.get(url).json()

    videos = []
    for item in res.get("items", []):
        video_id = item["snippet"]["resourceId"]["videoId"]
        title = item["snippet"]["title"]
        published_at = item["snippet"]["publishedAt"]
        thumbnail = item["snippet"]["thumbnails"]["medium"]["url"]

        stats_url = f"https://www.googleapis.com/youtube/v3/videos?part=statistics&id={video_id}&key={api_key}"
        stats_res = requests.get(stats_url).json()
        views = stats_res.get("items", [{}])[0].get("statistics", {}).get("viewCount", 0)

        videos.append({
            "title": title,
            "video_id": video_id,
            "published_at": published_at,
            "views": views,
            "thumbnail": thumbnail
        })

    return pd.DataFrame(videos)