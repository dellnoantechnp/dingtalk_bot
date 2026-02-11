from typing import Self

from pydantic import BaseModel, Field, model_validator


class WorkflowOutputParameterModel(BaseModel):
    """workflows task output parameters"""
    workflow_id: str = Field(default=None, description="workflow id")
    node_id: str = Field(default=None, description="workflow task node id")
    template_name: str = Field(default=None, description="workflow template name")
    name: str = Field(default=None, description="Parameters name")
    value: str = Field(default=None, description="Parameters value")
    description: str = Field(default=None, description="Parameters description string")

    @property
    def ok(self) -> bool:
        return bool(self.value)