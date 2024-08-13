from fastapi import APIRouter, HTTPException, Depends
from prisma import models
from starlette import status
from starlette.responses import JSONResponse

from app import schemas
from app.api.deps import api_key_auth
from app.settings import prisma

router = APIRouter(
    prefix="/leads", tags=["Leads"], dependencies=[Depends(api_key_auth)]
)


@router.post("/", response_model=models.Lead)
async def create_lead(
    lead: schemas.LeadCreateInput,
):
    data = {
        "type": lead.type,
        "apiToken": lead.apiToken,
        "product": lead.product,
        "stream": lead.stream,
        "meta": lead.meta.create.model_dump(),
        "sales": [x.model_dump() for x in lead.sales.create],
        "user": lead.user.create.model_dump(),
        "addressReg": lead.addressReg.create.model_dump(),
        "addressFact": lead.addressFact.create.model_dump(),
    }
    lead = await prisma.lead.create(
        data=data,
        include={
            "meta": True,
            "sales": True,
            "user": True,
            "addressReg": True,
            "addressFact": True,
        },
    )
    return lead


@router.get("/{id}", response_model=models.Lead)
async def read_lead(id: int):
    lead = await prisma.lead.find_unique(where={"id": id})
    if lead is None:
        raise HTTPException(status_code=404, detail="schemas.Lead not found")
    return lead


@router.get("/", response_model=list[models.Lead])
async def read_lead_list():
    lead = await prisma.lead.find_many()
    return lead


@router.put("/{id}", response_model=models.Lead)
async def update_lead(id: int, lead_obj: models.Lead):
    lead = await prisma.lead.update(data=lead_obj, where={"id": lead_obj.id})
    return lead


@router.delete("/{id}", response_model=models.Lead)
async def delete_lead(id: int):
    lead = await prisma.lead.delete(where={"id": id})
    return JSONResponse(status_code=status.HTTP_200_OK, content="success")
