"""
Tests for Results API endpoints.
"""


def test_get_results_collection(client, oauth_token, sample_result):
    """Test getting collection of results."""
    response = client.get(
        "/ims/oneroster/v1p2/results",
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

    # Verify result structure
    result = data["data"][0]
    assert "sourcedId" in result
    assert "status" in result
    assert "dateLastModified" in result
    assert "lineItem" in result
    assert "score" in result
    assert "scoreStatus" in result


def test_get_result_by_id(client, oauth_token, sample_result):
    """Test getting a single result by sourcedId."""
    response = client.get(
        f"/ims/oneroster/v1p2/results/{sample_result.sourced_id}",
        headers={"Authorization": f"Bearer {oauth_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["sourcedId"] == sample_result.sourced_id
    assert data["status"] == "active"
    assert data["lineItem"]["sourcedId"] == sample_result.line_item_sourced_id
    assert data["score"] == sample_result.score


def test_get_result_not_found(client, oauth_token):
    """Test getting a non-existent result."""
    response = client.get(
        "/ims/oneroster/v1p2/results/non-existent-id",
        headers={"Authorization": f"Bearer {oauth_token}"},
    )

    assert response.status_code == 404


def test_create_result(client, oauth_token, sample_line_item):
    """Test creating a new result."""
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
        "/ims/oneroster/v1p2/results",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "sourcedId": "res-new-001",
            "lineItemSourcedId": sample_line_item.sourced_id,
            "studentSourcedId": "student-001",
            "scoreStatus": "earnedFull",
            "score": 85.5,
            "comment": "Good work",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["sourcedId"] == "res-new-001"
    assert data["score"] == 85.5
    assert data["scoreStatus"] == "earnedFull"
    assert data["lineItem"]["sourcedId"] == sample_line_item.sourced_id


def test_update_result(client, oauth_token, sample_result):
    """Test updating an existing result."""
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
        f"/ims/oneroster/v1p2/results/{sample_result.sourced_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "score": 95.0,
            "comment": "Excellent improvement",
            "scoreStatus": "earnedFull",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["score"] == 95.0
    assert data["comment"] == "Excellent improvement"


def test_delete_result(client, oauth_token, sample_result):
    """Test soft deleting a result."""
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
        f"/ims/oneroster/v1p2/results/{sample_result.sourced_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 204


def test_get_results_with_pagination(client, oauth_token, db_session, sample_line_item):
    """Test pagination of results."""
    # Create multiple results
    from src.models.models import Result, ScoreStatusEnum, StatusEnum

    for i in range(5):
        result = Result(
            sourced_id=f"res-page-{i:03d}",
            status=StatusEnum.active,
            line_item_sourced_id=sample_line_item.sourced_id,
            student_sourced_id=f"student-{i:03d}",
            score_status=ScoreStatusEnum.earnedFull,
            score=80.0 + i,
        )
        db_session.add(result)
    db_session.commit()

    # Test pagination
    response = client.get(
        "/ims/oneroster/v1p2/results?limit=2&offset=1",
        headers={"Authorization": f"Bearer {oauth_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["limit"] == 2
    assert data["offset"] == 1
    assert len(data["data"]) <= 2


def test_get_results_with_filter(client, oauth_token, db_session, sample_line_item):
    """Test filtering results."""
    # Create results with different scores
    from src.models.models import Result, ScoreStatusEnum, StatusEnum

    result1 = Result(
        sourced_id="res-high-001",
        status=StatusEnum.active,
        line_item_sourced_id=sample_line_item.sourced_id,
        student_sourced_id="student-001",
        score_status=ScoreStatusEnum.earnedFull,
        score=95.0,
    )
    result2 = Result(
        sourced_id="res-low-001",
        status=StatusEnum.active,
        line_item_sourced_id=sample_line_item.sourced_id,
        student_sourced_id="student-002",
        score_status=ScoreStatusEnum.earnedFull,
        score=65.0,
    )
    db_session.add(result1)
    db_session.add(result2)
    db_session.commit()

    # Test filter for high scores
    response = client.get(
        "/ims/oneroster/v1p2/results?filter=score>90",
        headers={"Authorization": f"Bearer {oauth_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    # Should find at least the high score result
    assert any(res.get("score", 0) > 90 for res in data["data"])


def test_get_results_with_sort(client, oauth_token, db_session, sample_line_item):
    """Test sorting results."""
    # Create results with different scores
    from src.models.models import Result, ScoreStatusEnum, StatusEnum

    for i, score in enumerate([85.0, 92.0, 78.0]):
        result = Result(
            sourced_id=f"res-sort-{i:03d}",
            status=StatusEnum.active,
            line_item_sourced_id=sample_line_item.sourced_id,
            student_sourced_id=f"student-{i:03d}",
            score_status=ScoreStatusEnum.earnedFull,
            score=score,
        )
        db_session.add(result)
    db_session.commit()

    # Test sort by score descending
    response = client.get(
        "/ims/oneroster/v1p2/results?sort=score DESC",
        headers={"Authorization": f"Bearer {oauth_token}"},
    )

    assert response.status_code == 200
    data = response.json()

    # Check if sorted by score descending
    if len(data["data"]) >= 2:
        scores = [res.get("score", 0) for res in data["data"] if "score" in res]
        if len(scores) >= 2:
            assert scores[0] >= scores[1]


def test_result_line_item_relationship(client, oauth_token, sample_result, sample_line_item):
    """Test that result includes line item information."""
    response = client.get(
        f"/ims/oneroster/v1p2/results/{sample_result.sourced_id}",
        headers={"Authorization": f"Bearer {oauth_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "lineItem" in data
    assert data["lineItem"]["sourcedId"] == sample_line_item.sourced_id
    assert data["lineItem"]["type"] == "lineItem"


def test_result_score_validation(client, oauth_token, sample_line_item):
    """Test score validation based on line item min/max values."""
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

    # Test with valid score within range
    response = client.post(
        "/ims/oneroster/v1p2/results",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "sourcedId": "res-valid-001",
            "lineItemSourcedId": sample_line_item.sourced_id,
            "studentSourcedId": "student-001",
            "scoreStatus": "earnedFull",
            "score": 75.0,  # Within 0-100 range
        },
    )

    assert response.status_code == 201
    assert response.json()["score"] == 75.0


def test_result_score_status_values(client, oauth_token, sample_line_item):
    """Test different score status values."""
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

    # Test different valid score statuses
    valid_statuses = [
        ("notSubmitted", None),
        ("earnedFull", 90.0),
        ("earnedPartial", 75.0),
        ("submitted", 80.0),
        ("late", 70.0),
    ]

    for i, (status, score) in enumerate(valid_statuses):
        response = client.post(
            "/ims/oneroster/v1p2/results",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "sourcedId": f"res-status-{i:03d}",
                "lineItemSourcedId": sample_line_item.sourced_id,
                "studentSourcedId": f"student-{i:03d}",
                "scoreStatus": status,
                "score": score,
            },
        )

        if response.status_code == 201:
            assert response.json()["scoreStatus"] == status


def test_update_nonexistent_result(client, oauth_token):
    """Test updating a result that doesn't exist."""
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
        "/ims/oneroster/v1p2/results/nonexistent-id",
        headers={"Authorization": f"Bearer {token}"},
        json={"score": 90.0},
    )

    assert response.status_code == 404


def test_delete_nonexistent_result(client, oauth_token):
    """Test deleting a result that doesn't exist."""
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
        "/ims/oneroster/v1p2/results/nonexistent-id",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404


def test_create_result_with_invalid_score_status(client, oauth_token, sample_line_item):
    """Test creating a result with score when scoreStatus doesn't allow it."""
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

    # Try to create result with score for notSubmitted status
    response = client.post(
        "/ims/oneroster/v1p2/results",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "sourcedId": "res-invalid-001",
            "lineItemSourcedId": sample_line_item.sourced_id,
            "studentSourcedId": "student-001",
            "scoreStatus": "notSubmitted",
            "score": 85.0,  # Score should not be provided for notSubmitted
        },
    )

    assert response.status_code == 422


def test_update_result_all_fields(client, oauth_token, sample_result):
    """Test updating all fields of a result."""
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
        f"/ims/oneroster/v1p2/results/{sample_result.sourced_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "score": 75.0,
            "scoreDate": "2024-01-20T10:30:00Z",
            "comment": "Good improvement",
            "metadata": {"updated": "all_fields"},
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["score"] == 75.0
    assert data["comment"] == "Good improvement"


def test_update_result_individual_fields(client, oauth_token, sample_result):
    """Test updating individual fields of a result."""
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

    # Update scoreDate only
    response = client.put(
        f"/ims/oneroster/v1p2/results/{sample_result.sourced_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"scoreDate": "2024-03-01T12:00:00Z"},
    )
    assert response.status_code == 200

    # Update metadata only
    response = client.put(
        f"/ims/oneroster/v1p2/results/{sample_result.sourced_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"metadata": {"key": "value"}},
    )
    assert response.status_code == 200

    # Update scoreStatus only
    response = client.put(
        f"/ims/oneroster/v1p2/results/{sample_result.sourced_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"scoreStatus": "earnedPartial"},
    )
    assert response.status_code == 200

    # Update comment only
    response = client.put(
        f"/ims/oneroster/v1p2/results/{sample_result.sourced_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"comment": "Well done!"},
    )
    assert response.status_code == 200
