import pytest
from unittest.mock import patch, MagicMock
from io import StringIO, BytesIO

from app.services.csv_invitation.csv_invitation import CSVInvitationProcessor
from app.services.csv_invitation.exceptions import InvalidCSVException, MissingColumnsException



@pytest.fixture
def processor():
    #mock_invitation_repo = MagicMock()
    mock_email_service = MagicMock()

    return CSVInvitationProcessor(
        #invitation_repo=mock_invitation_repo,
        email_service=mock_email_service
    )

@pytest.fixture
def valid_csv_content():
    return (
        "first_name,last_name,cohort,email\n"
        "jhon,doe,101,Doe@example.com\n"
        "jon,snow,102,Snow@example.com"
    )

@pytest.fixture
def invalid_csv_content():
    return (
        "first_name,last_name,email\n"
        "jhon,doe,Doe@example.com\n"
        "jon,snow,Snow@example.com"
    )

def create_mock_file(content: str) -> BytesIO:
    return BytesIO(content.encode("utf-8"))


def test_validate_csv(processor, valid_csv_content, invalid_csv_content):
    """
    This test covers the validate_csv function,
    showing the successful case and
    the two exceptions to this function.
    """

    # --- SUCCESSFUL TEST ---
    archivo = create_mock_file(valid_csv_content)
    respuesta = processor._validate_csv(archivo)

    assert isinstance(respuesta, list)
    assert len(respuesta) == 2
    assert "first_name" in respuesta[0]
    assert "last_name" in respuesta[1]
    assert "cohort" in respuesta[0]
    assert "email" in respuesta[1]

    # --- FAILURE MissingColumns TEST ---
    invalid_archivo = create_mock_file(invalid_csv_content)
    with pytest.raises(MissingColumnsException):
        processor._validate_csv(invalid_archivo)
    
    # --- FAILURE InvalidCSV TEST --
    invalid_csv = BytesIO(b'\xf0')
    with pytest.raises(InvalidCSVException):
        processor._validate_csv(invalid_csv)

# --------------------------------------------------------------- #

@pytest.fixture
def validated_graduates_list():
    return [
        {"first_name": "jhon", "last_name": "doe", "cohort": 101, "email": "Doe@example.com"},
        {"first_name":"jon", "last_name": "snow", "cohort": 102, "email": "Snow@example.com"}
    ]

@patch("app.services.csv_invitation.csv_invitation.Invitation")
def test_generate_invitations(MockInvitation, processor, validated_graduates_list):
    """This test covers the generate_invitations function,
    showing that the function returns a list, checking how many
    times I called the Invitation mock, and 2 asserts that check
    the arguments with which that mock was called.
    """
    lista = validated_graduates_list
    respuesta = processor._generate_invitations(lista)

    assert isinstance(respuesta, list)
    assert len(respuesta) == 2

    # --- times the mock was called
    assert MockInvitation.call_count == 2

    # --- parameters used in a call
    # --- the assert is == None because assert_any_call only generates exceptions, otherwise it returns None
    assert MockInvitation.assert_any_call(
        full_name="jhon doe", 
        cohort=101, 
        email="Doe@example.com"
    ) == None

    # --- parameters used in other call
    MockInvitation.assert_any_call(
        full_name="jon snow",
        cohort=102,
        email="Snow@example.com"
    )

# ----------------------------------------------------------------------- #

@pytest.fixture
def mock_invitations_list():
    mock_First_invitation = MagicMock()
    mock_First_invitation.email = "Doe@example.com"
    mock_First_invitation.full_name = "jhon doe"
    mock_First_invitation.cohort = 101

    mock_second_invitation = MagicMock()
    mock_second_invitation.email = "Snow@example.com"
    mock_second_invitation.full_name = "jon snow"
    mock_second_invitation.cohort = 102

    return [mock_First_invitation, mock_second_invitation]

def test_send_invitations(processor, mock_invitations_list):
    """
    With this test we cover the send_invitations function, testing how many
    times it calls send_email and verifying the parameters it uses for the calls.
    """

    processor._send_invitations(mock_invitations_list)

    # mock the service to see how many times it was called
    mock_email_service = processor.email_service

    assert mock_email_service.send_email.call_count == len(mock_invitations_list)

    # expected data 
    expected_subject = "Spotly app invitation from Holberton"
    expected_body_1 = (
        f"<strong>Hola! jhon doe</strong>\
                    <br>\
                    <br>\
                    <p>Esta es una invitación de prueba</p>"
    )
    expected_body_2 = (
        f"<strong>Hola! jon snow</strong>\
                    <br>\
                    <br>\
                    <p>Esta es una invitación de prueba</p>"
    )

    # Check that the calls were made with the expected data
    mock_email_service.send_email.assert_any_call(
        "Doe@example.com",
        expected_subject,
        expected_body_1
    )
    mock_email_service.send_email.assert_any_call(
        "Snow@example.com",
        expected_subject,
        expected_body_2
    )

# ---------------------------------------------------------------------------- #

@patch("app.services.csv_invitation.csv_invitation.Invitation")
def test_process_csv(MockInvitation, processor, valid_csv_content):

    mock_invitation_1 = MagicMock(email="Doe@example.com", full_name="jhon doe")
    mock_invitation_2 = MagicMock(email="Snow@example.com", full_name="jon snow")
    MockInvitation.side_effect = [mock_invitation_1, mock_invitation_2]

    mock_file = create_mock_file(valid_csv_content)
    mock_service_email = processor.email_service

    processor.process_csv(mock_file)

    MockInvitation.call_count == 2
    MockInvitation.assert_any_call(
        full_name="jon snow",
        email="Snow@example.com",
        cohort=102
    )

    mock_service_email.send_email.call_count == 2
    mock_service_email.send_email.assert_any_call(
        "Doe@example.com",
        "Spotly app invitation from Holberton",
        f"<strong>Hola! jhon doe</strong>\
                    <br>\
                    <br>\
                    <p>Esta es una invitación de prueba</p>"
    )


