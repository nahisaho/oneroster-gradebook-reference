"""Tests for database connection handling."""
import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import OperationalError

from src.config.database import get_db


def test_get_db_connection_error():
    """Test database connection error handling."""
    with patch("src.config.database.SessionLocal") as mock_session:
        # Mock session that raises error on commit
        mock_db = MagicMock()
        mock_db.commit.side_effect = OperationalError("Connection failed", None, None)
        mock_session.return_value = mock_db
        
        # Call get_db generator
        gen = get_db()
        db = next(gen)
        
        # Try to trigger error
        try:
            db.commit()
        except OperationalError:
            pass
        
        # Ensure finally block is executed
        try:
            next(gen)
        except StopIteration:
            pass
        
        # Verify close was called
        mock_db.close.assert_called_once()
