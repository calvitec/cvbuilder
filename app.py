from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import uuid
import json
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'allison-beauty-secret-2026'

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
        'badge': 'Best Seller',
        'stock': 45
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
        'badge': 'New',
        'stock': 60
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
        'badge': "Editor's Choice",
        'stock': 30
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
        'badge': '',
        'stock': 80
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
        'badge': '',
        'stock': 55
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
        'badge': 'Trending',
        'stock': 40
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
        'badge': '',
        'stock': 70
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
        'badge': '',
        'stock': 90
    },
    'niacinamide': {
        'id': 'niacinamide',
        'name': 'Niacinamide Serum',
        'price': 29.99,
        'image': '🌟',
        'category': 'Serums',
        'description': 'Brightening serum with 10% niacinamide to minimize pores and even skin tone.',
        'features': ['Niacinamide', 'Pore Minimizing', 'Brightening', 'Oil Control'],
        'rating': 4.7,
        'reviews': 203,
        'popular': True,
        'badge': 'Best Seller',
        'stock': 50
    },
    'peptide_cream': {
        'id': 'peptide_cream',
        'name': 'Peptide Firming Cream',
        'price': 38.99,
        'image': '🔬',
        'category': 'Moisturizers',
        'description': 'Advanced peptide cream that firms and lifts skin for a youthful appearance.',
        'features': ['Peptides', 'Firming', 'Anti-Wrinkle', 'Collagen Boost'],
        'rating': 4.8,
        'reviews': 167,
        'popular': False,
        'badge': 'New',
        'stock': 35
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
        'popular': True,
        'image': '🎁'
    },
    'glow_bundle': {
        'id': 'glow_bundle',
        'name': 'Glow Getter Bundle',
        'price': 69.99,
        'products': ['glow_serum', 'hydrating_cream', 'sunscreen_spf'],
        'savings': 28.98,
        'popular': True,
        'image': '✨'
    },
    'night_renewal': {
        'id': 'night_renewal',
        'name': 'Night Renewal Bundle',
        'price': 89.99,
        'products': ['cleansing_balm', 'retinol_night', 'eye_cream', 'hydrating_cream'],
        'savings': 41.97,
        'popular': False,
        'image': '🌙'
    },
    'complete_routine': {
        'id': 'complete_routine',
        'name': 'Complete Skincare Routine',
        'price': 129.99,
        'products': ['cleansing_balm', 'toner', 'glow_serum', 'hydrating_cream', 'sunscreen_spf', 'eye_cream'],
        'savings': 63.94,
        'popular': True,
        'image': '💎'
    }
}

# ============================================
# ROUTES
# ============================================

@app.route('/')
def index():
    """Allison Beauty Homepage"""
    # Get products by badge
    best_sellers = []
    new_arrivals = []
    trending = []
    
    for product in PRODUCTS.values():
        if product.get('badge') == 'Best Seller':
            best_sellers.append(product)
        elif product.get('badge') == 'New':
            new_arrivals.append(product)
        elif product.get('badge') == 'Trending':
            trending.append(product)
    
    # If no products in a category, add some defaults
    if not best_sellers:
        best_sellers = list(PRODUCTS.values())[:4]
    if not new_arrivals:
        new_arrivals = list(PRODUCTS.values())[2:6]
    if not trending:
        trending = list(PRODUCTS.values())[4:8]
    
    return render_template('shop.html', 
        products=PRODUCTS, 
        bundles=BUNDLES, 
        best_sellers=best_sellers,
        new_arrivals=new_arrivals,
        trending=trending,
        all_products=PRODUCTS
    )

@app.route('/product/<product_id>')
def product_detail(product_id):
    """Product detail page"""
    if product_id not in PRODUCTS:
        return redirect(url_for('index'))
    
    product = PRODUCTS[product_id]
    related = [p for p in PRODUCTS.values() if p['category'] == product['category'] and p['id'] != product_id][:4]
    
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
                'image': bundle['image'],
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
            return jsonify({'success': True, 'message': 'Added to bag!'})
        else:
            return jsonify({'success': False, 'message': 'Already in bag'})
    
    return jsonify({'success': False, 'message': 'Product not found'})

@app.route('/remove-from-cart/<item_id>', methods=['POST'])
def remove_from_cart(item_id):
    """Remove item from cart"""
    if 'cart' in session:
        if item_id in session['cart']:
            session['cart'].remove(item_id)
            session.modified = True
            return jsonify({'success': True, 'message': 'Removed from bag!'})
    return jsonify({'success': False, 'message': 'Item not in bag'})

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
            product = PRODUCTS[item_id]
            cart_data.append({
                'id': item_id, 
                'name': product['name'], 
                'price': product['price'], 
                'image': product['image']
            })
            total += product['price']
        elif item_id in BUNDLES:
            bundle = BUNDLES[item_id]
            cart_data.append({
                'id': item_id, 
                'name': bundle['name'], 
                'price': bundle['price'], 
                'image': bundle['image']
            })
            total += bundle['price']
    
    return render_template('checkout.html', cart_items=cart_data, total=total)

@app.route('/place-order', methods=['POST'])
def place_order():
    """Place order (simulated)"""
    cart_items = session.get('cart', [])
    if not cart_items:
        return jsonify({'success': False, 'message': 'Cart is empty'})
    
    order_id = f"AB-{uuid.uuid4().hex[:8].upper()}"
    
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
