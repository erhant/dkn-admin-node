from pydantic import BaseModel


class TaskModel(BaseModel):
    taskId: str
    signature: str
    filter: dict[bytes, int]
    prompt: str
    deadline: float
    pubKey: str
