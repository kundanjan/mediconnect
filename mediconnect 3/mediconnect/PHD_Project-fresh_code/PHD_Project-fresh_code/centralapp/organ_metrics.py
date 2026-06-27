from django.utils import timezone
from organ_donation.models import OrganDonation, OrganRequest, OrganTransaction, OrganType, BloodType


class OrganMetrics:
    def get_all_metrics(self):
        now = timezone.now()
        donations = OrganDonation.objects.all()
        requests = OrganRequest.objects.all()
        transactions = OrganTransaction.objects.all()
        organ_types = OrganType.objects.all()

        total_donations = donations.count()
        total_requests = requests.count()
        total_transactions = transactions.count()

        available = donations.filter(status='available').count()
        matched_d = donations.filter(status='matched').count()
        completed_d = donations.filter(status='completed').count()
        cancelled_d = donations.filter(status='cancelled').count()

        pending_r = requests.filter(status='pending').count()
        accepted_r = requests.filter(status='accepted').count()
        completed_r = requests.filter(status='completed').count()
        rejected_r = requests.filter(status='rejected').count()

        completed_tx = transactions.filter(status='completed').count()
        avg_success = 0.0
        if completed_tx > 0:
            success_sum = sum(t.success_rate for t in transactions.filter(status='completed'))
            avg_success = round(success_sum / completed_tx, 1)

        matching_accuracy = 0.0
        if total_donations > 0:
            matching_accuracy = round((matched_d + completed_d) / total_donations * 100, 1)

        match_rate = 0.0
        if total_requests > 0:
            match_rate = round((accepted_r + completed_r) / total_requests * 100, 1)

        allocation_times = []
        for d in donations.filter(status__in=['matched', 'completed']):
            if d.matched_request and d.available_from:
                delta = (d.matched_request.created_at - d.available_from).total_seconds()
                if delta >= 0:
                    allocation_times.append(delta)
        avg_allocation_sec = 0.0
        avg_allocation_days = 0.0
        if allocation_times:
            avg_allocation_sec = round(sum(allocation_times) / len(allocation_times), 1)
            avg_allocation_days = round(avg_allocation_sec / 86400, 1)

        urgent_requests = requests.filter(urgency__in=['high', 'critical']).count()
        urgent_fulfilled = requests.filter(
            urgency__in=['high', 'critical'],
            status__in=['accepted', 'completed', 'engaged']
        ).count()
        urgent_fulfill_rate = 0.0
        if urgent_requests > 0:
            urgent_fulfill_rate = round(urgent_fulfilled / urgent_requests * 100, 1)

        unique_donors = donations.values('donor').distinct().count()
        unique_recipients = requests.values('requester').distinct().count()
        fairness_index = 0.0
        if total_donations > 0 and unique_recipients > 0:
            per_recipient = completed_d / unique_recipients
            fairness_index = round(min(per_recipient / 2.0, 1.0), 2)

        organ_breakdown = []
        for ot in organ_types:
            count = donations.filter(organ_type=ot).count()
            if count > 0:
                organ_breakdown.append({'name': str(ot), 'count': count})

        blood_distribution = []
        for bt in BloodType.objects.all():
            count = donations.filter(blood_type=bt).count()
            if count > 0:
                blood_distribution.append({'type': bt.blood_type, 'count': count})

        urgency_distribution = []
        for label in ['low', 'medium', 'high', 'critical']:
            cnt = requests.filter(urgency=label).count()
            urgency_distribution.append({'label': label.capitalize(), 'count': cnt})

        status_distribution = {
            'donations': {
                'Available': available,
                'Matched': matched_d,
                'Completed': completed_d,
                'Cancelled': cancelled_d,
            },
            'requests': {
                'Pending': pending_r,
                'Accepted': accepted_r,
                'Completed': completed_r,
                'Rejected': rejected_r,
            },
        }

        return {
            'overview': {
                'total_donations': total_donations,
                'total_requests': total_requests,
                'total_transactions': total_transactions,
                'unique_donors': unique_donors,
                'unique_recipients': unique_recipients,
            },
            'performance': {
                'matching_accuracy_pct': matching_accuracy,
                'match_rate_pct': match_rate,
            'avg_allocation_time_sec': avg_allocation_sec,
            'avg_allocation_time_days': avg_allocation_days,
            'avg_success_rate_pct': avg_success,
                'urgent_fulfill_rate_pct': urgent_fulfill_rate,
                'fairness_index': fairness_index,
            },
            'breakdown': {
                'organ_distribution': organ_breakdown,
                'blood_distribution': blood_distribution,
                'urgency_distribution': urgency_distribution,
                'status_distribution': status_distribution,
            },
        }
