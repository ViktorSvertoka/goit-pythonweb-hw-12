import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException, status
from src.schemas import ContactModel

user_data = {
    "id": 1,
    "username": "dad",
    "email": "dad@gmail.com",
    "password": "12345678",
    "role": "user",
    "confirmed": True,
}

contacts = [
    {
        "id": 1,
        "name": "Evan",
        "surname": "Jedi",
        "birthday": "2002-02-02",
        "email": "evan@example.com",
        "phone": "111-222-3333",
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00",
        "info": "Test contact.",
    },
    {
        "id": 2,
        "name": "Mia",
        "surname": "Jedi",
        "birthday": "2004-04-04",
        "email": "mia@example.com",
        "phone": "111-333-5555",
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00",
        "info": None,
    },
]

payload = {
    "name": "Evan",
    "surname": "Jedi",
    "birthday": "2002-02-02",
    "email": "evan@example.com",
    "phone": "111-222-3333",
}


@pytest.mark.asyncio
async def test_get_upcoming_birthdays(client, monkeypatch, auth_headers):
    mock_jwt_decode = MagicMock(return_value={"sub": user_data["username"]})
    monkeypatch.setattr("src.services.auth.jwt.decode", mock_jwt_decode)

    mock_get_user_from_db = AsyncMock(return_value=user_data)
    monkeypatch.setattr("src.services.auth.get_user_from_db", mock_get_user_from_db)

    mock_get_upcoming_birthdays = AsyncMock(return_value=contacts)
    monkeypatch.setattr(
        "src.services.contacts.ContactService.get_upcoming_birthdays",
        mock_get_upcoming_birthdays,
    )

    response = client.get("/api/contacts/birthdays?days=7", headers=auth_headers)

    assert response.status_code == 200
    assert len(response.json()) == len(contacts)
    assert response.json()[0]["name"] == contacts[0]["name"]
    mock_get_upcoming_birthdays.assert_called_once_with(7, user_data)


@pytest.mark.asyncio
async def test_get_upcoming_birthdays_unauthenticated(client, monkeypatch):
    mock_get_current_user = AsyncMock(
        side_effect=HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не автентифіковано",
        )
    )
    monkeypatch.setattr(
        "src.services.auth_service.get_current_user", mock_get_current_user
    )

    response = client.get("/api/contacts/birthdays?days=7")

    assert response.status_code == 401
    assert response.json()["detail"] == "Не автентифіковано"


@pytest.mark.asyncio
async def test_get_contacts_no_filters(client, monkeypatch, auth_headers):
    mock_jwt_decode = MagicMock(return_value={"sub": user_data["username"]})
    monkeypatch.setattr("src.services.auth.jwt.decode", mock_jwt_decode)

    mock_get_user_from_db = AsyncMock(return_value=user_data)
    monkeypatch.setattr("src.services.auth.get_user_from_db", mock_get_user_from_db)

    mock_get_contacts = AsyncMock(return_value=contacts)
    monkeypatch.setattr(
        "src.services.contacts.ContactService.get_contacts", mock_get_contacts
    )

    response = client.get("/api/contacts/", headers=auth_headers)

    assert response.status_code == 200
    assert len(response.json()) == len(contacts)
    assert response.json()[0]["email"] == contacts[0]["email"]
    mock_get_contacts.assert_called_once_with("", "", "", 0, 100, user_data)


@pytest.mark.asyncio
async def test_get_contacts_with_filters(client, monkeypatch, auth_headers):
    mock_jwt_decode = MagicMock(return_value={"sub": user_data["username"]})
    monkeypatch.setattr("src.services.auth.jwt.decode", mock_jwt_decode)
    mock_get_user_from_db = AsyncMock(return_value=user_data)
    monkeypatch.setattr("src.services.auth.get_user_from_db", mock_get_user_from_db)

    filtered_contacts = [contacts[0]]
    mock_get_contacts = AsyncMock(return_value=filtered_contacts)
    monkeypatch.setattr(
        "src.services.contacts.ContactService.get_contacts", mock_get_contacts
    )

    response = client.get("/api/contacts/?name=Evan&surname=Jedi", headers=auth_headers)

    assert response.status_code == 200
    assert len(response.json()) == len(filtered_contacts)
    assert response.json()[0]["name"] == "Evan"
    mock_get_contacts.assert_called_once_with("Evan", "Jedi", "", 0, 100, user_data)


@pytest.mark.asyncio
async def test_get_contacts_pagination(client, monkeypatch, auth_headers):
    mock_jwt_decode = MagicMock(return_value={"sub": user_data["username"]})
    monkeypatch.setattr("src.services.auth.jwt.decode", mock_jwt_decode)
    mock_get_user_from_db = AsyncMock(return_value=user_data)
    monkeypatch.setattr("src.services.auth.get_user_from_db", mock_get_user_from_db)

    paginated_contacts = [
        {
            "id": 3,
            "name": "Inna",
            "surname": "Jedi",
            "email": "inna@example.com",
            "phone": "777-555-1111",
            "birthday": "2006-06-06",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
        }
    ]
    mock_get_contacts = AsyncMock(return_value=paginated_contacts)
    monkeypatch.setattr(
        "src.services.contacts.ContactService.get_contacts", mock_get_contacts
    )

    response = client.get("/api/contacts/?skip=2&limit=1", headers=auth_headers)

    assert response.status_code == 200
    assert len(response.json()) == len(paginated_contacts)
    assert response.json()[0]["id"] == 3
    mock_get_contacts.assert_called_once_with("", "", "", 2, 1, user_data)


@pytest.mark.asyncio
async def test_get_contacts_unauthenticated(client, monkeypatch):
    mock_get_current_user = AsyncMock(
        side_effect=HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не автентифіковано",
        )
    )
    monkeypatch.setattr("src.services.auth.get_current_user", mock_get_current_user)

    response = client.get("/api/contacts/")

    assert response.status_code == 401
    assert response.json()["detail"] == "Не автентифіковано"


@pytest.mark.asyncio
async def test_get_contact_success(client, monkeypatch, auth_headers):
    mock_jwt_decode = MagicMock(return_value={"sub": user_data["username"]})
    monkeypatch.setattr("src.services.auth.jwt.decode", mock_jwt_decode)

    mock_get_user_from_db = AsyncMock(return_value=user_data)
    monkeypatch.setattr("src.services.auth.get_user_from_db", mock_get_user_from_db)

    contact = contacts[0]
    mock_get_contact = AsyncMock(return_value=contact)
    monkeypatch.setattr(
        "src.services.contacts.ContactService.get_contact", mock_get_contact
    )

    response = client.get("/api/contacts/1", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["id"] == contact["id"]
    assert response.json()["name"] == contact["name"]
    mock_get_contact.assert_called_once_with(1, user_data)


@pytest.mark.asyncio
async def test_get_contact_not_found(client, monkeypatch, auth_headers):
    mock_jwt_decode = MagicMock(return_value={"sub": user_data["username"]})
    monkeypatch.setattr("src.services.auth.jwt.decode", mock_jwt_decode)
    mock_get_user_from_db = AsyncMock(return_value=user_data)
    monkeypatch.setattr("src.services.auth.get_user_from_db", mock_get_user_from_db)

    mock_get_contact = AsyncMock(return_value=None)
    monkeypatch.setattr(
        "src.services.contacts.ContactService.get_contact", mock_get_contact
    )

    response = client.get("/api/contacts/777", headers=auth_headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Контакт не знайдено"
    mock_get_contact.assert_called_once_with(777, user_data)


@pytest.mark.asyncio
async def test_get_contact_unauthenticated(client, monkeypatch):
    mock_get_current_user = AsyncMock(
        side_effect=HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не автентифіковано",
        )
    )
    monkeypatch.setattr("src.services.auth.get_current_user", mock_get_current_user)

    response = client.get("/api/contacts/1")

    assert response.status_code == 401
    assert response.json()["detail"] == "Не автентифіковано"


@pytest.mark.asyncio
async def test_create_contact_success(client, monkeypatch, auth_headers):
    mock_jwt_decode = MagicMock(return_value={"sub": user_data["username"]})
    monkeypatch.setattr("src.services.auth.jwt.decode", mock_jwt_decode)

    mock_get_user_from_db = AsyncMock(return_value=user_data)
    monkeypatch.setattr("src.services.auth.get_user_from_db", mock_get_user_from_db)

    new_contact = contacts[0]
    mock_create_contact = AsyncMock(return_value=new_contact)
    monkeypatch.setattr(
        "src.services.contacts.ContactService.create_contact",
        mock_create_contact,
    )

    response = client.post("/api/contacts/", json=payload, headers=auth_headers)

    expected_contact = ContactModel(**payload)

    assert response.status_code == 201
    assert response.json()["id"] == new_contact["id"]
    assert response.json()["name"] == new_contact["name"]
    mock_create_contact.assert_called_once_with(expected_contact, user_data)


@pytest.mark.asyncio
async def test_create_contact_invalid_data(client, monkeypatch, auth_headers):
    mock_jwt_decode = MagicMock(return_value={"sub": user_data["username"]})
    monkeypatch.setattr("src.services.auth.jwt.decode", mock_jwt_decode)
    mock_get_user_from_db = AsyncMock(return_value=user_data)
    monkeypatch.setattr("src.services.auth.get_user_from_db", mock_get_user_from_db)

    invalid_payload = {
        "name": "",
    }

    response = client.post("/api/contacts/", json=invalid_payload, headers=auth_headers)

    assert response.status_code == 422
    assert "detail" in response.json()


@pytest.mark.asyncio
async def test_create_contact_unauthenticated(client, monkeypatch):
    mock_get_current_user = AsyncMock(
        side_effect=HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не автентифіковано",
        )
    )
    monkeypatch.setattr("src.services.auth.get_current_user", mock_get_current_user)

    response = client.post("/api/contacts/", json=payload)

    assert response.status_code == 401
    assert response.json()["detail"] == "Не автентифіковано"


@pytest.mark.asyncio
async def test_update_contact_success(client, monkeypatch, auth_headers):
    mock_jwt_decode = MagicMock(return_value={"sub": user_data["username"]})
    monkeypatch.setattr("src.services.auth.jwt.decode", mock_jwt_decode)

    mock_get_user_from_db = AsyncMock(return_value=user_data)
    monkeypatch.setattr("src.services.auth.get_user_from_db", mock_get_user_from_db)

    updated_contact = {
        **contacts[0],
        "name": "UpdatedEvan",
        "surname": "UpdatedJedi",
    }
    mock_update_contact = AsyncMock(return_value=updated_contact)
    monkeypatch.setattr(
        "src.services.contacts.ContactService.update_contact",
        mock_update_contact,
    )

    payload = {
        "name": "UpdatedEvan",
        "surname": "UpdatedJedi",
        "birthday": "2002-02-02",
        "email": "evan@example.com",
        "phone": "111-222-3333",
    }

    contact_id = contacts[0]["id"]

    response = client.put(
        f"/api/contacts/{contact_id}", json=payload, headers=auth_headers
    )

    expected_contact = ContactModel(**payload)

    assert response.status_code == 200
    assert response.json()["id"] == updated_contact["id"]
    assert response.json()["name"] == updated_contact["name"]
    assert response.json()["surname"] == updated_contact["surname"]
    mock_update_contact.assert_called_once_with(contact_id, expected_contact, user_data)


@pytest.mark.asyncio
async def test_update_contact_not_found(client, monkeypatch, auth_headers):
    mock_jwt_decode = MagicMock(return_value={"sub": user_data["username"]})
    monkeypatch.setattr("src.services.auth.jwt.decode", mock_jwt_decode)
    mock_get_user_from_db = AsyncMock(return_value=user_data)
    monkeypatch.setattr("src.services.auth.get_user_from_db", mock_get_user_from_db)

    mock_update_contact = AsyncMock(return_value=None)
    monkeypatch.setattr(
        "src.services.contacts.ContactService.update_contact",
        mock_update_contact,
    )

    payload = {
        "name": "NonExistent",
        "surname": "Contact",
        "birthday": "2002-02-02",
        "email": "nonexistent@example.com",
        "phone": "777-777-7777",
    }

    response = client.put("/api/contacts/777", json=payload, headers=auth_headers)

    expected_contact = ContactModel(**payload)

    assert response.status_code == 404
    assert response.json()["detail"] == "Контакт не знайдено"
    mock_update_contact.assert_called_once_with(777, expected_contact, user_data)


@pytest.mark.asyncio
async def test_update_contact_invalid_data(client, monkeypatch, auth_headers):
    mock_jwt_decode = MagicMock(return_value={"sub": user_data["username"]})
    monkeypatch.setattr("src.services.auth.jwt.decode", mock_jwt_decode)
    mock_get_user_from_db = AsyncMock(return_value=user_data)
    monkeypatch.setattr("src.services.auth.get_user_from_db", mock_get_user_from_db)

    invalid_payload = {
        "name": "",
    }

    response = client.put("/api/contacts/1", json=invalid_payload, headers=auth_headers)

    assert response.status_code == 422
    assert "detail" in response.json()


@pytest.mark.asyncio
async def test_update_contact_unauthenticated(client, monkeypatch):
    mock_get_current_user = AsyncMock(
        side_effect=HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не автентифіковано",
        )
    )
    monkeypatch.setattr("src.services.auth.get_current_user", mock_get_current_user)

    response = client.put("/api/contacts/1", json={})

    assert response.status_code == 401
    assert response.json()["detail"] == "Не автентифіковано"


@pytest.mark.asyncio
async def test_delete_contact_success(client, monkeypatch, auth_headers):
    mock_jwt_decode = MagicMock(return_value={"sub": user_data["username"]})
    monkeypatch.setattr("src.services.auth.jwt.decode", mock_jwt_decode)

    mock_get_user_from_db = AsyncMock(return_value=user_data)
    monkeypatch.setattr("src.services.auth.get_user_from_db", mock_get_user_from_db)

    mock_delete_contact = AsyncMock(return_value=contacts[0])
    monkeypatch.setattr(
        "src.services.contacts.ContactService.remove_contact",
        mock_delete_contact,
    )

    contact_id = contacts[0]["id"]

    response = client.delete(f"/api/contacts/{contact_id}", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == contacts[0]
    mock_delete_contact.assert_called_once_with(contact_id, user_data)


@pytest.mark.asyncio
async def test_delete_contact_not_found(client, monkeypatch, auth_headers):
    mock_jwt_decode = MagicMock(return_value={"sub": user_data["username"]})
    monkeypatch.setattr("src.services.auth.jwt.decode", mock_jwt_decode)

    mock_get_user_from_db = AsyncMock(return_value=user_data)
    monkeypatch.setattr("src.services.auth.get_user_from_db", mock_get_user_from_db)

    mock_delete_contact = AsyncMock(return_value=None)
    monkeypatch.setattr(
        "src.services.contacts.ContactService.remove_contact",
        mock_delete_contact,
    )

    contact_id = 777

    response = client.delete(f"/api/contacts/{contact_id}", headers=auth_headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Контакт не знайдено"
    mock_delete_contact.assert_called_once_with(contact_id, user_data)


@pytest.mark.asyncio
async def test_delete_contact_unauthenticated(client, monkeypatch):
    mock_get_current_user = AsyncMock(
        side_effect=HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не автентифіковано",
        )
    )
    monkeypatch.setattr("src.services.auth.get_current_user", mock_get_current_user)

    contact_id = contacts[0]["id"]

    response = client.delete(f"/api/contacts/{contact_id}")

    assert response.status_code == 401
    assert response.json()["detail"] == "Не автентифіковано"
