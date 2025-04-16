from unittest.mock import patch

# from app.database.models import get_db_session


@patch("app.database.models.get_db_session")
def test_query_data(mock_session):
    mock_session.return_value.query.return_value.all.return_value = [
        {"name": "Item1", "value": 10, "description": "Test item"}
    ]
    # data = query_data(mock_session())
    # assert len(data) == 1
    # assert data[0]["name"] == "Item1"
