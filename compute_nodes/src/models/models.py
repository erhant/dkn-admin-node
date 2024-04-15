from pydantic import BaseModel


class InputModel(BaseModel):
    prompt: str
    context: str
    pkey: str


class OutputModel(BaseModel):
    result: str
    h: str
    s: str
    e: str
