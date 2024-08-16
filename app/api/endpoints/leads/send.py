import json
import pathlib
from datetime import datetime
from io import StringIO, BytesIO
from multiprocessing.util import get_temp_dir

import aiohttp
import pandas as pd
from fastapi import APIRouter, HTTPException, Depends, UploadFile
from fastapi.params import Query, File
from loguru import logger
from pydantic_core import ValidationError
from starlette import status
from starlette.responses import FileResponse

from app import schemas
from app.api.deps import api_key_auth
from app.api.endpoints.leads.serialize import to_formatted_json
from app.settings import settings

router = APIRouter(
    prefix="/leads/outgoing",
    tags=["Send Leads"],
    dependencies=[Depends(api_key_auth)] if not settings.IS_DEBUG else None,
)


async def send_lead_to_unicore(lead: schemas.SendLeadCreate):
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
                raise HTTPException(status_code=response.status, detail=response_data)


@router.post(
    "/",
    response_model=schemas.UnicoreResponseHTTP200
    | schemas.UnicoreResponseHTTP401
    | schemas.UnicoreResponseHTTP422
    | dict,
)
async def send_lead_to_unicore_ru(
    lead: schemas.SendLeadCreate,
):
    result = await send_lead_to_unicore(lead)
    return result


@router.post(
    "/file", response_model=schemas.ResponseModel, status_code=status.HTTP_201_CREATED
)
async def create_send_lead_from_file(
    file: UploadFile = File(
        ...,
        description="Upload a file containing lead data. Supported file types are `CSV`, `JSON`, `XLSX`. "
        "For `CSV` and `XLSX`, the file should be structured with columns matching the lead data attributes. "
        "For `JSON`, each line should be a valid JSON object representing a lead. Encoding `UTF-8`",
    ),
):
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

    processed_leads = []
    count = 0
    errors = []
    leads = to_formatted_json(df)
    for i, lead_data in enumerate(leads):
        try:
            logger.info(i)
            result = await send_lead_to_unicore(schemas.SendLeadCreate(**lead_data))
            count += 1
            processed_leads.append(result.model_dump())
        except ValidationError as e:
            logger.error(e)
            errors.append(e.__str__())
    if len(errors) > 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=errors)
    return schemas.ResponseModel(
        status=status.HTTP_200_OK,
        message={"sent_number": count, "errors": errors, "result": processed_leads},
    )


@router.get("/file/template", response_class=FileResponse)
async def download_file_send_leads_template(ext: schemas.FileExtEnum = Query(...)):
    date = datetime.now()
    template_file_path = pathlib.Path(
        f"{get_temp_dir()}/send_lead_template_{int(date.timestamp())}.{ext.name}"
    )
    df_to_save = pd.DataFrame(columns=list(schemas.SendLeadCreate.model_fields.keys()))
    media_type = None
    if ext.name == "csv":
        df_to_save.to_csv(template_file_path, index=False)
    elif ext.name == "xlsx":
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        df_to_save.to_excel(template_file_path, index=False, sheet_name="SendLeads")
    elif ext.name == "json":
        df_to_save.to_json(template_file_path, index=False, orient="records", indent=2)
    return FileResponse(
        path=template_file_path, filename=template_file_path.name, media_type=media_type
    )
