from fastapi import APIRouter, Depends, HTTPException
from prisma import models
from starlette import status
from starlette.responses import JSONResponse

router = APIRouter(prefix="/leads", tags=["Leads"])


@router.post("/", response_model=models.Person)
def create_Lead(
    lead: models.Lead,
):
    Lead = lead_repo.add(lead)
    return Lead


@router.get("/{id}", response_model=models.Lead)
def read_Lead(
    id: int, lead_repo: LeadRepository = Depends(lambda: get_repository(LeadRepository))
):
    Lead = lead_repo.get_by_id(id)
    if Lead is None:
        raise HTTPException(status_code=404, detail="schemas.Lead not found")
    return Lead


@router.get("/", response_model=list[models.Lead])
def read_Lead_list(

):
    Leads = lead_repo.list()
    return Leads


@router.put("/{id}", response_model=models.Lead)
def update_Lead(
    id: int,
    lead: models.Lead,

):
    try:
        updated_Lead = lead_repo.update(lead)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=",".join(e.args)
        )
    return updated_Lead


@router.delete("/{id}", response_model=models.Lead)
def delete_Lead(
    id: int, lead_repo: LeadRepository = Depends(lambda: get_repository(LeadRepository))
):
    lead_repo.delete(id)
    return JSONResponse(status_code=status.HTTP_200_OK, content="success")
