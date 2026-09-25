from django.urls import path
from . import views

urlpatterns = [
    # Catalog
    path('', views.product_list, name='home'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    
    # Wishlist & Reviews
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),
    path('review/add/<int:product_id>/', views.add_review, name='add_review'),
    
    # Cart & Checkout
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('payment-success/', views.payment_success, name='payment_success'),
    
    # Admin Analytics Dashboard
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # Auth
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]