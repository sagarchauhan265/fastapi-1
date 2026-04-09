from typing import List, Optional
from pydantic import BaseModel


class BulkRowError(BaseModel):
    row: int
    field: Optional[str] = None
    message: str


class BulkUploadResult(BaseModel):
    success_count: int
    failed_count: int
    errors: List[BulkRowError] = []
