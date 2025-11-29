import re
import time
from typing import Optional, List

from googleapiclient.discovery import build
from sqlalchemy.orm import sessionmaker, Session

from config import YOUTUBE_API_KEY
from db_setup import engine, Channel, Video, VideoStats

# ======================
# 1. DB session + YouTube client
# ======================

SessionLocal = sessionmaker(bind=engine)


def get_youtube_client():
    """Create a YouTube API client using your API key."""
    return build("youtube", "v3", developerKey=YOUTUBE_API_KEY)


# ======================
# 2. Resolve Channel ID from URL or ID
# ======================

def resolve_channel_id(youtube, channel_url_or_id: str) -> Optional[str]:
    """
    Accepts:
      - full channel URL (https://www.youtube.com/channel/UCxxxxx...)
      - handle URL (https://www.youtube.com/@SomeHandle)
      - or raw channel ID (UCxxxxx...)
    Returns a channel ID or None.
    """
    text = channel_url_or_id.strip()

    # Case 1: already an ID
    if text.startswith("UC") and len(text) >= 20:
        return text

    # Case 2: URL with /channel/<id>
    m = re.search(r"youtube\.com/channel/([^/?]+)", text)
    if m:
        return m.group(1)

    # Case 3: handle URL with @handle
    m = re.search(r"youtube\.com/@([^/?]+)", text)
    if m:
        handle = m.group(1)
        search_resp = youtube.search().list(
            part="snippet",
            q=handle,
            type="channel",
            maxResults=1
        ).execute()
        items = search_resp.get("items", [])
        if items:
            return items[0]["snippet"]["channelId"]

    return None


# ======================
# 3. Save channel info
# ======================

def save_channel_info(youtube, session: Session, channel_id: str) -> Channel:
    resp = youtube.channels().list(
        part="snippet,statistics",
        id=channel_id
    ).execute()

    items = resp.get("items", [])
    if not items:
        raise ValueError(f"No channel found for id={channel_id}")

    item = items[0]
    snippet = item["snippet"]
    stats = item["statistics"]

    channel = session.get(Channel, channel_id)
    if channel is None:
        channel = Channel(channel_id=channel_id)

    channel.channel_name = snippet.get("title")
    channel.channel_url = f"https://www.youtube.com/channel/{channel_id}"
    channel.subscriber_count = int(stats.get("subscriberCount", 0)) if "subscriberCount" in stats else None
    channel.total_views = int(stats.get("viewCount", 0))
    channel.video_count = int(stats.get("videoCount", 0))

    from datetime import datetime
    channel.created_at = datetime.fromisoformat(snippet["publishedAt"].replace("Z", "+00:00"))

    session.add(channel)
    session.commit()

    print(f"Saved channel: {channel.channel_name} ({channel.channel_id})")
    return channel


# ======================
# 4. Fetch video IDs for a channel
# ======================

def get_video_ids(youtube, channel_id: str, max_videos: int = 50) -> List[str]:
    video_ids: List[str] = []
    next_page = None

    while len(video_ids) < max_videos:
        resp = youtube.search().list(
            part="id",
            channelId=channel_id,
            maxResults=50,
            order="date",
            type="video",
            pageToken=next_page
        ).execute()

        for item in resp.get("items", []):
            vid = item["id"]["videoId"]
            video_ids.append(vid)
            if len(video_ids) >= max_videos:
                break

        next_page = resp.get("nextPageToken")
        if not next_page:
            break

    return video_ids[:max_videos]


# ======================
# 5. Save video details + stats
# ======================

def iso8601_duration_to_seconds(duration: str) -> int:
    """Convert 'PT1H2M30S' → total seconds."""
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration)
    if not m:
        return 0
    h = int(m.group(1) or 0)
    mi = int(m.group(2) or 0)
    s = int(m.group(3) or 0)
    return h * 3600 + mi * 60 + s


def save_video_details(youtube, session: Session, video_id: str, channel_id: str):
    resp = youtube.videos().list(
        part="snippet,statistics,contentDetails",
        id=video_id
    ).execute()

    items = resp.get("items", [])
    if not items:
        return

    item = items[0]
    snippet = item["snippet"]
    content = item["contentDetails"]
    stats = item.get("statistics", {})

    from datetime import datetime

    video = session.get(Video, video_id)
    if video is None:
        video = Video(video_id=video_id, channel_id=channel_id)

    video.title = snippet.get("title")
    video.description = snippet.get("description")
    video.published_at = datetime.fromisoformat(snippet["publishedAt"].replace("Z", "+00:00"))
    video.duration_seconds = iso8601_duration_to_seconds(content.get("duration", "PT0S"))
    tags = snippet.get("tags")
    video.tags = ",".join(tags) if tags else None
    video.category = snippet.get("categoryId")

    session.add(video)

    # stats row
    stats_row = VideoStats(
        video_id=video_id,
        views=int(stats.get("viewCount", 0)),
        likes=int(stats.get("likeCount", 0)) if "likeCount" in stats else None,
        comments=int(stats.get("commentCount", 0)) if "commentCount" in stats else None,
    )
    session.add(stats_row)

    session.commit()


# ======================
# 6. Main collector
# ======================

def collect_channel_data(channel_url_or_id: str, max_videos: int = 50):
    youtube = get_youtube_client()
    session = SessionLocal()

    try:
        print("Resolving channel ID...")
        channel_id = resolve_channel_id(youtube, channel_url_or_id)
        if not channel_id:
            print("❌ Could not resolve channel ID.")
            return

        print(f"✔ Channel ID: {channel_id}")
        channel = save_channel_info(youtube, session, channel_id)

        print("Fetching video IDs...")
        video_ids = get_video_ids(youtube, channel.channel_id, max_videos=max_videos)
        print(f"Found {len(video_ids)} videos")

        for vid in video_ids:
            print(f"Saving video: {vid}")
            save_video_details(youtube, session, vid, channel.channel_id)
            time.sleep(0.4)  # gentle delay for API quota

        print("🎉 Finished collecting data!")
    finally:
        session.close()


# ======================
# Run from terminal
# ======================

if __name__ == "__main__":
    url = input("Enter YouTube channel URL or ID: ").strip()
    collect_channel_data(url, max_videos=30)
