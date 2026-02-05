from uuid import UUID

def is_valid_uuid(id: str) -> bool:
    try:
        obj_value = UUID(id)
        return str(obj_value) == id.lower()
    except (TypeError, ValueError):
        return False