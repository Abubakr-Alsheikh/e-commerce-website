import random
import string
from django.utils import timezone
import stripe
from django.shortcuts import render
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from core.models import Item, Order, OrderItem, Address, Payment, Coupon
from .forms import CheckoutForm, RefundForm
from django.views.generic import ListView, DetailView, View
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages

stripe.api_key = settings.STRIPE_SECRET_KEY

class HomeView(ListView):
    model = Item
    template_name = 'core/index.html'
    paginate_by = 12
    context_object_name = 'items'

class MenView(ListView):
    model = Item
    template_name = 'core/men.html'
    paginate_by = 12
    context_object_name = 'items'

    def get_queryset(self):
        return Item.objects.filter(category='M', available=True)

class WomenView(ListView):
    model = Item
    template_name = 'core/women.html'
    paginate_by = 12
    context_object_name = 'items'

    def get_queryset(self):
        return Item.objects.filter(category='W', available=True)
    
class AllProductsView(ListView):
    model = Item
    template_name = 'core/all-products.html'
    paginate_by = 8
    context_object_name = 'items'

class ItemDetailView(DetailView):
    model = Item
    template_name = 'core/product-detail.html'
    context_object_name = 'item'

class CartView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order_items = OrderItem.objects.filter(order__user=self.request.user, order__is_ordered=False)
            # TODO: get the copoun of the order obejct
            order = Order.objects.filter(user=self.request.user, is_ordered=False)
            coupon_code = self.request.GET.get('coupon_code')
            coupon_discount = Coupon.objects.get(code=order.coupon)
            total_withou_discount = sum([item.get_total_cost() for item in order_items])
            total = sum([item.get_final_price() for item in order_items])
            saving = sum([item.get_total_discount() for item in order_items])
            context = {
                'order_items': order_items,
                'total_withou_discount': total_withou_discount,
                'total': total,
                'saving': saving,
                'coupon_code': coupon_code,
                'coupon_discount': coupon_discount,
            }
            return render(self.request, 'core/cart.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "There are no items in your cart.")
            return redirect("core:index")

def apply_coupon(self):
    form = self.POST
    coupon_code = form.get('coupon_code')
    print("test is working")
    try:
        coupon = Coupon.objects.get(code=coupon_code, active=True, valid_from__lte=timezone.now(), valid_to__gte=timezone.now())
        order = Order.objects.get(user=self.user, is_ordered=False)
        order.coupon = coupon
        order.discount = coupon.discount
        order.save()
        messages.success(self, "Successfully applied coupon!")
        return redirect("core:cart")
    except Coupon.DoesNotExist:
        messages.info(self, "This coupon does not exist")
    except Order.DoesNotExist:
        messages.warning(self, "You do not have an active order")
    return redirect("core:cart")



@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, is_ordered=False)
    if order_qs.exists():
        order = order_qs.first()
        order_item_qs = OrderItem.objects.filter(item=item, order=order)
        if order_item_qs.exists():
            order_item = order_item_qs.first()
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was increaced.")
        else:
            order_item = OrderItem.objects.create(item=item, order=order)
            messages.info(request, "This item was add it to your cart.")
    else:
        order = Order.objects.create(user=request.user)
        order_item = OrderItem.objects.create(item=item, order=order, user=request.user)
        order.items.add(order_item.item)  
        messages.info(request, "This item add it to your cart.")

    return redirect("core:product-detail", slug=slug)

@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, is_ordered=False)
    if order_qs.exists():
        order = order_qs.first()
        order_item_qs = OrderItem.objects.filter(item=item, order=order)
        if order_item_qs.exists():
            order_item = order_item_qs.first()
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
                messages.info(request, "This item quantity was decreased.")
            else:
                order_item.delete()
                messages.info(request, "This item was removed from your cart.")
        else:
            messages.warning(request, "This item was not in your cart.")
    else:
        messages.warning(request, "You do not have an active order.")
    return redirect("core:product-detail", slug=slug)

# adding the Remove complete from cart
def remove_completely_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, is_ordered=False)
    if order_qs.exists():
        order = order_qs.first()
        order_item_qs = OrderItem.objects.filter(item=item, order=order)
        if order_item_qs.exists():
            order_item = order_item_qs.first()
            order_item.delete()
            messages.info(request, "This item was removed from your cart.")
        else:
            messages.warning(request, "This item was not in your cart.")
    else:
        messages.warning(request, "You do not have an active order.")
    return redirect("core:cart")

@require_POST
def update_order_item_quantity(request, order_item_id):
    order_item = get_object_or_404(OrderItem, id=order_item_id)
    quantity = request.POST.get('quantity')
    if quantity:
        order_item.quantity = int(quantity)
        order_item.save()
    return redirect('core:cart')

def genterate_random_ref_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=20))

class CheckoutView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        form = CheckoutForm()

        order_items = OrderItem.objects.filter(order__user=self.request.user, order__is_ordered=False)
        default_billing_address = Address.objects.filter(
            user=self.request.user,
            address_type='B',
            default=True
        ).first()

        default_shipping_address = Address.objects.filter(
            user=self.request.user,
            address_type='S',
            default=True
        ).first()

        subtotal = sum([item.get_final_price() for item in order_items])
        shipping = 0.00  # Define your shipping logic here
        order_total = subtotal

        context = {
            'form': form,
            'order_items': order_items,
            'subtotal': f"${subtotal:.2f}",
            'shipping': f"${shipping:.2f}",
            'order_total': f"${order_total:.2f}",
            'default_billing_address': default_billing_address,
            'default_shipping_address': default_shipping_address,
        }
        return render(self.request, 'core/checkout.html', context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, is_ordered=False)
            use_default_billing = 'use_default_billing' in self.request.POST
            use_default_shipping = 'use_default_shipping' in self.request.POST

            # Simplify form field requirement handling
            address_fields = {
                'billing': ['billing_country', 'billing_address', 'billing_zip_code'],
                'shipping': ['shipping_country', 'shipping_address', 'shipping_zip_code']
            }
            for address_type, fields in address_fields.items():
                if self.request.POST.get(f'use_default_{address_type}'):
                    for field in fields:
                        form.fields[field].required = False

            if form.is_valid():
                # Refactor address retrieval or creation into a method
                billing_address = self.get_or_create_address(
                    use_default=use_default_billing,
                    address_type='B',
                    form=form
                )
                shipping_address = self.get_or_create_address(
                    use_default=use_default_shipping,
                    address_type='S',
                    form=form
                )

                # Assign addresses to the order
                order.billing_address = billing_address
                order.shipping_address = shipping_address
                order.save()

                save_info = form.cleaned_data.get('save_info')
                payment_option = form.cleaned_data.get('payment_options')
                order_item = OrderItem.objects.filter(order=order)
                if payment_option == 'S':
                    # Calculate total amount in cents
                    final_price = sum([item.get_final_price() for item in order_item])
                    amount = int(final_price * 100)

                    # try:
                    #     # Create a Stripe charge
                    #     charge = stripe.Charge.create(
                    #         amount=amount,
                    #         currency='usd',
                    #         description='Charge for {}'.format(self.request.user.email),
                    #         source=self.request.POST['stripeToken']
                    #     )
                    # except:
                    #     messages.warning(self.request, "Some problem happend because of the Stripe API key, we are sorry about that.")
                    #     return redirect('core:order-complete')

                    # # Check if the charge was successful
                    # if charge['paid']:
                    #     # Mark the order as paid
                    #     order.is_ordered = True
                    #     order.ref_code = genterate_random_ref_code()
                    #     order.save()

                    #     # Redirect to the order completed page
                    #     return redirect('core:order-complete')
                    # else:
                    #     # Payment was unsuccessful
                    #     messages.warning(self.request, "Your card has been declined.")
                    #     return redirect('core:checkout')
                    
                    order.is_ordered = True
                    order.ref_code = genterate_random_ref_code()
                    order.save()
                    
                    messages.success(self.request, "Your order has been add it successfully.")
                    return redirect('core:order-complete')
                elif payment_option == 'P':
                    # Calculate total amount in cents
                    final_price = sum([item.get_final_price() for item in order_item])
                    amount = int(final_price * 100)
                else:
                    return redirect('core:order-complete')
            messages.warning(self.request, "There was an error with your form. Please try again.")
            print(form.errors)
            return redirect('core:checkout')
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an order")
            return redirect("core:cart")
    
    def get_or_create_address(self, use_default, address_type, form):
        if use_default:
            address = Address.objects.filter(
                user=self.request.user,
                address_type=address_type,
                default=True
            ).first()
            if address:
                return address
            else:
                # Handle the case where there is no default address
                pass  # You can redirect to an error page or show a message
        else:
            # Extract address data from form
            if address_type == 'B':
                address_type = 'billing'
            elif address_type == 'S':
                address_type ='shipping'
            country = form.cleaned_data.get(f'{address_type.lower()}_country')
            address_line = form.cleaned_data.get(f'{address_type.lower()}_address')
            zip_code = form.cleaned_data.get(f'{address_type.lower()}_zip_code')
            set_default = form.cleaned_data.get(f'set_default_{address_type.lower()}')
            if address_type == 'billing':
                address_type = 'B'
            elif address_type == 'shipping':
                address_type ='S'
            # Update existing default address or create a new one
            address, created = Address.objects.update_or_create(
                user=self.request.user,
                address_type=address_type,
                defaults={
                    'country': country,
                    'address': address_line,
                    'zipcode': zip_code,
                    'default': set_default
                }
            )
            return address

def refund_view(request):
    if request.method == 'POST':
        form = RefundForm(request.POST)
        if form.is_valid():
            refund = form.save(commit=False)
            order = get_object_or_404(Order, ref_code=refund.ref_code)
            order.request_refund()
            refund.save()
            # Send an email or notify staff here
            messages.success(request, "Your request has been add it successfully.")
            return redirect('core:index')
    else:
        form = RefundForm()
    return render(request, 'core/refund_request.html', {'form': form})

# Add a new view for handling the payment
class PaymentView(View):
    def get(self, payement_method, *args, **kwargs):
        # Add your logic here for creating Stripe payment intent
        # and passing any necessary information to the frontend
        return render(self.request, 'core/payment.html')

    def post(self, request, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, is_ordered=False)
        token = request.POST.get('stripeToken')
        amount = int(order.get_total() * 100)  # cents

        try:
            charge = stripe.Charge.create(
                amount=amount,  # in cents
                currency='usd',
                source=token,
                description=f'Charge for {request.user.username}'
            )

            # create payment
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()

            # assign the payment to the order
            order.is_ordered = True
            order.payment = payment
            order.save()

            messages.success(self.request, "Your order was successful!")
            return redirect("/")

        except stripe.error.CardError as e:
            messages.error(self.request, "There was a card error.")
        except stripe.error.RateLimitError as e:
            messages.error(self.request, "Too many requests to Stripe.")
        except stripe.error.InvalidRequestError as e:
            messages.error(self.request, "Invalid parameters.")
        except stripe.error.AuthenticationError as e:
            messages.error(self.request, "Authentication with Stripe failed.")
        except stripe.error.APIConnectionError as e:
            messages.error(self.request, "Network communication with Stripe failed.")
        except stripe.error.StripeError as e:
            messages.error(self.request, "Something went wrong. You were not charged. Please try again.")
        except Exception as e:
            messages.error(self.request, "A serious error occurred. We have been notified.")

        return redirect("/")
    
def order_complete(request):
    context ={
    }
    return render(request, 'core/order-complete.html',context)