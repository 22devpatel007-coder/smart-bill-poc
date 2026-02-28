import pytest
from services.billing_service import BillingCart

def test_add_item():
    cart = BillingCart()
    cart.add_item({'product_id': 1, 'name': 'Item A', 'unit_price': 100.0, 'gst_rate': 0.0}, 1.0)
    assert len(cart.items) == 1
    assert cart.items[1]['qty'] == 1.0

def test_add_same_item_twice():
    cart = BillingCart()
    prod = {'product_id': 1, 'name': 'Item A', 'unit_price': 100.0, 'gst_rate': 0.0}
    cart.add_item(prod, 1.0)
    cart.add_item(prod, 2.0)
    assert len(cart.items) == 1
    assert cart.items[1]['qty'] == 3.0

def test_remove_item():
    cart = BillingCart()
    cart.add_item({'product_id': 1, 'name': 'Item A', 'unit_price': 100.0, 'gst_rate': 0.0}, 1.0)
    cart.remove_item(1)
    assert len(cart.items) == 0

def test_update_qty_to_zero_removes():
    cart = BillingCart()
    cart.add_item({'product_id': 1, 'name': 'Item A', 'unit_price': 100.0, 'gst_rate': 0.0}, 1.0)
    cart.update_qty(1, 0.0)
    assert len(cart.items) == 0

def test_calculate_totals():
    cart = BillingCart()
    cart.add_item({'product_id': 1, 'name': 'Item A', 'unit_price': 100.0, 'gst_rate': 0.0}, 1.0)
    cart.add_item({'product_id': 2, 'name': 'Item B', 'unit_price': 200.0, 'gst_rate': 0.0}, 2.0) # total 400
    totals = cart.calculate_totals()
    assert totals['grand_total'] == 500.00

def test_bill_discount():
    cart = BillingCart()
    cart.add_item({'product_id': 1, 'name': 'Item A', 'unit_price': 100.0, 'gst_rate': 0.0}, 1.0)
    cart.set_bill_discount(10.0)
    totals = cart.calculate_totals()
    assert totals['grand_total'] == 90.00

def test_clear_cart():
    cart = BillingCart()
    cart.add_item({'product_id': 1, 'name': 'Item A', 'unit_price': 100.0, 'gst_rate': 0.0}, 1.0)
    cart.clear()
    assert len(cart.items) == 0
