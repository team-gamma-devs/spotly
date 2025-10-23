import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi import FastAPI, status
from datetime import datetime
from pydantic import ValidationError

# ====================================================================
#      IMPORTS AND INITIAL CONFIGURATION
# ====================================================================

# import the routers with aliases to avoid conflicts
from app.api.routes.manager import router as admin_router
from app.api.routes.auth import router as auth_router
from app.api.routes.health import router as health_router
from app.api.routes.signup import router as signup_router

# We import the necessary exceptions
from app.services.exceptions.csv_invitation_exceptions import (
    InvalidCSVException,
    MissingColumnsException,
)
from app.services.exceptions.user_login_exceptions import (
    UserNotRegistered,
    InvitationNotFound,
    InvitationExpired,
)
from app.services.exceptions.register_user_exceptions import (
    InvalidFileType,
    FileTooLarge,
    InvalidCV
)

# the FastAPI instance is created and we ADD BOTH ROUTERS
app = FastAPI()
app.include_router(admin_router)
app.include_router(auth_router)
app.include_router(health_router)
app.include_router(signup_router)
client = TestClient(app)

# The route is defined
PROCESSOR_PATCH_TARGET = 'app.api.routes.manager.CSVInvitationProcessor'
USER_LOGIN_PATCH_TARGET = 'app.api.routes.auth.UserLogin'
GET_USER_PATCH_TARGET = 'app.api.routes.auth.GetUser'
MONGO_CLIENT_PATCH_TARGET = 'app.api.routes.health.MongoDB'
SETTINGS_PATCH_TARGET = 'app.api.routes.health.settings' 
SIGNUP_USECASE_PATCH_TARGET = 'app.api.routes.signup.RegisterUser'

# ====================================================================
#      FIXTURES AND MOCKS
# ====================================================================

@pytest.fixture
def mock_processor_instance():
    """Fixture that mocks the CSVInvitationProcessor."""
    mock_instance = MagicMock(spec=object)
    mock_instance.process_csv = AsyncMock(return_value=['invite1', 'invite2'])
    mock_instance.send_invitations = MagicMock()

    with patch(PROCESSOR_PATCH_TARGET, return_value=mock_instance):
        yield mock_instance

@pytest.fixture
def mock_mongodb():
    """Mocks the MongoDB class and its client to simulate the connection."""
    with patch(MONGO_CLIENT_PATCH_TARGET) as MockMongoDBClass:
        mock_client = MagicMock()
        mock_client.command = AsyncMock() 
        MockMongoDBClass.client = mock_client
        yield mock_client

@pytest.fixture
def mock_settings():
    """Mocks app settings for health checks and root."""
    mock_settings_obj = MagicMock()
    mock_settings_obj.app_name = "Mocked API"
    mock_settings_obj.app_env = "testing"
    mock_settings_obj.debug = True
    with patch(SETTINGS_PATCH_TARGET, new=mock_settings_obj):
        yield mock_settings_obj

class MockUser:
    """
    Mock class to simulate the User object returned by GetUser().verify.
    """
    def to_dict(self):
        now = datetime.now().isoformat()
        return {
            "id": "1",
            "email": "test@user.com",
            "firstName": "Test",
            "lastName": "User",
            "role": "standard",
            "cohort": 101,
            #"is_active": True,
            "avatarUrl": "http://example.com/avatar.png",
            "createdAt": now,
            "updatedAt": now
        }

# ====================================================================
#     TESTS FOR THE ADMIN (MANAGER) ROUTER
# ====================================================================

@pytest.mark.asyncio
async def test_successful_csv_upload(mock_processor_instance):
    """Covers the success path for /admin/uploadCSV."""
    mock_csv_content = b"email,name\ntest@example.com,TestUser"
    files = {"file": ("invitations.csv", mock_csv_content, "text/csv")}

    response = client.post("/manager/uploadCSV", files=files)

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json() == {"message": "Invitations generated successfully"}

    mock_processor_instance.process_csv.assert_called_once_with(mock_csv_content)
    mock_processor_instance.send_invitations.assert_called_once_with(['invite1', 'invite2'])


@pytest.mark.asyncio
async def test_non_csv_file_upload(mock_processor_instance):
    """Covers file extension validation."""
    mock_txt_content = b"just a text file"
    files = {"file": ("document.txt", mock_txt_content, "text/plain")}

    response = client.post("/manager/uploadCSV", files=files)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "File must be CSV"
    mock_processor_instance.process_csv.assert_not_called()


@pytest.mark.asyncio
@patch(PROCESSOR_PATCH_TARGET)
async def test_handles_invalid_csv_exception(MockProcessorClass):
    """Covers InvalidCSVException (status 400)."""
    mock_instance = MockProcessorClass.return_value
    error_message = "Archivo mal formado, revise comas."
    mock_instance.process_csv.side_effect = InvalidCSVException(error_message)

    files = {"file": ("invitations.csv", b"corrupted data", "text/csv")}
    
    response = client.post("/manager/uploadCSV", files=files)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == error_message
    mock_instance.process_csv.assert_called_once()


@pytest.mark.asyncio
@patch(PROCESSOR_PATCH_TARGET)
async def test_handles_missing_columns_exception(MockProcessorClass):
    """Covers MissingColumnsException (status 422)."""
    mock_instance = MockProcessorClass.return_value
    error_message = "Faltan Columnas"
    mock_instance.process_csv.side_effect = MissingColumnsException(error_message)

    files = {"file": ("invitations.csv", b"data", "text/csv")}
    
    response = client.post("/manager/uploadCSV", files=files)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert response.json()["detail"] == f"Faltan columnas requeridas: {error_message}"
    mock_instance.process_csv.assert_called_once()

# ====================================================================
#      TESTS FOR THE AUTH ROUTER
# ====================================================================

@pytest.mark.asyncio
@patch(USER_LOGIN_PATCH_TARGET)
async def test_login_success(MockUserLoginClass):
    """Covers the success path for /auth/login (status 200)."""
    mock_instance = MockUserLoginClass.return_value
    mock_instance.login = AsyncMock(return_value={
        "token": "mock-access-token-12345",
        "role": "admin",
        "is_first_time": False,
    })

    login_payload = {"email": "admin@test.com", "password": "securepassword"}
    
    response = client.post("/auth/login", json=login_payload)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "message": "Logged Successfully",
        "accessToken": "mock-access-token-12345", 
        "tokenType": "bearer", 
        "role": "admin",
        "isFirstTime": False
    }
    mock_instance.login.assert_called_once_with(login_payload['email'])


@pytest.mark.asyncio
@patch(USER_LOGIN_PATCH_TARGET)
async def test_login_user_not_registered(MockUserLoginClass):
    """Covers InvitationNotFound exception for /auth/login (status 403)."""
    mock_instance = MockUserLoginClass.return_value
    error_message = "User not found"
    mock_instance.login.side_effect = InvitationNotFound(error_message)

    login_payload = {"email": "unknown@test.com", "password": "anypassword"}
    
    response = client.post("/auth/login", json=login_payload)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == error_message
    mock_instance.login.assert_called_once()


@pytest.mark.asyncio
@patch(GET_USER_PATCH_TARGET)
async def test_auth_me_success(MockGetUserClass):
    """Covers the success path for /auth/me (status 200)."""
    mock_user = MockUser()
    mock_data = mock_user.to_dict()
    mock_instance = MockGetUserClass.return_value
    mock_instance.verify = AsyncMock(return_value=mock_user)

    test_token = "valid-token-xyz"
    headers = {"Authorization": f"Bearer {test_token}"}
    
    response = client.get("/auth/me", headers=headers)
    response_data = response.json()

    assert response.status_code == status.HTTP_200_OK
    def compare_dicts_ignoring_dates(dict1, dict2):
        d1 = dict1.copy()
        d2 = dict2.copy()
        
        # Keys that change over time are eliminated
        d1.pop('createdAt', None)
        d1.pop('updatedAt', None)
        d2.pop('createdAt', None)
        d2.pop('updatedAt', None)
        
        return d1 == d2

    # The helper function is used to ignore time differences and avoid errors due to those fields.
    assert compare_dicts_ignoring_dates(response_data, mock_data)
    mock_instance.verify.assert_called_once_with(test_token)


@pytest.mark.asyncio
@patch(GET_USER_PATCH_TARGET)
async def test_auth_me_unauthorized(MockGetUserClass):
    """Covers UserNotRegistered exception for /auth/me (status 401).(If the file is fixed)"""
    mock_instance = MockGetUserClass.return_value
    error_message = "Expired or invalid token"
    mock_instance.verify.side_effect = UserNotRegistered(error_message)

    test_token = "invalid-token"
    headers = {"Authorization": f"Bearer {test_token}"}
    
    response = client.get("/auth/me", headers=headers)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == error_message
    mock_instance.verify.assert_called_once_with(test_token)

@pytest.mark.asyncio
async def test_auth_me_missing_token():
    """Covers the case where the token is missing (handled by HTTPBearer, status 403)."""
    response = client.get("/auth/me")
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Not authenticated"


# ====================================================================
#     TESTS FOR THE HEALTH AND ROOT ROUTER
# ====================================================================

@pytest.mark.asyncio
async def test_health_check_success(mock_settings):
    """Covers the GET /health endpoint."""
    mock_settings.app_name = "Test App"
    mock_settings.app_env = "test"
    
    response = client.get("/health")
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "status": "healthy",
        "service": "Test App",
        "environment": "test",
    }


@pytest.mark.asyncio
async def test_liveness_check_success():
    """Covers the GET /health/live endpoint."""
    response = client.get("/health/live")
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "alive"}


@pytest.mark.asyncio
async def test_readiness_check_success(mock_mongodb):
    """Covers the GET /health/ready endpoint with the DB connected."""
    response = client.get("/health/ready")
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "status": "ready",
        "database": "connected",
    }
    mock_mongodb.command.assert_called_once_with("ping")


@pytest.mark.asyncio
async def test_readiness_check_db_failure(mock_mongodb):
    """Covers the GET /health/ready endpoint when the DB fails."""
    # The mock is configured to simulate an exception on the connection
    mock_mongodb.command.side_effect = Exception("DB Connection Error")
    
    response = client.get("/health/ready")
    
    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert response.json()["status"] == "not_ready"
    assert response.json()["database"] == "disconnected"
    assert "DB Connection Error" in response.json()["error"]
    mock_mongodb.command.assert_called_once_with("ping")


@pytest.mark.asyncio
async def test_root_endpoint_debug_true(mock_settings):
    """Covers the GET / endpoint when settings.debug is True (shows headers)."""
    mock_settings.app_name = "Root App"
    mock_settings.app_env = "development"
    mock_settings.debug = True

    response = client.get("/", headers={"host": "test-host.com"})
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["message"] == "Welcome to Root App"
    assert data["environment"] == "development"
    # Verify that the headers field contains the expected key (only if debug=True)
    assert data["headers"]["host"] == "test-host.com"


@pytest.mark.asyncio
async def test_root_endpoint_debug_false(mock_settings):
    """Covers the GET / endpoint when settings.debug is False (hides headers)."""
    mock_settings.debug = False
    
    response = client.get("/")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    # Verify that the headers field is hidden
    assert data["headers"] == "hidden in production"
    assert data["docs"] == "disabled in production"


# ====================================================================
#     TESTS FOR THE SIGN-UP ROUTER
# ====================================================================

#@pytest.mark.asyncio
#@patch(SIGNUP_USECASE_PATCH_TARGET)
#async def test_check_invitation_success(MockRegisterUser):
#    """Covers the success path for GET /sign-up/invite."""
#    mock_instance = MockRegisterUser.return_value
#    expected_state = True
#    mock_instance.check_invitation = AsyncMock(return_value=expected_state)
#
#    response = client.get("/sign-up/invite?token=validtoken123")
#    
#    assert response.status_code == status.HTTP_200_OK
#    assert response.json() == {"token_state": expected_state}
#    mock_instance.check_invitation.assert_called_once_with("validtoken123")
#
#
#@pytest.mark.asyncio
#@patch(SIGNUP_USECASE_PATCH_TARGET)
#async def test_check_invitation_not_found(MockRegisterUser):
#    """Covers the InvitationNotFound exception (status 404)."""
#    mock_instance = MockRegisterUser.return_value
#    error_message = "Not Found"
#    mock_instance.check_invitation = AsyncMock(side_effect=InvitationNotFound(error_message))
#
#    response = client.get("/sign-up/invite?token=missing")
#    
#    assert response.status_code == status.HTTP_404_NOT_FOUND
#    assert response.json()["detail"] == error_message
#    mock_instance.check_invitation.assert_called_once_with("missing")
#
#
#@pytest.mark.asyncio
#@patch(SIGNUP_USECASE_PATCH_TARGET)
#async def test_check_invitation_expired(MockRegisterUser):
#    """Covers the InvitationExpired exception (status 410)."""
#    mock_instance = MockRegisterUser.return_value
#    error_message = "Token 'expired' expired"
#    mock_instance.check_invitation = AsyncMock(side_effect=InvitationExpired(error_message))
#
#    response = client.get("/sign-up/invite?token=expired")
#    
#    assert response.status_code == status.HTTP_410_GONE
#    assert response.json()["detail"] == error_message
#    mock_instance.check_invitation.assert_called_once_with("expired")


@pytest.mark.asyncio
@patch(SIGNUP_USECASE_PATCH_TARGET)
async def test_signup_successful_validation(MockRegisterUser):
    """
    Covers the success path for POST /sign-up/ (file validation only).
    """
    mock_instance = MockRegisterUser.return_value
    mock_instance.register_user = AsyncMock(return_value={"id": "mock-user-id"}) 

    files = [
        ('personal_cv', ('personal.pdf', b'PDF_CONTENT', 'application/pdf')),
        ('linkedin_cv', ('linkedin.pdf', b'PDF_CONTENT', 'application/pdf')),
        ('avatar_img', ('avatar.jpg', b'IMAGE_CONTENT', 'image/jpeg')),
    ]
    
    response = client.post(
        "/sign-up/?token=valid-token", 
        files=files,
        data={'github_username': 'testuser'}
    )
    
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.asyncio
@patch(SIGNUP_USECASE_PATCH_TARGET)
async def test_signup_invalid_cv_type(MockRegisterUser):
    """Covers the validation that personal_cv must be PDF (status 415)."""
    mock_instance = MockRegisterUser.return_value
    error_message = "personal.txt is not a valid PDF"
    mock_instance.register_user = AsyncMock(side_effect=InvalidFileType(error_message))
    files = [
        ('personal_cv', ('personal.txt', b'TEXT_CONTENT', 'text/plain')),
        ('linkedin_cv', ('linkedin.pdf', b'PDF_CONTENT', 'application/pdf')),
        ('avatar_img', ('avatar.jpg', b'IMAGE_CONTENT', 'image/jpeg'))
    ]

    response = client.post(
        "/sign-up/?token=t",
        files=files
    )
    
    assert response.status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    assert response.json()["detail"] == error_message
    mock_instance.register_user.assert_called_once()


@pytest.mark.asyncio
@patch(SIGNUP_USECASE_PATCH_TARGET)
async def test_signup_invalid_linkedin_cv_type(MockRegisterUser):
    """Covers validation that linkedin_cv must be PDF (status 415)."""
    mock_instance = MockRegisterUser.return_value
    error_message = "linkedin.zip is not a valid PDF"
    mock_instance.register_user = AsyncMock(side_effect=InvalidFileType(error_message))
    files = [
        ('personal_cv', ('personal.pdf', b'PDF_CONTENT', 'application/pdf')),
        ('linkedin_cv', ('linkedin.zip', b'ZIP_CONTENT', 'application/zip')),
        ('avatar_img', ('avatar.jpg', b'IMAGE_CONTENT', 'image/jpeg')) 
    ]
    
    response = client.post(
        "/sign-up/?token=t",
        files=files
    )
    
    assert response.status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    assert response.json()["detail"] == error_message
    mock_instance.register_user.assert_called_once()


@pytest.mark.asyncio
async def test_signup_invalid_avatar_type():
    """Covers validation that avatar_img should be an image (status 400)."""
    files = [
        ('personal_cv', ('personal.pdf', b'PDF_CONTENT', 'application/pdf')),
        ('linkedin_cv', ('linkedin.pdf', b'PDF_CONTENT', 'application/pdf')),
        ('avatar_img', ('avatar.txt', b'TEXT_CONTENT', 'text/plain')),
    ]
    
    response = client.post(
        "/sign-up/?token=t",
        files=files
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "avatar.txt is not a valid image"

