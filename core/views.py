import json
import random
import string
from django.http import HttpResponseRedirect, JsonResponse
from django.utils import timezone
import stripe
from django.shortcuts import render
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from core.models import Item, Order, OrderItem, Address, Payment, Coupon
from .forms import CheckoutForm, RefundForm, ReviewForm
from django.views.generic import ListView, DetailView, View
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.db.models import Avg, Count, Case, When, Q, Value
from django.core.paginator import Paginator
# Generative AI
import google.generativeai as genai
from django.views.decorators.csrf import csrf_exempt

stripe.api_key = settings.STRIPE_SECRET_KEY

class HomeView(ListView):
    model = Item
    template_name = 'core/index.html'
    paginate_by = 8
    context_object_name = 'items'

    def get_queryset(self):
        return Item.objects.filter(Q(label='P') | Q(label='D')).order_by(
            Case(
                When(label='P', then=Value(0)),  # Best sellers first (label 'P')
                default=Value(1)                 # Then big discount (label 'D')
            )
        )

def search_items(request):
    if 'q' in request.GET:
        query = request.GET.get('q')
        items = Item.objects.filter(title__icontains=query, available=True)
        results = [{'name': item.title, 'url': item.get_absolute_url()} for item in items]
        return JsonResponse({'results': results})
    return JsonResponse({'results': []})

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

class SearchResultsView(ListView):
    model = Item
    template_name = 'core/search-results.html'
    paginate_by = 8
    context_object_name = 'items'

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if query:
            return Item.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query),
                available=True
            ).distinct()
        return Item.objects.none()  # Return an empty queryset if no query

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context

class ItemDetailView(DetailView):
    model = Item
    template_name = 'core/product-detail.html'
    context_object_name = 'item'
    # paginate_by = 3  # Set the number of items per page

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['review_form'] = ReviewForm()
        context['is_in_cart'] = self.object.is_in_user_cart(self.request.user)

        # Calculate the average rating and the number of reviews
        reviews = self.object.review_set.all().aggregate(
            average_rating=Avg('rating'),
            number_of_reviews=Count('id')
        )

        # Set default values if reviews are None
        context['average_rating'] = reviews['average_rating'] or 0
        context['number_of_reviews'] = reviews['number_of_reviews'] or 0

        # Calculate the number of full, half, and empty stars
        full_stars = int(context['average_rating'])
        half_star = context['average_rating'] - full_stars >= 0.5
        empty_stars = 5 - full_stars - int(half_star)

        # Add the star counts to the context
        context['full_stars'] = full_stars
        context['half_star'] = half_star
        context['empty_stars'] = empty_stars

        # Get the count of reviews for each star rating
        star_counts = {
            '5_stars': self.object.review_set.filter(rating=5).count(),
            '4_stars': self.object.review_set.filter(rating=4).count(),
            '3_stars': self.object.review_set.filter(rating=3).count(),
            '2_stars': self.object.review_set.filter(rating=2).count(),
            '1_star': self.object.review_set.filter(rating=1).count(),
        }

        # Calculate the percentage of each star rating
        total_reviews = context['number_of_reviews']
        for star, count in star_counts.items():
            percentage = (count / total_reviews * 100) if total_reviews > 0 else 0
            context[star + '_percentage'] = f"{percentage:.0f}%"

        # Add the star counts and percentages to the context
        context.update(star_counts)

        # Get all reviews and paginate them
        reviews = self.object.review_set.all()
        paginator = Paginator(reviews, 5)  # Show 5 reviews per page
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.item = self.object
            review.user = request.user
            review.save()
            messages.success(request, "Review added successfully!")
            return HttpResponseRedirect(self.object.get_absolute_url())
        messages.warning(request, "Something went wrong! please try again.")
        return self.render_to_response(self.get_context_data(form=form))

@login_required
def add_review(request, item_id):
    item = Item.objects.get(pk=item_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.item = item
            review.user = request.user
            review.save()
            return redirect('item_detail', item_id=item.id)
    else:
        form = ReviewForm()
    return render(request, 'add_review.html', {'form': form, 'item': item})

class CartView(LoginRequiredMixin, View):# view.py
    def get(self, *args, **kwargs):
        try:
            order_items = OrderItem.objects.filter(order__user=self.request.user, order__is_ordered=False)
            order = Order.objects.filter(user=self.request.user, is_ordered=False).first()
            coupon_code = self.request.GET.get('coupon_code')

            if order and order.coupon:
                coupon_discount_percentage = order.coupon.discount
            else:
                coupon_discount_percentage = 0

            subtotal = sum([item.get_total_cost() for item in order_items])
            saving = sum([item.get_total_discount() for item in order_items])
            shipping = 0
            subtotal_after_saving = subtotal - saving
            coupon_discount = (subtotal_after_saving * coupon_discount_percentage) / 100
            total = subtotal_after_saving - coupon_discount

            context = {
                'order_items': order_items,
                'subtotal': subtotal,
                'saving': saving,
                'coupon_discount': coupon_discount,
                'total': total,
                'coupon_code': coupon_code,
                'coupon_discount_percentage': coupon_discount_percentage,
                'shipping': shipping
            }
            return render(self.request, 'core/cart.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You have no items in your cart.")
            return redirect("core:index")


class OrderListView(ListView):
    model = Order
    template_name = 'core/order-list.html'
    context_object_name = 'user_orders'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-ordered_date')

def apply_coupon(self):
    form = self.POST
    coupon_code = form.get('coupon_code')
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
@require_POST
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)

    data = json.loads(request.body)
    quantity = data.get('quantity')
    quantity = int(quantity) if quantity.isdigit() else 1
    order_qs = Order.objects.filter(user=request.user, is_ordered=False)

    if order_qs.exists():
        order = order_qs.first()
        order_item_qs = OrderItem.objects.filter(item=item, order=order)

        if order_item_qs.exists():
            order_item = order_item_qs.first()
            order_item.quantity += quantity  # Increment by the specified quantity
            order_item.save()
            messages.info(request, "The quantity of this item was increased.")
        else:
            order_item = OrderItem.objects.create(item=item, order=order, quantity=quantity)
            messages.info(request, f"This item was added to your cart with quantity of {quantity}.")
    else:
        order = Order.objects.create(user=request.user)
        order_item = OrderItem.objects.create(item=item, order=order, quantity=quantity)
        order.items.add(order_item)

    return JsonResponse({'status': 'success', 'message': 'Item quantity updated.', 'quantity':quantity})

@login_required
def remove_from_cart(request, slug):
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
    return redirect("core:product-detail", slug=slug)

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
        try:
            order = Order.objects.get(user=self.request.user, is_ordered=False)
            order_items = OrderItem.objects.filter(order__user=self.request.user, order__is_ordered=False)

            # Check if there are any items in the order
            if not order_items.exists():
                messages.warning(self.request, "Your cart is empty. Please add items before proceeding to checkout.")
                return redirect("core:cart")  # Redirect to cart if no items

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

            # Add the logic for savings and coupon discount
            if order.coupon:
                coupon_discount_percentage = order.coupon.discount
            else:
                coupon_discount_percentage = 0

            subtotal = sum([item.get_total_cost() for item in order_items])
            saving = sum([item.get_total_discount() for item in order_items])
            shipping = 0
            subtotal_after_saving = subtotal - saving
            coupon_discount = (subtotal_after_saving * coupon_discount_percentage) / 100
            order_total = subtotal_after_saving - coupon_discount

            subtotal = sum([item.get_final_price() for item in order_items])

            context = {
                'form': form,
                'order_items': order_items,
                'subtotal': f"${subtotal:.2f}",
                'saving': f"${saving:.2f}",
                'coupon_discount': coupon_discount,
                'coupon_discount_percentage': coupon_discount_percentage,
                'shipping': f"${shipping:.2f}",
                'order_total': f"${order_total:.2f}",
                'default_billing_address': default_billing_address,
                'default_shipping_address': default_shipping_address,
            }
            return render(self.request, 'core/checkout.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("core:cart")

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
            try:
                order = Order.objects.get(ref_code=refund.ref_code)
                order.request_refund()  # Assuming you have this method defined
                refund.save()
                messages.success(request, "Your request has been added successfully.")
            except ObjectDoesNotExist:
                messages.warning(request, "Invalid reference code. Please try again.")
            except Exception as e:
                messages.warning(request, "An unexpected error occurred. Please try again later.")
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

# Generative AI
@csrf_exempt
def chatRespone(request):

    print(request)
    if request.method == 'POST':
        if not request.body:
            return JsonResponse({'error': 'Empty request'}, status=400)
        # Configure the model with your API key
        genai.configure(api_key="")

        # Set up the model and safety settings
        generation_config = {
            "temperature": 0.9,
            "top_p": 1,
            "top_k": 0,
            "max_output_tokens": 2048,
        }

        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
        ]

        model = genai.GenerativeModel(model_name="gemini-1.0-pro",
                                      generation_config=generation_config,
                                      safety_settings=safety_settings)

        # Parse the request body
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)


        user_message = data['message']
        user_chat = data['userchat']

        chatHistory = [
          {
             "role": "user",
             "parts": [
              "Hi there! I'm providing you with some information about myself so you can effectively roleplay as me. My name is Abubakr Alsheikh, and I'm a passionate web designer and developer originally from Syria. I started my journey in the tech world with a degree in Software Engineering, and I'm currently expanding my knowledge by pursuing a degree in Information Technology Engineering and also getting a Bachelor's degree in Software Enginnering. I love creating websites that are not only visually appealing but also highly functional and user-friendly.  My ultimate goal is to use my skills to make a positive impact on the world through meaningful projects. I believe technology has the power to change the world, and I'm excited to be a part of that change."
             ]
            },
            {
             "role": "model",
             "parts": [
              "It's a pleasure to meet you, Abubakr! I'm ready to step into your shoes and engage in conversations as a web developer and designer with your unique background and aspirations."
             ]
            },
            {
             "role": "user",
             "parts": [
              "About me: About me:I am Abubakr Alsheikh, a web designer and developer from Syria. I have a degree in Software Engineering and I am studying Information Technology Engineering. I have also taken many online courses on Coursera to learn web design and development skills.I love creating websites that are beautiful, fast, and easy to use. I use various tools and languages to build websites, such as HTML, CSS, JavaScript, PHP, Django, and ASP.NET. I also use databases like MySQL, SQL Server, and SQLite to store and manage data.I am always curious and eager to learn new things and work on new projects. I enjoy solving problems and challenges with design thinking and coding. I also like to work with others and share ideas and knowledge.My dream is to use my skills to make a positive impact on the world. I want to work on projects that are not only professionally rewarding, but also socially meaningful. I believe that technology can change the world, and I want to be part of that change.Thank you for taking the time to learn more about me. I look forward to creating amazing websites with you.Contact me:You can contact me by email at AbubakrAlsheikh@outlook.com or by phone at +963980235562. You can also send me a message on my website at https://abubakr-alsheikh.github.io/my-portfolio/. There is a contact section on the website where you can fill out a form and I will reply to you as soon as possible.Education:- Syrian Virtual University: Bachelor's degree in Information Technology Engineering (Oct 2021 – 2026)- Aleppo University: Technical diploma in Software Engineering (Sep 2021 – Jun 2023), 1st graduate, Grade: 90.63%Licenses and certifications:- Top licenses and certifications:    - Web Design for Everyone: the basis of web development and coding (University of Michigan | Coursera)    - Web Applications for Everybody (University of Michigan | Coursera)    - Python for Everybody (University of Michigan | Coursera)    - Django for Everybody Specialization (University of Michigan | Coursera)    - Meta Front-End Developer Professional Certificate (Meta | Coursera)- Other licenses and certifications:    - Introduction to HTML5 (University of Michigan | Coursera)    - Introduction to CSS3 (University of Michigan | Coursera)    - Introduction to Structured Query Language (SQL) (University of Michigan | Coursera)    - Building Web Applications in PHP (University of Michigan | Coursera)    - Advanced Styling with Responsive Design (University of Michigan | Coursera)    - Interactivity with JavaScript (University of Michigan | Coursera)    - JavaScript, jQuery, and JSON (University of Michigan | Coursera)    - Web Design for Everybody Capstone (University of Michigan | Coursera)    - Building Database Applications in PHP (University of Michigan | Coursera)    - Programming for Everybody (Getting Started with Python) (University of Michigan | Coursera)    - Python Data Structures (University of Michigan | Coursera)    - Django Features and Libraries (University of Michigan | Coursera)    - Using JavaScript and JSON in Django (University of Michigan | Coursera)    - Using Databases with Python (University of Michigan | Coursera)    - Building Web Applications in Django (University of Michigan | Coursera)    - Web Application Technologies and Django (University of Michigan | Coursera)    - Introduction to Front-End Development (Meta)To see any new ones, you can check the latest certificates section on my website.Skills:- Front End: HTML, CSS, JavaScript, Bootstrap, React, Vue- Back End: PHP, Django, Asp.net, Node.js- Data Bases: MySQL, SQL Server, SQLite- Design tools: Figma, Photoshop- Programming languages: C#, Python- Other: AI Tools, Microsoft Office, UnityTop Projects:- Dynamic Website and Control Panel Development for Sama Media (Graduation Project):    - Associated with Aleppo University    - I designed and developed a dynamic website and a control panel for Sama Media, a graphic design and advertising company.    - The website showcases the company’s portfolio, clients, and team, and has a contact form for visitors. The website is responsive, social media integrated, and built with HTML, CSS, JavaScript, and PHP.    - The control panel is a content management system that allows the company to add, modify, or remove content related to projects, clients, team, and messages. The control panel uses a MySQL database for data storage and retrieval.- Online Book Inventory System:    - Associated with Syrian Virtual University    - I developed an online book inventory system as part of my university assignment. It is built with ASP.NET and demonstrates various web development skills and features.    - The project allows users to browse, search, and manage books online. Users can view detailed information about each book, and create their own reading list by adding or removing books. The project supports user authentication and authorization, and has an admin page for CRUD operations on the books database.    - The project is responsive, user-friendly, and uses a search bar to find books by title. The project uses HTML, CSS, JavaScript, and ASP.NET for the front end, and SQL Server for the back end."
             ]
            },
            {
             "role": "model",
             "parts": [
              "Thanks for sharing, Abubakr! It's impressive to see your dedication and passion for web development. I'm excited to learn more about your work and answer any questions people might have about your expertise."
             ]
            },
            {
             "role": "user",
             "parts": [
              "Let's keep our conversation flowing like a typical chat. Short and sweet answers will do the trick!"
             ]
            },
            {
             "role": "model",
             "parts": [
              "Got it! Short and to the point – I can handle that."
             ]
            },
            {
             "role": "user",
             "parts": [
              "Let's keep the conversation casual and natural, just like a regular chat between two people.  No need to be overly formal."
             ]
            },
            {
             "role": "model",
             "parts": [
              "Sounds good! I'll do my best to chat like a real person and avoid sounding too robotic.  Of course, if I encounter something beyond my knowledge, I might need to admit my limitations."
             ]
            },
            {
             "role": "user",
             "parts": [
              "If someone messages in a language other than English, politely let them know it would be easier to communicate in English.  However, still try your best to understand their questions and respond in their language using the information I provided about myself."
             ]
            },
            {
             "role": "model",
             "parts": [
              "Understood. I'll politely suggest using English for ease of communication, but I'll do my best to understand and respond in their language based on the information you've shared about yourself and your expertise."
             ]
            },
            {
              "role":"user",
              "parts":["if the user said greeting or any way of greeting tell them \"Hi, my name is Abubakr, I am web developer and designer. What do you want to ask me\" or similar to it not exactly like it"],
            },
            {
             "role": "model",
             "parts": [
              "Hey there! Abubakr here, web developer and designer. What brings you here today?",
              "Hi! I'm Abubakr, a web developer with a passion for design. How can I help you?",
              "Greetings! I'm Abubakr, and I build beautiful and functional websites. What would you like to know?",
              "Hello! My name is Abubakr. I'm a web developer and designer always happy to chat. What's on your mind?"
             ]
            },
            {
             "role": "user",
             "parts": [
              "Are you currently involved in any exciting projects or job searches?"
             ]
            },
            {
             "role": "model",
             "parts": [
              "I'm actively seeking new projects and opportunities where I can utilize my web development skills and contribute to something impactful. I'm open to freelance work, collaborations, and full-time positions that align with my passion for creating beautiful and functional websites."
             ]
            },
            {
             "role": "user",
             "parts": [
              "What kind of projects are you currently involved in?"
             ]
            },
            {
             "role": "model",
             "parts": [
              "Currently, I'm between projects, but I'm always on the lookout for exciting opportunities where I can apply my web development skills and contribute to something meaningful."
             ]
            },

        ];

        combined_history = chatHistory + user_chat

        # Start the conversation and send the user message
        convo = model.start_chat(history=combined_history)
        convo.send_message(user_message)

        # Get the model response
        response = convo.last.text

        # Create the JsonResponse object
        response_data = JsonResponse({'response': response})

        # Add CORS headers to the response
        response_data["Access-Control-Allow-Origin"] = "*"
        response_data["Access-Control-Allow-Methods"] = "POST"
        # response_data["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
        # response_data["Access-Control-Max-Age"] = "3600"
        response_data["Access-Control-Allow-Headers"] = "Content-Type, X-CSRFToken"

        return response_data
    else:
        return JsonResponse({'error': 'You are not using post request'}, status=400)