from fastapi import APIRouter

router = APIRouter(tags=["Health Check"])

@router.get("/health", summary="Health Check Endpoint")
def health():
    return {"status": "ok"}