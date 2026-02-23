from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.csrf import csrf_protect
from django.db.models import Q, Avg, Count
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import (CartOrder, Product, ContactMessage, ProductReview, WishlistItem, 
                     Cart, CartItem, ProductImage, Coupon, Invoice, RefundRequest,
                     NewsletterSubscription, Profile, SellerAnalytics)
from .forms import (SellerSignUpForm, ProductReviewForm, AddToCartForm, ApplyCouponForm,
                   NewsletterForm, RefundRequestForm, ProductFilterForm)
from io import BytesIO
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
import json
import hmac
import hashlib
import io
import razorpay
import json
from django.utils import timezone

# PDF libraries: prefer xhtml2pdf (works on all platforms)
try:
    from xhtml2pdf import pisa
    HAS_XHTML2PDF = True
except Exception:
    HAS_XHTML2PDF = False

# WeasyPrint fallback (requires system libraries on Windows)
try:
    import weasyprint
    HAS_WEASY = True
except Exception:
    HAS_WEASY = False

# --- 1. HOME & SEARCH ---
def index(request):
    query = request.GET.get("q") 
    cat = request.GET.get("cat") 
    trend = Product.objects.all()
    if query:
        trend = trend.filter(Q(title__icontains=query) | Q(brand__icontains=query))
    elif cat:
        trend = trend.filter(category=cat)
    return render(request, "index.html", {"trend": trend, "query": query, "cat": cat})

# --- 2. AUTHENTICATION (The Elite Version) ---
def auth_view(request):
    """Main entry for the premium login/signup portal."""
    from django.middleware.csrf import get_token
    # Explicitly get CSRF token to ensure it's in context
    csrf_token = get_token(request)
    return render(request, 'login.html', {
        'signup_form': SellerSignUpForm(),
        'login_form': AuthenticationForm(),
        'csrf_token': csrf_token
    })

@csrf_protect
def register_user(request):
    """Handles the creation of Customers and Sellers."""
    if request.method == "POST":
        form = SellerSignUpForm(request.POST)
        if form.is_valid():
            # This save() method in your forms.py creates the User + Profile
            user = form.save() 
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('/') 
        else:
            # Return form with errors to be displayed in template
            return render(request, "login.html", {
                "signup_form": form, 
                "login_form": AuthenticationForm(),
            })
    return redirect('auth_view')
@csrf_protect

def login_user(request):
    """Authenticates the user via Email."""
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        try:
            # Multi-vendor logic: We look up by email since we use it as login ID
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)
            if user is not None:
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                next_url = request.POST.get('next')
                return redirect(next_url if next_url else '/')
            else:
                return render(request, "login.html", {
                    "error": "Invalid Password!", 
                    "signup_form": SellerSignUpForm(),
                    "login_form": AuthenticationForm()
                })
        except User.DoesNotExist:
            return render(request, "login.html", {
                "error": "Email not found!",
                "signup_form": SellerSignUpForm(),
                "login_form": AuthenticationForm()
            })
    return redirect('auth_view')

def logout_user(request):
    logout(request)
    return redirect("/")

# --- 3. SHOPPING SYSTEM ---
def product_detail(request, cat, id):
    try:
        product = Product.objects.get(id=id)
        related = Product.objects.filter(category=cat).exclude(id=id)[:6]
    except Product.DoesNotExist:
        raise Http404("Product Not Found")
    
    # Handle POST actions: review submission or add-to-cart
    if request.method == 'POST' and request.user.is_authenticated:
        # Review submission
        if request.POST.get('rating'):
            rating = int(request.POST.get('rating') or 0)
            title = request.POST.get('title', '')[:200]
            review_text = request.POST.get('review_text', '')
            # mark verified_purchase if user has a delivered/shipped order for this product
            verified = CartOrder.objects.filter(user=request.user, product=product, status__in=['shipped', 'delivered']).exists()
            ProductReview.objects.update_or_create(
                product=product,
                user=request.user,
                defaults={
                    'rating': rating,
                    'title': title,
                    'review_text': review_text,
                    'verified_purchase': verified,
                }
            )
            return redirect('product_detail', cat=cat, id=id)

        # Add to cart submission
        if request.POST.get('add_to_cart'):
            qty = int(request.POST.get('quantity', 1))
            cart, _ = Cart.objects.get_or_create(user=request.user)
            # create or update item
            ci, created = CartItem.objects.get_or_create(cart=cart, product=product, variant=None, defaults={'quantity': qty})
            if not created:
                ci.quantity = max(1, ci.quantity + qty)
                ci.save()
            return redirect('cart_view_new')
    
    # Get product images
    images = ProductImage.objects.filter(product=product)
    
    # Get reviews and calculate average rating
    reviews = ProductReview.objects.filter(product=product).order_by('-created_at')
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    avg_rating = round(avg_rating, 1)
    review_count = reviews.count()
    
    return render(request, "product_detail.html", {
        "product": product,
        "images": images,
        "reviews": reviews,
        "avg_rating": avg_rating,
        "review_count": review_count,
        "related": related,
        "cat": cat
    })

def add_to_cart(request, p_id):
    if not request.user.is_authenticated:
        return redirect('auth_view')
    item = Product.objects.get(id=p_id)
    
    # Get quantity from POST or default to 1
    quantity = int(request.POST.get('quantity', 1)) if request.method == 'POST' else 1
    quantity = max(1, quantity)  # Ensure at least 1
    
    CartOrder.objects.create(
        user=request.user, 
        product=item, 
        product_name=item.title, 
        price=item.price, 
        quantity=quantity,
        status='pending'
    )
    return redirect('cart_view')

def cart_view(request):
    if not request.user.is_authenticated:
        return redirect('auth_view')
    items = CartOrder.objects.filter(user=request.user, status='pending')
    total = sum(item.total_price for item in items)  # Use total_price property
    return render(request, "cart.html", {"items": items, "total": total})

def remove_from_cart(request, item_id):
    if not request.user.is_authenticated:
        return redirect('auth_view')
    CartOrder.objects.filter(user=request.user, id=item_id).delete()
    return redirect('cart_view')

def checkout_view(request):
    if not request.user.is_authenticated:
        return redirect('auth_view')
    items = CartOrder.objects.filter(user=request.user, status='pending')
    total = sum(item.total_price for item in items)  # Use total_price property
    return render(request, "checkout.html", {"items": items, "total": total})

def confirm_order(request):
    if request.method == "POST" and request.user.is_authenticated:
        address = request.POST.get("address")
        mobile = request.POST.get("mobile")
        payment_method = request.POST.get("payment_method", "cod")
        transaction_id = request.POST.get("transaction_id", "").strip()
        
        user_cart = CartOrder.objects.filter(user=request.user, status='pending')

        # If no CartOrder pending (new cart system uses Cart/CartItem), create CartOrder(s)
        if not user_cart.exists():
            cart = None
            try:
                cart = Cart.objects.get(user=request.user)
            except Cart.DoesNotExist:
                cart = None

            created_orders = []
            if cart:
                items = CartItem.objects.filter(cart=cart)
                for ci in items:
                    price = ci.total_price
                    # Payment status is always pending initially; webhook/manual confirmation updates it
                    order = CartOrder.objects.create(
                        user=request.user,
                        product=ci.product,
                        product_name=ci.product.title,
                        price=price,
                        status='packed',
                        shipping_address=address or "Not Provided",
                        mobile=mobile or "",
                        payment_method=payment_method,
                        payment_status='pending',
                        transaction_id=transaction_id if payment_method == 'upi_qr' else None,
                    )
                    created_orders.append(order)
                # clear cart after creating orders
                items.delete()

            # use created orders as the user_cart for invoice creation
            if created_orders:
                user_cart = CartOrder.objects.filter(id__in=[o.id for o in created_orders])
        else:
            # Update existing pending orders with payment info
            user_cart.update(
                status='packed',
                shipping_address=address,
                mobile=mobile,
                payment_method=payment_method,
                payment_status='pending',
                transaction_id=transaction_id if payment_method == 'upi_qr' else None,
            )
        
        # Handle Razorpay payment initialization
        if payment_method == 'razorpay' and user_cart.exists():
            try:
                razorpay_key_id = getattr(settings, 'RAZORPAY_KEY_ID', None)
                razorpay_key_secret = getattr(settings, 'RAZORPAY_KEY_SECRET', None)
                
                if not razorpay_key_id or not razorpay_key_secret:
                    return render(request, "checkout.html", {"error": "Razorpay keys not configured"})
                
                # Initialize Razorpay client
                client = razorpay.Client(auth=(razorpay_key_id, razorpay_key_secret))
                
                # Calculate total amount in paise (Razorpay expects amount in 1/100 of currency unit)
                total_amount = sum(order.total_price for order in user_cart)
                amount_paise = int(total_amount * 100)
                
                # Create Razorpay order
                razorpay_order = client.order.create(dict(
                    amount=amount_paise,
                    currency='INR',
                    receipt=f"order_{request.user.id}_{int(timezone.now().timestamp())}",
                    notes={
                        'user_id': request.user.id,
                        'orders': list(user_cart.values_list('id', flat=True)),
                    }
                ))
                
                # Store Razorpay order ID in the orders
                for order in user_cart:
                    order.transaction_id = razorpay_order['id']
                    order.save()
                
                # Pass Razorpay details to frontend payment page
                context = {
                    'razorpay_order_id': razorpay_order['id'],
                    'razorpay_key_id': razorpay_key_id,
                    'amount': total_amount,
                    'amount_paise': amount_paise,
                    'user_email': request.user.email,
                    'user_name': request.user.get_full_name() or request.user.username,
                    'orders': user_cart,
                }
                return render(request, "razorpay_payment.html", context)
            except Exception as e:
                import traceback
                traceback.print_exc()
                return render(request, "checkout.html", {"error": f"Razorpay error: {str(e)}"})
        
        # For UPI QR and COD payments: continue with invoice creation
        consolidate = getattr(settings, 'CONSOLIDATED_INVOICE', True)
        invoices = []

        if user_cart.exists():
            if consolidate:
                # Create a single invoice for all orders in this checkout
                subtotal = sum([o.total_price for o in user_cart])  # Use total_price (price × quantity)
                invoice_number = f"INV{request.user.id}{int(timezone.now().timestamp())}"
                invoice = Invoice.objects.create(
                    invoice_number=invoice_number,
                    subtotal=subtotal,
                    tax=0,
                    total=subtotal,
                )
                invoice.orders.set(user_cart)
                invoices = [invoice]
            else:
                # Keep legacy behavior: one invoice per order
                for order in user_cart:
                    invoice = Invoice.objects.create(
                        invoice_number=f"INV{order.id}{int(order.ordered_date.timestamp())}",
                        subtotal=order.total_price,  # Use total_price
                        tax=0,
                        total=order.total_price,
                    )
                    invoice.orders.add(order)
                    invoices.append(invoice)

        # If no invoices were created (empty list), try to fetch any existing invoices for the user
        if not invoices:
            invoices = list(Invoice.objects.filter(orders__user=request.user).distinct())

        total_amount = sum(inv.total for inv in invoices)
        # Attempt to generate PDF invoices and email them to the customer
        attachments = []

        def render_invoice_pdf(inv):
            html = render_to_string('invoice.html', {'invoice': inv})
            # WeasyPrint preferred
            if HAS_WEASY:
                try:
                    pdf_bytes = weasyprint.HTML(string=html).write_pdf()
                    return pdf_bytes
                except Exception:
                    pass
            # xhtml2pdf fallback
            if HAS_XHTML2PDF:
                try:
                    result = BytesIO()
                    pisa_status = pisa.CreatePDF(html, dest=result)
                    if pisa_status.err:
                        return None
                    return result.getvalue()
                except Exception:
                    return None
            return None

        for inv in invoices:
            pdf = render_invoice_pdf(inv)
            if pdf:
                attachments.append((f"{inv.invoice_number}.pdf", pdf, 'application/pdf'))
            else:
                # Attach HTML fallback
                html = render_to_string('invoice.html', {'invoice': inv})
                attachments.append((f"{inv.invoice_number}.html", html.encode('utf-8'), 'text/html'))

        # Send email with attachments if the user has an email
        user_email = getattr(request.user, 'email', None)
        if user_email:
            subject = f"Your Invoice(s) from {getattr(settings, 'DEFAULT_FROM_EMAIL', 'Our Store')}"
            body = "Thank you for your order. Attached are your invoice(s)."
            email = EmailMessage(subject=subject, body=body, from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None), to=[user_email])
            for name, content, mimetype in attachments:
                try:
                    email.attach(name, content, mimetype)
                except Exception:
                    # skip attachment if it fails
                    continue
            try:
                email.send(fail_silently=True)
            except Exception:
                pass

        context = {
            'invoices': invoices,
            'total_amount': total_amount,
            'shipping_address': address,
            'mobile': mobile,
        }
        return render(request, "order_success.html", context)
    return redirect('cart_view')


@login_required(login_url='auth_view')
def invoice_view(request, invoice_id):
    """Render a printable invoice for the customer."""
    invoice = get_object_or_404(Invoice, id=invoice_id)
    # Ensure the invoice belongs to the requesting user (any linked order)
    if not invoice.orders.filter(user=request.user).exists():
        raise Http404("Invoice not found")

    return render(request, 'invoice.html', {'invoice': invoice})


@login_required(login_url='auth_view')
def invoice_list(request):
    """List all invoices visible to the current user."""
    invoices = Invoice.objects.filter(orders__user=request.user).distinct().order_by('-issued_at')
    # Also include any non-pending CartOrder rows as a fallback (so users without Invoice objects can still download PDFs)
    orders = CartOrder.objects.filter(user=request.user).exclude(status='pending').order_by('-ordered_date')
    return render(request, 'invoices_list.html', {'invoices': invoices, 'orders': orders})


def generate_invoice(request, order_id):
    """Generate a PDF for a single CartOrder (downloadable)."""
    try:
        order = CartOrder.objects.get(id=order_id, user=request.user)
    except CartOrder.DoesNotExist:
        return HttpResponse('Order not found', status=404)

    # Render template to HTML
    template = get_template('invoice_pdf.html')
    context = {'order': order, 'user': request.user}
    html = template.render(context)

    if HAS_XHTML2PDF:
        result = io.BytesIO()
        pdf = pisa.pisaDocument(io.BytesIO(html.encode('utf-8')), result)
        if not pdf.err:
            resp = HttpResponse(result.getvalue(), content_type='application/pdf')
            resp['Content-Disposition'] = f'attachment; filename="Invoice_Order_{order_id}.pdf"'
            return resp
        return HttpResponse('Error generating PDF', status=400)

    return HttpResponse('PDF generator not available', status=500)


@login_required(login_url='auth_view')
def download_consolidated_invoice(request, invoice_id):
    """Generate a single PDF that contains the consolidated `Invoice` (all linked orders)."""
    invoice = get_object_or_404(Invoice, id=invoice_id)
    # Ensure ownership
    if not invoice.orders.filter(user=request.user).exists():
        return HttpResponse('Invoice not found', status=404)

    html = render_to_string('invoice.html', {'invoice': invoice})

    # Try xhtml2pdf first (works on all platforms)
    if HAS_XHTML2PDF:
        try:
            result = BytesIO()
            pisa_status = pisa.CreatePDF(io.BytesIO(html.encode('utf-8')), dest=result)
            if not pisa_status.err:
                return HttpResponse(result.getvalue(), content_type='application/pdf')
        except Exception:
            pass

    # Fallback to WeasyPrint
    if HAS_WEASY:
        try:
            pdf_bytes = weasyprint.HTML(string=html).write_pdf()
            return HttpResponse(pdf_bytes, content_type='application/pdf')
        except Exception:
            pass

    return HttpResponse('PDF generator not available', status=500)

# --- 4. EXTRA PAGES ---
def profile(request): 
    # Use request.user.profile to show Seller data in profile.html
    user = request.user
    profile = None
    if user.is_authenticated:
        try:
            profile = user.profile
        except Exception:
            profile, _ = Profile.objects.get_or_create(user=user)
    pic = None
    if profile:
        pic = getattr(profile, 'profile_pic', None)
    return render(request, "profile.html", {"user": user, "profile": profile, "name": user.first_name, "last_name": user.last_name, "email": user.email, "pic": pic})

def about(request): 
    return render(request, "about.html")

def contact(request):
    if request.method == "POST":
        ContactMessage.objects.create(
            name=request.POST.get('name'), 
            email=request.POST.get('email'), 
            subject=request.POST.get('subject'), 
            message=request.POST.get('message')
        )
        return render(request, "contact.html", {"success": True})
    return render(request, "contact.html")


# ==================== NEW PREMIUM FEATURES ====================

# --- FEATURE 1: PRODUCT DETAIL PAGE (30 min) ---
@login_required(login_url='auth_view')
def product_detail_new(request, product_id):
    """Premium product detail page with gallery, reviews, and wishlist."""
    product = get_object_or_404(Product, id=product_id)

    # Handle POST actions: review submission or add-to-cart
    if request.method == 'POST' and request.user.is_authenticated:
        # Review submission
        if request.POST.get('rating'):
            rating = int(request.POST.get('rating') or 0)
            title = request.POST.get('title', '')[:200]
            review_text = request.POST.get('review_text', '')
            # mark verified_purchase if user has a delivered/shipped order for this product
            verified = CartOrder.objects.filter(user=request.user, product=product, status__in=['shipped', 'delivered']).exists()
            ProductReview.objects.update_or_create(
                product=product,
                user=request.user,
                defaults={
                    'rating': rating,
                    'title': title,
                    'review_text': review_text,
                    'verified_purchase': verified,
                }
            )
            return redirect('product_detail_new', product_id=product_id)

        # Add to cart submission
        if request.POST.get('add_to_cart'):
            qty = int(request.POST.get('quantity', 1))
            cart, _ = Cart.objects.get_or_create(user=request.user)
            # create or update item
            ci, created = CartItem.objects.get_or_create(cart=cart, product=product, variant=None, defaults={'quantity': qty})
            if not created:
                ci.quantity = max(1, ci.quantity + qty)
                ci.save()
            return redirect('cart_view_new')

    # Get all images for gallery
    images = ProductImage.objects.filter(product=product).order_by('uploaded_at')

    # Get all reviews with ratings
    reviews = ProductReview.objects.filter(product=product).order_by('-created_at')
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    review_count = reviews.count()

    # Check if in wishlist
    in_wishlist = WishlistItem.objects.filter(user=request.user, product=product).exists()

    # Get related products (same category)
    related = Product.objects.filter(category=product.category).exclude(id=product_id)[:6]

    context = {
        'product': product,
        'images': images if images.exists() else [],
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1),
        'review_count': review_count,
        'in_wishlist': in_wishlist,
        'related': related,
    }
    return render(request, 'product_detail.html', context)


# --- FEATURE 2: PRODUCT SEARCH & FILTERS (25 min) ---
def product_list(request):
    """Advanced product search with filters and sorting."""
    products = Product.objects.all()
    
    # Search query
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(title__icontains=search_query) | 
            Q(brand__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Category filter
    category = request.GET.get('category', '')
    if category:
        products = products.filter(category=category)
    
    # Price range filter
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # In stock filter
    in_stock = request.GET.get('in_stock', '')
    if in_stock:
        products = products.filter(in_stock=True)
    
    # Rating filter
    min_rating = request.GET.get('min_rating', '')
    if min_rating:
        products = products.annotate(
            avg_rating=Avg('productreview__rating')
        ).filter(avg_rating__gte=min_rating)
    
    # Sorting
    sort_by = request.GET.get('sort', '-created_at')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'rating':
        products = products.annotate(
            avg_rating=Avg('productreview__rating')
        ).order_by('-avg_rating')
    elif sort_by == 'popular':
        products = products.annotate(
            review_count=Count('productreview')
        ).order_by('-review_count')
    else:
        products = products.order_by(sort_by)
    
    # Get unique categories for filter
    categories = Product.objects.values_list('category', flat=True).distinct()
    
    form = ProductFilterForm(request.GET or None)
    
    context = {
        'products': products,
        'search_query': search_query,
        'category': category,
        'categories': categories,
        'min_price': min_price,
        'max_price': max_price,
        'in_stock': in_stock,
        'min_rating': min_rating,
        'sort_by': sort_by,
        'form': form,
    }
    return render(request, 'product_list.html', context)


# --- FEATURE 3: WISHLIST MANAGEMENT (20 min) ---
@login_required(login_url='auth_view')
def add_to_wishlist(request, product_id):
    """Add product to wishlist."""
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        wishlist_item, created = WishlistItem.objects.get_or_create(
            user=request.user,
            product=product
        )
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': 'Added to wishlist' if created else 'Already in wishlist',
                'in_wishlist': True
            })
        return redirect(request.META.get('HTTP_REFERER', '/'))
    
    return redirect('product_detail_new', product_id=product_id)


@login_required(login_url='auth_view')
def remove_from_wishlist(request, product_id):
    """Remove product from wishlist."""
    WishlistItem.objects.filter(
        user=request.user,
        product_id=product_id
    ).delete()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'message': 'Removed from wishlist'})
    
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required(login_url='auth_view')
def wishlist_view(request):
    """Display user's wishlist."""
    wishlist_items = WishlistItem.objects.filter(user=request.user).select_related('product')
    total_items = wishlist_items.count()
    total_price = sum(item.product.price for item in wishlist_items)
    
    context = {
        'wishlist_items': wishlist_items,
        'total_items': total_items,
        'total_price': total_price,
    }
    return render(request, 'wishlist.html', context)


@login_required(login_url='auth_view')
def move_to_cart(request, product_id):
    """Move wishlist item to cart."""
    product = get_object_or_404(Product, id=product_id)
    
    # Create cart item
    cart, _ = Cart.objects.get_or_create(user=request.user)
    CartItem.objects.create(cart=cart, product=product, quantity=1)
    
    # Remove from wishlist
    WishlistItem.objects.filter(user=request.user, product=product).delete()
    
    return redirect('cart_view_new')


# --- FEATURE 4: ADVANCED CART SYSTEM (25 min) ---
@login_required(login_url='auth_view')
def cart_view_new(request):
    """Premium shopping cart with coupon application."""
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart).select_related('product')
    
    subtotal = sum(item.total_price for item in cart_items)
    discount = 0
    coupon_msg = None
    
    if cart.coupon:
        if cart.coupon.is_active:
            if cart.coupon.discount_flat:
                discount = min(cart.coupon.discount_flat, subtotal)
            elif cart.coupon.discount_percentage:
                discount = (subtotal * cart.coupon.discount_percentage) / 100
            coupon_msg = f"Coupon {cart.coupon.code} applied!"
        else:
            cart.coupon = None
            cart.save()
            coupon_msg = "This coupon has expired"
    
    total = max(0, subtotal - discount)
    
    coupon_form = ApplyCouponForm()
    
    context = {
        'cart_items': cart_items,
        'cart': cart,
        'subtotal': subtotal,
        'discount': discount,
        'total': total,
        'coupon_form': coupon_form,
        'coupon_msg': coupon_msg,
        # Backwards-compatible keys for the older cart template
        'items': cart_items,
        'total': total,
    }
    # Render the existing cart template (cart.html) which expects 'items' and 'total'
    return render(request, 'cart.html', context)


@login_required(login_url='auth_view')
def update_cart_quantity(request, item_id):
    """Update quantity of item in cart."""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
    else:
        cart_item.delete()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart = cart_item.cart if quantity > 0 else Cart.objects.get(user=request.user)
        return JsonResponse({
            'status': 'success',
            'total_price': cart_item.total_price if quantity > 0 else 0
        })
    
    return redirect('cart_view_new')


@login_required(login_url='auth_view')
def remove_cart_item(request, item_id):
    """Remove item from cart."""
    CartItem.objects.filter(id=item_id, cart__user=request.user).delete()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    return redirect('cart_view_new')


@login_required(login_url='auth_view')
def apply_coupon(request):
    """Apply coupon code to cart."""
    if request.method == 'POST':
        code = request.POST.get('code', '').strip().upper()
        try:
            coupon = Coupon.objects.get(code=code)
            if not coupon.is_active:
                msg = 'This coupon is not active'
            elif coupon.usage_count >= coupon.max_usage:
                msg = 'Coupon usage limit reached'
            else:
                cart = Cart.objects.get(user=request.user)
                cart.coupon = coupon
                cart.save()
                msg = f'Coupon {code} applied!'
        except Coupon.DoesNotExist:
            msg = f'Coupon code "{code}" not found'
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'message': msg})
        
        return redirect('cart_view_new')
    
    return redirect('cart_view_new')


# --- FEATURE 5: CUSTOMER DASHBOARD (30 min) ---
@login_required(login_url='auth_view')
def customer_dashboard(request):
    """Premium customer dashboard with orders, returns, and profile."""
    user = request.user
    
    # Profile data - ensure Profile exists
    try:
        profile = user.profile
    except Exception:
        # Create a profile if missing
        profile, _ = Profile.objects.get_or_create(user=user)
    
    # Orders
    # CartOrder uses `ordered_date` as the timestamp field
    orders = CartOrder.objects.filter(user=user).order_by('-ordered_date')
    total_orders = orders.count()
    total_spent = sum(order.price for order in orders)
    
    # Refunds/Returns
    refunds = RefundRequest.objects.filter(order__user=user).select_related('order')

    # Invoices
    # Invoice model uses `orders` (ManyToMany) and `issued_at`
    invoices = Invoice.objects.filter(orders__user=user).distinct().order_by('-issued_at')
    
    # Recent activity
    recent_orders = orders[:5]
    
    context = {
        'user': user,
        'profile': profile,
        'orders': orders,
        'total_orders': total_orders,
        'total_spent': total_spent,
        'refunds': refunds,
        'invoices': invoices,
        'recent_orders': recent_orders,
    }
    return render(request, 'customer_dashboard.html', context)


@login_required(login_url='auth_view')
def order_detail(request, order_id):
    """View full order details."""
    order = get_object_or_404(CartOrder, id=order_id, user=request.user)
    refund = RefundRequest.objects.filter(order=order).first()
    invoice = Invoice.objects.filter(order=order).first()
    
    context = {
        'order': order,
        'refund': refund,
        'invoice': invoice,
    }
    return render(request, 'order_detail.html', context)


@login_required(login_url='auth_view')
def request_refund(request, order_id):
    """Request refund for an order."""
    order = get_object_or_404(CartOrder, id=order_id, user=request.user)
    
    if request.method == 'POST':
        form = RefundRequestForm(request.POST)
        if form.is_valid():
            refund = form.save(commit=False)
            refund.order = order
            refund.save()
            return redirect('customer_dashboard')
    else:
        form = RefundRequestForm()
    
    context = {
        'order': order,
        'form': form,
    }
    return render(request, 'request_refund.html', context)


@login_required(login_url='auth_view')
def update_profile(request):
    """Update customer profile information."""
    user = request.user
    
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()
        
        try:
            profile = user.profile
        except Exception:
            profile, _ = Profile.objects.get_or_create(user=user)
        profile.phone = request.POST.get('phone', profile.phone)
        profile.address = request.POST.get('address', profile.address)
        profile.city = request.POST.get('city', profile.city)
        profile.state = request.POST.get('state', profile.state)
        profile.pincode = request.POST.get('pincode', profile.pincode)
        profile.save()
        
        return redirect('customer_dashboard')
    
    context = {
        'user': user,
        'profile': user.profile,
    }
    return render(request, 'update_profile.html', context)


# --- SELLER PREMIUM FEATURES ---
@login_required(login_url='auth_view')
def seller_profile(request, seller_id):
    """View seller profile with products and ratings."""
    seller = get_object_or_404(User, id=seller_id, profile__user_type='seller')
    seller_profile = seller.profile
    
    # Get seller's products
    products = Product.objects.filter(seller=seller)
    product_count = products.count()
    
    # Seller analytics
    analytics = SellerAnalytics.objects.filter(seller=seller).first()
    
    # Seller reviews (from product reviews)
    reviews = ProductReview.objects.filter(product__seller=seller).order_by('-created_at')[:10]
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    context = {
        'seller': seller,
        'seller_profile': seller_profile,
        'products': products[:12],
        'product_count': product_count,
        'analytics': analytics,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1),
    }
    return render(request, 'seller_profile.html', context)


@login_required(login_url='auth_view')
def seller_dashboard(request):
    """Seller analytics and management dashboard."""
    if not request.user.profile.user_type == 'seller':
        return redirect('/')
    
    seller = request.user
    
    # Products
    products = Product.objects.filter(seller=seller)
    product_count = products.count()
    
    # Sales
    orders = CartOrder.objects.filter(product__seller=seller)
    total_sales = sum(order.price for order in orders)
    total_orders = orders.count()
    
    # Analytics
    analytics = SellerAnalytics.objects.filter(seller=seller).first()
    
    # Top products
    top_products = products.annotate(
        review_count=Count('productreview')
    ).order_by('-review_count')[:5]
    
    context = {
        'seller': seller,
        'product_count': product_count,
        'total_sales': total_sales,
        'total_orders': total_orders,
        'analytics': analytics,
        'products': products[:10],
        'top_products': top_products,
    }
    return render(request, 'seller_dashboard.html', context)


# --- PAYMENT GATEWAY VIEWS ---
@login_required(login_url='auth_view')
@csrf_protect
def verify_razorpay(request):
    """
    Verify Razorpay payment signature and update order status.
    Expected POST data:
    {
        'razorpay_order_id': str,
        'razorpay_payment_id': str,
        'razorpay_signature': str
    }
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=400)
    
    try:
        data = json.loads(request.body)
        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_signature = data.get('razorpay_signature')
        
        # Get the secret key
        razorpay_key_secret = getattr(settings, 'RAZORPAY_KEY_SECRET', None)
        if not razorpay_key_secret:
            return JsonResponse({
                'status': 'error',
                'message': 'Razorpay secret not configured'
            }, status=500)
        
        # Create the signature string to verify
        verify_string = f"{razorpay_order_id}|{razorpay_payment_id}"
        
        # Compute HMAC SHA256 signature
        computed_signature = hmac.new(
            razorpay_key_secret.encode(),
            verify_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Verify signature
        if computed_signature != razorpay_signature:
            return JsonResponse({
                'status': 'error',
                'message': 'Payment signature verification failed'
            }, status=400)
        
        # Find and update orders with this Razorpay order ID
        orders = CartOrder.objects.filter(
            transaction_id=razorpay_order_id,
            user=request.user,
            payment_method='razorpay'
        )
        
        if not orders.exists():
            return JsonResponse({
                'status': 'error',
                'message': 'Order not found'
            }, status=404)
        
        # Update all matching orders
        for order in orders:
            order.payment_status = 'paid'
            order.transaction_id = razorpay_payment_id  # Store payment ID for reference
            order.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Payment verified successfully'
        })
    
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'status': 'error',
            'message': f'Verification error: {str(e)}'
        }, status=500)


@login_required(login_url='auth_view')
def order_success(request):
    """
    Display order success page with invoice details and download options.
    Shows all recent orders that haven't been paid yet (or recently paid).
    """
    user = request.user
    
    # Get recent orders (last 24 hours or unpaid)
    from datetime import timedelta
    from django.db.models import Q
    
    recent_time = timezone.now() - timedelta(hours=24)
    
    recent_orders = CartOrder.objects.filter(
        user=user,
        status='packed'
    ).filter(
        Q(ordered_date__gte=recent_time) | Q(payment_status='pending')
    ).order_by('-ordered_date')
    
    # Get invoices for these orders
    invoices = Invoice.objects.filter(
        orders__in=recent_orders
    ).distinct().order_by('-issued_at')
    
    # Get total amount
    total_amount = sum(order.total_price for order in recent_orders)
    
    # Get address and mobile from first order
    address = recent_orders.first().shipping_address if recent_orders.exists() else 'Not Provided'
    mobile = recent_orders.first().mobile if recent_orders.exists() else 'Not Provided'
    payment_method = recent_orders.first().payment_method if recent_orders.exists() else 'cod'
    payment_status = recent_orders.first().payment_status if recent_orders.exists() else 'pending'
    
    context = {
        'orders': recent_orders,
        'invoices': invoices,
        'total_amount': total_amount,
        'shipping_address': address,
        'mobile': mobile,
        'payment_method': payment_method,
        'payment_status': payment_status,
    }
    
    return render(request, 'order_success.html', context)
