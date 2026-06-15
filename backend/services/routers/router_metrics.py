from fastapi import APIRouter, Depends
from typing import Annotated

from services.service_auth import get_current_user
from metrics import getMetrics, getMetricsDetails
from schemas import userLogin

router = APIRouter(prefix="/metrics", tags=["metrics"])

@router.get("/")
async def getProjectMetrics(current_user: Annotated[userLogin, Depends(get_current_user)],
                            project_id: int):
    return await getMetrics(project_id)

@router.get("/details")
async def getDetails(current_user: Annotated[userLogin, Depends(get_current_user)],
                     metric_id: int):
    return await getMetricsDetails(metric_id)