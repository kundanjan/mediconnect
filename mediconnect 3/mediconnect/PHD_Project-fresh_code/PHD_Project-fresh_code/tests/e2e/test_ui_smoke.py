import json
import os
import re
from pathlib import Path

import pytest
from playwright.sync_api import expect


BASE_URL = os.getenv("E2E_BASE_URL", "http://127.0.0.1:8000")
TEST_PASSWORD = "TestPass123!"


def _load_seeded_ids():
    root = Path(__file__).resolve().parents[2]
    ids_path = root / "scripts" / "seeded_ids.json"
    if ids_path.exists():
        with ids_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    return {}


SEED_IDS = _load_seeded_ids()


def _id(name, default=1):
    return SEED_IDS.get(name, default)


def _assert_ok(response):
    assert response is not None and response.status < 400


@pytest.mark.e2e
def test_public_pages(page):
    response = page.goto(f"{BASE_URL}/")
    _assert_ok(response)

    response = page.goto(f"{BASE_URL}/About_us/")
    _assert_ok(response)

    response = page.goto(f"{BASE_URL}/FAQS/")
    _assert_ok(response)

    response = page.goto(f"{BASE_URL}/performance-scores/")
    _assert_ok(response)

    response = page.goto(f"{BASE_URL}/organ-metrics/")
    _assert_ok(response)


@pytest.mark.e2e
def test_insurance_login_and_dashboard(page):
    response = page.goto(f"{BASE_URL}/insurance/login/")
    _assert_ok(response)

    page.fill("input[name='username']", "insurance1")
    page.fill("input[name='password']", TEST_PASSWORD)
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle")

    expect(page).to_have_url(re.compile(r"/insurance/"))
    response = page.goto(f"{BASE_URL}/insurance/dashboard/")
    _assert_ok(response)

    insurance_id = _id("insurance_id")
    for url in [
        "/insurance/profile/",
        "/insurance/profile/edit/",
        f"/insurance/claim/{insurance_id}/",
        "/insurance/approved/",
        "/insurance/rejected/",
        "/insurance/policies/",
        "/insurance/policies/NAT_SCH_001/",
    ]:
        response = page.goto(f"{BASE_URL}{url}")
        _assert_ok(response)


@pytest.mark.e2e
def test_medical_login_and_dashboard(page):
    response = page.goto(f"{BASE_URL}/medical/login/")
    _assert_ok(response)

    page.fill("input[name='username']", "medical1")
    page.fill("input[name='password']", TEST_PASSWORD)
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle")

    expect(page).to_have_url(re.compile(r"/medical/"))
    response = page.goto(f"{BASE_URL}/medical/dashboard/")
    _assert_ok(response)

    prescription_id = _id("prescription_id")
    medicine_id = _id("medicine_id")
    for url in [
        "/medical/profile/",
        "/medical/profile/edit/",
        "/medical/billing/history/",
        f"/medical/prescription/{prescription_id}/",
        "/medical/prescription/history/",
        "/medical/medicines/",
        "/medical/medicines/create/",
        f"/medical/medicines/{medicine_id}/update/",
        f"/medical/medicines/{medicine_id}/delete/",
    ]:
        response = page.goto(f"{BASE_URL}{url}")
        _assert_ok(response)


@pytest.mark.e2e
def test_labstaff_login_and_dashboard(page):
    response = page.goto(f"{BASE_URL}/labtests/login/")
    _assert_ok(response)

    page.fill("input[name='username']", "labstaff1")
    page.fill("input[name='password']", TEST_PASSWORD)
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle")

    expect(page).to_have_url(re.compile(r"/labtests/"))
    response = page.goto(f"{BASE_URL}/labtests/dashboard/")
    _assert_ok(response)

    lab_test_id = _id("lab_test_id")
    for url in [
        "/labtests/profile/",
        "/labtests/profile/edit/",
        f"/labtests/test/{lab_test_id}/",
        "/labtests/tests/approved/",
        "/labtests/tests/rejected/",
        "/labtests/records/",
        "/labtests/billing/history/",
    ]:
        response = page.goto(f"{BASE_URL}{url}")
        _assert_ok(response)


@pytest.mark.e2e
def test_patient_login_and_pages(page):
    response = page.goto(f"{BASE_URL}/login/")
    _assert_ok(response)

    page.fill("input[name='username']", "patient1")
    page.fill("input[name='password']", TEST_PASSWORD)
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle")

    expect(page).to_have_url(re.compile(r"/patientProfile/"))

    lab_test_id = _id("lab_test_id")
    for url in [
        "/patientProfile/",
        "/patientRecords/",
        "/patientvitals/",
        "/editPatient/",
        "/editPatientVitals/",
        "/LabReports/",
        "/Medications/",
        "/create_insurance/",
        "/my_insurance/",
        "/labtests/",
        f"/labtest/{lab_test_id}/",
    ]:
        response = page.goto(f"{BASE_URL}{url}")
        _assert_ok(response)


@pytest.mark.e2e
def test_doctor_login_and_pages(page):
    response = page.goto(f"{BASE_URL}/login/")
    _assert_ok(response)

    page.fill("input[name='username']", "doctor1")
    page.fill("input[name='password']", TEST_PASSWORD)
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle")

    expect(page).to_have_url(re.compile(r"/doctor/profile/"))

    patient_id = _id("patient_profile_id")
    lab_test_id = _id("lab_test_id")
    for url in [
        "/doctor/profile/",
        "/doctor/PatientList/",
        f"/doctor/pat_profile/{patient_id}",
        f"/doctor/newReport/{patient_id}",
        "/doctor/editdocprofile/",
        "/doctor/clinic/login/",
        "/doctor/clinic/dashboard/",
        f"/doctor/labtest/{lab_test_id}/detail/",
        "/doctor/insurances/",
        "/doctor/labtests/",
        "/doctor/prescriptions/",
        "/doctor/billings/",
        "/doctor/medical/",
    ]:
        response = page.goto(f"{BASE_URL}{url}")
        _assert_ok(response)


@pytest.mark.e2e
def test_accountant_login_and_pages(page):
    response = page.goto(f"{BASE_URL}/login/")
    _assert_ok(response)

    page.fill("input[name='username']", "accountant1")
    page.fill("input[name='password']", TEST_PASSWORD)
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle")

    expect(page).to_have_url(re.compile(r"/billing/profile/"))

    billing_id = _id("billing_id")
    for url in [
        "/billing/profile/",
        "/billing/bills/unpaid/",
        f"/billing/bill/{billing_id}/update/",
        "/billing/bills/history/",
    ]:
        response = page.goto(f"{BASE_URL}{url}")
        _assert_ok(response)


@pytest.mark.e2e
def test_clinic_login(page):
    response = page.goto(f"{BASE_URL}/doctor/clinic/login/")
    _assert_ok(response)

    page.fill("input[name='username']", "clinicadmin")
    page.fill("input[name='password']", TEST_PASSWORD)
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle")

    expect(page).to_have_url(re.compile(r"/doctor/clinic/dashboard/"))


@pytest.mark.e2e
def test_organ_donation_pages(page):
    response = page.goto(f"{BASE_URL}/login/")
    _assert_ok(response)

    page.fill("input[name='username']", "patient1")
    page.fill("input[name='password']", TEST_PASSWORD)
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle")

    donation_id = _id("donation_id")
    request_id = _id("request_id")
    for url in [
        "/organ_donation/",
        "/organ_donation/donations/",
        f"/organ_donation/donations/{donation_id}/",
        "/organ_donation/donations/register/",
        "/organ_donation/my-donations/",
        "/organ_donation/matched-donations/",
        f"/organ_donation/donations/{donation_id}/recipient-info/",
        f"/organ_donation/donations/{donation_id}/confirm-transplant/",
        f"/organ_donation/donations/{donation_id}/cancel/",
        "/organ_donation/requests/",
        f"/organ_donation/requests/{request_id}/",
        "/organ_donation/requests/new/",
        "/organ_donation/my-requests/",
        f"/organ_donation/requests/{request_id}/cancel/",
        f"/organ_donation/donations/{donation_id}/requests/{request_id}/accept/",
        f"/organ_donation/requests/{request_id}/donor-accept/",
        "/organ_donation/transactions/",
    ]:
        response = page.goto(f"{BASE_URL}{url}")
        _assert_ok(response)
