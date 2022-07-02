import typing

import strawberry


@strawberry.type
class GqlBlock:
    id: int
    timestamp_unix: int
    tx_id: str
    user_id: str
    vote: str


@strawberry.type
class GqlBlocksList:
    code: int
    errors: list[str]
    blocks: list[GqlBlock]  # todo


@strawberry.type
class GqlEntity:
    id: int
    entity_id: str
    entity_key: str
    entity_name: str
    name: str
    node: int
    slug: str
    type_name: str
    type_value: str


@strawberry.type
class GqlEntitiesList:
    code: int
    errors: list[str]
    objects: list[GqlEntity]


@strawberry.type
class GqlUser:
    id: int
    credentials_count: int
    emails_count: int
    mobile: str
    mobile_count: int
    state: str
    totp_count: int
    user_id: str


@strawberry.type
class GqlUserGet:
    code: int
    errors: list[str]
    user: typing.Optional[GqlUser]


@strawberry.type
class GqlUsersList:
    code: int
    errors: list[str]
    objects: list[GqlUser]
