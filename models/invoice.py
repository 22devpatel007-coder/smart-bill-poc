from dataclasses import dataclass
from typing import List

@dataclass
class InvoiceItem:
    id: int
    invoice_id: int
    product_id: int
    product_name: str
    qty: float
    unit_price: float
    discount: float
    gst_rate: float
    gst_amt: float
    line_total: float

@dataclass
class Invoice:
    id: int
    invoice_number: str
    customer_id: int
    user_id: int
    subtotal: float
    discount_pct: float
    discount_amt: float
    cgst_amt: float
    sgst_amt: float
    total: float
    payment_mode: str
    payment_status: str
    notes: str
    created_at: str
    items: List[InvoiceItem]
