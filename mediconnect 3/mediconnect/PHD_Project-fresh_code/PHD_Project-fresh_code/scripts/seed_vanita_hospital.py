import datetime
import os
import sys
import json
import subprocess

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

# ---------------------------------------------------------------------------
# REAL DATA FROM VANITA MULTISPECIALITY HOSPITAL
# ---------------------------------------------------------------------------

HOSPITAL_NAME = "Vanita Multispeciality Hospital"
HOSPITAL_ADDRESS = "Vanita Hospital, Pune"
HOSPITAL_CITY = "Pune"
HOSPITAL_STATE = "Maharashtra"
HOSPITAL_PINCODE = "411001"
HOSPITAL_PHONE = "9876543210"
HOSPITAL_EMAIL = "admin@vanitahospital.com"

# Each entry: (username, full_name, specialisation, degree, gender, reg_number)
DOCTORS = [
    ("dr_pratik_kabra",   "Dr. Pratik V. Kabra",        "Anaesthesiology",                "M.B.B.S., M.D.- Anaesthesia, IDCCM",                                    "Male",   "REG001"),
    ("dr_ruturaj_kakad",  "Dr. Ruturaj Kakad",           "Anaesthesiology",                "M.B.B.S., M.D.- Anaesthesia",                                           "Male",   "REG002"),
    ("dr_kundan_patil",   "Dr. Kundan V. Patil",         "Cardiology",                     "M.B.B.S., D.N.B.- Gen Med., D.M. & Dr.N.B.- Cardiology",               "Male",   "REG003"),
    ("dr_ankur_jhawar",   "Dr. Ankur A. Jhawar",         "Cardiology",                     "M.B.B.S., D.N.B.- Gen Med., Dr.N.B.- Cardiology",                      "Male",   "REG004"),
    ("dr_anushree_agrawal","Dr. Anushree D. Agrawal",    "ENT",                            "M.B.B.S., M.S.- ENT",                                                   "Female", "REG005"),
    ("dr_prashant_chopda","Dr. Prashant D. Chopda",      "ENT",                            "M.D.S.- Maxillofacial, Fellowship- Head & Neck Surgery",                 "Male",   "REG006"),
    ("dr_ashish_patil",   "Dr. Ashish S. Patil",         "Gastroenterology",               "M.B.B.S., M.D.- Medicine, Dr.N.B.- Gastroenterology",                   "Male",   "REG007"),
    ("dr_bhushan_chopade","Dr. Bhushan Chopade",         "Gastroenterology",               "M.B.B.S., M.D.- Medicine, Dr.N.B.- Gastroenterology",                   "Male",   "REG008"),
    ("dr_bhushan_a_patil","Dr. Bhushan A. Patil",        "General Medicine",               "M.B.B.S., M.D. (BJMC, Pune)",                                           "Male",   "REG009"),
    ("dr_bhushan_somani", "Dr. Bhushan G. Somani",       "General Surgery",                "M.B.B.S., M.S.- Gen Surgery",                                           "Male",   "REG010"),
    ("dr_saurabh_patil",  "Dr. Saurabh Patil",           "General Surgery",                "M.B.B.S., D.N.B.- Gen Surgery",                                         "Male",   "REG011"),
    ("dr_kiran_patil",    "Dr. Kiran C. Patil",          "Interventional Radiology",       "M.B.B.S., M.D. & D.N.B.- Radiology, F.I.N.R.",                         "Male",   "REG012"),
    ("dr_gopal_gholap",   "Dr. Gopal A. Gholap",         "Neurology",                      "MBBS, M.D.- Med, Dr.N.B.- Neurology, F.I.N.R.",                         "Male",   "REG013"),
    ("dr_ketan_borole",   "Dr. Ketan A. Borole",         "Neurosurgery",                   "M.B.B.S., M.S.- Gen Surgery, Dr.N.B.- Neurosurgery",                    "Male",   "REG014"),
    ("dr_amit_bhangale",  "Dr. Amit A. Bhangale",        "Nephrology",                     "M.B.B.S., D.N.B.- Gen Med., Dr.N.B.- Nephrology, M.N.A.M.S.",          "Male",   "REG015"),
    ("dr_swapnil_bharambe","Dr. Swapnil Bharambe",       "Nephrology",                     "M.B.B.S., D.N.B.- Gen Med., Dr.N.B.- Nephrology",                      "Male",   "REG016"),
    ("dr_gajanan_patil",  "Dr. Gajanan G. Patil",        "Obstetrics and Gynaecology",     "M.B.B.S., M.S., Fellowship- Endoscopic & Laparoscopic Surgery",         "Male",   "REG017"),
    ("dr_manjeet_sanghavi","Dr. Manjeet Sanghavi",       "Obstetrics and Gynaecology",     "M.B.B.S., D.G.O., D.N.B.- Obs & Gynec",                                "Male",   "REG018"),
    ("dr_sachin_deshmukh","Dr. Sachin Deshmukh",         "Ophthalmology",                  "M.B.B.S., D.O.",                                                        "Male",   "REG019"),
    ("dr_deepak_agrawal", "Dr. Deepak P. Agrawal",       "Orthopaedic Surgery",            "M.B.B.S., M.S.- Ortho, Fellowship- Arthroplasty",                       "Male",   "REG020"),
    ("dr_gaurav_jain",    "Dr. Gaurav R. Jain",          "Orthopaedic Surgery",            "M.B.B.S., M.S.- Ortho, Fellowship- Joint Replacement & Arthroscopy",    "Male",   "REG021"),
    ("dr_neha_kabra",     "Dr. Neha P. Kabra",           "Paediatrics and Neonatology",    "M.B.B.S., D.C.H., D.N.B.- Paediatrics",                                "Female", "REG022"),
    ("dr_chandrashekhar_sikchi","Dr. Chandrashekhar G. Sikchi","Paediatrics and Neonatology","M.B.B.S., D.C.H., M.D.- Paediatrics",                                "Male",   "REG023"),
    ("dr_dheeraj_maheshwari","Dr. Dheeraj Maheshwari",   "Pathology",                      "M.B.B.S., M.D.- Pathology",                                             "Male",   "REG024"),
    ("dr_pooja_somani",   "Dr. Pooja B. Somani",         "Radiology",                      "M.B.B.S., D.M.R.E.- Radiology",                                         "Female", "REG025"),
    ("dr_samir_sonar",    "Dr. Samir R. Sonar",          "Radiology",                      "M.B.B.S., D.M.R.D & D.N.B.- Radiology",                                "Male",   "REG026"),
    ("dr_mayur_muthe",    "Dr. Mayur Muthe",             "Psychiatry",                     "M.B.B.S., M.D.- Psychiatry",                                            "Male",   "REG027"),
    ("dr_abhay_chaudhari","Dr. Abhay Chaudhari",         "Urology",                        "M.B.B.S., M.S.- Gen Surgery, Dr.N.B.- Urosurgery",                      "Male",   "REG028"),
    ("dr_renuka_sarap",   "Dr. Renuka P. Sarap",         "Physiotherapy",                  "B.Pt., M.Pt.- Cardio Respiratory",                                      "Female", "REG029"),
    ("dt_lalit_mahajan",  "Dt. Lalit Mahajan",           "Clinical Nutrition",             "M.Sc.- Clinical Nutrition",                                              "Male",   "REG030"),
]

# ---------------------------------------------------------------------------

def create_user(username, email=None):
    if email is None:
        email = f"{username}@vanitahospital.com"
    user, created = User.objects.get_or_create(
        username=username,
        defaults={"email": email},
    )
    if created or not user.check_password(TEST_PASSWORD):
        user.set_password(TEST_PASSWORD)
        user.save()
    return user, created


def main():
    credentials = []   # collect all login info for the report

    # -----------------------------------------------------------------------
    # 1. Clinic admin
    # -----------------------------------------------------------------------
    clinic_user, _ = create_user("clinic_admin", HOSPITAL_EMAIL)
    credentials.append({
        "role": "Clinic Admin",
        "name": HOSPITAL_NAME,
        "username": "clinic_admin",
        "password": TEST_PASSWORD,
        "email": HOSPITAL_EMAIL,
    })

    clinic, _ = Clinic.objects.get_or_create(
        name=HOSPITAL_NAME,
        defaults={
            "address": HOSPITAL_ADDRESS,
            "city": HOSPITAL_CITY,
            "state": HOSPITAL_STATE,
            "pincode": HOSPITAL_PINCODE,
            "phone": HOSPITAL_PHONE,
            "email": HOSPITAL_EMAIL,
            "Clinic": clinic_user,
        },
    )
    if clinic.Clinic_id != clinic_user.id:
        clinic.Clinic = clinic_user
        clinic.save()

    # -----------------------------------------------------------------------
    # 2. Doctors (30 real consultants from the hospital board)
    # -----------------------------------------------------------------------
    doctor_profiles = []
    for idx, (username, full_name, specialisation, degree, gender, reg_no) in enumerate(DOCTORS, start=1):
        email = f"{username}@vanitahospital.com"
        doc_user, _ = create_user(username, email)
        credentials.append({
            "role": "Doctor",
            "name": full_name,
            "username": username,
            "password": TEST_PASSWORD,
            "email": email,
            "specialisation": specialisation,
            "degree": degree,
        })

        profile, _ = DoctorProfile.objects.get_or_create(
            doctor=doc_user,
            defaults={
                "clinic": clinic,
                "name": full_name,
                "Gender": gender,
                "Specialisation": specialisation,
                "phone": f"98765{str(idx).zfill(5)}",
                "City": HOSPITAL_CITY,
                "Registration_Number": reg_no,
                "Registration_Council": "Maharashtra Medical Council",
                "Registration_year": 2010 + (idx % 12),
                "Degree": degree,
                "College": "B.J. Medical College, Pune",
                "Year_of_completion": 2008 + (idx % 12),
                "Current_place_of_work": "Vanita Hospital",
                "hospital_name": HOSPITAL_NAME,
                "Aadhar_Number": 100000000000 + idx,
            },
        )
        doctor_profiles.append(profile)

    # Use first doctor as default for FK references below
    default_doctor = doctor_profiles[0]

    # -----------------------------------------------------------------------
    # 3. Sample patient
    # -----------------------------------------------------------------------
    patient_user, _ = create_user("patient_demo", "patient@example.com")
    credentials.append({
        "role": "Patient",
        "name": "Demo Patient",
        "username": "patient_demo",
        "password": TEST_PASSWORD,
        "email": "patient@example.com",
    })

    patient_profile, created_patient = PatientProfile.objects.get_or_create(
        patient=patient_user,
        defaults={
            "userid": patient_user.id,
            "name": "Demo Patient",
            "age": 35,
            "address": "456 Demo Street, Pune",
            "phone": "9000000001",
            "emergency_contact": "9000000002",
            "profession": "Engineer",
            "gender": "Male",
            "Aadhar_Number": 999900001111,
            "access_code": "202600001",
        },
    )

    # Ensure access_code is numeric for PatientDocConfig (IntegerField)
    if not patient_profile.access_code.isdigit():
        patient_profile.access_code = "202600001"
        patient_profile.save()

    patient_access_code_int = int(patient_profile.access_code)

    PatientVitals.objects.get_or_create(
        patientv=patient_user,
        defaults={
            "Height_in_Centimeters": "172",
            "Weight_in_kilograms": "68",
            "Allergies": "None",
            "Smoker_or_not": "No",
            "Chronic_conditions": "None",
        },
    )

    Records.objects.get_or_create(
        patient_id=patient_profile.id,
        doctor_id=default_doctor.id,
        defaults={
            "date": datetime.date.today().isoformat(),
            "doctor_name": default_doctor.name,
            "diagnosis": "Routine check-up",
            "Symptoms": "None",
            "additional_precautions": "None",
        },
    )

    PatientDocConfig.objects.get_or_create(
        doctor_id=default_doctor.doctor.id,
        access_code=patient_access_code_int,
    )

    # -----------------------------------------------------------------------
    # 4. Insurance
    # -----------------------------------------------------------------------
    insurance_user, _ = create_user("insurance_vanita", "insurance@vanitahospital.com")
    credentials.append({
        "role": "Insurance",
        "name": "Vanita Insurance Desk",
        "username": "insurance_vanita",
        "password": TEST_PASSWORD,
        "email": "insurance@vanitahospital.com",
    })

    insurance_profile, _ = InsuranceProfile.objects.get_or_create(
        user=insurance_user,
        defaults={
            "clinic": clinic,
            "company_name": "Star Health Insurance",
            "phone": "9000000010",
            "email": "insurance@vanitahospital.com",
            "address": HOSPITAL_ADDRESS,
            "department": "Claims",
        },
    )

    today = datetime.date.today()
    insurance, _ = Insurance.objects.get_or_create(
        patient=patient_profile,
        insurance_provider=insurance_profile,
        policy_number="VNT-POL-2026",
        defaults={
            "doctor": default_doctor,
            "clinic": clinic,
            "policy_type": "Individual",
            "valid_from": today,
            "valid_to": today + datetime.timedelta(days=365),
            "coverage_amount": 500000,
        },
    )

    # -----------------------------------------------------------------------
    # 5. Accountant
    # -----------------------------------------------------------------------
    accountant_user, _ = create_user("accountant_vanita", "accounts@vanitahospital.com")
    credentials.append({
        "role": "Accountant",
        "name": "Vanita Accounts Dept",
        "username": "accountant_vanita",
        "password": TEST_PASSWORD,
        "email": "accounts@vanitahospital.com",
    })

    AccountantProfile.objects.get_or_create(
        user=accountant_user,
        defaults={
            "clinic": clinic,
            "phone": "9000000011",
            "email": "accounts@vanitahospital.com",
            "address": HOSPITAL_ADDRESS,
            "department": "Billing",
        },
    )

    billing_hospital, _ = Billing.objects.get_or_create(
        patient=patient_user,
        billing_type="Hospital",
        defaults={
            "doctor": default_doctor,
            "clinic": clinic,
            "total_amount": 2500,
            "paid": False,
            "payment_method": "Cash",
            "paid_by": "Patient",
        },
    )

    billing_medical, _ = Billing.objects.get_or_create(
        patient=patient_user,
        billing_type="Medical",
        defaults={
            "doctor": default_doctor,
            "clinic": clinic,
            "total_amount": 800,
            "paid": False,
            "payment_method": "Cash",
            "paid_by": "Patient",
        },
    )

    # -----------------------------------------------------------------------
    # 6. Pharmacy / Medical
    # -----------------------------------------------------------------------
    medical_user, _ = create_user("pharmacy_vanita", "pharmacy@vanitahospital.com")
    credentials.append({
        "role": "Pharmacy",
        "name": "Vanita Dispensary",
        "username": "pharmacy_vanita",
        "password": TEST_PASSWORD,
        "email": "pharmacy@vanitahospital.com",
    })

    MedicalProfile.objects.get_or_create(
        user=medical_user,
        defaults={
            "clinic": clinic,
            "email": "pharmacy@vanitahospital.com",
            "pharmacy_name": "Vanita Dispensary",
            "phone": "9000000012",
            "address": HOSPITAL_ADDRESS,
        },
    )

    medicine, _ = Medicine.objects.get_or_create(
        name="Paracetamol",
        defaults={
            "brand": "Crocin",
            "strength": "500mg",
            "price_per_unit": 2,
            "stock_quantity": 500,
        },
    )

    prescription, _ = Prescription.objects.get_or_create(
        patient=patient_profile,
        doctor=default_doctor,
        defaults={"status": "Pending"},
    )

    PrescriptionItem.objects.get_or_create(
        prescription=prescription,
        medicine=medicine,
        defaults={
            "quantity": 10,
            "instructions": "Take one tablet twice daily after meals",
        },
    )

    # -----------------------------------------------------------------------
    # 7. Lab Staff
    # -----------------------------------------------------------------------
    lab_user, _ = create_user("lab_vanita", "lab@vanitahospital.com")
    credentials.append({
        "role": "Lab Staff",
        "name": "Vanita Lab",
        "username": "lab_vanita",
        "password": TEST_PASSWORD,
        "email": "lab@vanitahospital.com",
    })

    LabStaffProfile.objects.get_or_create(
        user=lab_user,
        defaults={
            "clinic": clinic,
            "full_name": "Lab Staff",
            "phone": "9000000013",
            "email": "lab@vanitahospital.com",
            "address": HOSPITAL_ADDRESS,
            "qualification": "B.Sc. - Clinical Pathology",
            "gender": "Male",
            "age": 28,
        },
    )

    lab_test, _ = LabTest.objects.get_or_create(
        doctor=default_doctor,
        patient=patient_profile,
        test_type="Blood Test",
        defaults={
            "clinic": clinic,
            "status": "Pending",
            "amount": 350,
        },
    )

    # -----------------------------------------------------------------------
    # 8. Organ donation stubs
    # -----------------------------------------------------------------------
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
            "age_at_donation": 35,
            "status": "available",
        },
    )

    organ_request, _ = OrganRequest.objects.get_or_create(
        requester=patient_profile,
        organ_type=organ_type,
        defaults={
            "blood_type": blood_type,
            "medical_condition": "Needs transplant",
            "age_at_request": 35,
            "urgency": "medium",
            "status": "pending",
        },
    )

    # -----------------------------------------------------------------------
    # 9. Save seeded IDs
    # -----------------------------------------------------------------------
    ids_path = os.path.join(PROJECT_ROOT, "scripts", "seeded_ids.json")
    ids_payload = {
        "clinic_id": clinic.id,
        "doctor_profile_id": default_doctor.id,
        "all_doctor_profile_ids": [p.id for p in doctor_profiles],
        "patient_profile_id": patient_profile.id,
        "insurance_id": insurance.id,
        "lab_test_id": lab_test.id,
        "prescription_id": prescription.id,
        "medicine_id": medicine.id,
        "billing_id": billing_hospital.id,
        "billing_medical_id": billing_medical.id,
        "donation_id": donation.id,
        "request_id": organ_request.id,
    }
    os.makedirs(os.path.dirname(ids_path), exist_ok=True)
    with open(ids_path, "w", encoding="utf-8") as fh:
        json.dump(ids_payload, fh, ensure_ascii=True, indent=2)

    # -----------------------------------------------------------------------
    # 10. Generate credentials Word document
    # -----------------------------------------------------------------------
    _generate_credentials_doc(credentials)

    print("=" * 60)
    print("Vanita Hospital data seeded successfully.")
    print(f"  Doctors created : {len(DOCTORS)}")
    print(f"  Total accounts  : {len(credentials)}")
    print("  Credentials doc : scripts/vanita_credentials.docx")
    print("=" * 60)


def _generate_credentials_doc(credentials):
    """Generate a Word document listing all login credentials."""
    script_dir = os.path.join(PROJECT_ROOT, "scripts")
    os.makedirs(script_dir, exist_ok=True)
    js_path = os.path.join(script_dir, "_gen_creds.js")
    doc_path = os.path.join(script_dir, "vanita_credentials.docx")

    # Build JS rows
    doctor_rows = []
    other_rows = []

    for c in credentials:
        if c["role"] == "Doctor":
            doctor_rows.append(c)
        else:
            other_rows.append(c)

    def js_cell(text, bold=False, bg="FFFFFF"):
        return (
            f"new TableCell({{"
            f"borders, width: {{ size: 0, type: WidthType.AUTO }},"
            f"shading: {{ fill: '{bg}', type: ShadingType.CLEAR }},"
            f"margins: {{ top: 80, bottom: 80, left: 120, right: 120 }},"
            f"children: [new Paragraph({{ children: [new TextRun({{ text: {json.dumps(str(text))}, "
            f"bold: {'true' if bold else 'false'}, size: 20 }})] }})]"
            f"}})"
        )

    def header_row(cols, bg="1F4E79"):
        cells = ", ".join(
            f"new TableCell({{"
            f"borders, width: {{ size: 0, type: WidthType.AUTO }},"
            f"shading: {{ fill: '{bg}', type: ShadingType.CLEAR }},"
            f"margins: {{ top: 80, bottom: 80, left: 120, right: 120 }},"
            f"children: [new Paragraph({{ children: [new TextRun({{ text: {json.dumps(c)}, bold: true, color: 'FFFFFF', size: 20 }})] }})]"
            f"}})"
            for c in cols
        )
        return f"new TableRow({{ tableHeader: true, children: [{cells}] }})"

    # Other accounts table rows
    other_table_rows = [header_row(["Role", "Name", "Username", "Password", "Email"])]
    for c in other_rows:
        bg = "EBF3FB" if other_rows.index(c) % 2 == 0 else "FFFFFF"
        cells = ", ".join([
            js_cell(c["role"], bold=True, bg=bg),
            js_cell(c["name"], bg=bg),
            js_cell(c["username"], bg=bg),
            js_cell(c["password"], bg=bg),
            js_cell(c["email"], bg=bg),
        ])
        other_table_rows.append(f"new TableRow({{ children: [{cells}] }})")

    # Doctor table rows
    doc_table_rows = [header_row(["Name", "Username", "Password", "Email", "Specialisation", "Degree"])]
    for i, c in enumerate(doctor_rows):
        bg = "EBF3FB" if i % 2 == 0 else "FFFFFF"
        cells = ", ".join([
            js_cell(c["name"], bold=True, bg=bg),
            js_cell(c["username"], bg=bg),
            js_cell(c["password"], bg=bg),
            js_cell(c["email"], bg=bg),
            js_cell(c["specialisation"], bg=bg),
            js_cell(c["degree"], bg=bg),
        ])
        doc_table_rows.append(f"new TableRow({{ children: [{cells}] }})")

    js_code = f"""
const fs = require('fs');
const {{
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  AlignmentType, WidthType, ShadingType, BorderStyle, HeadingLevel
}} = require('docx');

const border = {{ style: BorderStyle.SINGLE, size: 1, color: 'AAAAAA' }};
const borders = {{ top: border, bottom: border, left: border, right: border }};

function section(title, color) {{
  return new Paragraph({{
    spacing: {{ before: 360, after: 160 }},
    children: [new TextRun({{ text: title, bold: true, size: 28, color }})]
  }});
}}

const doc = new Document({{
  styles: {{
    default: {{ document: {{ run: {{ font: 'Arial', size: 20 }} }} }}
  }},
  sections: [{{
    properties: {{
      page: {{
        size: {{ width: 20160, height: 15840 }},
        margin: {{ top: 1080, right: 1080, bottom: 1080, left: 1080 }}
      }}
    }},
    children: [
      new Paragraph({{
        alignment: AlignmentType.CENTER,
        spacing: {{ after: 80 }},
        children: [new TextRun({{ text: 'Vanita Multispeciality Hospital', bold: true, size: 40, color: '1F4E79' }})]
      }}),
      new Paragraph({{
        alignment: AlignmentType.CENTER,
        spacing: {{ after: 320 }},
        children: [new TextRun({{ text: 'System Login Credentials — CONFIDENTIAL', size: 22, color: 'C00000', italics: true }})]
      }}),
      new Paragraph({{
        spacing: {{ after: 80 }},
        children: [new TextRun({{ text: 'Default Password for all accounts: TestPass123!', bold: true, size: 22, color: '375623' }})]
      }}),
      new Paragraph({{
        spacing: {{ after: 320 }},
        children: [new TextRun({{ text: 'Please change passwords immediately after first login.', size: 20, italics: true, color: 'FF0000' }})]
      }}),

      section('Staff & Support Accounts', '1F4E79'),
      new Table({{
        width: {{ size: 100, type: WidthType.PERCENTAGE }},
        rows: [
          {chr(10) + (',' + chr(10)).join(other_table_rows)}
        ]
      }}),

      section('Doctor Accounts ({len(doctor_rows)} Consultants)', '1F4E79'),
      new Table({{
        width: {{ size: 100, type: WidthType.PERCENTAGE }},
        rows: [
          {chr(10) + (',' + chr(10)).join(doc_table_rows)}
        ]
      }}),

      new Paragraph({{
        spacing: {{ before: 480 }},
        children: [new TextRun({{ text: 'Generated on: {datetime.date.today().strftime("%d %B %Y")}  |  MedicDiary System', size: 18, color: '888888', italics: true }})]
      }})
    ]
  }}]
}});

Packer.toBuffer(doc).then(buf => {{
  fs.writeFileSync({json.dumps(doc_path)}, buf);
  console.log('Credentials doc written to: {doc_path}');
}});
"""

    with open(js_path, "w", encoding="utf-8") as fh:
        fh.write(js_code)

    result = subprocess.run(["node", js_path], capture_output=True, text=True)
    if result.returncode != 0:
        print("WARNING: Could not generate credentials doc.")
        print(result.stderr)
    else:
        print(result.stdout.strip())

    # Clean up temp JS
    try:
        os.remove(js_path)
    except OSError:
        pass


if __name__ == "__main__":
    main()
