def test_register_masks_license_and_login_works(client):
    registration = client.post(
        "/auth/register",
        json={
            "email": "customer@example.com",
            "password": "simple-password",
            "full_name": "Test Customer",
            "phone": "1234567890",
            "licence_no": "AB123456789",
        },
    )

    assert registration.status_code == 201
    assert registration.json()["licence_no"] == "AB****6789"

    login = client.post(
        "/auth/login",
        json={"email": "customer@example.com", "password": "simple-password"},
    )
    assert login.status_code == 200
    assert login.json()["access_token"]


def test_login_rejects_wrong_password(client):
    client.post(
        "/auth/register",
        json={
            "email": "customer@example.com",
            "password": "simple-password",
            "full_name": "Test Customer",
            "phone": "1234567890",
        },
    )

    response = client.post(
        "/auth/login",
        json={"email": "customer@example.com", "password": "incorrect"},
    )

    assert response.status_code == 401
