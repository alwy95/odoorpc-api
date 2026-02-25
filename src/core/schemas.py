from pydantic import BaseModel, ConfigDict


class OdooBaseModel(BaseModel):
    _name = "odoorpc.api"
    model_config = ConfigDict(extra="ignore")

    @classmethod
    def fields(cls):
        return list(cls.model_fields.keys())
