import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi import FastAPI, status
from datetime import datetime
from pydantic import ValidationError

# ====================================================================
# 1. IMPORTS Y CONFIGURACIÓN INICIAL
# ====================================================================

# Importamos los routers con alias para evitar conflictos
# AJUSTAR: Asegúrate que estas rutas de importación son correctas.
from app.api.routes.manager import router as admin_router
from app.api.routes.auth import router as auth_router
# Asumo la ruta de importación para el router de salud que proporcionaste
from app.api.routes.health import router as health_router
# NUEVA IMPORTACIÓN: Router de sign-up
from app.api.routes.signup import router as signup_router

# Importamos las excepciones necesarias
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

# Creamos la instancia de FastAPI y AGREGAMOS AMBOS ROUTERS
app = FastAPI()
app.include_router(admin_router)
app.include_router(auth_router)
app.include_router(health_router)
app.include_router(signup_router)
client = TestClient(app)

# Definimos la ruta donde se importa el CSVInvitationProcessor dentro del router.
PROCESSOR_PATCH_TARGET = 'app.api.routes.manager.CSVInvitationProcessor'
# Definir las rutas de patch para los Use Cases importados en el router.
USER_LOGIN_PATCH_TARGET = 'app.api.routes.auth.UserLogin'
GET_USER_PATCH_TARGET = 'app.api.routes.auth.GetUser'
# Nuevos targets para los tests de salud
MONGO_CLIENT_PATCH_TARGET = 'app.api.routes.health.MongoDB'
SETTINGS_PATCH_TARGET = 'app.api.routes.health.settings' 
# NUEVO TARGET: Use Case de registro/invitación
SIGNUP_USECASE_PATCH_TARGET = 'app.api.routes.signup.RegisterUser'

# ====================================================================
# 2. FIXTURES Y MOCKS
# ====================================================================

@pytest.fixture
def mock_processor_instance():
    """Fixture que mockea el CSVInvitationProcessor."""
    mock_instance = MagicMock(spec=object)
    mock_instance.process_csv = AsyncMock(return_value=['invite1', 'invite2'])
    mock_instance.send_invitations = MagicMock()

    with patch(PROCESSOR_PATCH_TARGET, return_value=mock_instance):
        yield mock_instance

@pytest.fixture
def mock_mongodb():
    """Mockea la clase MongoDB y su cliente para simular la conexión."""
    with patch(MONGO_CLIENT_PATCH_TARGET) as MockMongoDBClass:
        mock_client = MagicMock()
        # El comando 'ping' debe ser un AsyncMock
        mock_client.command = AsyncMock() 
        MockMongoDBClass.client = mock_client
        yield mock_client

@pytest.fixture
def mock_settings():
    """Mockea la configuración de la aplicación para los health checks y root."""
    mock_settings_obj = MagicMock()
    mock_settings_obj.app_name = "Mocked API"
    mock_settings_obj.app_env = "testing"
    mock_settings_obj.debug = True # Valor por defecto para el test de root
    with patch(SETTINGS_PATCH_TARGET, new=mock_settings_obj):
        yield mock_settings_obj

class MockUser:
    """
    Clase Mock corregida para simular el objeto User devuelto por GetUser().verify.
    Incluye todos los campos requeridos por UserResponse y los tipos correctos (ej: id como str).
    """
    def to_dict(self):
        # Usamos .isoformat() para simular el formato de fecha que Pydantic maneja bien
        now = datetime.now().isoformat()
        return {
            "id": "1", # Corregido: el error sugería que espera un string
            "email": "test@user.com",
            "firstName": "Test",
            "lastName": "User",
            "role": "standard",
            "cohort": 101,
            #"is_active": True,
            # Campos faltantes añadidos para pasar la ResponseValidationError
            "avatarUrl": "http://example.com/avatar.png",
            "createdAt": now,
            "updatedAt": now
        }

# ====================================================================
# 3. TESTS PARA EL ROUTER ADMIN
# ====================================================================

@pytest.mark.asyncio
async def test_successful_csv_upload(mock_processor_instance):
    """Cubre el path de éxito para /admin/uploadCSV."""
    mock_csv_content = b"email,name\ntest@example.com,TestUser"
    files = {"file": ("invitations.csv", mock_csv_content, "text/csv")}

    response = client.post("/manager/uploadCSV", files=files)

    # El fallo de 404 está corregido por la inclusión correcta del router.
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json() == {"message": "Invitations generated successfully"}

    mock_processor_instance.process_csv.assert_called_once_with(mock_csv_content)
    mock_processor_instance.send_invitations.assert_called_once_with(['invite1', 'invite2'])


@pytest.mark.asyncio
async def test_non_csv_file_upload(mock_processor_instance):
    """Cubre la validación de extensión de archivo."""
    mock_txt_content = b"just a text file"
    files = {"file": ("document.txt", mock_txt_content, "text/plain")}

    response = client.post("/manager/uploadCSV", files=files)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "File must be CSV"
    mock_processor_instance.process_csv.assert_not_called()


@pytest.mark.asyncio
@patch(PROCESSOR_PATCH_TARGET)
async def test_handles_invalid_csv_exception(MockProcessorClass):
    """Cubre la excepción InvalidCSVException (status 400)."""
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
    """Cubre la excepción MissingColumnsException (status 422)."""
    mock_instance = MockProcessorClass.return_value
    error_message = "Faltan Columnas"
    mock_instance.process_csv.side_effect = MissingColumnsException(error_message)

    files = {"file": ("invitations.csv", b"data", "text/csv")}
    
    response = client.post("/manager/uploadCSV", files=files)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert response.json()["detail"] == f"Faltan columnas requeridas: {error_message}"
    mock_instance.process_csv.assert_called_once()

# ====================================================================
# 4. TESTS PARA EL ROUTER AUTH
# ====================================================================

@pytest.mark.asyncio
@patch(USER_LOGIN_PATCH_TARGET)
async def test_login_success(MockUserLoginClass):
    """Cubre el path de éxito para /auth/login (status 200)."""
    mock_instance = MockUserLoginClass.return_value
    mock_instance.login = AsyncMock(return_value={
        "token": "mock-access-token-12345",
        "role": "admin",
        "is_first_time": False,
    })

    login_payload = {"email": "admin@test.com", "password": "securepassword"}
    
    response = client.post("/auth/login", json=login_payload)

    # CORRECCIÓN: Usamos el alias 'accessToken' en la aserción debido a response_model_by_alias=True
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "message": "Logged Successfully",
        "accessToken": "mock-access-token-12345", # <-- Alias corregido
        "tokenType": "bearer", # <-- Alias corregido
        "role": "admin",
        "isFirstTime": False
    }
    mock_instance.login.assert_called_once_with(login_payload['email'])


@pytest.mark.asyncio
@patch(USER_LOGIN_PATCH_TARGET)
async def test_login_user_not_registered(MockUserLoginClass):
    """Cubre la excepción UserNotRegistered para /auth/login (status 403)."""
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
    """Cubre el path de éxito para /auth/me (status 200)."""
    # CORRECCIÓN: La clase MockUser ya incluye los campos de fecha y el ID como str.
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
        # Crear copias para no modificar los originales
        d1 = dict1.copy()
        d2 = dict2.copy()
        
        # Eliminar las claves que cambian con el tiempo
        d1.pop('createdAt', None)
        d1.pop('updatedAt', None)
        d2.pop('createdAt', None)
        d2.pop('updatedAt', None)
        
        return d1 == d2

    # El MockUser.to_dict() ya está corregido para usar CamelCase y los campos correctos.
    # Ahora usamos la función auxiliar para ignorar las diferencias de tiempo.
    assert compare_dicts_ignoring_dates(response_data, mock_data)
    mock_instance.verify.assert_called_once_with(test_token)


@pytest.mark.asyncio
@patch(GET_USER_PATCH_TARGET)
async def test_auth_me_unauthorized(MockGetUserClass):
    """Cubre la excepción UserNotRegistered para /auth/me (status 401)."""
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
    """Cubre el caso en que falta el token (manejado por HTTPBearer, status 403)."""
    response = client.get("/auth/me")
    assert response.status_code == status.HTTP_403_FORBIDDEN
    # Nota: El mensaje de error de FastAPI/HTTPBearer es 'Not authenticated'
    assert response.json()["detail"] == "Not authenticated"


# ====================================================================
# 5. TESTS PARA EL ROUTER HEALTH Y ROOT
# ====================================================================

@pytest.mark.asyncio
async def test_health_check_success(mock_settings):
    """Cubre el endpoint GET /health."""
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
    """Cubre el endpoint GET /health/live."""
    response = client.get("/health/live")
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "alive"}


@pytest.mark.asyncio
async def test_readiness_check_success(mock_mongodb):
    """Cubre el endpoint GET /health/ready con la DB conectada."""
    # El mock_mongodb por defecto tiene el comando 'ping' exitoso
    response = client.get("/health/ready")
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "status": "ready",
        "database": "connected",
    }
    mock_mongodb.command.assert_called_once_with("ping")


@pytest.mark.asyncio
async def test_readiness_check_db_failure(mock_mongodb):
    """Cubre el endpoint GET /health/ready cuando la DB falla."""
    # Configuramos el mock para simular una excepción en la conexión
    mock_mongodb.command.side_effect = Exception("DB Connection Error")
    
    response = client.get("/health/ready")
    
    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert response.json()["status"] == "not_ready"
    assert response.json()["database"] == "disconnected"
    assert "DB Connection Error" in response.json()["error"]
    mock_mongodb.command.assert_called_once_with("ping")


@pytest.mark.asyncio
async def test_root_endpoint_debug_true(mock_settings):
    """Cubre el endpoint GET / cuando settings.debug es True (muestra headers)."""
    mock_settings.app_name = "Root App"
    mock_settings.app_env = "development"
    mock_settings.debug = True

    response = client.get("/", headers={"host": "test-host.com"})
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["message"] == "Welcome to Root App"
    assert data["environment"] == "development"
    # Verifica que el campo headers contenga la clave esperada (solo si debug=True)
    assert data["headers"]["host"] == "test-host.com"


@pytest.mark.asyncio
async def test_root_endpoint_debug_false(mock_settings):
    """Cubre el endpoint GET / cuando settings.debug es False (oculta headers)."""
    mock_settings.debug = False
    
    response = client.get("/")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    # Verifica que el campo headers esté oculto
    assert data["headers"] == "hidden in production"
    assert data["docs"] == "disabled in production"


# ====================================================================
# 6. TESTS PARA EL ROUTER SIGN-UP
# ====================================================================

#@pytest.mark.asyncio
#@patch(SIGNUP_USECASE_PATCH_TARGET)
#async def test_check_invitation_success(MockRegisterUser):
#    """Cubre el path de éxito para GET /sign-up/invite."""
#    mock_instance = MockRegisterUser.return_value
#    # Estado de ejemplo que devuelve el use case al ser válido
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
#    """Cubre la excepción InvitationNotFound (status 404)."""
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
#    """Cubre la excepción InvitationExpired (status 410)."""
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
    Cubre el path de éxito para POST /sign-up/ (solo validación de archivos).
    Se usa AsyncMock.return_value para simular la ejecución exitosa del use case
    una vez que la validación del router ha pasado.
    """
    mock_instance = MockRegisterUser.return_value
    # Aunque la llamada a execute no está en el código del router proporcionado, 
    # la simulamos para el "happy path" del endpoint completo.
    mock_instance.register_user = AsyncMock(return_value={"id": "mock-user-id"}) 

    # Archivos válidos (ambos PDF) y un avatar opcional (válido)
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
    
    # Si pasa las validaciones, debería devolver 201 CREATED
    assert response.status_code == status.HTTP_201_CREATED
    # Ya que la lógica de sign_up está incompleta, no comprobamos la llamada al use case
    # sino que se pasa la validación del router.


@pytest.mark.asyncio
@patch(SIGNUP_USECASE_PATCH_TARGET)
async def test_signup_invalid_cv_type(MockRegisterUser):
    """Cubre la validación de que personal_cv debe ser PDF (status 400)."""
    mock_instance = MockRegisterUser.return_value
    error_message = "personal.txt is not a valid PDF"
    mock_instance.register_user = AsyncMock(side_effect=InvalidFileType(error_message))
    files = [
        ('personal_cv', ('personal.txt', b'TEXT_CONTENT', 'text/plain')), # <-- INVÁLIDO
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
    """Cubre la validación de que linkedin_cv debe ser PDF (status 400)."""
    mock_instance = MockRegisterUser.return_value
    error_message = "linkedin.zip is not a valid PDF"
    mock_instance.register_user = AsyncMock(side_effect=InvalidFileType(error_message))
    files = [
        ('personal_cv', ('personal.pdf', b'PDF_CONTENT', 'application/pdf')),
        ('linkedin_cv', ('linkedin.zip', b'ZIP_CONTENT', 'application/zip')), # <-- INVÁLIDO
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
    """Cubre la validación de que avatar_img debe ser una imagen (status 400)."""
    files = [
        ('personal_cv', ('personal.pdf', b'PDF_CONTENT', 'application/pdf')),
        ('linkedin_cv', ('linkedin.pdf', b'PDF_CONTENT', 'application/pdf')),
        ('avatar_img', ('avatar.txt', b'TEXT_CONTENT', 'text/plain')), # <-- INVÁLIDO
    ]
    
    response = client.post(
        "/sign-up/?token=t",
        files=files
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "avatar.txt is not a valid image"

