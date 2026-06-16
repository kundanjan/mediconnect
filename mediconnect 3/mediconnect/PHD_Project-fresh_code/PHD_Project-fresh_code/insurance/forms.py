
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Insurance, InsuranceProfile
from billing.models import Billing

# User registration form
class InsuranceRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

# # Insurance company profile form
# class InsuranceProfileForm(forms.ModelForm):
#     class Meta:
#         model = InsuranceProfile
#         fields = ['company_name', 'contact_number', 'address']


# Insurance policy form

class InsuranceProfileForm(forms.ModelForm):
    class Meta:
        model = InsuranceProfile
        fields = ['company_name', 'phone', 'email', 'address', 'department', 'profile_pic']


class InsuranceProviderCreateForm(forms.ModelForm):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

    class Meta:
        model = InsuranceProfile
        fields = ['company_name', 'phone', 'email', 'address', 'department', 'profile_pic']
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company Name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Address', 'rows': 3}),
            'department': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Department'}),
            'profile_pic': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Username already taken.')
        return username

class InsurancePolicyForm(forms.ModelForm):
    class Meta:
        model = Insurance
        fields = ['patient', 'insurance_provider', 'policy_number', 'policy_type',
                  'valid_from', 'valid_to', 'coverage_amount', 'policy_document', 'doctor']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-control'}),
            'insurance_provider': forms.Select(attrs={'class': 'form-control'}),
            'policy_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. POL-2024-001'}),
            'policy_type': forms.Select(attrs={'class': 'form-control'}),
            'valid_from': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'valid_to': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'coverage_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'policy_document': forms.FileInput(attrs={'class': 'form-control'}),
            'doctor': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'patient': 'Patient',
            'insurance_provider': 'Insurance Provider',
            'policy_number': 'Policy Number',
            'policy_type': 'Policy Type',
            'valid_from': 'Valid From',
            'valid_to': 'Valid To',
            'coverage_amount': 'Coverage Amount (₹)',
            'policy_document': 'Policy Document',
            'doctor': 'Doctor (optional)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['doctor'].required = False
        self.fields['policy_document'].required = False
        from doctor.models import DoctorProfile
        self.fields['doctor'].queryset = DoctorProfile.objects.all()

class ClaimBillForm(forms.ModelForm):
    class Meta:
        model = Billing
        fields = ['billing_type', 'total_amount', 'doctor']
        widgets = {
            'billing_type': forms.Select(attrs={'class': 'form-control'}),
            'total_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Enter amount'
            }),
            'doctor': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'billing_type': 'Bill Type',
            'total_amount': 'Amount (₹)',
            'doctor': 'Doctor (optional)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['doctor'].required = False
        from doctor.models import DoctorProfile
        self.fields['doctor'].queryset = DoctorProfile.objects.all()

# class InsuranceForm(forms.ModelForm):
#     class Meta:
#         model = Insurance
#         fields = [
#             'insurance_status',
#             'insurance_provider',
#             'policy_number',
#             'policy_type',
#             'valid_from',
#             'valid_to',
#             'coverage_amount',
#             'is_active',
#             'policy_document',
#         ]

#         widgets = {
#             'valid_from': forms.DateInput(attrs={'type': 'date'}),
#             'valid_to': forms.DateInput(attrs={'type': 'date'}),
#         }

#         labels = {
#             'insurance_status': 'Insurance Status',
#             'insurance_provider': 'Provider Name',
#             'policy_number': 'Policy Number',
#             'policy_type': 'Policy Type',
#             'valid_from': 'Valid From',
#             'valid_to': 'Valid To',
#             'coverage_amount': 'Coverage Amount (INR)',
#             'is_active': 'Is Active?',
#             'policy_document': 'Upload Policy Document',
#         }

#     def __init__(self, *args, **kwargs):
#         super(InsuranceForm, self).__init__(*args, **kwargs)
#         for field in self.fields.values():
#             field.widget.attrs.update({'class': 'form-control'})
#         self.fields['is_active'].widget.attrs.update({'class': 'form-check-input'})
    
#     def clean_email(self):
#         email = self.cleaned_data.get('email')
#         if User.objects.filter(email=email).exists():
#             raise forms.ValidationError("Email is already in use.")
#         return email
