from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from organ_donation.models import OrganType, BloodType, OrganDonation, OrganRequest, OrganTransaction, DoctorApproval
from patient.models import PatientProfile
from doctor.models import DoctorProfile


class Command(BaseCommand):
    help = 'Seed organ donation data with matched/completed donations and transactions'

    def handle(self, *args, **options):
        now = timezone.now()

        organ_types = {ot.name: ot for ot in OrganType.objects.all()}
        blood_types = {bt.blood_type: bt for bt in BloodType.objects.all()}
        patients = list(PatientProfile.objects.all())

        if not patients or len(patients) < 3:
            self.stdout.write(self.style.WARNING('Need at least 3 patient profiles. Run seed_test_data first.'))
            return

        donor_patients = patients[:3]
        recipient1 = patients[0]
        recipient2 = patients[-1] if len(patients) > 1 else patients[0]
        recipient3 = patients[1] if len(patients) > 1 else patients[0]

        doctor = DoctorProfile.objects.first()

        kidney = organ_types.get('kidney')
        liver = organ_types.get('liver')
        heart = organ_types.get('heart')
        lung = organ_types.get('lung')
        cornea = organ_types.get('cornea')

        o_plus = blood_types.get('O+')
        a_plus = blood_types.get('A+')
        b_plus = blood_types.get('B+')
        ab_plus = blood_types.get('AB+')
        o_minus = blood_types.get('O-')

        self.stdout.write('Seeding organ donations...')

        # Create various organ types if missing
        if not liver:
            liver, _ = OrganType.objects.get_or_create(name='liver', defaults={'description': 'Liver'})
        if not heart:
            heart, _ = OrganType.objects.get_or_create(name='heart', defaults={'description': 'Heart'})
        if not lung:
            lung, _ = OrganType.objects.get_or_create(name='lung', defaults={'description': 'Lung'})
        if not cornea:
            cornea, _ = OrganType.objects.get_or_create(name='cornea', defaults={'description': 'Cornea'})

        # ===== DONATIONS =====
        # Kidney from donor1 - available
        d1, _ = OrganDonation.objects.get_or_create(
            donor=donor_patients[0],
            organ_type=kidney,
            defaults={
                'blood_type': o_plus,
                'health_condition': 'Healthy donor',
                'age_at_donation': 35,
                'status': 'available',
                'created_at': now - timedelta(days=30),
                'available_from': now - timedelta(days=30),
            }
        )

        # Liver from donor2 - matched
        r1, _ = OrganRequest.objects.get_or_create(
            requester=recipient1,
            organ_type=liver,
            defaults={
                'blood_type': a_plus,
                'medical_condition': 'Liver cirrhosis',
                'age_at_request': 45,
                'urgency': 'high',
                'status': 'pending' if not a_plus else 'pending',
                'created_at': now - timedelta(days=20),
            }
        )

        d2, created_d2 = OrganDonation.objects.get_or_create(
            donor=donor_patients[1],
            organ_type=liver,
            defaults={
                'blood_type': a_plus,
                'health_condition': 'Healthy liver donor',
                'age_at_donation': 28,
                'status': 'matched',
                'created_at': now - timedelta(days=25),
                'available_from': now - timedelta(days=25),
            }
        )
        if created_d2:
            r1.status = 'accepted'
            r1.matched_donation = d2
            r1.save()
            d2.matched_request = r1
            d2.save()

        # Heart from donor3 - completed
        d3, created_d3 = OrganDonation.objects.get_or_create(
            donor=donor_patients[2],
            organ_type=heart,
            defaults={
                'blood_type': o_minus,
                'health_condition': 'Heart donor',
                'age_at_donation': 32,
                'status': 'completed',
                'created_at': now - timedelta(days=60),
                'available_from': now - timedelta(days=60),
            }
        )

        r2, created_r2 = OrganRequest.objects.get_or_create(
            requester=recipient2,
            organ_type=heart,
            defaults={
                'blood_type': o_minus,
                'medical_condition': 'Heart failure',
                'age_at_request': 55,
                'urgency': 'critical',
                'status': 'completed',
                'created_at': now - timedelta(days=55),
            }
        )
        if created_d3 or created_r2:
            r2.matched_donation = d3
            d3.matched_request = r2
            r2.save()
            d3.save()

        # Completed transaction for heart
        tx, _ = OrganTransaction.objects.get_or_create(
            donation=d3,
            request=r2,
            defaults={
                'donor': donor_patients[2],
                'recipient': recipient2,
                'status': 'completed',
                'organ_type': heart,
                'success_rate': 85.0,
                'notes': 'Successful heart transplant',
                'created_at': now - timedelta(days=50),
                'completed_at': now - timedelta(days=48),
            }
        )
        if doctor:
            DrApproval = DoctorApproval
            DrApproval.objects.get_or_create(
                donation=d3,
                request=r2,
                doctor=doctor,
                defaults={'status': 'approved', 'approval_date': now - timedelta(days=52)}
            )

        # Additional lung donation - available
        OrganDonation.objects.get_or_create(
            donor=recipient3,
            organ_type=lung,
            defaults={
                'blood_type': b_plus,
                'health_condition': 'Lung donor',
                'age_at_donation': 40,
                'status': 'available',
                'created_at': now - timedelta(days=10),
                'available_from': now - timedelta(days=10),
            }
        )

        # Cornea donation - cancelled
        OrganDonation.objects.get_or_create(
            donor=donor_patients[0],
            organ_type=cornea,
            defaults={
                'blood_type': o_plus,
                'health_condition': 'Cornea donor',
                'age_at_donation': 35,
                'status': 'cancelled',
                'created_at': now - timedelta(days=15),
                'available_from': now - timedelta(days=15),
            }
        )

        # Additional pending request
        OrganRequest.objects.get_or_create(
            requester=recipient3,
            organ_type=lung,
            defaults={
                'blood_type': b_plus,
                'medical_condition': 'Lung disease',
                'age_at_request': 50,
                'urgency': 'low',
                'status': 'pending',
                'created_at': now - timedelta(days=5),
            }
        )

        self.stdout.write(self.style.SUCCESS(f'Seeded organ donation data:'))
        self.stdout.write(f'  Donations: {OrganDonation.objects.count()}')
        self.stdout.write(f'  Requests: {OrganRequest.objects.count()}')
        self.stdout.write(f'  Transactions: {OrganTransaction.objects.count()}')
