from fastapi import APIRouter, HTTPException, Request, Query
from app.api.v1.handlers import features_handler

router = APIRouter()

@router.get("/features/{feature_name}")
async def use_feature(feature_name: str, user_id: str = Query(...), request: Request = None):
    ip_address = request.client.host if request else "unknown"
    user_agent = request.headers.get("user-agent") if request else "unknown"
    session_id = request.cookies.get("session")  # get FastAPI session cookie

    result, error = features_handler.handle_feature_use(user_id, feature_name, ip_address, user_agent,session_id)
    if error:
        if error == "Feature not found.":
            raise HTTPException(status_code=404, detail=error)
        elif error == "User wallet not found.":
            raise HTTPException(status_code=404, detail=error)
        elif error == "Insufficient credits.":
            raise HTTPException(status_code=402, detail=error)
        else:
            raise HTTPException(status_code=400, detail=error)

    return result
