from unittest import mock
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException, status


user_data_admin = {
    "id": 1,
    "username": "dad",
    "email": "dad@gmail.com",
    "password": "12345678",
    "role": "admin",
    "confirmed": True,
    "avatar": "https://example.com/avatar.png",
}

user_data_not_admin = {
    "id": 1,
    "username": "dad",
    "email": "dad@gmail.com",
    "password": "12345678",
    "role": "user",
    "confirmed": True,
    "avatar": "https://example.com/avatar.png",
}


@pytest.mark.asyncio
async def test_me(client, monkeypatch, auth_headers):
    mock_jwt_decode = MagicMock(return_value={"sub": user_data_admin["username"]})
    monkeypatch.setattr("src.services.auth.jwt.decode", mock_jwt_decode)

    mock_get_user_from_db = AsyncMock(return_value=user_data_admin)
    monkeypatch.setattr("src.services.auth.get_user_from_db", mock_get_user_from_db)

    response = client.get("/api/users/me", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["email"] == user_data_admin["email"]
    assert response.json()["username"] == user_data_admin["username"]
    mock_jwt_decode.assert_called_once()
    mock_get_user_from_db.assert_called_once_with(user_data_admin["username"], mock.ANY)


@pytest.mark.asyncio
async def test_me_unauthenticated(client, monkeypatch):
    mock_get_current_user = AsyncMock(
        side_effect=HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не автентифіковано",
        )
    )
    monkeypatch.setattr("src.services.auth.get_current_user", mock_get_current_user)

    response = client.get("/api/users/me")

    assert response.status_code == 401
    assert response.json()["detail"] == "Не автентифіковано"
