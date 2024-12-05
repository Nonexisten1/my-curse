from pydantic import BaseModel
from datetime import date
from typing import List, Optional


class EmployeeBase(BaseModel):
    name: str
    position: str
    age: int


class EmployeeCreate(EmployeeBase):
    pass


class WorkLogBase(BaseModel):
    date: date
    hours_worked: int
    description: str
    employee_id: int


class WorkLogCreate(WorkLogBase):
    pass


class EmployeeSummary(BaseModel):
    id: int
    name: str
    position: str

    class Config:
        orm_mode = True


class WorkLogResponse(WorkLogBase):
    id: int
    employee: Optional[EmployeeSummary]

    class Config:
        orm_mode = True


class Employee(EmployeeBase):
    id: int
    worklogs: List[WorkLogResponse] = []

    class Config:
        orm_mode = True


class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None


class ProjectCreate(ProjectBase):
    pass


class Project(ProjectBase):
    id: int

    class Config:
        orm_mode = True


class EmployeeProjectBase(BaseModel):
    employee_id: int
    project_id: int
    role: Optional[str] = None


class EmployeeProject(EmployeeProjectBase):
    pass
