from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import RegisterForm
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .models import Order, OrderItem
from django.contrib.auth.decorators import login_required
from .models import Wishlist, Review
from .forms import ReviewForm
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count, F

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Automatically log in user after registration
            messages.success(request, f"Welcome to the store, {user.username}!")
            return redirect('home')
        else:
            messages.error(request, "Registration failed. Please check the form errors.")
    else:
        form = RegisterForm()
    
    return render(request, 'shop/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
        
    return render(request, 'shop/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')

def home_view(request):
    return render(request, 'shop/home.html')

from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Product, Category, Cart, CartItem

# --- PRODUCT CATALOG & SEARCH ---
def product_list(request):
    query = request.GET.get('q', '')
    category_slug = request.GET.get('category', '')
    
    products = Product.objects.filter(is_available=True)
    categories = Category.objects.all()

    if category_slug:
        products = products.filter(category__slug=category_slug)

    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    context = {
        'products': products,
        'categories': categories,
        'query': query,
        'selected_category': category_slug,
    }
    return render(request, 'shop/product_list.html', context)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_available=True)
    reviews = product.reviews.all().order_by('-created_at')
    review_form = ReviewForm()
    
    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()

    context = {
        'product': product,
        'reviews': reviews,
        'review_form': review_form,
        'in_wishlist': in_wishlist,
    }
    return render(request, 'shop/product_detail.html', context)


# --- SHOPPING CART MANAGEMENT ---
def _get_cart(request):
    """ Helper helper function to retrieve or create a cart session """
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        cart_id = request.session.get('cart_id')
        if cart_id:
            cart = Cart.objects.filter(id=cart_id).first()
            if not cart:
                cart = Cart.objects.create()
                request.session['cart_id'] = cart.id
        else:
            cart = Cart.objects.create()
            request.session['cart_id'] = cart.id
    return cart

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = _get_cart(request)
    
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
        
    messages.success(request, f"Added {product.name} to your cart.")
    return redirect('cart_detail')

def remove_from_cart(request, item_id):
    cart = _get_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    cart_item.delete()
    messages.info(request, "Item removed from your cart.")
    return redirect('cart_detail')

def cart_detail(request):
    cart = _get_cart(request)
    items = cart.items.all()
    
    # Calculate cart total
    total = sum(item.product.price * item.quantity for item in items)
    
    context = {
        'cart': cart,
        'items': items,
        'total': total
    }
    return render(request, 'shop/cart_detail.html', context)

# Initialize Razorpay Client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def checkout_view(request):
    cart = _get_cart(request)
    items = cart.items.all()
    if not items:
        messages.warning(request, "Your cart is empty!")
        return redirect('home')

    total_amount = sum(item.product.price * item.quantity for item in items)
    
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        address = request.POST.get('address')
        
        # 1. Create Local Order
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            full_name=full_name,
            email=email,
            shipping_address=address,
            total_amount=total_amount,
            status='Pending'
        )
        
        # Save order items
        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                price=item.product.price,
                quantity=item.quantity
            )

        # 2. Create Razorpay Order (Amount in paise: 1 INR = 100 paise)
        razorpay_order = razorpay_client.order.create({
            "amount": int(total_amount * 100), 
            "currency": "INR",
            "payment_capture": "1"
        })
        
        order.razorpay_order_id = razorpay_order['id']
        order.save()
        
        # Clear Cart
        items.delete()

        context = {
            'order': order,
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_merchant_key': settings.RAZORPAY_KEY_ID,
            'amount': int(total_amount * 100),
            'currency': "INR",
        }
        return render(request, 'shop/payment.html', context)

    return render(request, 'shop/checkout.html', {'items': items, 'total': total_amount})

@csrf_exempt
def payment_success(request):
    if request.method == "POST":
        payment_id = request.POST.get('razorpay_payment_id', '')
        razorpay_order_id = request.POST.get('razorpay_order_id', '')
        
        order = Order.objects.filter(razorpay_order_id=razorpay_order_id).first()
        if order:
            order.is_paid = True
            order.razorpay_payment_id = payment_id
            order.save()
            
            return render(request, 'shop/payment_success.html', {'order': order})
            
    return redirect('home')



# --- WISHLIST VIEWS ---
@login_required
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    
    if not created:
        wishlist_item.delete()
        messages.info(request, f"Removed {product.name} from your wishlist.")
    else:
        messages.success(request, f"Added {product.name} to your wishlist!")
        
    return redirect('product_detail', slug=product.slug)

@login_required
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, 'shop/wishlist.html', {'wishlist_items': wishlist_items})


# --- PRODUCT REVIEWS ---
@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, "Thank you! Your review has been submitted.")
    return redirect('product_detail', slug=product.slug)


@staff_member_required
def admin_dashboard(request):
    total_revenue = Order.objects.filter(is_paid=True).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_orders = Order.objects.count()
    completed_orders = Order.objects.filter(is_paid=True).count()
    
    # Low Stock Alerts (Stock < 10)
    low_stock_products = Product.objects.filter(stock__lt=10)
    
    # Recent Orders
    recent_orders = Order.objects.all().order_by('-created_at')[:5]

    context = {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'completed_orders': completed_orders,
        'low_stock_products': low_stock_products,
        'recent_orders': recent_orders,
    }
    return render(request, 'shop/admin_dashboard.html', context)