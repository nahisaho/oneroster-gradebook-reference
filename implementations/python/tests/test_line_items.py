"""
Tests for Line Items API endpoints.
"""


def test_get_line_items_collection(client, oauth_token, sample_line_item):
    """Test getting collection of line items."""
    response = client.get(
        "/ims/oneroster/v1p2/lineItems",
        headers={"Authorization": f"Bearer {oauth_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "total" in data
    assert "limit" in data
    assert "offset" in data
    assert data["total"] >= 1
    assert len(data["data"]) >= 1

    # Verify line item structure
    line_item = data["data"][0]
    assert "sourcedId" in line_item
    assert "status" in line_item
    assert "dateLastModified" in line_item
    assert "title" in line_item
    assert "category" in line_item


def test_get_line_item_by_id(client, oauth_token, sample_line_item):
    """Test getting a single line item by sourcedId."""
    response = client.get(
        f"/ims/oneroster/v1p2/lineItems/{sample_line_item.sourced_id}",
        headers={"Authorization": f"Bearer {oauth_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["sourcedId"] == sample_line_item.sourced_id
    assert data["title"] == sample_line_item.title
    assert data["status"] == "active"
    assert data["category"]["sourcedId"] == sample_line_item.category_sourced_id


def test_get_line_item_not_found(client, oauth_token):
    """Test getting a non-existent line item."""
    response = client.get(
        "/ims/oneroster/v1p2/lineItems/non-existent-id",
        headers={"Authorization": f"Bearer {oauth_token}"},
    )

    assert response.status_code == 404


def test_create_line_item(client, oauth_token, sample_category):
    """Test creating a new line item."""
    # Get token with createput scope
    token_response = client.post(
        "/oauth/token",
        data={
            "grant_type": "client_credentials",
            "client_id": "test_client",
            "client_secret": "test_secret",
            "scope": "https://purl.imsglobal.org/spec/or/v1p2/scope/results.createput",
        },
    )
    token = token_response.json()["access_token"]

    response = client.post(
        "/ims/oneroster/v1p2/lineItems",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "sourcedId": "li-new-001",
            "title": "New Assignment",
            "description": "Test assignment",
            "assignDate": "2024-01-15",
            "dueDate": "2024-01-20",
            "classSourcedId": "class-001",
            "categorySourcedId": sample_category.sourced_id,
            "resultValueMin": 0.0,
            "resultValueMax": 100.0,
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["sourcedId"] == "li-new-001"
    assert data["title"] == "New Assignment"
    if data.get("category"):
        assert data["category"]["sourcedId"] == sample_category.sourced_id


def test_update_line_item(client, oauth_token, sample_line_item):
    """Test updating an existing line item."""
    # Get token with createput scope
    token_response = client.post(
        "/oauth/token",
        data={
            "grant_type": "client_credentials",
            "client_id": "test_client",
            "client_secret": "test_secret",
            "scope": "https://purl.imsglobal.org/spec/or/v1p2/scope/results.createput",
        },
    )
    token = token_response.json()["access_token"]

    response = client.put(
        f"/ims/oneroster/v1p2/lineItems/{sample_line_item.sourced_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Updated Assignment",
            "description": "Updated description",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Assignment"
    assert data["description"] == "Updated description"


def test_delete_line_item(client, oauth_token, sample_line_item):
    """Test soft deleting a line item."""
    # Get token with delete scope
    token_response = client.post(
        "/oauth/token",
        data={
            "grant_type": "client_credentials",
            "client_id": "test_client",
            "client_secret": "test_secret",
            "scope": "https://purl.imsglobal.org/spec/or/v1p2/scope/results.delete",
        },
    )
    token = token_response.json()["access_token"]

    response = client.delete(
        f"/ims/oneroster/v1p2/lineItems/{sample_line_item.sourced_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 204


def test_get_line_items_with_pagination(client, oauth_token, db_session, sample_category):
    """Test pagination of line items."""
    # Create multiple line items
    import time

    from src.models.models import LineItem, StatusEnum

    base_ts = int(time.time() * 1000000)
    for i in range(5):
        line_item = LineItem(
            sourced_id=f"li-page-{base_ts + i}",
            status=StatusEnum.active,
            title=f"Assignment {i}",
            description=f"Description {i}",
            class_sourced_id="class-001",
            category_sourced_id=sample_category.sourced_id,
            result_value_min=0.0,
            result_value_max=100.0,
        )
        db_session.add(line_item)
    db_session.commit()

    # Test pagination
    response = client.get(
        "/ims/oneroster/v1p2/lineItems?limit=2&offset=1",
        headers={"Authorization": f"Bearer {oauth_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["limit"] == 2
    assert data["offset"] == 1
    assert len(data["data"]) <= 2


def test_get_line_items_with_filter(client, oauth_token, db_session, sample_category):
    """Test filtering line items."""
    # Create line items with different titles
    import time

    from src.models.models import LineItem, StatusEnum

    base_ts = int(time.time() * 1000000)
    line_item1 = LineItem(
        sourced_id=f"li-math-{base_ts}",
        status=StatusEnum.active,
        title="Math Homework",
        description="Math assignment",
        class_sourced_id="class-001",
        category_sourced_id=sample_category.sourced_id,
        result_value_min=0.0,
        result_value_max=100.0,
    )
    line_item2 = LineItem(
        sourced_id=f"li-science-{base_ts}",
        status=StatusEnum.active,
        title="Science Project",
        description="Science assignment",
        class_sourced_id="class-001",
        category_sourced_id=sample_category.sourced_id,
        result_value_min=0.0,
        result_value_max=100.0,
    )
    db_session.add(line_item1)
    db_session.add(line_item2)
    db_session.commit()

    # Test filter
    response = client.get(
        "/ims/oneroster/v1p2/lineItems?filter=title~'Math'",
        headers={"Authorization": f"Bearer {oauth_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    # Should find at least the Math line item
    assert any("Math" in li["title"] for li in data["data"])


def test_get_line_items_with_sort(client, oauth_token, db_session, sample_category):
    """Test sorting line items."""
    # Create line items with different due dates
    import time
    from datetime import datetime

    from src.models.models import LineItem, StatusEnum

    base_ts = int(time.time() * 1000000)
    for i, due_date_str in enumerate(["2024-01-20", "2024-01-18", "2024-01-22"]):
        line_item = LineItem(
            sourced_id=f"li-sort-{base_ts + i}",
            status=StatusEnum.active,
            title=f"Assignment {i}",
            description=f"Description {i}",
            class_sourced_id="class-001",
            category_sourced_id=sample_category.sourced_id,
            due_date=datetime.fromisoformat(due_date_str),
            result_value_min=0.0,
            result_value_max=100.0,
        )
        db_session.add(line_item)
    db_session.commit()

    # Test sort by due_date ascending
    response = client.get(
        "/ims/oneroster/v1p2/lineItems?sort=dueDate ASC",
        headers={"Authorization": f"Bearer {oauth_token}"},
    )

    assert response.status_code == 200
    data = response.json()

    # Check if sorted by dueDate ascending
    if len(data["data"]) >= 2:
        due_dates = [li.get("dueDate") for li in data["data"] if "dueDate" in li]
        if len(due_dates) >= 2:
            assert due_dates[0] <= due_dates[1]


def test_line_item_category_relationship(client, oauth_token, sample_line_item, sample_category):
    """Test that line item includes category information."""
    response = client.get(
        f"/ims/oneroster/v1p2/lineItems/{sample_line_item.sourced_id}",
        headers={"Authorization": f"Bearer {oauth_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "category" in data
    assert data["category"]["sourcedId"] == sample_category.sourced_id
    assert data["category"]["type"] == "category"


def test_update_nonexistent_line_item(client, oauth_token):
    """Test updating a line item that doesn't exist."""
    token_response = client.post(
        "/oauth/token",
        data={
            "grant_type": "client_credentials",
            "client_id": "test_client",
            "client_secret": "test_secret",
            "scope": "https://purl.imsglobal.org/spec/or/v1p2/scope/results.createput",
        },
    )
    token = token_response.json()["access_token"]

    response = client.put(
        "/ims/oneroster/v1p2/lineItems/nonexistent-id",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Updated Title"},
    )

    assert response.status_code == 404


def test_delete_nonexistent_line_item(client, oauth_token):
    """Test deleting a line item that doesn't exist."""
    token_response = client.post(
        "/oauth/token",
        data={
            "grant_type": "client_credentials",
            "client_id": "test_client",
            "client_secret": "test_secret",
            "scope": "https://purl.imsglobal.org/spec/or/v1p2/scope/results.delete",
        },
    )
    token = token_response.json()["access_token"]

    response = client.delete(
        "/ims/oneroster/v1p2/lineItems/nonexistent-id",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404


def test_update_line_item_all_fields(client, oauth_token, sample_line_item, sample_category):
    """Test updating all fields of a line item."""
    from datetime import datetime

    token_response = client.post(
        "/oauth/token",
        data={
            "grant_type": "client_credentials",
            "client_id": "test_client",
            "client_secret": "test_secret",
            "scope": "https://purl.imsglobal.org/spec/or/v1p2/scope/results.createput",
        },
    )
    token = token_response.json()["access_token"]

    response = client.put(
        f"/ims/oneroster/v1p2/lineItems/{sample_line_item.sourced_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Fully Updated Assignment",
            "description": "Fully updated description",
            "assignDate": "2024-01-15T00:00:00Z",
            "dueDate": "2024-01-30T23:59:59Z",
            "categorySourcedId": sample_category.sourced_id,
            "resultValueMin": 10.0,
            "resultValueMax": 110.0,
            "metadata": {"updated": "all_fields"},
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Fully Updated Assignment"
    assert data["description"] == "Fully updated description"
    assert "assignDate" in data or "assign_date" in data
    assert "dueDate" in data or "due_date" in data


def test_update_line_item_individual_fields(client, oauth_token, sample_line_item, sample_category):
    """Test updating individual fields of a line item."""
    token_response = client.post(
        "/oauth/token",
        data={
            "grant_type": "client_credentials",
            "client_id": "test_client",
            "client_secret": "test_secret",
            "scope": "https://purl.imsglobal.org/spec/or/v1p2/scope/results.createput",
        },
    )
    token = token_response.json()["access_token"]

    # Update assignDate only
    response = client.put(
        f"/ims/oneroster/v1p2/lineItems/{sample_line_item.sourced_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"assignDate": "2024-02-01T00:00:00Z"},
    )
    assert response.status_code == 200

    # Update dueDate only
    response = client.put(
        f"/ims/oneroster/v1p2/lineItems/{sample_line_item.sourced_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"dueDate": "2024-02-28T23:59:59Z"},
    )
    assert response.status_code == 200

    # Update resultValueMin only
    response = client.put(
        f"/ims/oneroster/v1p2/lineItems/{sample_line_item.sourced_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"resultValueMin": 5.0},
    )
    assert response.status_code == 200

    # Update resultValueMax only
    response = client.put(
        f"/ims/oneroster/v1p2/lineItems/{sample_line_item.sourced_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"resultValueMax": 95.0},
    )
    assert response.status_code == 200

    # Update metadata only
    response = client.put(
        f"/ims/oneroster/v1p2/lineItems/{sample_line_item.sourced_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"metadata": {"field": "value"}},
    )
    assert response.status_code == 200

    # Update categorySourcedId only
    response = client.put(
        f"/ims/oneroster/v1p2/lineItems/{sample_line_item.sourced_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"categorySourcedId": sample_category.sourced_id},
    )
    assert response.status_code == 200
