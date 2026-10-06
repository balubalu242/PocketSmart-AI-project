from conftest import client


def register_and_login():
    import uuid
    email = f"{uuid.uuid4().hex}@example.com"
    response = client.post(
        "/register",
        data={
            "full_name": "Test User",
            "email": email,
            "password": "password123",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303

    response = client.post(
        "/login",
        data={"email": email, "password": "password123"},
        follow_redirects=False,
    )
    assert response.status_code == 303


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_auth_and_home_planner():
    register_and_login()

    response = client.get("/session-info")
    assert response.status_code == 200
    assert response.json()["authenticated"] is True

    response = client.post(
        "/generate-home",
        json={
            "budget": 50000,
            "rooms": [
                {
                    "room_type": "Living Room",
                    "quantity": 1,
                    "items": ["sofa", "lighting"],
                }
            ],
            "style": "modern",
            "city": "Chennai",
            "notes": "",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["planner"] == "home"
    assert data["budget"] == 50000
    assert len(data["recommendations"]) > 0
    assert data["id"] > 0


def test_party_planner_and_history():
    register_and_login()

    response = client.post(
        "/generate-party",
        json={
            "budget": 30000,
            "guest_count": 25,
            "event_type": "birthday",
            "venue": "home",
            "city": "Chennai",
            "food_preference": "vegetarian",
            "notes": "",
        },
    )
    assert response.status_code == 200

    history = client.get("/history")
    assert history.status_code == 200
    assert len(history.json()["items"]) >= 1


def test_jewelry_planner():
    register_and_login()

    response = client.post(
        "/generate-jewelry",
        data={
            "budget": "15000",
            "occasion": "wedding",
            "style": "traditional",
            "metal_preference": "gold-tone",
            "notes": "lightweight",
        },
    )
    assert response.status_code == 200
    assert response.json()["planner"] == "jewelry"


def test_protected_endpoint_requires_login():
    client.get("/logout")
    response = client.get("/session-info")
    assert response.status_code == 401
