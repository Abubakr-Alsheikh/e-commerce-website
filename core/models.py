from django.db import models
from django.conf import settings
from django.urls import reverse
from django_countries.fields import CountryField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify

CATEGORY_CHOICES = (
    ('M', 'Men'),
    ('W', 'Women')
)

LABEL_CHOICES = (
    ('P', 'primary'),
    ('S', 'secondary'),
    ('D', 'danger')
)

ADDRESS_CHOESIES=(
    ('B','Billing'),
    ('S','Shipping')
)

class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    description = models.TextField()
    available = models.BooleanField(default=True)
    category = models.CharField(max_length=1, choices=CATEGORY_CHOICES)
    label = models.CharField(max_length=1, choices=LABEL_CHOICES, null=True, blank=True)
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(upload_to='item_images/', null=True, blank=True)

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        original_slug = self.slug
        count = 1
        while Item.objects.filter(slug=self.slug).exists():
            self.slug = original_slug + '-' + str(count)
            count += 1
        super().save(*args, **kwargs)

    
    def get_absolute_url(self):
        return reverse("core:product-detail",kwargs={
            'slug':self.slug
        })
    
    def get_add_to_cart_url(self):
        return reverse("core:add-to-cart",kwargs={
            'slug':self.slug
        })
    
    def get_remove_from_cart_url(self):
        return reverse("core:remove-from-cart",kwargs={
            'slug':self.slug
        })
    
    def get_remove_completely_from_cart_url(self):
        return reverse("core:remove-completely-from-cart",kwargs={
            'slug':self.slug
        })
    
    def is_in_user_cart(self, user):
        """
        Check if the item is in the user's cart.
        Returns True if the item is in the cart, False otherwise.
        """
        # Check if there is an order that is not ordered yet (is in the cart)
        # and contains the item
        if user.is_authenticated:
            return Order.objects.filter(user=user, is_ordered=False, items=self).exists()
        else:
            # If the user is not authenticated, return False
            return False
    
class Review(models.Model):
    item = models.ForeignKey('Item', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(max_length=500)  # Assuming a max length of 500 for comments
    date_added = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return f"Review by {self.user} for {self.item}"

    class Meta:
        ordering = ['-date_added']
    
class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    item = models.ForeignKey('Item', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    is_ordered = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.quantity} of {self.item.title} ordered by {self.user}"
    
    def get_total_cost(self):
        return self.quantity * self.item.price
    
    def get_discount_total_cost(self):
        if self.item.discount_price:
            return self.quantity * self.item.discount_price
        return 0
    
    def get_total_discount(self):
        if self.item.discount_price:
            return self.quantity * (self.item.price - self.item.discount_price)
        return 0
    
    def get_total_saving(self):
        return self.get_total_cost() - self.get_discount_total_cost()
    
    def get_discount_from_coupon(self):
        return self.order.coupon.discount if self.order.coupon else 0
    
    def get_final_price(self):
        if self.item.discount_price:
            return self.get_discount_total_cost()
        return self.get_total_cost()
    
    
class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    ref_code = models.CharField(max_length=20, blank=True, null=True)
    items = models.ManyToManyField('Item', through='OrderItem', related_name='ordered_items')
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField(auto_now=True)
    is_ordered = models.BooleanField(default=False)
    billing_address = models.ForeignKey('Address', related_name='billing_address', on_delete=models.SET_NULL, null=True, blank=True)
    shipping_address = models.ForeignKey('Address', related_name='shipping_address', on_delete=models.SET_NULL, null=True, blank=True)
    coupon = models.ForeignKey('Coupon', on_delete=models.SET_NULL, null=True, blank=True)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)

    def __str__(self):
        return f"Order by {self.user.username} and the ref code is {self.ref_code}"
    
    def request_refund(self):
        self.refund_requested = True
        self.save()

class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    country = CountryField(multiple=False)
    address = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=100)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOESIES)
    default = models.BooleanField(default=False)

    def __str__(self):
        return f"Address of {self.user.username} where his address is ({self.address})"
    
    class Meta:
        verbose_name_plural = 'Addresses'

class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    stripe_charge_id = models.CharField(max_length=50)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
    
class Coupon(models.Model):
    code = models.CharField(max_length=15, unique=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    discount = models.IntegerField(help_text="Percentage discount")
    active = models.BooleanField()

    def __str__(self):
        return self.code
    
class Refund(models.Model):
    ref_code = models.CharField(max_length=50)
    reason = models.TextField()
    email = models.EmailField()
    accepted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.email} - Refund Requested for Order {self.ref_code}"