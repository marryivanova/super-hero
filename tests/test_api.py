from src.app.routers import _call_api_method, Endpoint


def test_call_api_method_returns_valid_response():
    response = _call_api_method("id", hero_id=1)

    assert response is not None
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, dict)

    if "id" in data:
        assert "name" in data
        assert "powerstats" in data or "biography" in data


def test_call_api_method_returns_valid_search_results():
    response = _call_api_method(endpoint=Endpoint.SEARCH, search_name="Abe Sapien")

    assert response.status_code == 200
    data = response.json()

    assert "results" in data
    assert len(data["results"]) > 0

    character = data["results"][0]

    assert "id" in character
    assert "name" in character
    assert character["name"] == "Abe Sapien"
