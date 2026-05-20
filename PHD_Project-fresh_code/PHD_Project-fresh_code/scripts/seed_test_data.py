import datetime
import os
import sys
import json

import django


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MedicDiary.settings")
django.setup()

from django.contrib.auth.models import User
from billing.models import AccountantProfile, Billing
from doctor.models import Clinic, DoctorProfile, PatientDocConfig
from insurance.models import Insurance, InsuranceProfile
from labtest.models import LabStaffProfile, LabTest
from medical.models import MedicalProfile, Medicine, Prescription, PrescriptionItem
from organ_donation.models import BloodType, OrganDonation, OrganRequest, OrganType
from patient.models import PatientProfile, PatientVitals, Records


TEST_PASSWORD = "TestPass123!"


def create_user(username):
    user, created = User.objects.get_or_create(
        username=username,
        defaults={"email": f"{username}@example.com"},
    )
    if created or not user.check_password(TEST_PASSWORD):
        user.set_password(TEST_PASSWORD)
        user.save()
    return user


def main():
    clinic_user = create_user("clinicadmin")
    clinic, _ = Clinic.objects.get_or_create(
        name="Test Clinic",
        defaults={
            "address": "123 Main St",
            "city": "Metro",
            "state": "State",
            "pincode": "123456",
            "phone": "1234567890",
            "email": "clinic@example.com",
            "Clinic": clinic_user,
        },
    )
    if clinic.Clinic_id != clinic_user.id:
        clinic.Clinic = clinic_user
        clinic.save()

    doctor_user = create_user("doctor1")
    doctor_profile, _ = DoctorProfile.objects.get_or_create(
        doctor=doctor_user,
        defaults={
            "clinic": clinic,
            "name": "Dr Test",
            "Gender": "Male",
            "Specialisation": "Cardiology",
            "phone": "1234567890",
            "City": "Metro",
            "Registration_Number": "REG123",
            "Registration_Council": "Council",
            "Registration_year": 2020,
            "Degree": "MBBS",
            "College": "Med College",
            "Year_of_completion": 2020,
            "Current_place_of_work": "Test Hospital",
            "hospital_name": "Test Hospital",
            "Aadhar_Number": 123456789012,
        },
    )

    patient_user = create_user("patient1")
    patient_profile, _ = PatientProfile.objects.get_or_create(
        patient=patient_user,
        defaults={
            "userid": patient_user.id,
            "name": "Patient One",
            "age": 30,
            "address": "456 Street",
            "phone": "1234567890",
            "emergency_contact": "0987654321",
            "profession": "Engineer",
            "gender": "Male",
            "Aadhar_Number": 111122223333,
            "access_code": "123456789",
        },
    )

    PatientVitals.objects.get_or_create(
        patientv=patient_user,
        defaults={
            "Height_in_Centimeters": "170",
            "Weight_in_kilograms": "70",
            "Allergies": "None",
            "Smoker_or_not": "No",
            "Chronic_conditions": "None",
        },
    )

    Records.objects.get_or_create(
        patient_id=patient_profile.id,
        doctor_id=doctor_profile.id,
        defaults={
            "date": "2026-05-19",
            "doctor_name": "Dr Test",
            "diagnosis": "Test diagnosis",
            "Symptoms": "Test symptoms",
            "additional_precautions": "None",
        },
    )

    PatientDocConfig.objects.get_or_create(
        doctor_id=doctor_user.id,
        access_code=patient_profile.access_code,
    )

    insurance_user = create_user("insurance1")
    insurance_profile, _ = InsuranceProfile.objects.get_or_create(
        user=insurance_user,
        defaults={
            "clinic": clinic,
            "company_name": "InsureCo",
            "phone": "1234567890",
            "email": "insure@example.com",
            "address": "789 Avenue",
            "department": "Claims",
        },
    )

    today = datetime.date.today()
    insurance, _ = Insurance.objects.get_or_create(
        patient=patient_profile,
        insurance_provider=insurance_profile,
        policy_number="POL12345",
        defaults={
            "doctor": doctor_profile,
            "clinic": clinic,
            "policy_type": "Individual",
            "valid_from": today,
            "valid_to": today + datetime.timedelta(days=365),
            "coverage_amount": 10000,
        },
    )

    accountant_user = create_user("accountant1")
    AccountantProfile.objects.get_or_create(
        user=accountant_user,
        defaults={
            "clinic": clinic,
            "phone": "1234567890",
            "email": "acct@example.com",
            "address": "1010 Road",
            "department": "Billing",
        },
    )

    billing_hospital, _ = Billing.objects.get_or_create(
        patient=patient_user,
        billing_type="Hospital",
        total_amount=500,
        defaults={
            "doctor": doctor_profile,
            "clinic": clinic,
            "paid": False,
            "payment_method": "Cash",
            "paid_by": "Patient",
        },
    )

    billing_medical, _ = Billing.objects.get_or_create(
        patient=patient_user,
        billing_type="Medical",
        total_amount=200,
        defaults={
            "doctor": doctor_profile,
            "clinic": clinic,
            "paid": False,
            "payment_method": "Cash",
            "paid_by": "Patient",
        },
    )

    medical_user = create_user("medical1")
    MedicalProfile.objects.get_or_create(
        user=medical_user,
        defaults={
            "clinic": clinic,
            "email": "medical@example.com",
            "pharmacy_name": "Test Pharmacy",
            "phone": "1234567890",
            "address": "111 Lane",
        },
    )

    medicine, _ = Medicine.objects.get_or_create(
        name="Paracetamol",
        defaults={
            "brand": "TestBrand",
            "strength": "500mg",
            "price_per_unit": 10,
            "stock_quantity": 100,
        },
    )

    prescription, _ = Prescription.objects.get_or_create(
        patient=patient_profile,
        doctor=doctor_profile,
        defaults={"status": "Pending"},
    )

    PrescriptionItem.objects.get_or_create(
        prescription=prescription,
        medicine=medicine,
        defaults={
            "quantity": 1,
            "instructions": "Take one daily",
        },
    )

    lab_user = create_user("labstaff1")
    LabStaffProfile.objects.get_or_create(
        user=lab_user,
        defaults={
            "clinic": clinic,
            "full_name": "Lab Staff",
            "phone": "1234567890",
            "email": "lab@example.com",
            "address": "222 Drive",
            "qualification": "BSc",
            "gender": "Male",
            "age": 25,
        },
    )

    lab_test, _ = LabTest.objects.get_or_create(
        doctor=doctor_profile,
        patient=patient_profile,
        test_type="Blood Test",
        defaults={
            "clinic": clinic,
            "status": "Pending",
            "amount": 100,
        },
    )

    organ_type, _ = OrganType.objects.get_or_create(
        name="kidney",
        defaults={"description": "Kidney"},
    )
    blood_type, _ = BloodType.objects.get_or_create(blood_type="O+")

    donation, _ = OrganDonation.objects.get_or_create(
        donor=patient_profile,
        organ_type=organ_type,
        defaults={
            "blood_type": blood_type,
            "health_condition": "Healthy",
            "age_at_donation": 30,
            "status": "available",
        },
    )

    request, _ = OrganRequest.objects.get_or_create(
        requester=patient_profile,
        organ_type=organ_type,
        defaults={
            "blood_type": blood_type,
            "medical_condition": "Needs transplant",
            "age_at_request": 30,
            "urgency": "medium",
            "status": "pending",
        },
    )

    ids_path = os.path.join(PROJECT_ROOT, "scripts", "seeded_ids.json")
    ids_payload = {
        "clinic_id": clinic.id,
        "doctor_profile_id": doctor_profile.id,
        "patient_profile_id": patient_profile.id,
        "insurance_id": insurance.id,
        "lab_test_id": lab_test.id,
        "prescription_id": prescription.id,
        "medicine_id": medicine.id,
        "billing_id": billing_hospital.id,
        "billing_medical_id": billing_medical.id,
        "donation_id": donation.id,
        "request_id": request.id,
    }
    with open(ids_path, "w", encoding="utf-8") as handle:
        json.dump(ids_payload, handle, ensure_ascii=True, indent=2)

    print("Seeded test data successfully.")


if __name__ == "__main__":
    main()
