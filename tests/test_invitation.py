import pytest
from unittest.mock import patch
from datetime import datetime, timezone, timedelta
from app.domain.invitation import Invitation, EmailNotValidError
"""
This module contains a collection of tests that check for possible paths and exceptions
that the data may encounter while traversing the code in the invitation.py file.

With these tests, we are covering 99% of the file.
"""


MOCKED_NOW = datetime(2025, 10, 1, 10, 0, 0, tzinfo=timezone.utc)
EXPECTED_EXPIRY = MOCKED_NOW + timedelta(days=30)

# Mock object to simulate the successful return of 'email_validator.validate_email'
class MockValidEmail:
    def __init__(self, email):
        self.email = email.lower() 

    @property
    def normalized(self):
        return self.email

@pytest.fixture
def db_data():
    return {
        "_id": "6789-EFGH-4321",
        "full_name": "DB User",
        "email": "db@example.com",
        "cohort": 101,
        "token": "FIXED_TOKEN_FROM_DB",
        "token_state": True,
        "log_state": False,
        "created_at": datetime.now(),
        "expires_at": datetime.now() + timedelta(days=30)
    }


@patch('app.domain.invitation.validate_email')
@patch('app.domain.invitation.uuid4')
@patch('app.domain.invitation.secrets')
@patch('app.domain.invitation.datetime')
def test_invitation_creation_and_setters(mock_dt, mock_secrets, mock_uuid, mock_validate_email, db_data):
    """
    Verifies the successful creation and use of the setters (token_state and log_state).
    """
    mock_uuid.return_value = 'UUID-1234'
    mock_secrets.token_urlsafe.return_value = 'TOKEN-XYZ'
    mock_dt.now.return_value = MOCKED_NOW
    mock_dt.timezone = timezone
    mock_dt.datetime = datetime
    mock_dt.timedelta = timedelta
    
    mock_validate_email.side_effect = lambda email: MockValidEmail(email)

    invitation = Invitation("test", "test@example.com", 101)


    assert invitation.created_at == MOCKED_NOW
    assert invitation.cohort == 101
    assert invitation.email == "test@example.com"
    assert invitation.full_name == "test"
    assert invitation.expires_at == EXPECTED_EXPIRY

    # Coverage of setters
    invitation.token_state = True
    assert invitation.token_state == True

    invitation.log_state = True
    assert invitation.log_state == True

    # Coverage of TypeError of setters
    with pytest.raises(TypeError, match="Token state must be a boolean"):
        invitation.token_state = "invalid"

    with pytest.raises(TypeError, match="Log state must be a boolean"):
        invitation.log_state = 1

    # Coverage of return of to_dict function
    respuesta = invitation.to_dict()

    assert isinstance(respuesta, dict)
    assert len(respuesta) == 9
    assert "_id" in respuesta
    assert "full_name" in respuesta
    assert "created_at" in respuesta
    assert respuesta["email"] == "test@example.com"
    assert "log_state" in respuesta
    assert "token_state" in respuesta


# ----------------- FAILED VALIDATION TEST -----------------

@patch('app.domain.invitation.validate_email')
def test_invitation_validation_failures(mock_validate_email):
    """
    Verify that the model throws the expected exceptions (ValueError/TypeError)
    for invalid data in full_name, email, and cohort
    """
    valid_name = "User Name"
    valid_email = "valid@email.com"
    valid_cohort = 100

    mock_validate_email.side_effect = lambda email: MockValidEmail(email)
    
    # full_name no string (TypeError)
    with pytest.raises(TypeError, match="full_name must be a string!"):
        Invitation(full_name=12345, email=valid_email, cohort=valid_cohort)
    
    # full_name vacío (ValueError)
    with pytest.raises(ValueError, match="full_name cannot be empty!"):
        Invitation(full_name="  ", email=valid_email, cohort=valid_cohort)


    # cohort no int (TypeError)
    with pytest.raises(TypeError, match="Cohort must be a number"):
        Invitation(full_name=valid_name, email=valid_email, cohort="2024")
        
    # cohort no positive (ValueError)
    with pytest.raises(ValueError, match="Cohort must be positive"):
        Invitation(full_name=valid_name, email=valid_email, cohort=0)


    # email empty (ValueError)
    with pytest.raises(ValueError, match="email cannot be empty!"):
        Invitation(full_name=valid_name, email="", cohort=valid_cohort)
        
    # inválid format email (ValueError)
    # We force the mocked function to throw the library error
    mock_validate_email.side_effect = EmailNotValidError("Invalid structure or DNS failure")
    with pytest.raises(ValueError, match="Invalid email: Invalid structure or DNS failure"):
        Invitation(full_name=valid_name, email="not-an-email", cohort=valid_cohort)



# ------------ FUNCTION IS VALID --------

@patch('app.domain.invitation.validate_email')
@patch('app.domain.invitation.uuid4')
@patch('app.domain.invitation.secrets')
def test_invitation_is_valid_function( mock_secrets, mock_uuid, mock_validate_email):
    """
    with these test we cover some line related with the logic of
    validate the token and expiration of invitation
    """

    mock_uuid.return_value = 'UUID-1234'
    mock_secrets.token_urlsafe.return_value = 'TOKEN-XYZ'
    mock_validate_email.side_effect = lambda email: MockValidEmail(email)

    instancia1 = Invitation("jhon doe", "jhon@example.com", 101)

    assert instancia1.is_valid() == True

    instancia2 = Invitation("jhon doe", "jhon@example.com", 101, token_state=True)

    assert instancia2.is_valid() == False


# ------------ FUNCTION INVITATION FROM DB -----------

@patch('app.domain.invitation.validate_email')
@patch('app.domain.invitation.uuid4')
@patch('app.domain.invitation.secrets')
def test_invitation_from_db(mock_secrets, mock_uuid, mock_validate_email, db_data):
    """
    With this test we cover the from_db function which makes a call to the database,
    the response is displayed and we see how the data matches.
    """
    mock_uuid.return_value = 'UUID-1234'
    mock_secrets.token_urlsafe.return_value = 'TOKEN-XYZ'
    mock_validate_email.side_effect = lambda email: MockValidEmail(email)

    invitation = Invitation("DB User", "db@example.com", 101)

    result = invitation.from_db(**db_data)

    assert isinstance(result, Invitation)
    assert result.id == "6789-EFGH-4321"
    assert result.cohort == 101
    assert result.full_name == "DB User"


# ---------- TEST EXCEPTIONS OF EXPIRES_AT -------------
def test_expires_at_setter_exceptions():
    """
    This test covers expires_at exceptions.

    TypeError -> for invalid date
    ValueError -> for date prior to creation
    """
    base_time = datetime.now(timezone.utc)

    invitation = Invitation("pepe", "pepe@gmail.com", 101)

    # --- 1. TEST OF TypeError ---
    with pytest.raises(TypeError, match="Expires at must be a valid date"):
        invitation.expires_at = "fecha-invalida"
        
    # --- 2. TEST OF ValueError ---
    fecha_anterior = base_time - timedelta(hours=1)
    
    with pytest.raises(ValueError, match="Expiration date must be after the creation date"):
        invitation.expires_at = fecha_anterior
