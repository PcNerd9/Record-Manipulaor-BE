from typing import Any


class RecordRepository:
    from fastapi import HTTPException

    def validate_record_payload(
        self,
        payload: dict[str, Any],
        dataset_schema: dict[str, Any],
        allow_partial: bool = False  # for updates
    ) -> tuple[bool, str | None]:
        
        payload_keys = set(payload.keys())
        schema_keys = set(dataset_schema.keys())

        # -------- Missing fields -------- #
        if not allow_partial:
            missing = schema_keys - payload_keys
            if missing:
                return False, f"Missing required fields: {list(missing)}"

        # -------- Extra fields -------- #
        extra = payload_keys - schema_keys
        if extra:
            return False, f"Unknown fields: {list(extra)}"
        
        return True, None



record_repository = RecordRepository()