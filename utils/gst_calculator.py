def calculate_line_item(sell_price: float, qty: float, discount_pct: float, gst_rate: float) -> dict:
    """
    Calculates the detailed amounts for a single line item.
    Discount is applied BEFORE GST calculation.
    All values rounded to 2 decimal places.
    """
    base_amount = round(sell_price * qty, 2)
    discount_amt = round(base_amount * (discount_pct / 100.0), 2)
    taxable_amount = round(base_amount - discount_amt, 2)
    
    cgst_rate = round(gst_rate / 2.0, 2)
    sgst_rate = round(gst_rate / 2.0, 2)
    
    cgst_amt = round(taxable_amount * (cgst_rate / 100.0), 2)
    sgst_amt = round(taxable_amount * (sgst_rate / 100.0), 2)
    gst_amt = round(cgst_amt + sgst_amt, 2)
    
    line_total = round(taxable_amount + gst_amt, 2)
    
    return {
        "base_amount": base_amount,
        "discount_amt": discount_amt,
        "taxable_amount": taxable_amount,
        "cgst_rate": cgst_rate,
        "sgst_rate": sgst_rate,
        "cgst_amt": cgst_amt,
        "sgst_amt": sgst_amt,
        "gst_amt": gst_amt,
        "line_total": line_total
    }

if __name__ == "__main__":
    # Test
    res = calculate_line_item(sell_price=100, qty=2, discount_pct=10, gst_rate=18)
    print("Test calculation:", res)
