"""Pydantic 请求/响应模型。"""

from pydantic import BaseModel, Field, field_validator


class ClassIn(BaseModel):
    name: str = Field(min_length=1, max_length=30)
    grade: str | None = Field(default=None, max_length=30)
    color: str | None = Field(default=None, max_length=20)


class ClassPatch(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=30)
    grade: str | None = Field(default=None, max_length=30)
    color: str | None = Field(default=None, max_length=20)
    sort_order: int | None = None


class ClassDeleteIn(BaseModel):
    confirm_name: str


class StudentIn(BaseModel):
    name: str = Field(min_length=1, max_length=20)
    student_no: str | None = Field(default=None, max_length=20)
    seat_no: int | None = Field(default=None, ge=1, le=99)
    species: str | None = None

    @field_validator("student_no")
    @classmethod
    def _strip_no(cls, v: str | None) -> str | None:
        if v is None:
            return None
        v = v.strip()
        return v or None


class StudentPatch(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=20)
    student_no: str | None = Field(default=None, max_length=20)
    seat_no: int | None = Field(default=None, ge=1, le=99)
    is_present: bool | None = None


class BulkIn(BaseModel):
    text: str = Field(max_length=20000)
    preview: bool = True


class ScoreIn(BaseModel):
    delta: int = Field(ge=-5, le=5)
    reason: str | None = Field(default=None, max_length=60)

    @field_validator("delta")
    @classmethod
    def _nonzero(cls, v: int) -> int:
        if v == 0:
            raise ValueError("delta 不能为 0")
        return v


class SwitchPetIn(BaseModel):
    species: str


class RollcallIn(BaseModel):
    mode: str = Field(default="fair", pattern="^(fair|random)$")
    exclude_absent: bool = True


class SettingsPatch(BaseModel):

    motion_pref: str | None = Field(default=None, pattern="^(system|reduced)$")
    display_sort: str | None = Field(default=None, pattern="^(seat|score)$")


class ImportIn(BaseModel):
    confirm: str
    backup: dict