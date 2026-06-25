from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import uuid
import json
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'beauty-shop-secret-2026'

# ============================================
# BEAUTY PRODUCTS CATALOG
# ============================================
PRODUCTS = {
    'glow_serum': {
        'id': 'glow_serum',
        'name': 'Glow Repair Serum',
        'price': 34.99,
        'image': '✨',
        'category': 'Serums',
        'description': 'Powerful vitamin C serum for radiant, glowing skin. Reduces dark spots and fine lines.',
        'features': ['Vitamin C', 'Hydrating', 'Brightening', 'Cruelty-Free'],
        'rating': 4.8,
        'reviews': 234,
        'popular': True,
        'badge': 'Best Seller'
    },
    'hydrating_cream': {
        'id': 'hydrating_cream',
        'name': 'Hydrating Moisture Cream',
        'price': 28.99,
        'image': '💧',
        'category': 'Moisturizers',
        'description': 'Deep hydration cream with hyaluronic acid for plump, dewy skin.',
        'features': ['Hyaluronic Acid', '24hr Hydration', 'Non-comedogenic'],
        'rating': 4.6,
        'reviews': 189,
        'popular': False,
        'badge': 'New'
    },
    'retinol_night': {
        'id': 'retinol_night',
        'name': 'Retinol Night Treatment',
        'price': 42.99,
        'image': '🌙',
        'category': 'Treatments',
        'description': 'Advanced retinol formula for overnight skin renewal and anti-aging benefits.',
        'features': ['Retinol', 'Anti-Aging', 'Overnight Repair', 'Dermatologist Tested'],
        'rating': 4.9,
        'reviews': 312,
        'popular': True,
        'badge': "Editor's Choice"
    },
    'sunscreen_spf': {
        'id': 'sunscreen_spf',
        'name': 'SPF 50 Sunscreen',
        'price': 24.99,
        'image': '☀️',
        'category': 'Sun Care',
        'description': 'Lightweight, non-greasy sunscreen with broad-spectrum SPF 50 protection.',
        'features': ['SPF 50', 'Broad Spectrum', 'Non-greasy', 'Water Resistant'],
        'rating': 4.5,
        'reviews': 156,
        'popular': False,
        'badge': ''
    },
    'face_mask': {
        'id': 'face_mask',
        'name': 'Detox Clay Mask',
        'price': 19.99,
        'image': '🧖',
        'category': 'Masks',
        'description': 'Purifying clay mask that draws out impurities and leaves skin refreshed.',
        'features': ['Kaolin Clay', 'Detoxifying', 'Pore Minimizing', 'Natural'],
        'rating': 4.4,
        'reviews': 98,
        'popular': False,
        'badge': ''
    },
    'eye_cream': {
        'id': 'eye_cream',
        'name': 'Brightening Eye Cream',
        'price': 32.99,
        'image': '👁️',
        'category': 'Eye Care',
        'description': 'Targets dark circles, puffiness, and fine lines for a refreshed look.',
        'features': ['Caffeine', 'Brightening', 'Anti-Puffiness', 'Fine Line Reduction'],
        'rating': 4.7,
        'reviews': 145,
        'popular': True,
        'badge': 'Trending'
    },
    'cleansing_balm': {
        'id': 'cleansing_balm',
        'name': 'Cleansing Balm',
        'price': 22.99,
        'image': '🧴',
        'category': 'Cleansers',
        'description': 'Gentle cleansing balm that melts away makeup and impurities.',
        'features': ['Oil-Based', 'Makeup Remover', 'Hydrating', 'Sensitive Skin'],
        'rating': 4.3,
        'reviews': 78,
        'popular': False,
        'badge': ''
    },
    'toner': {
        'id': 'toner',
        'name': 'Hydrating Facial Toner',
        'price': 18.99,
        'image': '💦',
        'category': 'Toners',
        'description': 'Alcohol-free toner that balances and hydrates skin after cleansing.',
        'features': ['Alcohol-Free', 'Balancing', 'Hydrating', 'Rose Water'],
        'rating': 4.2,
        'reviews': 67,
        'popular': False,
        'badge': ''
    }
}

# ============================================
# BUNDLES
# ============================================
BUNDLES = {
    'skincare_starter': {
        'id': 'skincare_starter',
        'name': 'Skincare Starter Bundle',
        'price': 49.99,
        'products': ['cleansing_balm', 'toner', 'hydrating_cream'],
        'savings': 20.98,
        'popular': True
    },
    'glow_bundle': {
        'id': 'glow_bundle',
        'name': 'Glow Getter Bundle',
        'price': 69.99,
        'products': ['glow_serum', 'hydrating_cream', 'sunscreen_spf'],
        'savings': 28.98,
        'popular': True
    },
    'night_renewal': {
        'id': 'night_renewal',
        'name': 'Night Renewal Bundle',
        'price': 89.99,
        'products': ['cleansing_balm', 'retinol_night', 'eye_cream', 'hydrating_cream'],
        'savings': 41.97,
        'popular': False
    }
}

# ============================================
# ROUTES
# ============================================

@app.route('/')
def index():
    """Beauty Shop Homepage"""
    # Get top products
    featured = [p for p in PRODUCTS.values() if p.get('popular', False)][:4]
    return render_template('shop.html', products=PRODUCTS, bundles=BUNDLES, featured=featured)

@app.route('/product/<product_id>')
def product_detail(product_id):
    """Product detail page"""
    if product_id not in PRODUCTS:
        return redirect(url_for('index'))
    
    # Get related products (same category)
    product = PRODUCTS[product_id]
    related = [p for p in PRODUCTS.values() if p['category'] == product['category'] and p['id'] != product_id][:3]
    
    return render_template('product.html', product=product, related=related)

@app.route('/cart')
def cart():
    """Shopping cart page"""
    cart_items = session.get('cart', [])
    cart_data = []
    total = 0
    
    for item_id in cart_items:
        if item_id in PRODUCTS:
            product = PRODUCTS[item_id]
            cart_data.append({
                'id': item_id,
                'name': product['name'],
                'price': product['price'],
                'image': product['image'],
                'type': 'product'
            })
            total += product['price']
        elif item_id in BUNDLES:
            bundle = BUNDLES[item_id]
            cart_data.append({
                'id': item_id,
                'name': bundle['name'],
                'price': bundle['price'],
                'image': '🎁',
                'type': 'bundle',
                'products': bundle['products']
            })
            total += bundle['price']
    
    return render_template('cart.html', cart_items=cart_data, total=total)

@app.route('/add-to-cart/<item_id>', methods=['POST'])
def add_to_cart(item_id):
    """Add item to cart"""
    if 'cart' not in session:
        session['cart'] = []
    
    if item_id in PRODUCTS or item_id in BUNDLES:
        if item_id not in session['cart']:
            session['cart'].append(item_id)
            session.modified = True
            return jsonify({'success': True, 'message': 'Added to cart!'})
        else:
            return jsonify({'success': False, 'message': 'Already in cart'})
    
    return jsonify({'success': False, 'message': 'Product not found'})

@app.route('/remove-from-cart/<item_id>', methods=['POST'])
def remove_from_cart(item_id):
    """Remove item from cart"""
    if 'cart' in session:
        if item_id in session['cart']:
            session['cart'].remove(item_id)
            session.modified = True
            return jsonify({'success': True, 'message': 'Removed from cart!'})
    return jsonify({'success': False, 'message': 'Item not in cart'})

@app.route('/checkout')
def checkout():
    """Checkout page"""
    cart_items = session.get('cart', [])
    if not cart_items:
        return redirect(url_for('index'))
    
    cart_data = []
    total = 0
    for item_id in cart_items:
        if item_id in PRODUCTS:
            cart_data.append({'id': item_id, 'name': PRODUCTS[item_id]['name'], 'price': PRODUCTS[item_id]['price'], 'image': PRODUCTS[item_id]['image']})
            total += PRODUCTS[item_id]['price']
        elif item_id in BUNDLES:
            cart_data.append({'id': item_id, 'name': BUNDLES[item_id]['name'], 'price': BUNDLES[item_id]['price'], 'image': '🎁'})
            total += BUNDLES[item_id]['price']
    
    return render_template('checkout.html', cart_items=cart_data, total=total)

@app.route('/place-order', methods=['POST'])
def place_order():
    """Place order (simulated)"""
    cart_items = session.get('cart', [])
    if not cart_items:
        return jsonify({'success': False, 'message': 'Cart is empty'})
    
    order_id = f"BEAUTY-{uuid.uuid4().hex[:8].upper()}"
    
    session['cart'] = []
    session.modified = True
    
    return jsonify({
        'success': True,
        'order_id': order_id,
        'message': 'Order placed successfully!'
    })

@app.route('/order-confirmation/<order_id>')
def order_confirmation(order_id):
    """Order confirmation page"""
    return render_template('confirmation.html', order_id=order_id)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
