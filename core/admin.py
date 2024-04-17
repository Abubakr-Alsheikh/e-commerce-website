from django.contrib import admin
from .models import Item, Order, OrderItem, Coupon, Address, Payment, Refund

# Register your models here.
admin.site.register(Item)

class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'ref_code', 'is_ordered', 'being_delivered', 'received', 'refund_requested', 'refund_granted')
    list_display_links = ('user', 'ref_code')
    list_filter = ('is_ordered', 'being_delivered', 'received', 'refund_requested', 'refund_granted')
    search_fields = ('user__username', 'ref_code')

    actions = ['grant_refund']

    def grant_refund(self, request, queryset):
        queryset.update(refund_requested=False, refund_granted=True)

    grant_refund.short_description = "Mark selected orders as refund granted"

    def get_items(self, obj):
        # Custom method to display items associated with the order
        return ", ".join([item.title for item in obj.items.all()])

    get_items.short_description = 'Items'  # Custom column name

class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'country', 'address', 'zipcode', 'address_type', 'default']
    list_filter = ['country', 'default', 'address_type']
    search_fields = ['user__username', 'address', 'zipcode']

admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem) # Register models to make them available in the Django admin interface
admin.site.register(Coupon)
admin.site.register(Address, AddressAdmin)
admin.site.register(Payment)
admin.site.register(Refund)

