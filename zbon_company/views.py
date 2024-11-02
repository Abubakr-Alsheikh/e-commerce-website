from django.shortcuts import get_object_or_404, redirect, render

from django.views.generic import ListView, DetailView
from .forms import ContactForm
from .models import Category, Product
from django.contrib import messages


def home(request):
    """
    Displays the homepage.
    """
    featured_products = Product.objects.filter(
        is_featured=True, is_active=True
    ).order_by("-created_at")[:6]
    context = {
        "featured_products": featured_products,
    }
    return render(request, "zbon_company/home/index.html", context)


class ProductListView(ListView):
    model = Product
    template_name = "zbon_company/home/products.html"
    context_object_name = "products"
    paginate_by = 16  # Display 16 products per page

    def get_queryset(self):
        return Product.objects.filter(is_active=True).order_by("-created_at")


class ProductDetailView(DetailView):
    model = Product
    template_name = "zbon_company/home/product_detail.html"
    context_object_name = "product"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['show_modal'] = len(messages.get_messages(self.request)) > 0
        return context

def contact_us(request, slug=None):
    """
    Handles both general and product-specific contact forms.
    """
    product = None
    print(slug)
    if slug:
        product = get_object_or_404(Product, slug=slug)  # Use get_object_or_404 for better error handling

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)  # Don't save yet
            if product:
                contact.product = product # associate the contact with product
            contact.save() # Now save 
            messages.success(request, 'تم إرسال رسالتك بنجاح!')
            if product:
                return redirect('home:product_detail', slug=product.slug)
            else:
                return redirect('home:contact_us')  # Redirect to the general contact page
    else:
        form = ContactForm()

    context = {'form': form, 'show_modal': len(messages.get_messages(request)) > 0 }  # Check for existing messages from GET request
    if product:
        context['product'] = product

    return render(request, 'zbon_company/home/contact_us.html', context)

def product_care_guides(request):
    return render(request, "zbon_company/home/product_care_guides.html")


def fashion_consultations(request):
    return render(request, "zbon_company/home/fashion_consultations.html")
