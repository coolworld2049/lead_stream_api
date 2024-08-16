import json
import pathlib
from datetime import datetime
from io import StringIO, BytesIO
from multiprocessing.util import get_temp_dir

import pandas as pd
import typing_extensions
from fastapi import APIRouter, HTTPException, Depends, UploadFile
from fastapi.params import Query, File
from loguru import logger
from prisma import Json, types
from pydantic_core import ValidationError
from starlette import status
from starlette.responses import FileResponse
from typing_extensions import Optional, List, Union

from app import schemas
from app.api.deps import api_key_auth
from app.api.endpoints.leads.serialize import (
    accept_lead_schema_to_prisma_model,
    to_formatted_json,
)
from app.settings import prisma, settings

router = APIRouter(
    prefix="/leads/incoming",
    tags=["Accept Leads"],
    dependencies=[Depends(api_key_auth)] if not settings.IS_DEBUG else None,
)


@router.post(
    "/", response_model=schemas.ResponseModel, status_code=status.HTTP_201_CREATED
)
async def create_lead(
    lead: schemas.AcceptLeadCreate,
):
    lead_create_input = accept_lead_schema_to_prisma_model(lead)
    lead = await prisma.lead.create(
        data=lead_create_input,
    )
    return schemas.ResponseModel(
        status=status.HTTP_200_OK,
        message="success",
    )


@router.post(
    "/file", response_model=schemas.ResponseModel, status_code=status.HTTP_201_CREATED
)
async def create_lead_from_file(
    file: UploadFile = File(
        ...,
        description="Upload a file containing lead data. Supported file types are `CSV`, `JSON`, `XLSX`. "
        "For `CSV` and `XLSX`, the file should be structured with columns matching the lead data attributes. "
        "For `JSON`, each line should be a valid JSON object representing a lead. Encoding `UTF-8`",
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
            lead = schemas.AcceptLead.model_validate(lead_data, from_attributes=True)
            lead_create_unput = accept_lead_schema_to_prisma_model(lead)
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


@router.get("/file/template", response_class=FileResponse)
async def download_file_leads_template(
    ext: schemas.FileExtEnum = Query(...), example_row: bool = False
):
    date = datetime.now()
    template_file_path = pathlib.Path(
        f"{get_temp_dir()}/accept_lead_template_{int(date.timestamp())}.{ext.name}"
    )
    example_lead = await prisma.lead.find_many(take=1)
    if len(example_lead) < 1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    df = pd.json_normalize(example_lead[0].model_dump())
    df["applied_at"] = df["applied_at"].dt.tz_localize(None)
    df["sales"] = df["sales"].apply(lambda x: json.dumps(x, ensure_ascii=False))
    df_to_save = (
        pd.DataFrame(columns=list(df.iloc[0].to_dict().keys()))
        if not example_row
        else df
    )
    media_type = None
    if ext.name == "csv":
        df_to_save.to_csv(template_file_path, index=False)
    elif ext.name == "xlsx":
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        df_to_save.to_excel(template_file_path, index=False, sheet_name="AcceptLead")
    elif ext.name == "json":
        df_to_save.to_json(template_file_path, index=False, orient="records", indent=2)
    return FileResponse(
        path=template_file_path, filename=template_file_path.name, media_type=media_type
    )


@router.get("/", response_model=schemas.ResponseDataModel)
async def read_leads(
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
    export: schemas.FileExtEnum | None = Query(None),
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
    leads = await prisma.lead.find_many(**filter_params.model_dump(exclude_none=True))
    if len(leads) < 1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if export is not None:
        lead_dict = []
        for item in leads:
            item.applied_at = item.applied_at.replace(tzinfo=None)
            lead_dict.append(item.model_dump())
        date = datetime.now()
        template_file_path = pathlib.Path(
            f"{get_temp_dir()}/lead_template_{int(date.timestamp())}.{export.name}"
        )
        df = pd.json_normalize(lead_dict)
        df["sales"] = df["sales"].apply(lambda x: json.dumps(x, ensure_ascii=False))
        media_type = None
        if export.name == "csv":
            df.to_csv(template_file_path, index=False)
        elif export.name == "xlsx":
            media_type = (
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            df.to_excel(template_file_path, index=False, sheet_name="Lead")
        elif export.name == "json":
            df.to_json(template_file_path, index=False, orient="records", indent=2)
        return FileResponse(
            path=template_file_path,
            filename=template_file_path.name,
            media_type=media_type,
        )
    return schemas.ResponseDataModel(data=leads, count=len(leads))
