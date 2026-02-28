from dataclasses import dataclass

@dataclass
class User:
    id: int
    username: str
    full_name: str
    role: str
    is_active: bool
