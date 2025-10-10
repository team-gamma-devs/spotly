import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from typing import Optional
from bson import ObjectId as RealObjectId
from bson.errors import InvalidId

from app.infrastructure.database.repositories.base_repository import BaseRepository
"""
This module contains the fixtures and mocks needed for the tests involved
in covering the entire contents of the base_repository file.
"""


# mock model for testing
class TestModel:
    def __init__(self, id: Optional[str] = None, name: str = ""):
        self.id = id
        self.name = name

    def to_dict(self):
        # implementation required for to_dict
        return {"id": self.id, "name": self.name}

# --- FIXTURES ---

# Mock ObjectId to be able to control it in _to_dict
@pytest.fixture
def mock_object_id():
    """Mock the ObjectId function to return a controllable mock."""
    # We use patch to replace bson.ObjectId during test scope.
    with patch("app.infrastructure.database.repositories.base_repository.ObjectId") as mock_id:
        mock_id.side_effect = lambda x: MagicMock(spec=RealObjectId, return_value=f"ObjectId('{x}')")
        yield mock_id

@pytest.fixture
def mock_collection():
    """Returns an AsyncMock to simulate AsyncIOMotorCollection."""
    return AsyncMock()

@pytest.fixture
def repository(mock_collection):
    """Repository instance with mocks."""
    return BaseRepository(collection=mock_collection, model=TestModel)

# mock to simulate an asynchronous iterator
async def mock_async_cursor(data):
    for doc in data:
        yield doc


# Conversion test
def test_to_dict(repository, mock_object_id):
    """Verifies the Mongo model-to-document conversion."""
    test_id = "507f1f77bcf86cd799439011"
    entity = TestModel(id=test_id, name="Test Name")

    doc = repository._to_dict(entity)

    mock_object_id.assert_called_once_with(test_id)

    assert doc["_id"].return_value == f"ObjectId('{test_id}')"
    assert "id" not in doc
    assert doc["name"] == "Test Name"


# --- ASYNCHRONOUS METHOD TEST ---

@pytest.mark.asyncio
async def test_create(repository, mock_collection):
    """Tests the creation of an entity in the DB."""
    test_id = "507f1f77bcf86cd799439011"
    entity = TestModel(id=test_id, name="New Item")
    expected_inserted_id = RealObjectId(test_id)

    mock_result = MagicMock()
    mock_result.inserted_id = expected_inserted_id
    mock_collection.insert_one.return_value = mock_result
    
    inserted_id = await repository.create(entity)

    mock_collection.insert_one.assert_called_once()

    assert inserted_id == str(expected_inserted_id)


@pytest.mark.asyncio
async def test_find_by_id(repository, mock_collection):
    """Tests the search for an object by its ID"""
    test_id = "0123456789abcdf012345678"

    mock_collection.find_one.return_value = {
        "_id": "0123456789abcdf012345678",
        "name": "rick sanchez"
        }

    result = await repository.find_by_id(test_id)

    mock_collection.find_one.assert_called_once()

    assert result.id == test_id
    assert result.name == "rick sanchez"
    
    # the last line to cover
    # the if not data of from_dict()
    mock_collection.find_one.return_value = None
    result = await repository.find_by_id(test_id)

    assert result is None

@pytest.mark.asyncio
async def test_find_all(repository, mock_collection):
    """test the search for all objects without filters"""
    id1 = "0123456789abcdf012345678"
    id2 = "0123456789abcdf012345679"
    id3 = "0123456789abcdf01234567a"

    data_list = [
        {
        "_id": id1,
        "name": "rick sanchez"
        },
        {
        "_id": id2,
        "name": "morty smith"
        },
        {
        "_id": id3,
        "name": "jerry smith"
        }
    ]
    mock_collection.find.return_value = mock_async_cursor(data_list)    

    result = await repository.find_all({})


    mock_collection.find.assert_called_once()
    mock_collection.find.assert_called_once_with({})
    assert isinstance(result, list)
    assert len(result) == len(data_list)
    assert result[0].name == "rick sanchez"

@pytest.mark.asyncio
async def test_find_all_with_filters(repository, mock_collection):
    """Test the search for all objects but using filters"""
    data_filtered = [
        {
            "_id": "1a2b3c4d5e6f7a8b9c0d1e2f",
            "name": "summer smith"
        },
        {
            "_id": "1a2b3c4d5e6f7a8b9c0d1e2a",
            "name": "beth sanchez"
        }
    ]
    mock_collection.find.return_value = mock_async_cursor(data_filtered)

    result = await repository.find_all({"name": "summer smith", "name": "beth smith"})
    mock_collection.find.assert_called_once()
    mock_collection.find.assert_called_once_with({"name": "summer smith", "name": "beth smith"})
    assert len(result) == 2
    assert result[0].name == "summer smith"


@pytest.mark.asyncio
async def test_update(repository, mock_collection):
    """test the update an object"""
    object_id = "12345abcdef1234567890abc"
    real_id = RealObjectId(object_id)

    mock_update_result = MagicMock()
    mock_update_result.modified_count = 1

    mock_collection.update_one.return_value = mock_update_result

    result = await repository.update(real_id, {"name": "rick sanchez"})

    mock_collection.update_one.assert_called_once()
    mock_collection.update_one.assert_called_once_with({'_id': real_id}, {"$set": {"name": "rick sanchez"}})

    assert result is True
    assert isinstance(result, bool)

@pytest.mark.asyncio
async def test_update_not_modified(repository, mock_collection):
    """Tests the update flow of an object that was not found"""
    object_id = "12345abcdef1234567890abc"
    real_id = RealObjectId(object_id)

    mock_update_not_found = MagicMock()
    mock_update_not_found.modified_count = 0

    mock_collection.update_one.return_value = mock_update_not_found

    result = await repository.update(real_id, {"not": "found"})

    mock_collection.update_one.assert_called_once()
    mock_collection.update_one.assert_called_once_with({'_id': real_id}, {"$set": {"not": "found"}})
    assert result is False

@pytest.mark.asyncio
async def test_update_failure(repository):
    """Tests for a failure in the update flow"""
    with pytest.raises(InvalidId):
        await repository.update("aaa", {"id": "invalid"})


@pytest.mark.asyncio
async def test_delete(repository, mock_collection):
    """tests the deletion of an object"""
    object_id = "12345abcdef1234567890abc"
    real_id = RealObjectId(object_id)

    mock_update_result = MagicMock()
    mock_update_result.deleted_count = 1

    mock_collection.delete_one.return_value = mock_update_result

    result = await repository.delete(real_id)

    mock_collection.delete_one.assert_called_once()
    mock_collection.delete_one.assert_called_once_with({'_id': real_id})

    assert result is True
    assert isinstance(result, bool)

@pytest.mark.asyncio
async def test_not_object_to_delete(repository, mock_collection):
    """Test the flow of deleting an unfound object"""
    object_id = "12345abcdef1234567890abc"
    real_id = RealObjectId(object_id)

    mock_update_result = MagicMock()
    mock_update_result.deleted_count = 0

    mock_collection.delete_one.return_value = mock_update_result

    result = await repository.delete(real_id)

    mock_collection.delete_one.assert_called_once()
    mock_collection.delete_one.assert_called_once_with({'_id': real_id})

    assert result is False
    assert isinstance(result, bool)