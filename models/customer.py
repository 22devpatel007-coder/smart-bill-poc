from dataclasses import dataclass

@dataclass
class Customer:
    id: int
    name: str
    phone: str
    email: str
    address: str
    outstanding: float
    created_at: str
