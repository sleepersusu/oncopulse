import logging
import re

from transformers import pipeline

from config import settings
from models.schemas import EmotionResult, RawTextRecord

logger = logging.getLogger(__name__)

_classifier = None


def _get_classifier():
    global _classifier
    if _classifier is None:
        logger.info("Loading emotion model: %s", settings.emotion_model_name)
        _classifier = pipeline(
            "sentiment-analysis",
            model=settings.emotion_model_name,
            top_k=None,
        )
        logger.info("Emotion model loaded")
    return _classifier


def _preprocess(text: str) -> str:
    text = re.sub(r"http\S+", "[URL]", text)
    text = re.sub(r"@\w+", "[USER]", text)
    text = re.sub(r"\n+", " ", text)
    return text.strip()[:2000]


def classify(record: RawTextRecord) -> EmotionResult:
    clf = _get_classifier()
    text = _preprocess(record.text)
    results = clf(text)[0]

    scores: dict[str, float] = {}
    for r in results:
        label = r["label"].lower()
        # model may use label_0/label_1/label_2 — normalise
        if "neg" in label or label == "label_0":
            scores["negative"] = r["score"]
        elif "pos" in label or label == "label_2":
            scores["positive"] = r["score"]
        else:
            scores["neutral"] = r["score"]

    scores.setdefault("negative", 0.0)
    scores.setdefault("neutral", 0.0)
    scores.setdefault("positive", 0.0)

    dominant = max(scores, key=scores.get)

    return EmotionResult(
        external_user_id=record.external_user_id,
        source=record.source,
        record_id=record.record_id,
        recorded_at=record.recorded_at,
        text_snippet=record.text[:200],
        emotion_label=dominant,
        emotion_score=scores[dominant],
        positive_score=scores["positive"],
        neutral_score=scores["neutral"],
        negative_score=scores["negative"],
    )


def classify_batch(records: list[RawTextRecord], batch_size: int = 32) -> list[EmotionResult]:
    results: list[EmotionResult] = []
    for i in range(0, len(records), batch_size):
        batch = records[i : i + batch_size]
        for record in batch:
            try:
                results.append(classify(record))
            except Exception as e:
                logger.warning("Classification failed for %s: %s", record.record_id, e)
    return results
