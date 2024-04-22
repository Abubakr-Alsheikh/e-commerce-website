from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from .models import Refund, Address, Review
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

# class CheckoutForm(forms.Form):
#     # Billing Address Fields
#     billing_country = CountryField(blank_label='(select country)').formfield(
#         widget=CountrySelectWidget(attrs={
#             'class': 'form-control',
#             'placeholder': 'Select Country'
#         }),
#         label='Billing Country'
#     )
#     billing_address = forms.CharField(
#         widget=forms.TextInput(attrs={
#             'placeholder': 'Enter Your Billing Address'
#         }),
#         label='Billing Address',
#         required=True
#     )
#     billing_zip_code = forms.CharField(
#         widget=forms.TextInput(attrs={
#             'placeholder': 'Billing Zip / Postal'
#         }),
#         label='Billing Zip/Postal Code',
#         required=True
#     )

#     # Shipping Address Fields
#     shipping_country = CountryField(blank_label='(select country)').formfield(
#         widget=CountrySelectWidget(attrs={
#             'class': 'form-control',
#             'placeholder': 'Select Country'
#         }),
#         label='Shipping Country'
#     )
#     shipping_address = forms.CharField(
#         widget=forms.TextInput(attrs={
#             'placeholder': 'Enter Your Shipping Address'
#         }),
#         label='Shipping Address',
#         required=True
#     )
#     shipping_zip_code = forms.CharField(
#         widget=forms.TextInput(attrs={
#             'placeholder': 'Shipping Zip / Postal'
#         }),
#         label='Shipping Zip/Postal Code',
#         required=True
#     )

#     # Check settings
#     set_default_billing = forms.BooleanField(
#         widget=forms.CheckboxInput(),
#         label='Set as default billing address',
#         required=False
#     )
#     set_default_shipping = forms.BooleanField(
#         widget=forms.CheckboxInput(),
#         label='Set as default shipping address',
#         required=False
#     )

#     saved_billing_address = forms.ModelChoiceField(
#         Address.objects.none(),
#         widget=forms.RadioSelect(),
#         required=False,
#         empty_label=None
#     )
#     saved_shipping_address = forms.ModelChoiceField(
#         Address.objects.none(),
#         widget=forms.RadioSelect(),
#         required=False,
#         empty_label=None
#     )

#     save_info = forms.BooleanField(
#         widget=forms.CheckboxInput(attrs={
#             'class': 'form-check-input'
#         }),
#         label='Save info for another payment',
#         required=False
#     )
#     payment_options = forms.ChoiceField(
#         choices=(
#             ('P', 'Paypal'),
#             ('S', 'Stripe'),
#         ),
#         widget=forms.RadioSelect()
#     )


class CheckoutForm(forms.Form):
    # Billing Address Fields
    billing_country = CountryField(blank_label='(select country)').formfield(
        widget=CountrySelectWidget(attrs={
            'class': 'form-control',
            'id': 'id_billing_country',
            'placeholder': 'Select Country'
        }),
        label='Billing Country'
    )
    billing_address = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'id_billing_address',
            'placeholder': 'Enter Your Billing Address'
        }),
        label='Billing Address',
        required=True
    )
    billing_zip_code = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'id_billing_zip_code',
            'placeholder': 'Billing Zip / Postal'
        }),
        label='Billing Zip/Postal Code',
        required=True
    )

    # Shipping Address Fields
    shipping_country = CountryField(blank_label='(select country)').formfield(
        widget=CountrySelectWidget(attrs={
            'class': 'form-control',
            'id': 'id_shipping_country',
            'placeholder': 'Select Country'
        }),
        label='Shipping Country'
    )
    shipping_address = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'id_shipping_address',
            'placeholder': 'Enter Your Shipping Address'
        }),
        label='Shipping Address',
        required=True
    )
    shipping_zip_code = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'id_shipping_zip_code',
            'placeholder': 'Shipping Zip / Postal'
        }),
        label='Shipping Zip/Postal Code',
        required=True
    )

    # Check settings
    set_default_billing = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'id_set_default_billing'
        }),
        label='Set as default billing address',
        required=False
    )
    set_default_shipping = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'id_set_default_shipping'
        }),
        label='Set as default shipping address',
        required=False
    )

    use_default_billing = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'id_use_default_billing'
        }),
        label='Use default billing address',
        required=False
    )

    use_default_shipping = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'id_use_default_shipping'
        }),
        label='Use default shipping address',
        required=False
    )

    save_info = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'id_save_info'
        }),
        label='Save info for another payment',
        required=False
    )
    payment_options = forms.ChoiceField(
        choices=(
            ('P', 'Paypal'),
            ('S', 'Stripe'),
        ),
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input',
            'id': 'id_payment_options'
        })
    )

    # # Override the clean method to make certain fields optional
    # def clean(self):
    #     cleaned_data = super().clean()
    #     use_default_billing = cleaned_data.get('use_default_billing')
    #     use_default_shipping = cleaned_data.get('use_default_shipping')

    #     if not use_default_billing:
    #         if not cleaned_data.get('billing_country'):
    #             self.add_error('billing_country', 'This field is required.')
    #         if not cleaned_data.get('billing_address'):
    #             self.add_error('billing_address', 'This field is required.')
    #         if not cleaned_data.get('billing_zip_code'):
    #             self.add_error('billing_zip_code', 'This field is required.')

    #     if not use_default_shipping:
    #         if not cleaned_data.get('shipping_country'):
    #             self.add_error('shipping_country', 'This field is required.')
    #         if not cleaned_data.get('shipping_address'):
    #             self.add_error('shipping_address', 'This field is required.')
    #         if not cleaned_data.get('shipping_zip_code'):
    #             self.add_error('shipping_zip_code', 'This field is required.')

    #     return cleaned_data


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']

    def __init__(self, *args, **kwargs):
        super(ReviewForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Submit Review'))

class RefundForm(forms.ModelForm):
    class Meta:
        model = Refund
        fields = ['ref_code', 'email', 'reason']