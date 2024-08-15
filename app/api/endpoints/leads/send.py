import aiohttp
from fastapi import APIRouter, Depends, HTTPException

from app import schemas
from app.api.deps import api_key_auth
from app.settings import settings

router = APIRouter(
    prefix="/leads/outgoing",
    tags=["Send Leads"],
    dependencies=[Depends(api_key_auth)] if not settings.IS_DEBUG else None,
)


@router.post(
    "/",
    response_model=schemas.UnicoreResponseHTTP200 | schemas.UnicoreResponseHTTP401 | schemas.UnicoreResponseHTTP422 | dict
)
async def send_lead_to_unicore_ru(
    lead: schemas.SendLead,
):
    lead.token = settings.UNICORE_API_KEY
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{settings.UNICORE_API_URL}/leads/store",
            data=lead.model_dump_json(),
            headers={"Content-Type": "application/json"},
        ) as response:
            response_data = await response.json()
            if response.status == 200:
                return schemas.UnicoreResponseHTTP200(**response_data)
            elif response.status == 401:
                return schemas.UnicoreResponseHTTP401(**response_data)
            elif response.status == 422:
                return schemas.UnicoreResponseHTTP422(**response_data)
            else:
                raise HTTPException(
                    status_code=response.status, detail=response_data
                )
