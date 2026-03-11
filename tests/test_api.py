import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date, timedelta

from app.main import app
from app.database import Base, SessionLocal
from app.dependencies.auth_dependency import get_db
from app.models.user_model import User
from app.models.role_model import Role
from app.models.attendance_model import Attendance
from app.models.leave_model import Leave, LeaveStatus
from passlib.context import CryptContext

# Test Database Setup
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Clear and setup test database for each test"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Create roles
    db = TestingSessionLocal()
    admin_role = Role(id=1, name="admin")
    employee_role = Role(id=2, name="employee")
    manager_role = Role(id=3, name="manager")
    db.add_all([admin_role, employee_role, manager_role])

    # Create test users
    admin_user = User(
        id=1,
        employee_id="ADMIN001",
        full_name="Admin User",
        email="admin@test.com",
        department="Administration",
        password=pwd_context.hash("Admin@123"),
        role_id=1
    )

    manager_user = User(
        id=2,
        employee_id="MGR001",
        full_name="Manager User",
        email="manager@test.com",
        department="HR",
        password=pwd_context.hash("Manager@123"),
        role_id=3
    )

    employee_user = User(
        id=3,
        employee_id="EMP001",
        full_name="Employee User",
        email="employee@test.com",
        department="Engineering",
        password=pwd_context.hash("Employee@123"),
        role_id=2
    )

    db.add_all([admin_user, manager_user, employee_user])
    db.commit()
    db.close()

    yield

    Base.metadata.drop_all(bind=engine)


# ------- AUTH TESTS -------


class TestAuth:
    def test_login_success(self):
        """Test successful login"""
        response = client.post(
            "/auth/login",
            json={"email": "admin@test.com", "password": "Admin@123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data
        assert data["user"]["email"] == "admin@test.com"
        assert data["user"]["employee_id"] == "ADMIN001"

    def test_login_invalid_password(self):
        """Test login with wrong password"""
        response = client.post(
            "/auth/login",
            json={"email": "admin@test.com", "password": "WrongPassword"}
        )
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False

    def test_login_nonexistent_email(self):
        """Test login with non-existent email"""
        response = client.post(
            "/auth/login",
            json={"email": "nonexistent@test.com", "password": "Password@123"}
        )
        assert response.status_code == 401


# ------- USER TESTS -------


class TestUsers:
    @pytest.fixture
    def admin_token(self):
        """Get admin token"""
        response = client.post(
            "/auth/login",
            json={"email": "admin@test.com", "password": "Admin@123"}
        )
        return response.json()["access_token"]

    @pytest.fixture
    def manager_token(self):
        """Get manager token"""
        response = client.post(
            "/auth/login",
            json={"email": "manager@test.com", "password": "Manager@123"}
        )
        return response.json()["access_token"]

    @pytest.fixture
    def employee_token(self):
        """Get employee token"""
        response = client.post(
            "/auth/login",
            json={"email": "employee@test.com", "password": "Employee@123"}
        )
        return response.json()["access_token"]

    def test_create_employee_by_manager(self, manager_token):
        """Test manager creating employee"""
        response = client.post(
            "/users/",
            headers={"Authorization": f"Bearer {manager_token}"},
            json={
                "employee_id": "EMP002",
                "full_name": "New Employee",
                "email": "newemp@test.com",
                "department": "Engineering",
                "password": "NewPass@123",
                "role_id": 2
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["employee_id"] == "EMP002"

    def test_create_duplicate_email(self, manager_token):
        """Test creating user with duplicate email"""
        response = client.post(
            "/users/",
            headers={"Authorization": f"Bearer {manager_token}"},
            json={
                "employee_id": "EMP002",
                "full_name": "Duplicate",
                "email": "admin@test.com",
                "department": "HR",
                "password": "Pass@123",
                "role_id": 2
            }
        )
        assert response.status_code == 400
        data = response.json()
        assert "already registered" in data.get("detail", "").lower()

    def test_create_duplicate_employee_id(self, manager_token):
        """Test creating user with duplicate employee_id"""
        response = client.post(
            "/users/",
            headers={"Authorization": f"Bearer {manager_token}"},
            json={
                "employee_id": "ADMIN001",
                "full_name": "Duplicate",
                "email": "another@test.com",
                "department": "HR",
                "password": "Pass@123",
                "role_id": 2
            }
        )
        assert response.status_code == 400
        data = response.json()
        assert "already exists" in data.get("detail", "").lower()

    def test_get_all_users(self, manager_token):
        """Test getting all users"""
        response = client.get(
            "/users/",
            headers={"Authorization": f"Bearer {manager_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) >= 3

    def test_get_user_by_id(self, employee_token):
        """Test getting user by ID"""
        response = client.get(
            "/users/1",
            headers={"Authorization": f"Bearer {employee_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["employee_id"] == "ADMIN001"

    def test_delete_user_by_admin(self, admin_token):
        """Test admin deleting user"""
        response = client.delete(
            "/users/3",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_delete_nonexistent_user(self, admin_token):
        """Test deleting non-existent user"""
        response = client.delete(
            "/users/999",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 404


# ------- ATTENDANCE TESTS -------


class TestAttendance:
    @pytest.fixture
    def manager_token(self):
        response = client.post(
            "/auth/login",
            json={"email": "manager@test.com", "password": "Manager@123"}
        )
        return response.json()["access_token"]

    @pytest.fixture
    def employee_token(self):
        response = client.post(
            "/auth/login",
            json={"email": "employee@test.com", "password": "Employee@123"}
        )
        return response.json()["access_token"]

    def test_mark_attendance_present(self, employee_token):
        """Test marking attendance as present"""
        today = date.today().isoformat()
        response = client.post(
            "/attendance/",
            headers={"Authorization": f"Bearer {employee_token}"},
            json={
                "user_id": 3,
                "date": today,
                "status": "present"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_mark_attendance_duplicate(self, employee_token):
        """Test marking duplicate attendance"""
        today = date.today().isoformat()
        # First mark
        client.post(
            "/attendance/",
            headers={"Authorization": f"Bearer {employee_token}"},
            json={
                "user_id": 3,
                "date": today,
                "status": "present"
            }
        )
        # Try to mark again
        response = client.post(
            "/attendance/",
            headers={"Authorization": f"Bearer {employee_token}"},
            json={
                "user_id": 3,
                "date": today,
                "status": "absent"
            }
        )
        assert response.status_code == 400
        data = response.json()
        assert "already marked" in data.get("detail", "").lower()

    def test_mark_attendance_for_employee_by_manager(self, manager_token):
        """Test manager marking attendance for employee"""
        today = date.today().isoformat()
        response = client.post(
            "/attendance/mark/3",
            headers={"Authorization": f"Bearer {manager_token}"},
            json={
                "user_id": 3,
                "date": today,
                "status": "present"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_get_user_attendance(self, employee_token):
        """Test getting user attendance"""
        response = client.get(
            "/attendance/3",
            headers={"Authorization": f"Bearer {employee_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_get_weekly_attendance(self, employee_token):
        """Test getting weekly attendance"""
        response = client.get(
            "/attendance/weekly",
            headers={"Authorization": f"Bearer {employee_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 7


# ------- LEAVE TESTS -------


class TestLeaves:
    @pytest.fixture
    def manager_token(self):
        response = client.post(
            "/auth/login",
            json={"email": "manager@test.com", "password": "Manager@123"}
        )
        return response.json()["access_token"]

    @pytest.fixture
    def employee_token(self):
        response = client.post(
            "/auth/login",
            json={"email": "employee@test.com", "password": "Employee@123"}
        )
        return response.json()["access_token"]

    def test_apply_leave(self, employee_token):
        """Test employee applying for leave"""
        start_date = date.today().isoformat()
        end_date = (date.today() + timedelta(days=2)).isoformat()
        
        response = client.post(
            "/leaves/apply",
            headers={"Authorization": f"Bearer {employee_token}"},
            json={
                "leave_type": "casual",
                "start_date": start_date,
                "end_date": end_date,
                "reason": "Personal work"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["days_requested"] == 3
        assert data["data"]["status"] == "pending"

    def test_apply_leave_invalid_dates(self, employee_token):
        """Test applying leave with invalid dates"""
        start_date = date.today().isoformat()
        end_date = (date.today() - timedelta(days=1)).isoformat()
        
        response = client.post(
            "/leaves/apply",
            headers={"Authorization": f"Bearer {employee_token}"},
            json={
                "leave_type": "sick",
                "start_date": start_date,
                "end_date": end_date,
                "reason": "Invalid"
            }
        )
        assert response.status_code == 400

    def test_get_my_leaves(self, employee_token):
        """Test getting employee's leaves"""
        response = client.get(
            "/leaves/my-leaves",
            headers={"Authorization": f"Bearer {employee_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_get_pending_leaves_manager(self, manager_token, employee_token):
        """Test manager getting pending leaves"""
        # First apply a leave
        start_date = date.today().isoformat()
        end_date = (date.today() + timedelta(days=1)).isoformat()
        
        client.post(
            "/leaves/apply",
            headers={"Authorization": f"Bearer {employee_token}"},
            json={
                "leave_type": "annual",
                "start_date": start_date,
                "end_date": end_date,
                "reason": "Vacation"
            }
        )
        
        # Then get pending leaves
        response = client.get(
            "/leaves/pending",
            headers={"Authorization": f"Bearer {manager_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) > 0

    def test_approve_leave(self, manager_token, employee_token):
        """Test manager approving leave"""
        # Apply leave
        start_date = date.today().isoformat()
        end_date = (date.today() + timedelta(days=1)).isoformat()
        
        apply_response = client.post(
            "/leaves/apply",
            headers={"Authorization": f"Bearer {employee_token}"},
            json={
                "leave_type": "sick",
                "start_date": start_date,
                "end_date": end_date,
                "reason": "Sick leave"
            }
        )
        leave_id = apply_response.json()["data"]["id"]
        
        # Approve leave
        response = client.post(
            "/leaves/approve",
            headers={"Authorization": f"Bearer {manager_token}"},
            json={
                "leave_id": leave_id,
                "status": "approved"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["status"] == "approved"

    def test_reject_leave(self, manager_token, employee_token):
        """Test manager rejecting leave"""
        # Apply leave
        start_date = date.today().isoformat()
        end_date = (date.today() + timedelta(days=1)).isoformat()
        
        apply_response = client.post(
            "/leaves/apply",
            headers={"Authorization": f"Bearer {employee_token}"},
            json={
                "leave_type": "casual",
                "start_date": start_date,
                "end_date": end_date,
                "reason": "Casual"
            }
        )
        leave_id = apply_response.json()["data"]["id"]
        
        # Reject leave
        response = client.post(
            "/leaves/approve",
            headers={"Authorization": f"Bearer {manager_token}"},
            json={
                "leave_id": leave_id,
                "status": "rejected"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["status"] == "rejected"


# ------- REPORTS TESTS -------


class TestReports:
    @pytest.fixture
    def manager_token(self):
        response = client.post(
            "/auth/login",
            json={"email": "manager@test.com", "password": "Manager@123"}
        )
        return response.json()["access_token"]

    def test_get_statistics(self, manager_token):
        """Test getting statistics"""
        response = client.get(
            "/reports/statistics",
            headers={"Authorization": f"Bearer {manager_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "total_employees" in data["data"]
        assert "total_managers" in data["data"]

    def test_get_departments(self, manager_token):
        """Test getting department summary"""
        response = client.get(
            "/reports/departments",
            headers={"Authorization": f"Bearer {manager_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_get_employees_report(self, manager_token):
        """Test getting employee report"""
        response = client.get(
            "/reports/employees",
            headers={"Authorization": f"Bearer {manager_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_get_trend(self, manager_token):
        """Test getting attendance trend"""
        response = client.get(
            "/reports/trend",
            headers={"Authorization": f"Bearer {manager_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_get_today_summary(self, manager_token):
        """Test getting today's summary"""
        response = client.get(
            "/reports/today",
            headers={"Authorization": f"Bearer {manager_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "total_employees" in data["data"]
        assert "present" in data["data"]
        assert "absent" in data["data"]


# ------- UNAUTHORIZED ACCESS TESTS -------


class TestAuthorization:
    @pytest.fixture
    def employee_token(self):
        response = client.post(
            "/auth/login",
            json={"email": "employee@test.com", "password": "Employee@123"}
        )
        return response.json()["access_token"]

    def test_employee_cannot_access_reports(self, employee_token):
        """Test employee cannot access reports"""
        response = client.get(
            "/reports/statistics",
            headers={"Authorization": f"Bearer {employee_token}"}
        )
        assert response.status_code == 403

    def test_employee_cannot_mark_attendance_for_others(self, employee_token):
        """Test employee cannot mark attendance for others"""
        today = date.today().isoformat()
        response = client.post(
            "/attendance/mark/1",
            headers={"Authorization": f"Bearer {employee_token}"},
            json={
                "user_id": 1,
                "date": today,
                "status": "present"
            }
        )
        assert response.status_code == 403

    def test_employee_cannot_approve_leaves(self, employee_token):
        """Test employee cannot approve leaves"""
        response = client.post(
            "/leaves/approve",
            headers={"Authorization": f"Bearer {employee_token}"},
            json={
                "leave_id": 1,
                "status": "approved"
            }
        )
        assert response.status_code == 403
