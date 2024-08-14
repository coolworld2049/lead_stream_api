from prisma import Json, types
from typing_extensions import Any

from app import schemas


def lead_schema_to_prisma_model(lead: schemas.Lead, update: dict[str, Any] = None):
    dump = lead.model_copy(update=update).model_dump()
    attributes = schemas.LeadAttributes(**dump).model_dump(exclude={"sales"})
    attributes_json = {k: Json(v) for k, v in attributes.items()}
    attributes_json.update({"sales": [x.model_dump() for x in lead.sales]})
    lead_create_unput = types.LeadCreateInput(
        **schemas.LeadBase(**dump).model_dump(), **attributes_json
    )
    return lead_create_unput
