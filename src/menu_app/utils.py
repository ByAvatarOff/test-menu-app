"""
Utils
"""
from sqlalchemy import Row


async def model_object_2_dict(
        row: Row,
        additional_field: dict = None
) -> dict:
    """
    Convert model object or row object to dict
    """
    table_dict = {
        c.name: str(getattr(row, c.name))
        for c in row.__table__.columns
    }
    if not additional_field:
        return table_dict
    table_dict.update(additional_field)
    return table_dict
