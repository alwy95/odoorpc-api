from datetime import datetime, timedelta

from pydantic import BaseModel, Field, computed_field, field_validator


class PageParams(BaseModel):
    model_config = {"extra": "forbid"}

    offset: int = Field(0, ge=0)
    limit: int = Field(2000, ge=1, le=2000)

    create_date_from: datetime = Field(
        default=datetime.now()
        .replace(hour=0, minute=0, second=0)
        .strftime("%Y-%m-%d %H:%M:%S")
    )

    create_date_to: datetime = Field(
        default=(datetime.now() + timedelta(days=1))
        .replace(hour=0, minute=0, second=0)
        .strftime("%Y-%m-%d %H:%M:%S")
    )

    @field_validator("create_date_from", "create_date_to", mode="after")
    @classmethod
    def datetime_to_str(cls, value):
        return value.strftime("%Y-%m-%d %H:%M:%S")

    @computed_field
    @property
    def domain(self) -> list:
        return [
            ["create_date", ">=", self.create_date_from],
            ["create_date", "<=", self.create_date_to],
        ]

    @computed_field
    @property
    def param_domain_dict(self) -> dict:
        return {
            "create_date_from": self.create_date_from,
            "create_date_to": self.create_date_to,
        }

    @computed_field
    @property
    def param_dict(self) -> dict:
        params = self.param_domain_dict
        params["limit"] = self.limit
        params["offset"] = self.offset
        return params
