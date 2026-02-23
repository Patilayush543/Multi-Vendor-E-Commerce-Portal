from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import CartOrder, Product, ContactMessage, Profile

# --- 1. USER & PROFILE MANAGEMENT (The "Amazon" Style) ---
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Patilcraft Profile Info'

class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline, )
    list_display = ('username', 'email', 'get_user_type', 'is_staff', 'is_superuser')
    list_filter = ('is_staff', 'profile__user_type')

    def get_user_type(self, obj):
        return obj.profile.user_type
    get_user_type.short_description = 'Account Type'

# Re-register User with our custom Profile view
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# --- 2. PRODUCT MANAGEMENT (Multi-Vendor Logic) ---
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'seller', 'price', 'category', 'stock_count')
    list_filter = ('category', 'brand', 'seller')
    search_fields = ('title', 'brand')
    list_editable = ('price', 'stock_count') # Quick edits for sellers

    # Logic: Sellers only see THEIR products; Admin sees ALL
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(seller=request.user)

    # Automatically assign the logged-in user as the Seller when saving
    def save_model(self, request, obj, form, change):
        if not obj.seller:
            obj.seller = request.user
        super().save_model(request, obj, form, change)

# --- 3. ORDER MANAGEMENT (Sellers see only their orders) ---
@admin.register(CartOrder)
class CartOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product_name', 'price', 'status', 'ordered_date')
    list_filter = ('status', 'ordered_date')
    search_fields = ('user__username', 'product_name')
    readonly_fields = ('ordered_date', 'user', 'product', 'product_name', 'price')

    def get_queryset(self, request):
        """Sellers only see orders for their own products"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.profile.user_type == 'seller':
            return qs.filter(product__seller=request.user)
        return qs

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

# --- 4. CUSTOMER INQUIRIES ---
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'timestamp')
    search_fields = ('name', 'email', 'subject')
    readonly_fields = ('timestamp',)