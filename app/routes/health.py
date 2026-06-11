from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/api/health")
def health() -> dict:
    return {"ok": True, "app": "PathfinderKids", "version": "1.0.0"}
