import hashlib
import logging
from datetime import datetime, timezone

import praw

from config import settings
from models.schemas import RawTextRecord

logger = logging.getLogger(__name__)

SUBREDDITS = [
    "cancer",
    "breastcancer",
    "leukemia",
    "lymphoma",
    "coloncancer",
]

reddit = praw.Reddit(
    client_id=settings.reddit_client_id,
    client_secret=settings.reddit_client_secret,
    user_agent=settings.reddit_user_agent,
)


def _hash_user(username: str) -> str:
    raw = f"{settings.reddit_hash_salt}:{username}"
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


def _clean(text: str) -> str:
    return text.strip() if text and text.strip() != "[removed]" else ""


def collect(subreddit_name: str, limit: int = 100) -> list[RawTextRecord]:
    records: list[RawTextRecord] = []
    try:
        sub = reddit.subreddit(subreddit_name)
        for post in sub.new(limit=limit):
            body = _clean(post.selftext)
            title = _clean(post.title)
            text = f"{title}\n{body}".strip() if body else title
            if not text:
                continue
            if post.author is None:
                continue
            records.append(
                RawTextRecord(
                    external_user_id=_hash_user(post.author.name),
                    source="reddit",
                    record_id=post.id,
                    text=text,
                    recorded_at=datetime.fromtimestamp(
                        post.created_utc, tz=timezone.utc
                    ),
                )
            )
    except Exception as e:
        logger.error("Reddit collect failed for r/%s: %s", subreddit_name, e)
    return records


def collect_all(limit_per_sub: int = 100) -> list[RawTextRecord]:
    all_records: list[RawTextRecord] = []
    for sub in SUBREDDITS:
        records = collect(sub, limit=limit_per_sub)
        logger.info("r/%s: %d records collected", sub, len(records))
        all_records.extend(records)
    return all_records
