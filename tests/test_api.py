from unittest.mock import AsyncMock, patch


def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Go to /api/dashboard/view"}


# patch for no internet access
@patch("external_api.service.CatApiService.get_dashboard_data")
def test_dashboard_json(mock_get_data, client):
    # create mock return data
    mock_data = AsyncMock()
    mock_data.neko_image_url = "http://test.com/cat.jpg"
    mock_data.fact = "Testing cats is fun"
    mock_data.http_cat_url = "http://http.cat/200"

    # setting up mock for return object mock
    mock_get_data.return_value = mock_data

    response = client.get("/api/dashboard/json")

    assert response.status_code == 200
    data = response.json()
    assert data["fact"] == "Testing cats is fun"
