import pytest
from utils.gst_calculator import calculate_line_item

def test_zero_gst():
    res = calculate_line_item(sell_price=100.0, qty=1.0, discount_pct=0.0, gst_rate=0.0)
    assert res['line_total'] == 100.00

def test_5_percent_gst():
    res = calculate_line_item(sell_price=100.0, qty=1.0, discount_pct=0.0, gst_rate=5.0)
    assert res['cgst_amt'] == 2.50
    assert res['sgst_amt'] == 2.50
    assert res['line_total'] == 105.00

def test_18_percent_gst():
    res = calculate_line_item(sell_price=100.0, qty=1.0, discount_pct=0.0, gst_rate=18.0)
    assert res['cgst_amt'] == 9.00
    assert res['sgst_amt'] == 9.00
    assert res['line_total'] == 118.00

def test_discount_before_gst():
    res = calculate_line_item(sell_price=100.0, qty=1.0, discount_pct=10.0, gst_rate=18.0)
    assert res['taxable_amount'] == 90.00
    assert res['cgst_amt'] == 8.10
    assert res['sgst_amt'] == 8.10
    assert res['line_total'] == 106.20

def test_quantity_multiplier():
    res = calculate_line_item(sell_price=50.0, qty=3.0, discount_pct=0.0, gst_rate=12.0)
    assert res['line_total'] == 168.00

def test_rounding():
    res = calculate_line_item(sell_price=33.33, qty=1.0, discount_pct=0.0, gst_rate=18.0)
    assert res['line_total'] == 39.33

def test_cgst_equals_sgst():
    res = calculate_line_item(sell_price=77.77, qty=3.0, discount_pct=15.0, gst_rate=12.0)
    assert res['cgst_amt'] == res['sgst_amt']
