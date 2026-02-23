from .forms import SellerSignUpForm

def signup_form_context(request):
    return {
        'signup_form': SellerSignUpForm()
    }