from pydantic import BaseModel, HttpUrl
from typing import List, Optional

class User(BaseModel):
    id: str
    user_id: str
    user_name: str
    client_id: str
    email: str
    name: Optional[str] = ""
    pass_hash: str
    site_id: str
    created_at: time
    updated_at: time