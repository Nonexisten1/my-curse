from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
    start_date = Column(Date)
    end_date = Column(Date, nullable=True)

    employees = relationship("EmployeeProject", back_populates="project", cascade="all, delete-orphan")


class EmployeeProject(Base):
    __tablename__ = "employee_projects"

    employee_id = Column(Integer, ForeignKey("employees.id"), primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), primary_key=True)
    role = Column(String, nullable=True)  # Роль сотрудника в проекте

    employee = relationship("Employee", back_populates="projects")
    project = relationship("Project", back_populates="employees")


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    position = Column(String)
    age = Column(Integer)

    projects = relationship("EmployeeProject", back_populates="employee")
    worklogs = relationship("WorkLog", back_populates="employee")


class WorkLog(Base):
    __tablename__ = "worklogs"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date)
    hours_worked = Column(Integer)
    description = Column(String)
    employee_id = Column(Integer, ForeignKey("employees.id"))

    employee = relationship("Employee", back_populates="worklogs")
