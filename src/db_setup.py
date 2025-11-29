import os
from sqlalchemy import (
    create_engine, Column, String, Integer, DateTime, BigInteger, Text, ForeignKey
)
from sqlalchemy.orm import declarative_base
from datetime import datetime

# ========== 1. Make sure data folder exists ==========
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# ========== 2. SQLite database path ==========
DB_PATH = os.path.join(DATA_DIR, "youtube_analytics.db")
DB_URL = f"sqlite:///{DB_PATH}"

# ========== 3. Create Database Engine ==========
engine = create_engine(DB_URL, echo=True)   # echo=True prints SQL logs

# ========== 4. Base Class for Models ==========
Base = declarative_base()

# ========== 5. Define Tables ==========

class Channel(Base):
    __tablename__ = "channels"

    channel_id = Column(String, primary_key=True)
    channel_name = Column(String, nullable=False)
    channel_url = Column(String, nullable=False)
    subscriber_count = Column(BigInteger)
    total_views = Column(BigInteger)
    video_count = Column(Integer)
    created_at = Column(DateTime)
    fetched_at = Column(DateTime, default=datetime.utcnow)


class Video(Base):
    __tablename__ = "videos"

    video_id = Column(String, primary_key=True)
    channel_id = Column(String, ForeignKey("channels.channel_id"), nullable=False)
    title = Column(Text, nullable=False)
    description = Column(Text)
    published_at = Column(DateTime)
    duration_seconds = Column(Integer)
    tags = Column(Text)
    category = Column(String)


class VideoStats(Base):
    __tablename__ = "video_stats"

    stat_id = Column(Integer, primary_key=True, autoincrement=True)
    video_id = Column(String, ForeignKey("videos.video_id"), nullable=False)
    snapshot_date = Column(DateTime, default=datetime.utcnow)
    views = Column(BigInteger)
    likes = Column(BigInteger)
    comments = Column(BigInteger)

# ========== 6. Create Tables ==========
if __name__ == "__main__":
    print(f"Creating database at: {DB_PATH}")
    Base.metadata.create_all(engine)
    print("Tables created successfully.")
