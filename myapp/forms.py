from django import forms
from django.contrib.auth.models import User
from .models import Profile, ProductReview, WishlistItem, Cart, CartItem, Coupon, NewsletterSubscription, RefundRequest

class SellerSignUpForm(forms.Form):
    USER_TYPES = [
        ('customer', 'Customer'),
        ('seller', 'Seller'),
    ]
    
    # 1. Account Identity Fields
    user_type = forms.ChoiceField(
        choices=USER_TYPES, 
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}), 
        initial='customer',
        label="Account Type"
    )
    
    company_name = forms.CharField(
        max_length=200, 
        required=False, 
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter company name (Sellers only)'
        }),
        help_text="Provide your business name if you are registering as a Seller."
    )

    # 2. Basic User Fields (Required for your custom view logic)
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
        help_text="Username must be unique"
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
        help_text="Email must be unique"
    )
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

    def clean_username(self):
        """Validate that username is unique"""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(
                f"Username '{username}' is already taken. Please choose a different username.",
                code='username_exists'
            )
        return username

    def clean_email(self):
        """Validate that email is unique"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                f"Email '{email}' is already registered. Please use a different email or login.",
                code='email_exists'
            )
        return email

    def save(self):
        """
        Creates the User and the Profile in one atomic operation.
        """
        # Create the base user
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password']
        )
        
        # Get data for the profile
        user_type = self.cleaned_data.get('user_type')
        company_name = self.cleaned_data.get('company_name', '')

        # Update the Profile (The signal in models.py creates the empty profile first)
        profile = user.profile
        profile.user_type = user_type
        profile.company_name = company_name
        profile.save()

        # If seller, give admin staff access automatically
        if user_type == 'seller':
            user.is_staff = True
            user.save()
            
        return user

    def signup(self, request, user):
        """
        Kept for AllAuth compatibility (if you use AllAuth signup pages later).
        """
        user_type = self.cleaned_data.get('user_type')
        company_name = self.cleaned_data.get('company_name', '')
        
        user.save()
        
        # Access the profile created by your signal
        profile = user.profile
        profile.user_type = user_type
        profile.company_name = company_name
        profile.save()

        if user_type == 'seller':
            user.is_staff = True
            user.save()


# --- PRODUCT REVIEW FORM ---
class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ['rating', 'title', 'review_text']
        widgets = {
            'rating': forms.RadioSelect(choices=[(i, f'{i} ⭐') for i in range(1, 6)], attrs={
                'class': 'form-check-input'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Review Title',
                'maxlength': '200'
            }),
            'review_text': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write your detailed review...',
                'rows': '5'
            })
        }


# --- CART FORM ---
class AddToCartForm(forms.ModelForm):
    class Meta:
        model = CartItem
        fields = ['quantity']
        widgets = {
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '100',
                'type': 'number'
            })
        }


# --- COUPON FORM ---
class ApplyCouponForm(forms.Form):
    coupon_code = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter coupon code',
            'autocomplete': 'off'
        })
    )

    def clean_coupon_code(self):
        code = self.cleaned_data['coupon_code'].strip().upper()
        if not Coupon.objects.filter(code=code, is_active=True).exists():
            raise forms.ValidationError("Invalid or expired coupon code.")
        return code


# --- NEWSLETTER SUBSCRIPTION FORM ---
class NewsletterForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscription
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email',
                'required': True
            })
        }


# --- REFUND REQUEST FORM ---
class RefundRequestForm(forms.ModelForm):
    class Meta:
        model = RefundRequest
        fields = ['reason', 'description']
        widgets = {
            'reason': forms.Select(attrs={
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '5',
                'placeholder': 'Please describe why you want to return this product...'
            })
        }


# --- PRODUCT SEARCH & FILTER FORM ---
class ProductFilterForm(forms.Form):
    SORT_CHOICES = [
        ('newest', 'Newest'),
        ('price_low', 'Price: Low to High'),
        ('price_high', 'Price: High to Low'),
        ('rating', 'Highest Rated'),
        ('popular', 'Most Popular'),
    ]
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search products...'
        })
    )
    
    category = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple(),
        label="Category"
    )
    
    min_price = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min Price',
            'step': '100'
        })
    )
    
    max_price = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max Price',
            'step': '100'
        })
    )
    
    min_rating = forms.IntegerField(
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }, choices=[
            ('', 'Any Rating'),
            (4, '4⭐ & above'),
            (3, '3⭐ & above'),
            (2, '2⭐ & above'),
            (1, '1⭐ & above'),
        ])
    )
    
    sort_by = forms.CharField(
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }, choices=SORT_CHOICES),
        initial='newest'
    )
    
    in_stock_only = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label="In Stock Only"
    )
