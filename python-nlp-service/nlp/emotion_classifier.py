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


def load_model() -> None:
    """Public entry point to warm up the model at startup."""
    _get_classifier()


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
    clf = _get_classifier()
    results: list[EmotionResult] = []

    for i in range(0, len(records), batch_size):
        batch = records[i : i + batch_size]
        texts = [_preprocess(r.text) for r in batch]
        try:
            # Native batching: clf([text1, text2, ...]) is faster than one-by-one
            batch_outputs = clf(texts)
            for record, output in zip(batch, batch_outputs):
                scores: dict[str, float] = {}
                for item in output:
                    label = item["label"].lower()
                    if "neg" in label or label == "label_0":
                        scores["negative"] = item["score"]
                    elif "pos" in label or label == "label_2":
                        scores["positive"] = item["score"]
                    else:
                        scores["neutral"] = item["score"]
                scores.setdefault("negative", 0.0)
                scores.setdefault("neutral", 0.0)
                scores.setdefault("positive", 0.0)
                dominant = max(scores, key=scores.get)
                results.append(EmotionResult(
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
                ))
        except Exception as e:
            logger.warning("Batch classification failed (i=%d): %s — falling back one-by-one", i, e)
            for record in batch:
                try:
                    results.append(classify(record))
                except Exception as inner:
                    logger.warning("Single classify failed for %s: %s", record.record_id, inner)
    return results
