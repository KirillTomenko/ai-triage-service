import logging
from fastapi import APIRouter, HTTPException

from app.schemas import TriageRequest, TriageResponse
from app.llm import classify_ticket
from app.database import save_ticket
from app.limiter import check_rate_limit

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/triage", response_model=TriageResponse)
async def triage(req: TriageRequest):
    check_rate_limit(req.client_id)

    result = await classify_ticket(req.text)
    error = result.pop("error", None)

    ticket_id = await save_ticket(
        client_id=req.client_id,
        channel=req.channel,
        text=req.text,
        category=result["category"],
        confidence=result["confidence"],
        escalate=result["escalate"],
        draft_reply=result["draft_reply"],
        error=error,
    )

    logger.info(
        "ticket=%d client=%s channel=%s category=%s confidence=%s escalate=%s",
        ticket_id,
        req.client_id,
        req.channel,
        result["category"],
        result["confidence"],
        result["escalate"],
    )

    return TriageResponse(ticket_id=ticket_id, **result)
