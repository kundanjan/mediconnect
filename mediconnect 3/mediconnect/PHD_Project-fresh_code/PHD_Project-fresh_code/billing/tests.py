from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from billing.models import Billing, AccountantProfile
from doctor.models import Clinic


class BillingViewsTest(TestCase):
    def setUp(self):
        self.client = Client()

        self.accountant_user = User.objects.create_user(
            username='accountant',
            password='password123'
        )
        self.patient_user = User.objects.create_user(
            username='patient',
            password='password123'
        )
        self.clinic_owner = User.objects.create_user(
            username='clinicadmin',
            password='password123'
        )

        self.clinic = Clinic.objects.create(
            name='Test Clinic',
            address='123 Main St',
            city='Metro',
            state='State',
            pincode='123456',
            phone='1234567890',
            email='clinic@example.com',
            Clinic=self.clinic_owner,
        )

        self.accountant_profile = AccountantProfile.objects.create(
            user=self.accountant_user,
            clinic=self.clinic,
            phone='1234567890',
            email='acct@example.com',
            address='1010 Road',
            department='Billing',
        )

        self.billing = Billing.objects.create(
            patient=self.patient_user,
            clinic=self.clinic,
            billing_type='Hospital',
            total_amount=500,
            paid=False,
            payment_method='Cash',
            paid_by='Patient',
        )

        self.client.login(username='accountant', password='password123')

    def test_accountant_register_view(self):
        self.client.logout()
        response = self.client.get(reverse('billing:accountant_register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'billing/accountant_register.html')

    def test_create_accountant_profile_view_get(self):
        self.client.logout()
        temp_user = User.objects.create_user(
            username='accountant2',
            password='password123'
        )
        self.client.login(username='accountant2', password='password123')

        response = self.client.get(reverse('billing:create_accountant_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'billing/create_accountant_profile.html')

    def test_view_accountant_profile(self):
        response = self.client.get(reverse('billing:view_accountant_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'billing/view_accountant_profile.html')

    def test_process_unpaid_bills_view(self):
        response = self.client.get(reverse('billing:process_unpaid_bills'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'billing/process_unpaid_bills.html')

    def test_update_bill_view_get(self):
        response = self.client.get(reverse('billing:update_bill', args=[self.billing.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'billing/update_bill.html')

    def test_update_bill_view_post(self):
        response = self.client.post(
            reverse('billing:update_bill', args=[self.billing.id]),
            {
                'paid_by': 'Patient',
                'payment_method': 'Cash',
                'paid': 'on',
            },
        )
        self.assertEqual(response.status_code, 302)

    def test_paid_bills_history_view(self):
        response = self.client.get(reverse('billing:paid_bills_history'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'billing/paid_bills_history.html')
