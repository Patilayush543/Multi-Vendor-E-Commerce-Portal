from django.urls import path, include
from . import views 

urlpatterns = [
    # Main Pages
    path('', views.index, name='home'),
    path('about/', views.about, name='about'),
    path('profile/', views.profile, name='profile'),
    
    # Product Logic
    path('product/<str:cat>/<int:id>/', views.product_detail, name='product_detail'),
    
    # Cart System
    path('cart/', views.cart_view, name='cart_view'),
    path('add-to-cart/<int:p_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    
    # Checkout & Orders
    path('checkout/', views.checkout_view, name='checkout'),
    path('confirm-order/', views.confirm_order, name='confirm_order'),
    
    # Authentication (REWRITTEN to match auth_view)
    path('auth/', views.auth_view, name='auth'),
    path('login-user/', views.login_user, name='login_user'),
    path('register-user/', views.register_user, name='register_user'),
    path('logout-user/', views.logout_user, name='logout_user'),
    
    # Extra Pages
    path('contact/', views.contact, name='contact'),
    
    # ==================== NEW PREMIUM FEATURES ====================
    
    # FEATURE 1: Product Detail (PREMIUM VERSION)
    path('product-detail/<int:product_id>/', views.product_detail_new, name='product_detail_new'),
    
    # FEATURE 2: Product Search & Filters
    path('products/', views.product_list, name='product_list'),
    
    # FEATURE 3: Wishlist Management
    path('wishlist/', views.wishlist_view, name='wishlist_view'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/move-to-cart/<int:product_id>/', views.move_to_cart, name='move_to_cart'),
    
    # FEATURE 4: Advanced Cart System
    path('cart-new/', views.cart_view_new, name='cart_view_new'),
    path('cart/update-quantity/<int:item_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('cart/remove-item/<int:item_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('cart/apply-coupon/', views.apply_coupon, name='apply_coupon'),
    
    # FEATURE 5: Customer Dashboard
    path('dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('order/<int:order_id>/refund/', views.request_refund, name='request_refund'),
    path('profile/update/', views.update_profile, name='update_profile'),
    
    # PAYMENT GATEWAY
    path('verify-razorpay/', views.verify_razorpay, name='verify_razorpay'),
    path('order-success/', views.order_success, name='order_success'),
    
    # SELLER FEATURES
    path('seller/<int:seller_id>/', views.seller_profile, name='seller_profile'),
    path('seller/dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('invoice/', views.invoice_list, name='invoice_list'),
    path('invoice/<int:invoice_id>/', views.invoice_view, name='invoice_view'),
    path('download-invoice/<int:order_id>/', views.generate_invoice, name='generate_invoice'),
    path('download-invoice/invoice/<int:invoice_id>/', views.download_consolidated_invoice, name='download_invoice_consolidated'),
    
    # Social Login (Google/GitHub)
    path('accounts/', include('allauth.urls')),
]