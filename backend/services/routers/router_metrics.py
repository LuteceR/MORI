from fastapi import APIRouter, Depends
from typing import Annotated

from services.service_auth import get_current_user
from metrics import createCommonMetricsLabels, getMetrics
from schemas import userLogin

router = APIRouter(prefix="/metrics", tags=["metrics"])

@router.get("/")
async def getProjectMetrics(current_user: Annotated[userLogin, Depends(get_current_user)],
                            project_id: int):
    return await getMetrics(project_id)

# TODO: DEV-функция!
@router.patch("/create")
async def createCommonMetricsLabelsYeah(current_user: Annotated[userLogin, Depends(get_current_user)]):
    await createCommonMetricsLabels()
    return "Metrics are here"