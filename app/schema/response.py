from typing import Generic, Optional, TypeVar
from pydantic import BaseModel
T = TypeVar('T')
class ApiResponse(BaseModel, Generic[T]):
    model_config = {"exclude_none": True}
    success: bool
    current_page:int = None
    total_page:int = None
    #status_code: int = 200
    message:str
    data: Optional[T] = None,
    error: Optional[T] = None