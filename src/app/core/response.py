from typing import Any

def response_builder(
    status_code: int, 
    status: str, 
    message: str, 
    data: dict[str, Any] | list[dict[str, Any]] | None = None
) -> dict[str, Any]:
    
    response = {
        "status_code": status_code,
        "status": status,
        "message": message
    }
    if data:
        response["data"] = data
    
    return response
    