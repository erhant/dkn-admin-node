from typing import List

from pydantic import BaseModel, Field, field_validator


class NodeModel(BaseModel):
    uuid: str = Field(..., description="The unique identifier for the node set.")
    nodes: List[str] = Field(..., description="A list of node identifiers.")

    @field_validator('nodes')
    def nodes_must_be_unique(cls, nodes):
        if len(set(nodes)) != len(nodes):
            raise ValueError("Node identifiers must be unique")
        return nodes


class FilterModel(BaseModel):
    hex: str
    hashes: int


class AggregatorTaskModel(BaseModel):
    taskId: str
    filter: FilterModel
    input: str
    deadline: int
    publicKey: str
    privateKey: str


class SearchTaskModel(BaseModel):
    task_id: str
    query_id: str
    type: str
    query: str


class TaskDeliveryModel(BaseModel):
    id: str = Field(..., description="The unique identifier for the task.")
    filter: FilterModel = Field(..., description="The Bloom filter for the task.")
    prompt: str = Field(..., description="The task prompt.")
    public_key: str = Field(..., description="The public key for the task.")


class QuestionModel(BaseModel):
    question: str


class TaskModel(BaseModel):
    taskId: str
    filter: FilterModel
    input: str
    deadline: int
    publicKey: str
