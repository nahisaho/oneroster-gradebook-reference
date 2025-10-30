"""
OneRoster Query Parser
Parses OneRoster filter and sort expressions into SQLAlchemy queries.
"""

import re
from typing import Any, List

from sqlalchemy import asc, desc
from sqlalchemy.orm import DeclarativeMeta


def parse_filter(filter_expr: str, model: DeclarativeMeta) -> List[Any]:
    """
    Parse OneRoster filter expression into SQLAlchemy filter conditions.

    Supports operators: =, !=, <, <=, >, >=, ~
    Examples:
        - title='Math'
        - weight>0.5
        - status='active'
        - title~'Math'  (contains)

    Args:
        filter_expr: OneRoster filter expression
        model: SQLAlchemy model class

    Returns:
        List of SQLAlchemy filter conditions
    """
    conditions = []

    # Split by AND (simple implementation, doesn't handle OR yet)
    filters = filter_expr.split(" AND ")

    for f in filters:
        f = f.strip()

        # Parse filter expression
        # Operators: =, !=, <, <=, >, >=, ~
        match = re.match(r"(\w+)\s*(=|!=|<|<=|>|>=|~)\s*'([^']*)'", f)
        if not match:
            # Try without quotes for numbers
            match = re.match(r"(\w+)\s*(=|!=|<|<=|>|>=)\s*(\d+(?:\.\d+)?)", f)

        if match:
            field_name, operator, value = match.groups()

            # Convert camelCase to snake_case
            field_name = camel_to_snake(field_name)

            # Get model attribute
            if not hasattr(model, field_name):
                continue

            attr = getattr(model, field_name)

            # Convert value to appropriate type
            if value.replace(".", "", 1).isdigit():
                value = float(value) if "." in value else int(value)

            # Apply operator
            if operator == "=":
                conditions.append(attr == value)
            elif operator == "!=":
                conditions.append(attr != value)
            elif operator == "<":
                conditions.append(attr < value)
            elif operator == "<=":
                conditions.append(attr <= value)
            elif operator == ">":
                conditions.append(attr > value)
            elif operator == ">=":
                conditions.append(attr >= value)
            elif operator == "~":
                # Contains (case-insensitive)
                conditions.append(attr.ilike(f"%{value}%"))

    return conditions


def parse_sort(sort_expr: str, model: DeclarativeMeta) -> List[Any]:
    """
    Parse OneRoster sort expression into SQLAlchemy order_by clauses.

    Format: field1,field2 or field1 ASC,field2 DESC
    Examples:
        - title
        - title,weight
        - title ASC,weight DESC

    Args:
        sort_expr: OneRoster sort expression
        model: SQLAlchemy model class

    Returns:
        List of SQLAlchemy order_by clauses
    """
    order_by_clauses = []

    # Split by comma
    sorts = sort_expr.split(",")

    for s in sorts:
        s = s.strip()

        # Check for ASC/DESC
        if " " in s:
            field_name, direction = s.rsplit(" ", 1)
            direction = direction.upper()
        else:
            field_name = s
            direction = "ASC"

        # Convert camelCase to snake_case
        field_name = camel_to_snake(field_name)

        # Get model attribute
        if not hasattr(model, field_name):
            continue

        attr = getattr(model, field_name)

        # Apply direction
        if direction == "DESC":
            order_by_clauses.append(desc(attr))
        else:
            order_by_clauses.append(asc(attr))

    return order_by_clauses


def camel_to_snake(name: str) -> str:
    """
    Convert camelCase to snake_case.

    Examples:
        sourcedId -> sourced_id
        lineItemSourcedId -> line_item_sourced_id
    """
    # Insert underscore before uppercase letters and convert to lowercase
    name = re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()
    return name
