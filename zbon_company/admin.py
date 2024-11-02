from django.contrib import admin

from zbon_company.models import Category, Product

# Register your models here.
admin.site.register(Product)
admin.site.register(Category)