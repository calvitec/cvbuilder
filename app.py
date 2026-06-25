from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import uuid
import json
from datetime import datetime
from cv_generator import create_cv_from_dict

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cv-shop-secret-key-2026'

# ============================================
# PRODUCTS CATALOG
# ============================================
PRODUCTS = {
    'classic': {
        'id': 'classic',
        'name': 'Classic Professional',
        'price': 29.99,
        'image': '📄',
        'description': 'Traditional two-column CV with sidebar. Perfect for corporate roles.',
        'features': ['ATS-Friendly', '2 Pages', 'Professional Design'],
        'popular': True
    },
    'modern': {
        'id': 'modern',
        'name': 'Modern Creative',
        'price': 34.99,
        'image': '🎨',
        'description': 'Contemporary design with timeline layout. Stand out from the crowd.',
        'features': ['Modern Layout', 'Timeline Experience', 'Colorful Design'],
        'popular': False
    },
    'elegant': {
        'id': 'elegant',
        'name': 'Elegant Executive',
        'price': 39.99,
        'image': '✨',
        'description': 'Sophisticated design with gold accents. Make a lasting impression.',
        'features': ['Premium Design', 'Gold Accents', 'Executive Style'],
        'popular': True
    },
    'professional': {
        'id': 'professional',
        'name': 'Corporate Pro',
        'price': 32.99,
        'image': '💼',
        'description': 'Clean corporate design for senior roles. Trusted by executives.',
        'features': ['Corporate Style', 'Structured Layout', 'Executive Ready'],
        'popular': False
    }
}

# ============================================
# BUNDLES
# ============================================
BUNDLES = {
    'starter': {
        'id': 'starter',
        'name': 'Starter Bundle',
        'price': 49.99,
        'products': ['classic', 'modern'],
        'savings': 14.99,
        'popular': True
    },
    'professional': {
        'id': 'professional',
        'name': 'Professional Bundle',
        'price': 79.99,
        'products': ['classic', 'modern', 'elegant'],
        'savings': 29.98,
        'popular': False
    },
    'premium': {
        'id': 'premium',
        'name': 'Premium Bundle',
        'price': 99.99,
        'products': ['classic', 'modern', 'elegant', 'professional'],
        'savings': 49.97,
        'popular': True
    }
}

# ============================================
# CV LAYOUTS (for the builder)
# ============================================
LAYOUTS = [
    {'id': 'classic', 'name': 'Classic', 'icon': 'fa-solid fa-crown', 'color': 'from-blue-500 to-indigo-600', 'desc': 'Traditional two-column with sidebar'},
    {'id': 'modern', 'name': 'Modern', 'icon': 'fa-solid fa-bolt', 'color': 'from-purple-500 to-pink-500', 'desc': 'Top header with timeline experience'},
    {'id': 'elegant', 'name': 'Elegant', 'icon': 'fa-solid fa-gem', 'color': 'from-amber-500 to-orange-500', 'desc': 'Centered with gold accents'},
    {'id': 'professional', 'name': 'Professional', 'icon': 'fa-solid fa-briefcase', 'color': 'from-emerald-500 to-teal-500', 'desc': 'Left sidebar corporate style'}
]

# ============================================
# ROUTES
# ============================================

@app.route('/')
def index():
    """Shop Homepage"""
    return render_template('shop.html', products=PRODUCTS, bundles=BUNDLES)

@app.route('/builder')
def builder():
    """CV Builder Page"""
    return render_template('index.html', layouts=LAYOUTS)

@app.route('/product/<product_id>')
def product_detail(product_id):
    """Product detail page"""
    if product_id not in PRODUCTS:
        return redirect(url_for('index'))
    return render_template('product.html', product=PRODUCTS[product_id])

@app.route('/cart')
def cart():
    """Shopping cart page"""
    cart_items = session.get('cart', [])
    total = 0
    for item in cart_items:
        if item in PRODUCTS:
            total += PRODUCTS[item]['price']
        elif item in BUNDLES:
            total += BUNDLES[item]['price']
    return render_template('cart.html', cart_items=cart_items, products=PRODUCTS, bundles=BUNDLES, total=total)

@app.route('/add-to-cart/<product_id>', methods=['POST'])
def add_to_cart(product_id):
    """Add item to cart"""
    if 'cart' not in session:
        session['cart'] = []
    
    if product_id in PRODUCTS or product_id in BUNDLES:
        if product_id not in session['cart']:
            session['cart'].append(product_id)
            session.modified = True
            return jsonify({'success': True, 'message': f'Added to cart!'})
    
    return jsonify({'success': False, 'message': 'Product not found'})

@app.route('/remove-from-cart/<product_id>', methods=['POST'])
def remove_from_cart(product_id):
    """Remove item from cart"""
    if 'cart' in session:
        if product_id in session['cart']:
            session['cart'].remove(product_id)
            session.modified = True
            return jsonify({'success': True, 'message': 'Removed from cart!'})
    return jsonify({'success': False, 'message': 'Item not in cart'})

@app.route('/checkout')
def checkout():
    """Checkout page"""
    cart_items = session.get('cart', [])
    if not cart_items:
        return redirect(url_for('index'))
    
    total = 0
    for item in cart_items:
        if item in PRODUCTS:
            total += PRODUCTS[item]['price']
        elif item in BUNDLES:
            total += BUNDLES[item]['price']
    
    return render_template('checkout.html', cart_items=cart_items, products=PRODUCTS, bundles=BUNDLES, total=total)

@app.route('/place-order', methods=['POST'])
def place_order():
    """Place order (simulated)"""
    cart_items = session.get('cart', [])
    if not cart_items:
        return jsonify({'success': False, 'message': 'Cart is empty'})
    
    # Generate order ID
    order_id = f"CV-{uuid.uuid4().hex[:8].upper()}"
    
    # Clear cart
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

# ============================================
# CV GENERATION (for after purchase)
# ============================================
@app.route('/generate-cv', methods=['POST'])
def generate_cv():
    """Generate CV after purchase"""
    data = request.json
    layout = data.get('layout', 'classic')
    name = data.get('name', 'John Doe')
    
    # Generate CV PDF
    cv_data = {
        'name': name,
        'title': data.get('title', 'Professional'),
        'summary': data.get('summary', ''),
        'skills': data.get('skills', []),
        'experience': data.get('experience', []),
        'education': data.get('education', []),
        'references': data.get('references', [])
    }
    
    pdf_path = create_cv_from_dict(cv_data, layout)
    
    return jsonify({
        'success': True,
        'download_url': f'/download/{os.path.basename(pdf_path)}'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
