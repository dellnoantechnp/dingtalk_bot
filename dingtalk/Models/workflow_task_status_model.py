import math
from datetime import datetime
from typing import List, Self, Optional

from nice_duration import duration_string
from pydantic import BaseModel, Field, model_validator


class WorkflowTaskNodeStatus(BaseModel):
    name: str = Field(description="The name of the workflow task")
    status: str = Field(default=None, description="The status of the task")
    duration_time: float = Field(default=None, description="The duration of the task", exclude=True)
    duration: str = Field(default=None, description="The duration of the workflow task")
    started_at: datetime = Field(default=None, description="The time the workflow was started")
    message: Optional[str] = Field(default=None, description="The message of the workflow task")


class WorkflowTaskStatusModel(BaseModel):
    namespace: str = Field(description="The namespace of the workflow task")
    name: str = Field(description="The name of the task")
    status: str = Field(default=None, description='Phase a simple, high-level summary of where the workflow is in its '
                                                  'lifecycle. Will be "" (Unknown), "Pending", or "Running" before the '
                                                  'workflow is completed, and "Succeeded", "Failed" or "Error" once the'
                                                  'workflow has completed.')
    suspend: Optional[bool] = Field(default=False, description="Suspend will suspend the workflow and prevent "
                                                               "execution of any"
                                                               "future steps in the workflow")
    progress: Optional[float] = Field(default=None, description="Progress to completion")
    total_task_count: int = Field(default=1, description="The number of tasks in the workflow template")
    complete_task_count: int = Field(default=0, description="The number of tasks in the workflow complete")
    started_at: datetime = Field(default=None, description="The time the workflow was started")
    finished_at: datetime = Field(default=None, description="The time the workflow was finished")
    duration: Optional[str] = Field(default=None, description="The duration of the workflow task")
    nodes: List[WorkflowTaskNodeStatus] = Field(default=None, description="The status of the workflow nodes")

    @model_validator(mode="after")
    def check_status(self) -> Self:
        # 增加暂停状态
        if self.suspend:
            self.status = "Paused"
        # 处理暂停状态下，duration 耗时为所有任务的duration之和
        if self.status == "Paused":
            self.duration = duration_string(seconds=sum(item.duration_time for item in self.nodes))
        # 如果实际任务数大于模板任务数，修改模板任务数
        if self.complete_task_count > self.total_task_count:
            self.total_task_count = self.complete_task_count
        self.progress = round(self.complete_task_count / self.total_task_count * 100, 1)
        # progress 99%
        if self.status != "Succeeded" and self.progress == 100:
            self.progress = self.progress - 1
        self.duration = duration_string(timedelta=self.finished_at - self.started_at)
        return self
