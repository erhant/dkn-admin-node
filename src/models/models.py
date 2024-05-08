from pydantic import BaseModel


class FilterModel(BaseModel):
    hex: str
    hashes: int


class TaskModel(BaseModel):
    taskId: str
    filter: FilterModel
    input: str
    deadline: int
    publicKey: str


class TaskDeliveryModel(BaseModel):
    id: str
    filter: FilterModel
    prompt: str
    public_key: str
