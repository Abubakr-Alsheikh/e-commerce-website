from django.urls import path
from .views import contact_us, fashion_consultations, home, ProductDetailView, ProductListView, product_care_guides
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

app_name= "home"
urlpatterns = [
    path("", home, name="index"),
    path('about-us/', home, name='about_us'),
    path("products", ProductListView.as_view(), name="products"),
    path('product-detail/<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),
    path("contact-us", contact_us, name="contact_us"),
    path('<slug:slug>/contact-us/', contact_us, name='product_contact_us'),
    path('product-care-guides/', product_care_guides, name='product_care_guides'),
    path('fashion-consultations/', fashion_consultations, name='fashion_consultations'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
