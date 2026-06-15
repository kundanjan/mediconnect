# billing/forms.py
from django import forms
from django.core.validators import RegexValidator
from .models import Billing, AccountantProfile
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Insurance

phone_validator = RegexValidator(
    regex=r'^\d{10}$',
    message='Phone number must be exactly 10 digits.'
)

class AccountantUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']
        
class BillingForm(forms.ModelForm):
    class Meta:
        model = Billing
        fields = [
            'doctor', 'clinic', 'billing_type', 'content_type', 'object_id',
            'total_amount', 'payment_method', 'paid_by','patient'
        ]


class AccountantProfileForm(forms.ModelForm):
    phone = forms.CharField(
        max_length=10,
        validators=[phone_validator],
        widget=forms.TextInput(attrs={'placeholder': '10-digit mobile number', 'maxlength': '10'})
    )
    
    class Meta:
        model = AccountantProfile
        fields = [
            'phone',
            'email',
            'address',
            'department',
            'profile_pic'
        ]

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone.isdigit():
            raise forms.ValidationError('Phone number must contain only digits.')
        if len(phone) != 10:
            raise forms.ValidationError('Phone number must be exactly 10 digits.')
        return phone

class BillUpdateForm(forms.ModelForm):
    # We define the insurance_claim field here to control its queryset
    insurance_claim = forms.ModelChoiceField(
        queryset=Insurance.objects.none(), # Start with an empty queryset
        required=False # It's not always required
    )

    class Meta:
        model = Billing
        # These are the fields the accountant can edit
        fields = ['paid_by', 'insurance_claim', 'payment_method', 'paid']
        widgets = {
            'paid_by': forms.Select(attrs={'class': 'form-control'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'paid': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    # This is the magic part that filters the dropdown
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If the form is for an existing bill (instance is passed)
        if self.instance and self.instance.pk:
            # Filter the insurance_claim dropdown to only show approved policies for this bill's patient
            patient_user = self.instance.patient
            self.fields['insurance_claim'].queryset = Insurance.objects.filter(
                patient__patient=patient_user, 
            )