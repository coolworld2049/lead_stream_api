from prisma import models

common_excluded = ["createdAt", "updatedAt"]
common_excluded_create = ["id"]

models.Meta.create_partial(
    "MetaCreateWithoutRelationsInput",
    exclude_relational_fields=True,
    exclude=[*common_excluded_create],
)

models.Sale.create_partial(
    "SaleCreateWithoutRelationsInput",
    exclude_relational_fields=True,
    exclude=[*common_excluded_create, "leadId"],
)

models.User.create_partial(
    "UserCreateWithoutRelationsInput",
    exclude_relational_fields=True,
    exclude=[*common_excluded_create],
)
models.Address.create_partial(
    "AddressCreateWithoutRelationsInput",
    exclude_relational_fields=True,
    exclude=[*common_excluded_create, *common_excluded],
)
