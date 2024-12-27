import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import Contact, User
from src.repository.contacts import ContactRepository
from src.schemas import ContactModel


@pytest.fixture
def mock_session():
    mock_session = AsyncMock(spec=AsyncSession)
    return mock_session


@pytest.fixture
def contact_repository(mock_session):
    return ContactRepository(mock_session)


@pytest.fixture
def user():
    return User(id=1, username="testuser", role="user")


@pytest.fixture
def contact(user: User):
    return Contact(
        id=1,
        name="Evan",
        surname="Jedi",
        email="evan@example.com",
        phone="111-222-3333",
        birthday="2002-02-02",
        user=user,
    )


@pytest.fixture
def contact_none():
    return None


@pytest.fixture
def contact_body():
    return ContactModel(
        name="Evan",
        surname="Jedi",
        email="evan@example.com",
        phone="111-222-3333",
        birthday="2002-02-02",
    )


@pytest.mark.asyncio
async def test_get_contacts(contact_repository, mock_session, user, contact):
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [contact]
    mock_session.execute = AsyncMock(return_value=mock_result)

    contacts = await contact_repository.get_contacts(
        skip=0,
        limit=10,
        user=user,
        name="",
        surname="",
        email="",
    )

    assert len(contacts) == 1
    assert contacts[0].name == "Evan"


@pytest.mark.asyncio
async def test_get_contact_by_id(contact_repository, mock_session, user, contact):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    contact_record = await contact_repository.get_contact_by_id(contact_id=1, user=user)

    assert contact_record is not None
    assert contact_record.id == 1
    assert contact_record.name == "Evan"


@pytest.mark.asyncio
async def test_create_contact_successful(
    contact_repository, mock_session, user, contact_body
):
    result = await contact_repository.create_contact(body=contact_body, user=user)

    assert isinstance(result, Contact)
    assert result.name == "Evan"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(result)


@pytest.mark.asyncio
async def test_create_contact_failure(
    contact_repository, mock_session, user, contact_body
):
    result = await contact_repository.create_contact(body=contact_body, user=user)

    assert isinstance(result, Contact)
    assert result.name != "Evan2"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(result)


@pytest.mark.asyncio
async def test_update_contact(contact_repository, mock_session, user, contact):
    contact_data = ContactModel(**contact.__dict__)
    contact_data.name = "Evan2"
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await contact_repository.update_contact(
        contact_id=1, body=contact_data, user=user
    )

    assert result is not None
    assert result.name == "Evan2"
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(contact)


@pytest.mark.asyncio
async def test_remove_contact(contact_repository, mock_session, user, contact):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await contact_repository.remove_contact(contact_id=1, user=user)

    assert result is not None
    assert result.name == "Evan"
    mock_session.delete.assert_awaited_once_with(contact)
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_is_contact_exists_success(
    contact_repository, mock_session, user, contact
):
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    is_contact_exist = await contact_repository.is_contact_exists(
        "qwerty@gmail.com", "111-22-33", user=user
    )

    assert is_contact_exist is True


@pytest.mark.asyncio
async def test_is_contact_exists_failure(
    contact_repository, mock_session, user, contact_none
):
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = contact_none
    mock_session.execute = AsyncMock(return_value=mock_result)

    is_contact_exist = await contact_repository.is_contact_exists(
        "qwerty@gmail.com", "111-22-33", user=user
    )

    assert is_contact_exist is False
