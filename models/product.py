from dataclasses import dataclass

@dataclass
class Product:
    id: int
    name: str
    sku: str
    barcode: str
    category_id: int
    gst_rate_id: int
    unit: str
    cost_price: float
    sell_price: float
    stock: float
    low_stock_qty: float
    expiry_date: str
    is_active: bool
