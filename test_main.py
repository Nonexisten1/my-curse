import pytest
from fastapi.testclient import TestClient
from main import app
from database import Base, engine, session_local
from models import Employee, WorkLog

# Создаем тестовый клиент
client = TestClient(app)

# Переопределяем базу данных для тестов
@pytest.fixture(autouse=True)
def setup_test_database():
    # Создаем таблицы
    Base.metadata.create_all(bind=engine)
    yield
    # Очищаем таблицы после теста
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    """Фикстура для работы с базой данных."""
    db = session_local()
    try:
        yield db
    finally:
        db.close()


def test_create_employees_and_worklogs(db_session):
    # 1. Создаем 3 сотрудников
    employees_data = [
        {"name": "Alice", "position": "Developer", "age": 25},
        {"name": "Bob", "position": "Designer", "age": 30},
        {"name": "Charlie", "position": "Manager", "age": 35},
    ]
    employee_ids = []

    for employee in employees_data:
        response = client.post("/employees/", json=employee)
        assert response.status_code == 200
        employee_data = response.json()
        assert employee_data["name"] == employee["name"]
        assert employee_data["position"] == employee["position"]
        assert employee_data["age"] == employee["age"]
        employee_ids.append(employee_data["id"])

    # 2. Добавляем worklogs для сотрудников
    worklogs_data = [
        {"date": "2024-11-18", "hours_worked": 8, "description": "Worked on project A", "employee_id": employee_ids[0]},
        {"date": "2024-11-19", "hours_worked": 6, "description": "Fixed bugs", "employee_id": employee_ids[0]},
        {"date": "2024-11-18", "hours_worked": 7, "description": "Designed UI", "employee_id": employee_ids[1]},
        {"date": "2024-11-19", "hours_worked": 5, "description": "Team meeting", "employee_id": employee_ids[2]},
    ]

    for worklog in worklogs_data:
        response = client.post("/worklogs/", json=worklog)
        assert response.status_code == 200
        worklog_data = response.json()
        assert worklog_data["date"] == worklog["date"]
        assert worklog_data["hours_worked"] == worklog["hours_worked"]
        assert worklog_data["description"] == worklog["description"]
        assert worklog_data["employee"]["id"] == worklog["employee_id"]

    # 3. Проверяем, что сотрудники имеют правильные worklogs
    for i, employee_id in enumerate(employee_ids):
        response = client.get(f"/employees/{employee_id}/worklogs/")
        assert response.status_code == 200
        worklogs = response.json()

        # Проверяем количество worklogs для каждого сотрудника
        employee_worklogs = [wl for wl in worklogs_data if wl["employee_id"] == employee_id]
        assert len(worklogs) == len(employee_worklogs)

        # Проверяем содержимое worklogs
        for worklog, expected in zip(worklogs, employee_worklogs):
            assert worklog["date"] == expected["date"]
            assert worklog["hours_worked"] == expected["hours_worked"]
            assert worklog["description"] == expected["description"]
