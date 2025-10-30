"""Tests for query parser utility."""
import pytest

from src.models.models import Category
from src.utils.query_parser import parse_filter, parse_sort


def test_parse_filter_with_equals(db_session):
    """Test parsing filter with equals operator."""
    filter_str = "title='Test'"
    conditions = parse_filter(filter_str, Category)

    assert len(conditions) == 1
    # Verify condition can be used in query
    query = db_session.query(Category).filter(*conditions)
    assert query is not None


def test_parse_filter_with_not_equals(db_session):
    """Test parsing filter with not equals operator."""
    filter_str = "title!='Test'"
    conditions = parse_filter(filter_str, Category)
    
    assert len(conditions) == 1


def test_parse_filter_with_less_than(db_session):
    """Test parsing filter with less than operator."""
    filter_str = "weight<10"
    conditions = parse_filter(filter_str, Category)
    
    assert len(conditions) == 1


def test_parse_filter_with_less_than_equals(db_session):
    """Test parsing filter with less than or equals operator."""
    filter_str = "weight<=10"
    conditions = parse_filter(filter_str, Category)
    
    assert len(conditions) == 1


def test_parse_filter_with_greater_than(db_session):
    """Test parsing filter with greater than operator."""
    filter_str = "weight>5"
    conditions = parse_filter(filter_str, Category)
    
    assert len(conditions) == 1


def test_parse_filter_with_greater_than_equals(db_session):
    """Test parsing filter with greater than or equals operator."""
    filter_str = "weight>=5"
    conditions = parse_filter(filter_str, Category)
    
    assert len(conditions) == 1


def test_parse_filter_with_contains(db_session):
    """Test parsing filter with contains operator."""
    filter_str = "title~'Test'"
    conditions = parse_filter(filter_str, Category)
    
    assert len(conditions) == 1


def test_parse_filter_with_multiple_conditions(db_session):
    """Test parsing multiple filter conditions."""
    filter_str = "title='Test' AND weight>5"
    conditions = parse_filter(filter_str, Category)
    
    assert len(conditions) == 2


def test_parse_filter_with_invalid_field(db_session):
    """Test parsing filter with non-existent field."""
    filter_str = "invalidField='Test'"
    conditions = parse_filter(filter_str, Category)
    
    # Should skip invalid fields
    assert len(conditions) == 0


def test_parse_filter_empty_string(db_session):
    """Test parsing empty filter string."""
    conditions = parse_filter("", Category)
    
    assert len(conditions) == 0


def test_parse_sort_ascending(db_session):
    """Test parsing sort with ascending order."""
    sort_str = "title"
    sort_columns = parse_sort(sort_str, Category)
    
    assert len(sort_columns) == 1


def test_parse_sort_descending(db_session):
    """Test parsing sort with descending order."""
    sort_str = "weight DESC"
    sort_columns = parse_sort(sort_str, Category)

    assert len(sort_columns) == 1


def test_parse_sort_multiple_columns(db_session):
    """Test parsing sort with multiple columns."""
    sort_str = "title ASC,weight DESC"
    sort_columns = parse_sort(sort_str, Category)

    assert len(sort_columns) == 2
def test_parse_sort_with_invalid_field(db_session):
    """Test parsing sort with non-existent field."""
    sort_str = "invalidField"
    sort_columns = parse_sort(sort_str, Category)
    
    # Should skip invalid fields
    assert len(sort_columns) == 0


def test_parse_sort_empty_string(db_session):
    """Test parsing empty sort string."""
    sort_columns = parse_sort("", Category)
    
    assert len(sort_columns) == 0


def test_parse_filter_with_float_value(db_session):
    """Test parsing filter with float value."""
    filter_str = "weight=10.5"
    conditions = parse_filter(filter_str, Category)
    
    assert len(conditions) == 1


def test_parse_filter_with_integer_value(db_session):
    """Test parsing filter with integer value."""
    filter_str = "weight=10"
    conditions = parse_filter(filter_str, Category)
    
    assert len(conditions) == 1
