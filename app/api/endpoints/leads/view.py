import datetime
import json
import pathlib
from io import StringIO, BytesIO
from multiprocessing.util import get_temp_dir

import aiohttp
import pandas as pd
import typing_extensions
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from fastapi.params import Query
from loguru import logger
from prisma import models, Json, types
from pydantic_core import ValidationError
from starlette import status
from starlette.responses import FileResponse
from typing_extensions import Optional, List, Union

from app import schemas
from app.api.deps import api_key_auth
from app.api.endpoints.leads.crud import lead_schema_to_prisma_model
from app.api.endpoints.leads.serialize import to_formatted_json
from app.settings import prisma, settings

router = APIRouter(
    prefix="/leads",
    tags=["Leads"],
    dependencies=[Depends(api_key_auth)] if not settings.IS_DEBUG else None,
)


@router.post("/", response_model=models.Lead | models.LeadCreateResponse)
async def create_lead(
    lead: schemas.Lead,
    meta__is_test: bool = Query(
        False,
        description="Override `lead.meta.is_test`. Default value `True`. "
                    "Please note that the `lead.api_token` is overwritten when the request is sent",
    ),
):
    lead.meta.is_test = meta__is_test
    lead.api_token = settings.LEADCRAFT_API_KEY
    lead_create_input = lead_schema_to_prisma_model(lead)

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{settings.LEADCRAFT_API_URL}/webmasters/lead",
            json=json.loads(json.dumps(lead_create_input, default=str)),
            headers={"Content-Type": "application/json"},

        ) as response:
            response_data = await response.json()
            if response.status == 200:
                response_model = schemas.LeadCreateResponse(
                    id=response_data["id"],
                    status=response_data["status"],
                    details=[
                        schemas.LeadCreateResponseCampaign(
                            campaignID=k, status=v["status"]
                        )
                        for k, v in response_data["details"].items()
                    ],
                )
                return response_data
            else:
                raise HTTPException(
                    status_code=response.status, detail=response_data
                )
    lead = await prisma.lead.create(
        data=lead_create_input,
    )
    return lead


@router.post("/file")
async def create_lead_from_file(
    file: UploadFile = File(
        ...,
        description="Upload a file containing lead data. Supported file types are `CSV`, `JSON`, `XLSX`. "
                    "For `CSV` and `XLSX`, the file should be structured with columns matching the lead data attributes. "
                    "For `JSON`, each line should be a valid JSON object representing a lead. Encoding `UTF-8`",
    ),
    meta__is_test: bool = Query(
        False, description="Override lead.meta.is_test. Default value `True`"
    ),
):
    # Determine the file type
    file_content = await file.read()
    file_extension = file.filename.split(".")[-1].lower()
    logger.info(
        f"Received file: {file.filename}, type: {file_extension}, size: {len(file_content)} bytes"
    )
    if file_extension == "csv":
        df = pd.read_csv(StringIO(file_content.decode("utf-8")))
    elif file_extension == "xlsx":
        df = pd.read_excel(BytesIO(file_content))
    elif file_extension == "json":
        data = json.loads(file_content)
        df = pd.DataFrame(data)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type",
        )

    leads = to_formatted_json(df, sep=".")

    processed_leads = []
    input_leads = []
    input_leads_prisma_models = []
    for lead_data in leads:
        try:
            lead_data["sales"] = json.loads(lead_data["sales"])
            lead = schemas.Lead.model_validate(lead_data, from_attributes=True)
            lead.meta.is_test = meta__is_test
            lead_create_unput = lead_schema_to_prisma_model(lead)
            input_leads_prisma_models.append(lead_create_unput)
        except ValidationError as e:
            logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=e.errors()
            )
    create_result = await prisma.lead.create_many(data=input_leads_prisma_models)
    return schemas.ResponseModel(
        status=status.HTTP_200_OK,
        message={"created_count": create_result},
    )


@router.get("/template", response_class=FileResponse)
async def download_template(file_ext: schemas.FileExtEnum = Query(...)):
    date = datetime.datetime.now()
    template_file_path = pathlib.Path(
        f"{get_temp_dir()}/lead_template_{int(date.timestamp())}.{file_ext.name}"
    )
    data = json.loads(
        pathlib.Path(__file__).parent.joinpath("schemas.Lead.json").read_bytes()
    )
    df = pd.json_normalize(data)
    df["sales"] = df["sales"].apply(lambda x: json.dumps(x, ensure_ascii=False))
    if file_ext.name == "csv":
        df.to_csv(template_file_path, index=False)
    elif file_ext.name == "xlsx":
        df.to_excel(template_file_path, index=False, sheet_name="Lead")
    elif file_ext.name == "json":
        df.to_json(template_file_path, index=False, orient="records", indent=2)
    return FileResponse(path=template_file_path, filename=template_file_path.name)


@router.get("/{id}", response_model=models.Lead)
async def read_lead(id: int):
    lead = await prisma.lead.find_unique(where={"id": id})
    if lead is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return lead


@router.get("/", response_model=list[models.Lead])
async def read_lead_list(
    take: Optional[int] = Query(50, description="Number of items to take"),
    skip: Optional[int] = Query(0, description="Number of items to skip"),
    where: Optional[Json] = Query(None, description="Filter criteria"),
    cursor: Optional[Json] = Query(None, description="Pagination cursor"),
    include: Optional[Json] = Query(None, description="Related items to include"),
    order: Optional[Union[Json, List[Json]]] = Query(
        '{"id": "asc"}', description="Order of items"
    ),
    distinct: Optional[List[str]] = Query(
        None,
        description=f"Distinct fields {typing_extensions.get_args(types.LeadScalarFieldKeys)}",
    ),
):
    filter_params = schemas.PrismaFilter(
        take=take,
        skip=skip,
        where=where,
        cursor=cursor,
        include=include,
        order=order[0],
        distinct=distinct,
    )
    lead = await prisma.lead.find_many(**filter_params.model_dump(exclude_none=True))
    return lead
