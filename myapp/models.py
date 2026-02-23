from django.db import models
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

# --- 1. USER PROFILE ---
class Profile(models.Model):
    USER_TYPES = [
        ('customer', 'Customer'),
        ('seller', 'Seller'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='customer')
    company_name = models.CharField(max_length=200, null=True, blank=True)
    mobile = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.user_type})"

# --- 2. PRODUCT MODEL ---
class Product(models.Model):
    CATEGORY_CHOICES = [
        ('tech', 'Tech'),
        ('fashion', 'Fashion'),
        ('home', 'Home & Living'),
        ('beauty', 'Beauty'),
    ]
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="products", null=True)
    title = models.CharField(max_length=200)
    brand = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    image_url = models.URLField(max_length=500)
    stock_count = models.PositiveIntegerField(default=10)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title
    
    @property
    def in_stock(self):
        """Check if product is in stock"""
        return self.stock_count > 0

# --- 3. CART ORDER MODEL ---
class CartOrder(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('packed', 'Packed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
    ]
    PAYMENT_METHOD_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('razorpay', 'Razorpay'),
        ('upi_qr', 'UPI QR / Manual Transfer'),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)  # Support multiple units
    ordered_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    shipping_address = models.TextField(default="Not Provided")
    mobile = models.CharField(max_length=15, default="0000000000")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cod')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True, null=True, help_text="UTR or transaction ID from payment")

    def __str__(self):
        return f"Order #{self.id} - {self.user.username} (x{self.quantity})"

    @property
    def total_price(self):
        """Compute total price for this line item: price × quantity"""
        return self.price * self.quantity

# --- 4. PRODUCT IMAGE GALLERY ---
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image_url = models.URLField(max_length=500)
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_primary', 'uploaded_at']

    def __str__(self):
        return f"Image for {self.product.title}"

# --- 5. PRODUCT VARIANTS (Size, Color, etc.) ---
class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    variant_type = models.CharField(max_length=50)  # e.g., "Size", "Color", "Specification"
    variant_value = models.CharField(max_length=100)  # e.g., "Large", "Red", "256GB"
    price_adjustment = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock_count = models.PositiveIntegerField(default=10)

    class Meta:
        unique_together = ('product', 'variant_type', 'variant_value')

    def __str__(self):
        return f"{self.product.title} - {self.variant_type}: {self.variant_value}"

# --- 6. PRODUCT REVIEWS & RATINGS ---
class ProductReview(models.Model):
    RATING_CHOICES = [(i, f'{i} Stars') for i in range(1, 6)]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    title = models.CharField(max_length=200)
    review_text = models.TextField()
    helpful_count = models.PositiveIntegerField(default=0)
    verified_purchase = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('product', 'user')

    def __str__(self):
        return f"{self.user.username} - {self.product.title} ({self.rating}★)"

# --- 7. WISHLIST ---
class WishlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wishlist")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.user.username}'s Wishlist - {self.product.title}"

# --- 8. COUPON / DISCOUNT ---
class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    discount_flat = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    min_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_uses = models.PositiveIntegerField(null=True, blank=True)
    used_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_till = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code

    def is_valid(self):
        return self.is_active and timezone.now() >= self.valid_from and timezone.now() <= self.valid_till

# --- 9. CART (Proper Shopping Cart) ---
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cart")
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.user.username}"

    @property
    def subtotal(self):
        return sum(item.total_price for item in self.items.all())

    @property
    def discount_amount(self):
        if self.coupon and self.coupon.is_valid():
            if self.coupon.discount_flat:
                return self.coupon.discount_flat
            return (self.subtotal * self.coupon.discount_percentage) / 100
        return 0

    @property
    def total(self):
        return max(0, self.subtotal - self.discount_amount)

# --- 10. CART ITEMS ---
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cart', 'product', 'variant')

    def __str__(self):
        return f"{self.product.title} x{self.quantity}"

    @property
    def total_price(self):
        base_price = self.product.price
        if self.variant:
            base_price += self.variant.price_adjustment
        return base_price * self.quantity

# --- 11. REFUND REQUEST ---
class RefundRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('processed', 'Refund Processed'),
    ]
    REASON_CHOICES = [
        ('damaged', 'Product Damaged'),
        ('defective', 'Defective Product'),
        ('not_as_described', 'Not as Described'),
        ('changed_mind', 'Changed Mind'),
        ('wrong_item', 'Wrong Item Received'),
        ('other', 'Other'),
    ]

    order = models.OneToOneField(CartOrder, on_delete=models.CASCADE, related_name="refund")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    description = models.TextField()
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Refund for Order #{self.order.id}"

# --- 12. INVOICE ---
class Invoice(models.Model):
    # Support consolidated invoices that can reference multiple CartOrder entries
    orders = models.ManyToManyField(CartOrder, related_name="invoices", blank=True)
    invoice_number = models.CharField(max_length=50, unique=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    issued_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.invoice_number

# --- 13. NEWSLETTER SUBSCRIPTION ---
class NewsletterSubscription(models.Model):
    email = models.EmailField(unique=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

# --- 14. REFERRAL PROGRAM ---
class Referral(models.Model):
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="referrals_made")
    referred_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="referred_by")
    reward_amount = models.DecimalField(max_digits=10, decimal_places=2, default=100)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('referrer', 'referred_user')

    def __str__(self):
        return f"{self.referrer.username} referred {self.referred_user.username}"

# --- 15. SELLER ANALYTICS ---
class SellerAnalytics(models.Model):
    seller = models.OneToOneField(User, on_delete=models.CASCADE, related_name="analytics")
    total_sales = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_orders = models.PositiveIntegerField(default=0)
    total_customers = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Analytics for {self.seller.username}"

# --- 16. CONTACT MESSAGE MODEL ---
class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name}"

# --- 5. SIGNALS (The "Glue") ---
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)

@receiver(post_save, sender=Profile)
def assign_seller_permissions(sender, instance, created, **kwargs):
    """Auto-grant seller permissions when profile is set as seller"""
    if instance.user_type == 'seller':
        # Use update_fields to avoid triggering post_save signal again (prevents recursion)
        User.objects.filter(pk=instance.user.pk).update(is_staff=True)
        
        product_ct = ContentType.objects.get_for_model(Product)
        cart_order_ct = ContentType.objects.get_for_model(CartOrder)
        
        seller_perms = Permission.objects.filter(
            content_type__in=[product_ct, cart_order_ct],
            codename__in=['add_product', 'change_product', 'delete_product', 'view_cartorder']
        )
        
        instance.user.user_permissions.set(seller_perms)
        
        # Create seller analytics
        SellerAnalytics.objects.get_or_create(seller=instance.user)

@receiver(post_save, sender=User)
def create_customer_cart(sender, instance, created, **kwargs):
    """Create shopping cart for new customers"""
    if created:
        # Check if user is a seller
        profile = getattr(instance, 'profile', None)
        if not profile or profile.user_type == 'customer':
            Cart.objects.get_or_create(user=instance)