import pytest


@pytest.mark.django_db
def test_smoke_get_pages(client, seeded_data):
    users = seeded_data["users"]
    profiles = seeded_data["profiles"]
    objects = seeded_data["objects"]

    cases = [
        ("/", None),
        ("/mainpage.html", None),
        ("/About_us/", None),
        ("/Aids/", None),
        ("/Cancer/", None),
        ("/Covid-19/", None),
        ("/Diabetes/", None),
        ("/FAQS/", None),
        ("/Heart_disorder/", None),
        ("/Hypertension/", None),
        ("/Inside_health_records/", None),
        ("/medical_practitioners/How_to_use", None),
        ("/friends-and-family/How_to_use", None),
        ("/login/", None),
        ("/doctor/doctorRegister/", None),
        ("/patientRegister/", None),
        ("/insurance/register/", None),
        ("/insurance/login/", None),
        ("/labtests/register/", None),
        ("/labtests/login/", None),
        ("/medical/register/", None),
        ("/medical/login/", None),
        ("/billing/register/", None),
        ("/organ_donation/", None),
        ("/performance-scores/", None),
        ("/organ-metrics/", None),

        ("/patientProfile/", "patient"),
        ("/patientRecords/", "patient"),
        ("/patientvitals/", "patient"),
        ("/editPatient/", "patient"),
        ("/editPatientVitals/", "patient"),
        ("/LabReports/", "patient"),
        ("/Medications/", "patient"),
        ("/create_insurance/", "patient"),
        ("/my_insurance/", "patient"),
        ("/labtests/", "patient"),
        (f"/labtest/{objects['lab_test'].id}/", "patient"),

        ("/doctor/profile/", "doctor"),
        ("/doctor/createDoctorProfile/", "doctor"),
        ("/doctor/PatientList/", "doctor"),
        (f"/doctor/pat_profile/{profiles['patient'].id}", "doctor"),
        (f"/doctor/newReport/{profiles['patient'].id}", "doctor"),
        ("/doctor/editdocprofile/", "doctor"),
        ("/doctor/clinic/create/", "doctor"),
        ("/doctor/clinic/login/", "doctor"),
        ("/doctor/clinic/dashboard/", "doctor"),
        (f"/doctor/labtest/{objects['lab_test'].id}/detail/", "doctor"),
        ("/doctor/insurances/", "doctor"),
        ("/doctor/labtests/", "doctor"),
        ("/doctor/prescriptions/", "doctor"),
        ("/doctor/billings/", "doctor"),
        ("/doctor/medical/", "doctor"),

        ("/insurance/profile/", "insurance"),
        ("/insurance/profile/edit/", "insurance"),
        ("/insurance/dashboard/", "insurance"),
        (f"/insurance/claim/{objects['insurance'].id}/", "insurance"),
        ("/insurance/approved/", "insurance"),
        ("/insurance/rejected/", "insurance"),
        ("/insurance/policies/", "insurance"),
        ("/insurance/policies/NAT_SCH_001/", "insurance"),

        ("/labtests/profile/", "labstaff"),
        ("/labtests/profile/edit/", "labstaff"),
        ("/labtests/dashboard/", "labstaff"),
        (f"/labtests/test/{objects['lab_test'].id}/", "labstaff"),
        ("/labtests/tests/approved/", "labstaff"),
        ("/labtests/tests/rejected/", "labstaff"),
        ("/labtests/records/", "labstaff"),
        (f"/labtests/labtest/{objects['lab_test'].id}/update/", "labstaff"),
        ("/labtests/billing/history/", "labstaff"),

        ("/medical/profile/", "medical"),
        ("/medical/profile/edit/", "medical"),
        ("/medical/dashboard/", "medical"),
        ("/medical/billing/history/", "medical"),
        (f"/medical/prescription/{objects['prescription'].id}/", "medical"),
        ("/medical/prescription/history/", "medical"),
        ("/medical/medicines/", "medical"),
        ("/medical/medicines/create/", "medical"),
        (f"/medical/medicines/{objects['medicine'].id}/update/", "medical"),
        (f"/medical/medicines/{objects['medicine'].id}/delete/", "medical"),

        ("/billing/profile/", "accountant"),
        ("/billing/bills/unpaid/", "accountant"),
        (f"/billing/bill/{objects['billing'].id}/update/", "accountant"),
        ("/billing/bills/history/", "accountant"),

        ("/organ_donation/", "patient"),
        ("/organ_donation/donations/", "patient"),
        (f"/organ_donation/donations/{objects['donation'].id}/", "patient"),
        ("/organ_donation/donations/register/", "patient"),
        ("/organ_donation/my-donations/", "patient"),
        ("/organ_donation/matched-donations/", "patient"),
        (f"/organ_donation/donations/{objects['donation'].id}/recipient-info/", "patient"),
        (f"/organ_donation/donations/{objects['donation'].id}/confirm-transplant/", "patient"),
        (f"/organ_donation/donations/{objects['donation'].id}/cancel/", "patient"),
        ("/organ_donation/requests/", "patient"),
        (f"/organ_donation/requests/{objects['request'].id}/", "patient"),
        ("/organ_donation/requests/new/", "patient"),
        ("/organ_donation/my-requests/", "patient"),
        (f"/organ_donation/requests/{objects['request'].id}/cancel/", "patient"),
        (f"/organ_donation/donations/{objects['donation'].id}/requests/{objects['request'].id}/accept/", "patient"),
        (f"/organ_donation/requests/{objects['request'].id}/donor-accept/", "patient"),
        ("/organ_donation/transactions/", "patient"),
    ]

    for path, role in cases:
        client.logout()
        if role:
            client.force_login(users[role])
        response = client.get(path)
        assert response.status_code < 500, f"GET {path} returned {response.status_code}"


@pytest.mark.django_db
def test_search_bar_post(client):
    response = client.post("/searchBar/", {"searchBar": "test"})
    assert response.status_code < 500
