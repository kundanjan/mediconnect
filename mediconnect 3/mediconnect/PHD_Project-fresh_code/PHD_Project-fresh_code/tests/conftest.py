import base64
import datetime
import os

import pytest
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

from billing.models import AccountantProfile, Billing
from doctor.models import Clinic, DoctorProfile, PatientDocConfig
from insurance.models import Insurance, InsuranceProfile
from labtest.models import LabStaffProfile, LabTest
from medical.models import MedicalProfile, Medicine, Prescription, PrescriptionItem
from organ_donation.models import BloodType, OrganDonation, OrganRequest, OrganType
from patient.models import PatientProfile, PatientVitals, Records


TEST_PASSWORD = "TestPass123!"


def _tiny_png_bytes():
    return base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGMA"
        "AQAABQABDQottAAAAABJRU5ErkJggg=="
    )


@pytest.fixture(scope="session", autouse=True)
def disable_external_api_calls():
    os.environ.setdefault("DISABLE_EXTERNAL_APIS", "1")


@pytest.fixture(autouse=True)
def _media_root(settings, tmp_path_factory):
    settings.MEDIA_ROOT = tmp_path_factory.mktemp("test_media")


@pytest.fixture()
def sample_image():
    return SimpleUploadedFile(
        "test.png",
        _tiny_png_bytes(),
        content_type="image/png",
    )


@pytest.fixture()
def sample_file():
    return SimpleUploadedFile(
        "test.txt",
        b"sample file",
        content_type="text/plain",
    )


@pytest.fixture()
def seeded_data(db):
    def create_user(username):
        user = User.objects.create_user(
            username=username,
            email=f"{username}@example.com",
            password=TEST_PASSWORD,
        )
        return user

    clinic_user = create_user("clinicadmin")
    clinic = Clinic.objects.create(
        name="Test Clinic",
        address="123 Main St",
        city="Metro",
        state="State",
        pincode="123456",
        phone="1234567890",
        email="clinic@example.com",
        Clinic=clinic_user,
    )

    doctor_user = create_user("doctor1")
    doctor_profile = DoctorProfile.objects.create(
        doctor=doctor_user,
        clinic=clinic,
        name="Dr Test",
        Gender="Male",
        Specialisation="Cardiology",
        phone="1234567890",
        City="Metro",
        Registration_Number="REG123",
        Registration_Council="Council",
        Registration_year=2020,
        Degree="MBBS",
        College="Med College",
        Year_of_completion=2020,
        Current_place_of_work="Test Hospital",
        hospital_name="Test Hospital",
        Aadhar_Number=123456789012,
    )

    patient_user = create_user("patient1")
    patient_profile = PatientProfile.objects.create(
        patient=patient_user,
        userid=patient_user.id,
        name="Patient One",
        age=30,
        address="456 Street",
        phone="1234567890",
        emergency_contact="0987654321",
        profession="Engineer",
        gender="Male",
        Aadhar_Number=111122223333,
        access_code="123456789",
    )

    PatientVitals.objects.create(
        patientv=patient_user,
        Height_in_Centimeters="170",
        Weight_in_kilograms="70",
        Allergies="None",
        Smoker_or_not="No",
        Chronic_conditions="None",
    )

    Records.objects.create(
        date="2026-05-19",
        patient_id=patient_profile.id,
        doctor_id=doctor_profile.id,
        doctor_name="Dr Test",
        diagnosis="Test diagnosis",
        Symptoms="Test symptoms",
        additional_precautions="None",
    )

    PatientDocConfig.objects.create(
        doctor_id=doctor_user.id,
        access_code=patient_profile.access_code,
    )

    insurance_user = create_user("insurance1")
    insurance_profile = InsuranceProfile.objects.create(
        user=insurance_user,
        clinic=clinic,
        company_name="InsureCo",
        phone="1234567890",
        email="insure@example.com",
        address="789 Avenue",
        department="Claims",
    )

    today = datetime.date.today()
    insurance = Insurance.objects.create(
        patient=patient_profile,
        doctor=doctor_profile,
        clinic=clinic,
        insurance_provider=insurance_profile,
        policy_number="POL12345",
        policy_type="Individual",
        valid_from=today,
        valid_to=today + datetime.timedelta(days=365),
        coverage_amount=10000,
    )

    accountant_user = create_user("accountant1")
    accountant_profile = AccountantProfile.objects.create(
        user=accountant_user,
        clinic=clinic,
        phone="1234567890",
        email="acct@example.com",
        address="1010 Road",
        department="Billing",
    )

    billing = Billing.objects.create(
        patient=patient_user,
        doctor=doctor_profile,
        clinic=clinic,
        billing_type="Hospital",
        total_amount=500,
        paid=False,
        payment_method="Cash",
        paid_by="Patient",
    )

    billing_medical = Billing.objects.create(
        patient=patient_user,
        doctor=doctor_profile,
        clinic=clinic,
        billing_type="Medical",
        total_amount=200,
        paid=False,
        payment_method="Cash",
        paid_by="Patient",
    )

    medical_user = create_user("medical1")
    medical_profile = MedicalProfile.objects.create(
        user=medical_user,
        clinic=clinic,
        email="medical@example.com",
        pharmacy_name="Test Pharmacy",
        phone="1234567890",
        address="111 Lane",
    )

    medicine = Medicine.objects.create(
        name="Paracetamol",
        brand="TestBrand",
        strength="500mg",
        price_per_unit=10,
        stock_quantity=100,
    )

    prescription = Prescription.objects.create(
        patient=patient_profile,
        doctor=doctor_profile,
        status="Pending",
    )

    PrescriptionItem.objects.create(
        prescription=prescription,
        medicine=medicine,
        quantity=1,
        instructions="Take one daily",
    )

    lab_user = create_user("labstaff1")
    lab_profile = LabStaffProfile.objects.create(
        user=lab_user,
        clinic=clinic,
        full_name="Lab Staff",
        phone="1234567890",
        email="lab@example.com",
        address="222 Drive",
        qualification="BSc",
        gender="Male",
        age=25,
    )

    lab_test = LabTest.objects.create(
        doctor=doctor_profile,
        patient=patient_profile,
        clinic=clinic,
        test_type="Blood Test",
        status="Pending",
        amount=100,
    )

    organ_type = OrganType.objects.create(name="kidney", description="Kidney")
    blood_type = BloodType.objects.create(blood_type="O+")
    donation = OrganDonation.objects.create(
        donor=patient_profile,
        organ_type=organ_type,
        blood_type=blood_type,
        health_condition="Healthy",
        age_at_donation=30,
        status="available",
    )
    request = OrganRequest.objects.create(
        requester=patient_profile,
        organ_type=organ_type,
        blood_type=blood_type,
        medical_condition="Needs transplant",
        age_at_request=30,
        urgency="medium",
        status="pending",
    )

    return {
        "users": {
            "clinic": clinic_user,
            "doctor": doctor_user,
            "patient": patient_user,
            "insurance": insurance_user,
            "accountant": accountant_user,
            "medical": medical_user,
            "labstaff": lab_user,
        },
        "profiles": {
            "clinic": clinic,
            "doctor": doctor_profile,
            "patient": patient_profile,
            "insurance": insurance_profile,
            "accountant": accountant_profile,
            "medical": medical_profile,
            "labstaff": lab_profile,
        },
        "objects": {
            "insurance": insurance,
            "billing": billing,
            "billing_medical": billing_medical,
            "medicine": medicine,
            "prescription": prescription,
            "lab_test": lab_test,
            "donation": donation,
            "request": request,
        },
    }
