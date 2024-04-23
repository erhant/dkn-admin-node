
from pydantic import BaseModel


class PublishModel(BaseModel):
    jobId: str
    signature: str
    filter: dict[bytes, int]
    prompt: str
    deadline: float
    pubKey: str

