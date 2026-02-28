from utils.gst_calculator import calculate_line_item

class BillingCart:
    """
    Manages the shopping cart for a POS terminal.
    """
    def __init__(self):
        self.items = {} # Maps product_id to cart item dict
        self.bill_discount_pct = 0.0
        
    def add_item(self, product_dict: dict, qty: float = 1.0):
        """Adds or increments an item in the cart. 
           product_dict should have: product_id, name, unit_price, discount_pct, gst_rate
        """
        product_id = product_dict['product_id']
        if product_id in self.items:
            self.items[product_id]['qty'] += qty
        else:
            self.items[product_id] = {
                'product_id': product_id,
                'name': product_dict.get('name', 'Unknown'),
                'qty': qty,
                'unit_price': product_dict.get('unit_price', 0.0),
                'discount_pct': product_dict.get('discount_pct', 0.0),
                'gst_rate': product_dict.get('gst_rate', 0.0)
            }
            
    def remove_item(self, product_id):
        """Removes an item from the cart completely."""
        if product_id in self.items:
            del self.items[product_id]
            
    def update_qty(self, product_id, qty: float):
        """Updates quantity, removes if qty less than or equal to 0."""
        if qty <= 0:
            self.remove_item(product_id)
        elif product_id in self.items:
            self.items[product_id]['qty'] = qty
            
    def set_bill_discount(self, pct: float):
        """Applies % discount to entire bill."""
        self.bill_discount_pct = pct
        
    def calculate_totals(self) -> dict:
        """
        Calculates all line items and aggregates totals for the bill.
        Returns {items, subtotal, discount_amt, cgst_total, sgst_total, grand_total}
        """
        items_details = []
        subtotal = 0.0
        total_discount_amt = 0.0
        cgst_total = 0.0
        sgst_total = 0.0
        grand_total = 0.0
        
        for pid, item in self.items.items():
            # Combine item-level discount and bill-level discount for line calculation
            eff_discount = item['discount_pct'] + self.bill_discount_pct
            
            calc = calculate_line_item(
                sell_price=item['unit_price'],
                qty=item['qty'],
                discount_pct=eff_discount,
                gst_rate=item['gst_rate']
            )
            
            detail = item.copy()
            detail.update(calc)
            items_details.append(detail)
            
            subtotal += calc['base_amount']
            total_discount_amt += calc['discount_amt']
            cgst_total += calc['cgst_amt']
            sgst_total += calc['sgst_amt']
            grand_total += calc['line_total']
            
        return {
            "items": items_details,
            "subtotal": round(subtotal, 2),
            "discount_amt": round(total_discount_amt, 2),
            "cgst_total": round(cgst_total, 2),
            "sgst_total": round(sgst_total, 2),
            "grand_total": round(grand_total, 2)
        }
        
    def clear(self):
        """Empties cart."""
        self.items.clear()
        self.bill_discount_pct = 0.0
