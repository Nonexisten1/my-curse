from fastapi import FastAPI, HTTPException, Depends
from typing import List
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from models import (
    Base, Employee, WorkLog, Project, EmployeeProject
)
from database import engine, session_local
from schemas import (
    ProjectCreate, Project as DbProject, 
    EmployeeCreate, Employee as DbEmployee, 
    WorkLogCreate, WorkLogResponse, 
    EmployeeProjectBase
)

app = FastAPI()

# CORS settings
origins = [
    "http://localhost:8084",
    "http://127.0.0.1:8084"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)


def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()


@app.post("/employees/", response_model=DbEmployee)
async def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)) -> DbEmployee:
    db_employee = Employee(name=employee.name, position=employee.position, age=employee.age)
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee


@app.post("/worklogs/", response_model=WorkLogResponse)
async def create_worklog(worklog: WorkLogCreate, db: Session = Depends(get_db)) -> WorkLogResponse:
    db_employee = db.query(Employee).filter(Employee.id == worklog.employee_id).first()
    if db_employee is None:
        raise HTTPException(status_code=404, detail='Employee not found')

    db_worklog = WorkLog(date=worklog.date, hours_worked=worklog.hours_worked, description=worklog.description, employee_id=worklog.employee_id)
    db.add(db_worklog)
    db.commit()
    db.refresh(db_worklog)
    return db_worklog


@app.get("/employees/", response_model=List[DbEmployee])
async def get_employees(db: Session = Depends(get_db)):
    return db.query(Employee).all()


@app.get("/employees/{employee_id}", response_model=DbEmployee)
async def get_employee(employee_id: int, db: Session = Depends(get_db)):
    db_employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if db_employee is None:
        raise HTTPException(status_code=404, detail='Employee not found')
    return db_employee


@app.get("/worklogs/", response_model=List[WorkLogResponse])
async def get_worklogs(db: Session = Depends(get_db)):
    return db.query(WorkLog).all()


@app.get("/employees/{employee_id}/worklogs/", response_model=List[WorkLogResponse])
async def get_worklogs_for_employee(employee_id: int, db: Session = Depends(get_db)):
    return db.query(WorkLog).filter(WorkLog.employee_id == employee_id).all()


@app.delete("/employees/{employee_id}", status_code=204)
async def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    db_employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    db.delete(db_employee)
    db.commit()
    return {"message": "Employee deleted successfully"}


@app.delete("/worklogs/{worklog_id}", status_code=204)
async def delete_worklog(worklog_id: int, db: Session = Depends(get_db)):
    db_worklog = db.query(WorkLog).filter(WorkLog.id == worklog_id).first()
    if db_worklog is None:
        raise HTTPException(status_code=404, detail="WorkLog not found")
    db.delete(db_worklog)
    db.commit()
    return {"message": "WorkLog deleted successfully"}


@app.put("/employees/{employee_id}", response_model=DbEmployee)
async def update_employee(employee_id: int, employee: EmployeeCreate, db: Session = Depends(get_db)):
    db_employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    db_employee.name = employee.name
    db_employee.position = employee.position
    db_employee.age = employee.age
    db.commit()
    db.refresh(db_employee)
    return db_employee


@app.put("/worklogs/{worklog_id}", response_model=WorkLogResponse)
async def update_worklog(worklog_id: int, worklog: WorkLogCreate, db: Session = Depends(get_db)):
    db_worklog = db.query(WorkLog).filter(WorkLog.id == worklog_id).first()
    if db_worklog is None:
        raise HTTPException(status_code=404, detail="WorkLog not found")
    db_worklog.date = worklog.date
    db_worklog.hours_worked = worklog.hours_worked
    db_worklog.description = worklog.description
    db_worklog.employee_id = worklog.employee_id
    db.commit()
    db.refresh(db_worklog)
    return db_worklog


# CRUD for Projects
@app.post("/projects/", response_model=DbProject)
async def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    db_project = Project(
        name=project.name, description=project.description,
        start_date=project.start_date, end_date=project.end_date
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


@app.get("/projects/", response_model=List[DbProject])
async def get_projects(db: Session = Depends(get_db)):
    return db.query(Project).all()


# Assign Employee to Project
@app.post("/employee-projects/", status_code=204)
async def assign_employee_to_project(data: EmployeeProjectBase, db: Session = Depends(get_db)):
    db_employee_project = EmployeeProject(
        employee_id=data.employee_id, project_id=data.project_id, role=data.role
    )
    db.add(db_employee_project)
    db.commit()
    return {"message": "Employee assigned to project successfully"}


# Update a project by id
@app.put("/projects/{project_id}", response_model=DbProject)
async def update_project(project_id: int, project: ProjectCreate, db: Session = Depends(get_db)):
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db_project.name = project.name
    db_project.description = project.description
    db_project.start_date = project.start_date
    db_project.end_date = project.end_date
    
    db.commit()
    db.refresh(db_project)
    return db_project


# Delete a project by id
@app.delete("/projects/{project_id}", status_code=204)
async def delete_project(project_id: int, db: Session = Depends(get_db)):
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(db_project)
    db.commit()
    return {"message": "Project deleted successfully"}


# Get Employees by Project ID
@app.get("/projects/{project_id}/employees/", response_model=List[DbEmployee])
async def get_employees_by_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    employee_projects = db.query(EmployeeProject).filter(EmployeeProject.project_id == project_id).all()
    employee_ids = [emp_proj.employee_id for emp_proj in employee_projects]
    
    employees = db.query(Employee).filter(Employee.id.in_(employee_ids)).all()
    
    return employees


@app.delete("/employee-projects/", status_code=204)
async def remove_employee_from_project(employee_id: int, project_id: int, db: Session = Depends(get_db)):
    # Проверяем, существует ли сотрудник и проект
    db_employee = db.query(Employee).filter(Employee.id == employee_id).first()
    db_project = db.query(Project).filter(Project.id == project_id).first()

    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Проверяем, существует ли связь между сотрудником и проектом
    db_employee_project = db.query(EmployeeProject).filter(
        EmployeeProject.employee_id == employee_id,
        EmployeeProject.project_id == project_id
    ).first()

    if not db_employee_project:
        raise HTTPException(status_code=404, detail="Employee is not assigned to this project")
    
    # Удаляем связь сотрудника и проекта
    db.delete(db_employee_project)
    db.commit()
    return {"message": "Employee removed from project successfully"}