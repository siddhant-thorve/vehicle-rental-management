from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class BranchCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    city: str = Field(min_length=1, max_length=50)
    address: str = Field(min_length=1, max_length=255)
    contact_no: str | None = Field(default=None, min_length=1, max_length=20)

    @model_validator(mode="after")
    def strip_text_fields(self) -> "BranchCreate":
        for field_name in ("name", "city", "address", "contact_no"):
            value = getattr(self, field_name)
            if value is not None:
                value = value.strip()
                if not value:
                    raise ValueError(f"{field_name} must not be blank")
                setattr(self, field_name, value)
        return self


class BranchUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    city: str | None = Field(default=None, min_length=1, max_length=50)
    address: str | None = Field(default=None, min_length=1, max_length=255)
    contact_no: str | None = Field(default=None, min_length=1, max_length=20)
    is_active: bool | None = None

    @model_validator(mode="after")
    def validate_update_fields(self) -> "BranchUpdate":
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")

        for field_name in ("name", "city", "address"):
            if field_name in self.model_fields_set:
                value = getattr(self, field_name)
                if value is None:
                    raise ValueError(f"{field_name} cannot be null")
                value = value.strip()
                if not value:
                    raise ValueError(f"{field_name} must not be blank")
                setattr(self, field_name, value)

        if self.contact_no is not None:
            self.contact_no = self.contact_no.strip()
            if not self.contact_no:
                raise ValueError("contact_no must not be blank")
        return self


class BranchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    city: str
    address: str
    contact_no: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
