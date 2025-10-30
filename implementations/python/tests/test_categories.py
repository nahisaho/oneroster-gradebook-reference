"""
Tests for Categories API endpoints.
"""


def test_get_categories_collection(client, oauth_token, sample_category):
    """Test getting collection of categories."""
    response = client.get(
        "/ims/oneroster/v1p2/categories",
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

    # Verify category structure
    category = data["data"][0]
    assert "sourcedId" in category
    assert "status" in category
    assert "dateLastModified" in category
    assert "title" in category


def test_get_category_by_id(client, oauth_token, sample_category):
    """Test getting a single category by sourcedId."""
    response = client.get(
        f"/ims/oneroster/v1p2/categories/{sample_category.sourced_id}",
        headers={"Authorization": f"Bearer {oauth_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["sourcedId"] == sample_category.sourced_id
    assert data["title"] == sample_category.title
    assert data["status"] == "active"


def test_get_category_not_found(client, oauth_token):
    """Test getting a non-existent category."""
    response = client.get(
        "/ims/oneroster/v1p2/categories/non-existent-id",
        headers={"Authorization": f"Bearer {oauth_token}"},
    )

    assert response.status_code == 404


def test_create_category(client, oauth_token):
    """Test creating a new category."""
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
        "/ims/oneroster/v1p2/categories",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "sourcedId": "cat-new-001",
            "title": "New Category",
            "weight": 0.4,
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["sourcedId"] == "cat-new-001"
    assert data["title"] == "New Category"
    assert data["weight"] == 0.4


def test_update_category(client, oauth_token, sample_category):
    """Test updating an existing category."""
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
        f"/ims/oneroster/v1p2/categories/{sample_category.sourced_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Updated Category",
            "weight": 0.6,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Category"
    assert data["weight"] == 0.6


def test_delete_category(client, oauth_token, sample_category):
    """Test soft deleting a category."""
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
        f"/ims/oneroster/v1p2/categories/{sample_category.sourced_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 204


def test_get_categories_with_pagination(client, oauth_token, db_session):
    """Test pagination of categories."""
    # Create multiple categories
    import time

    from src.models.models import Category, StatusEnum

    base_ts = int(time.time() * 1000000)
    for i in range(5):
        category = Category(
            sourced_id=f"cat-page-{base_ts + i}",
            status=StatusEnum.active,
            title=f"Category {i}",
            weight=0.2,
        )
        db_session.add(category)
    db_session.commit()

    # Test pagination
    response = client.get(
        "/ims/oneroster/v1p2/categories?limit=2&offset=1",
        headers={"Authorization": f"Bearer {oauth_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["limit"] == 2
    assert data["offset"] == 1
    assert len(data["data"]) <= 2


def test_get_categories_with_filter(client, oauth_token, db_session):
    """Test filtering categories."""
    # Create categories with different titles
    import time

    from src.models.models import Category, StatusEnum

    base_ts = int(time.time() * 1000000)
    category1 = Category(
        sourced_id=f"cat-math-{base_ts}",
        status=StatusEnum.active,
        title="Math Homework",
        weight=0.3,
    )
    category2 = Category(
        sourced_id=f"cat-science-{base_ts}",
        status=StatusEnum.active,
        title="Science Project",
        weight=0.4,
    )
    db_session.add(category1)
    db_session.add(category2)
    db_session.commit()

    # Test filter
    response = client.get(
        "/ims/oneroster/v1p2/categories?filter=title~'Math'",
        headers={"Authorization": f"Bearer {oauth_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    # Should find at least the Math category
    assert any("Math" in cat["title"] for cat in data["data"])


def test_get_categories_with_sort(client, oauth_token, db_session):
    """Test sorting categories."""
    # Create categories with different weights
    import time

    from src.models.models import Category, StatusEnum

    base_ts = int(time.time() * 1000000)
    for i, weight in enumerate([0.1, 0.5, 0.3]):
        category = Category(
            sourced_id=f"cat-sort-{base_ts + i}",
            status=StatusEnum.active,
            title=f"Category {i}",
            weight=weight,
        )
        db_session.add(category)
    db_session.commit()

    # Test sort by weight descending
    response = client.get(
        "/ims/oneroster/v1p2/categories?sort=weight DESC",
        headers={"Authorization": f"Bearer {oauth_token}"},
    )

    assert response.status_code == 200
    data = response.json()

    # Check if sorted by weight descending
    if len(data["data"]) >= 2:
        weights = [cat.get("weight", 0) for cat in data["data"] if "weight" in cat]
        if len(weights) >= 2:
            assert weights[0] >= weights[1]


def test_update_nonexistent_category(client, oauth_token):
    """Test updating a category that doesn't exist."""
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
        "/ims/oneroster/v1p2/categories/nonexistent-id",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Updated Title"},
    )

    assert response.status_code == 404


def test_delete_nonexistent_category(client, oauth_token):
    """Test deleting a category that doesn't exist."""
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
        "/ims/oneroster/v1p2/categories/nonexistent-id",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404


def test_create_category_with_metadata(client, oauth_token):
    """Test creating a category with metadata."""
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
        "/ims/oneroster/v1p2/categories",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "sourcedId": "cat-metadata-001",
            "title": "Category with Metadata",
            "weight": 0.3,
            "metadata": {"key1": "value1", "key2": "value2"},
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert "metadata" in data
    assert data["metadata"]["key1"] == "value1"


def test_create_category_with_invalid_weight(client, oauth_token):
    """Test creating a category with invalid weight value."""
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
        "/ims/oneroster/v1p2/categories",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "sourcedId": "cat-invalid-001",
            "title": "Invalid Category",
            "weight": 1.5,  # Weight should be between 0 and 1
        },
    )

    assert response.status_code == 422


def test_create_duplicate_category(client, oauth_token, sample_category):
    """Test creating a category with duplicate sourcedId."""
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
        "/ims/oneroster/v1p2/categories",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "sourcedId": sample_category.sourced_id,  # Duplicate ID
            "title": "Duplicate Category",
            "weight": 0.3,
        },
    )

    assert response.status_code == 409


def test_update_category_weight(client, oauth_token, sample_category):
    """Test updating category weight specifically."""
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
        f"/ims/oneroster/v1p2/categories/{sample_category.sourced_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "weight": 0.75,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["weight"] == 0.75


def test_update_category_metadata(client, oauth_token, sample_category):
    """Test updating category metadata specifically."""
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
        f"/ims/oneroster/v1p2/categories/{sample_category.sourced_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "metadata": {"updated": "true", "version": "2"},
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "metadata" in data
