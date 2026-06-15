import datetime
import uuid

import pytest
from django.contrib.auth.models import User
from medical.models import Medicine

from insurance.models import Insurance


TEST_PASSWORD = "TestPass123!"


def _unique_username(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


@pytest.mark.django_db
def test_patient_profile_flow(client, sample_image):
    username = _unique_username("patient")
    user = User.objects.create_user(username=username, password=TEST_PASSWORD)
    client.force_login(user)

    response = client.post(
        "/createPatientProfile/",
        {
            "name": "Patient Flow",
            "age": 29,
            "gender": "Male",
            "address": "123 Street",
            "phone": "1234567890",
            "emergency_contact": "0987654321",
            "profession": "Engineer",
            "Aadhar_Number": 123456789012,
            "profile_pic": sample_image,
        },
        follow=True,
    )
    assert response.status_code < 500

    response = client.post(
        "/patientvitals/",
        {
            "Height_in_Centimeters": "170",
            "Weight_in_kilograms": "70",
            "Allergies": "None",
            "Smoker_or_not": "No",
            "Chronic_conditions": "None",
        },
        follow=True,
    )
    assert response.status_code < 500


@pytest.mark.django_db
def test_doctor_profile_flow(client, sample_image, seeded_data):
    username = _unique_username("doctor")
    user = User.objects.create_user(username=username, password=TEST_PASSWORD)
    client.force_login(user)

    response = client.post(
        "/doctor/createDoctorProfile/",
        {
            "name": "Dr Flow",
            "phone": "1234567890",
            "Specialisation": "Cardiology",
            "City": "Metro",
            "Registration_Number": "REGFLOW",
            "Registration_Council": "Council",
            "Registration_year": 2020,
            "Degree": "MBBS",
            "College": "Medical College",
            "Year_of_completion": 2020,
            "Current_place_of_work": "Test Hospital",
            "hospital_name": "Test Hospital",
            "Gender": "Male",
            "Profile_pic": sample_image,
            "Aadhar_Number": 123456789012,
        },
        follow=True,
    )
    assert response.status_code < 500


@pytest.mark.django_db
def test_insurance_profile_flow(client, sample_image, seeded_data):
    username = _unique_username("insurance")
    user = User.objects.create_user(username=username, password=TEST_PASSWORD)
    client.force_login(user)

    response = client.post(
        "/insurance/profile/create/",
        {
            "company_name": "Flow Insurance",
            "phone": "1234567890",
            "email": "flow_insurance@example.com",
            "address": "456 Road",
            "department": "Claims",
            "profile_pic": sample_image,
        },
        follow=True,
    )
    assert response.status_code < 500


@pytest.mark.django_db
def test_labstaff_profile_flow(client, sample_image, seeded_data):
    username = _unique_username("labstaff")
    user = User.objects.create_user(username=username, password=TEST_PASSWORD)
    client.force_login(user)

    response = client.post(
        "/labtests/profile/create/",
        {
            "full_name": "Lab Staff Flow",
            "phone": "1234567890",
            "email": "lab_flow@example.com",
            "address": "789 Avenue",
            "qualification": "BSc",
            "gender": "Male",
            "age": 25,
            "profile_picture": sample_image,
        },
        follow=True,
    )
    assert response.status_code < 500


@pytest.mark.django_db
def test_medical_profile_flow(client, seeded_data, sample_image):
    username = _unique_username("medical")
    user = User.objects.create_user(username=username, password=TEST_PASSWORD)
    client.force_login(user)

    response = client.post(
        "/medical/profile/create/",
        {
            "pharmacy_name": "Flow Pharmacy",
            "phone": "1234567890",
            "email": "flow_medical@example.com",
            "address": "1010 Street",
            "profile_pic": sample_image,
        },
        follow=True,
    )
    assert response.status_code < 500


@pytest.mark.django_db
def test_accountant_profile_flow(client, sample_image, seeded_data):
    username = _unique_username("accountant")
    user = User.objects.create_user(username=username, password=TEST_PASSWORD)
    client.force_login(user)

    response = client.post(
        "/billing/profile/create/",
        {
            "phone": "1234567890",
            "email": "flow_accountant@example.com",
            "address": "101 Billing",
            "department": "Accounts",
            "profile_pic": sample_image,
        },
        follow=True,
    )
    assert response.status_code < 500


@pytest.mark.django_db
def test_medicine_crud_flow(client, seeded_data):
    client.force_login(seeded_data["users"]["medical"])

    response = client.post(
        "/medical/medicines/create/",
        {
            "name": "Ibuprofen",
            "brand": "BrandX",
            "strength": "200mg",
            "price_per_unit": 12,
            "stock_quantity": 50,
        },
        follow=True,
    )
    assert response.status_code < 500

    created_medicine = Medicine.objects.order_by("-id").first()
    medicine_id = created_medicine.id if created_medicine else None
    if medicine_id:
        response = client.post(
            f"/medical/medicines/{medicine_id}/update/",
            {
                "name": "Ibuprofen",
                "brand": "BrandX",
                "strength": "400mg",
                "price_per_unit": 14,
                "stock_quantity": 40,
            },
            follow=True,
        )
        assert response.status_code < 500

        response = client.post(
            f"/medical/medicines/{medicine_id}/delete/",
            follow=True,
        )
        assert response.status_code < 500


@pytest.mark.django_db
def test_labtest_create_flow(client, seeded_data):
    client.force_login(seeded_data["users"]["doctor"])

    patient_id = seeded_data["profiles"]["patient"].id
    response = client.post(
        f"/labtests/doctor/add-labtest/{patient_id}/",
        {"test_type": "X-Ray"},
        follow=True,
    )
    assert response.status_code < 500


@pytest.mark.django_db
def test_patient_create_insurance_flow(client, seeded_data, sample_file):
    client.force_login(seeded_data["users"]["patient"])

    provider_id = seeded_data["profiles"]["insurance"].id
    today = datetime.date.today()
    response = client.post(
        "/create_insurance/",
        {
            "insurance_provider": provider_id,
            "policy_number": f"POL{uuid.uuid4().hex[:6]}",
            "policy_type": "Individual",
            "valid_from": today,
            "valid_to": today + datetime.timedelta(days=365),
            "coverage_amount": 5000,
            "policy_document": sample_file,
        },
        follow=True,
    )
    assert response.status_code < 500


@pytest.mark.django_db
def test_insurance_claim_update_flow(client, seeded_data):
    client.force_login(seeded_data["users"]["insurance"])

    insurance = Insurance.objects.first()
    response = client.post(
        f"/insurance/claim/{insurance.id}/update_status/",
        {"status": "Approved"},
        follow=True,
    )
    assert response.status_code < 500


@pytest.mark.django_db
def test_billing_update_flow(client, seeded_data):
    client.force_login(seeded_data["users"]["accountant"])

    billing_id = seeded_data["objects"]["billing"].id
    response = client.post(
        f"/billing/bill/{billing_id}/update/",
        {
            "paid_by": "Patient",
            "payment_method": "Cash",
            "paid": "on",
        },
        follow=True,
    )
    assert response.status_code < 500
