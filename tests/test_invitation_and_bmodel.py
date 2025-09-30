import pytest
from unittest.mock import patch
from datetime import datetime, timezone, timedelta
from app.domain.invitation import Invitation
from app.domain.bmodel import EmailNotValidError
from app.domain.bmodel import BModel, abstractmethod
"""
This module contains a collection of tests that check for possible paths and exceptions
that the data may encounter while traversing the code in the invitation.py file.
It also contains a collection of tests that assess and cover all Bmodel lines.
"""


MOCKED_NOW = datetime(2025, 10, 1, 10, 0, 0)#, tzinfo=timezone.utc
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
        "id": "6789-EFGH-4321-abcd",
        "full_name": "DB User",
        "email": "db@gmail.com",
        "cohort": 101,
        "token": "FIXED_TOKEN_FROM_DB",
        "token_state": True,
        "log_state": False,
        "created_at": datetime.now() - timedelta(days=1),
        "expires_at": datetime.now() + timedelta(days=30)
    }


@patch('app.domain.bmodel.validate_email')
@patch('app.domain.invitation.uuid4')
@patch('app.domain.invitation.secrets')
@patch('app.domain.invitation.datetime')
def test_invitation_creation_and_setters(mock_dt, mock_secrets, mock_uuid, mock_validate_email):
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
    assert "id" in respuesta
    assert "full_name" in respuesta
    assert "created_at" in respuesta
    assert respuesta["email"] == "test@example.com"
    assert "log_state" in respuesta
    assert "token_state" in respuesta


# ----------------- FAILED VALIDATION TEST -----------------

@patch('app.domain.bmodel.validate_email')
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
    with pytest.raises(TypeError, match="cohort must be a number"):
        Invitation(full_name=valid_name, email=valid_email, cohort="2024")
        
    # cohort no positive (ValueError)
    with pytest.raises(ValueError, match="cohort must be positive"):
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

@pytest.fixture
def mock_datetime_now_aware():
    with patch('app.domain.invitation.datetime') as mock_dt:
        mock_dt.now.return_value = datetime(2025, 10, 1, 10, 0, 0, tzinfo=timezone.utc)
        mock_dt.timedelta = timedelta
        mock_dt.timezone = timezone
        yield mock_dt

@patch('app.domain.bmodel.validate_email')
@patch('app.domain.invitation.uuid4')
@patch('app.domain.invitation.secrets')
@pytest.mark.usefixtures("mock_datetime_now_aware")
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



# ---------- TEST EXCEPTIONS OF EXPIRES_AT -------------
#@pytest.mark.usefixtures("mock_datetime_now_aware")
def test_expires_at_setter_exceptions():
    """
    This test covers expires_at exceptions.

    TypeError -> for invalid date
    ValueError -> for date prior to creation
    """
    base_time = datetime.now()

    invitation = Invitation("pepe", "pepe@gmail.com", 101)

    # --- 1. TEST OF TypeError ---
    content = 2025, 10, 1, 10, 0, 0
    with pytest.raises(TypeError, match="Expires at must be a valid date"):
        invitation.expires_at = content
        
    ## --- 2. TEST OF ValueError ---
    fecha_anterior = base_time - timedelta(hours=1)
    
    with pytest.raises(ValueError, match="Expiration date must be after the creation date"):
        invitation.expires_at = fecha_anterior



# ---- TEST OF THE LAST LINES ON BMODEL ------


class BModelTestDummy(BModel):
    """
    Simple class that inherits from BModel to test its constructor
    without the interference of Invitation's incomplete signature.
    """
    def __init__(
        self, 
        id: str | None = None, 
        created_at: datetime | None = None, 
        updated_at: datetime | None = None
    ):
        super().__init__(id, created_at, updated_at)

    def to_dict(self):
        return {}

def test_bmodel_constructor_with_data_from_db(db_data):
    """
    Test BModel constructor with pre-defined values to cover 'id', 'created_at', and 'updated_at'.
    """
    
    instance = BModelTestDummy( 
        id=db_data["id"],
        created_at=db_data["created_at"],
        updated_at=db_data["created_at"]
    )
    
    # data match check
    assert instance.id == db_data["id"]
    assert instance.created_at == db_data["created_at"]
    assert instance.updated_at == db_data["created_at"]

    # data match type
    assert isinstance(instance.created_at, datetime)
    assert isinstance(instance.updated_at, datetime)

    instance_new_update = BModelTestDummy( 
        id=db_data["id"],
        created_at=db_data["created_at"],
    )
    assert instance_new_update.created_at == db_data["created_at"]
    assert isinstance(instance_new_update.updated_at, datetime)
    assert instance_new_update.updated_at >= instance_new_update.created_at 


def test_bmodel_updated_at_setter():
    """
    Test the successful case of updated_at setter in BModel
    """
    invitation = Invitation("test", "test@gmail.com", 101)
        
    new_date = invitation.created_at + timedelta(minutes=5)
    invitation.updated_at = new_date
    
    # data check match
    assert invitation.updated_at == new_date

    # assert is badly, but is difficult that this happen
    invitation.updated_at = "fecha-invalida"
    assert invitation.updated_at == "fecha-invalida"


def test_validate_uuid():
    """
    Test the validate_uuid static method for valid and invalid inputs.
    """
    valid_uuid = "a1b2c3d4-e5f6-4890-a1b2-c3d4e5f67890"
    
    # seccessful case
    assert BModel.validate_uuid(valid_uuid, "test_field") == valid_uuid
    
    # exceptions
    with pytest.raises(ValueError, match="Invalid UUID in test_field"):
        BModel.validate_uuid("invalid-uuid-string", "test_field")
        
    with pytest.raises(ValueError, match="Invalid UUID in test_field"):
        BModel.validate_uuid(12345, "test_field")


def test_validate_number():
    """
    Verifies that validate_number rejects boolean types and negative numbers.
    """
    with pytest.raises(TypeError, match="cohort must be a number"):
        Invitation("valid", "valid@email.com", cohort=True)

    with pytest.raises(ValueError, match="cohort must be positive"):
        Invitation("valid", "valid@email.com", cohort=-10)