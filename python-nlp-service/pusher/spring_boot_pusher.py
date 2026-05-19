import logging

import httpx

from config import settings
from models.schemas import EmotionResult, RiskLevel

logger = logging.getLogger(__name__)

_ENDPOINT = "/api/v1/emotion-records/batch"


def _build_payload(
    source: str,
    results: list[EmotionResult],
    risk_map: dict[str, RiskLevel],
) -> dict:
    return {
        "source": source,
        "records": [
            {
                "externalUserId": r.external_user_id,
                "postId": r.record_id,
                "textSnippet": r.text_snippet,
                "postedAt": r.recorded_at.isoformat(),
                "emotionLabel": r.emotion_label,
                "emotionScore": round(r.emotion_score, 4),
                "positiveScore": round(r.positive_score, 4),
                "neutralScore": round(r.neutral_score, 4),
                "negativeScore": round(r.negative_score, 4),
                "riskLevel": risk_map.get(r.external_user_id, RiskLevel.LOW).value,
            }
            for r in results
        ],
    }


def push(
    source: str,
    results: list[EmotionResult],
    risk_map: dict[str, RiskLevel],
) -> dict | None:
    if not results:
        logger.info("No results to push")
        return None

    url = f"{settings.spring_boot_url}{_ENDPOINT}"
    payload = _build_payload(source, results, risk_map)

    try:
        with httpx.Client(timeout=30) as client:
            resp = client.post(
                url,
                json=payload,
                headers={"X-API-Key": settings.nlp_service_api_key},
            )
            resp.raise_for_status()
            data = resp.json()
            logger.info(
                "Pushed %d records → saved=%s skipped=%s alerts=%s",
                len(results),
                data.get("saved"),
                data.get("skipped"),
                data.get("alertsTriggered"),
            )
            return data
    except httpx.HTTPStatusError as e:
        logger.error("Push failed: HTTP %s — %s", e.response.status_code, e.response.text)
    except Exception as e:
        logger.error("Push failed: %s", e)
    return None
