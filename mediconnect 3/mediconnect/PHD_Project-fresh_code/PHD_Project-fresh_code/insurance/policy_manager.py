import json
import os
from typing import Dict, List, Any, Optional
from django.conf import settings


class IndianHealthPolicyManager:
    def __init__(self, policies_file: str = None):
        self.policies_file = policies_file or self._get_default_policies_file()
        self.policy_data = self._load_policy_data()

    def _get_default_policies_file(self) -> str:
        paths = [
            os.path.join(settings.BASE_DIR, 'policy.json'),
            os.path.join(settings.BASE_DIR, '..', 'policy.json'),
        ]
        for path in paths:
            if os.path.exists(path):
                return path
        raise FileNotFoundError("policies.json not found in project. Please ensure it exists at the project root.")

    def _load_policy_data(self) -> Dict[str, Any]:
        try:
            with open(self.policies_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise Exception(f"Failed to load policies: {str(e)}")

    def get_all_policies(self) -> List[Dict[str, Any]]:
        all_policies = []
        national_policies = self.policy_data.get('national_baseline_policies', [])
        for policy in national_policies:
            policy_copy = policy.copy()
            policy_copy['scope'] = 'National'
            policy_copy['state_name'] = None
            policy_copy['state_code'] = None
            all_policies.append(policy_copy)
        states_policies = self.policy_data.get('states_welfare_policies', [])
        for state in states_policies:
            state_name = state.get('state_name')
            state_code = state.get('state_code')
            for policy in state.get('policies', []):
                policy_copy = policy.copy()
                policy_copy['scope'] = 'State'
                policy_copy['state_name'] = state_name
                policy_copy['state_code'] = state_code
                all_policies.append(policy_copy)
        return all_policies

    def get_policy_by_id(self, policy_id: str) -> Optional[Dict[str, Any]]:
        for policy in self.get_all_policies():
            if policy.get('policy_id') == policy_id:
                return policy
        return None

    def get_policies_by_category(self, category: str) -> List[Dict[str, Any]]:
        category_lower = category.lower()
        return [
            p for p in self.get_all_policies()
            if category_lower in p.get('category', '').lower()
        ]

    def get_policies_by_state(self, state_name: str) -> List[Dict[str, Any]]:
        state_lower = state_name.lower()
        return [
            p for p in self.get_all_policies()
            if p.get('scope') == 'State' and p.get('state_name', '').lower() == state_lower
        ]

    def get_categories(self) -> List[str]:
        categories = set()
        for policy in self.get_all_policies():
            cat = policy.get('category', 'Unknown')
            categories.add(cat)
        return sorted(categories)

    def get_states(self) -> List[str]:
        states = set()
        for policy in self.get_all_policies():
            if policy.get('scope') == 'State' and policy.get('state_name'):
                states.add(policy['state_name'])
        return sorted(states)

    def get_coverage_summary(self) -> Dict[str, Any]:
        all_policies = self.get_all_policies()
        national_count = len([p for p in all_policies if p.get('scope') == 'National'])
        state_count = len([p for p in all_policies if p.get('scope') == 'State'])
        categories = {}
        for policy in all_policies:
            cat = policy.get('category', 'Unknown')
            categories[cat] = categories.get(cat, 0) + 1
        return {
            'total_policies': len(all_policies),
            'national_policies': national_count,
            'state_policies': state_count,
            'categories': categories,
            'states_covered': list(set(p.get('state_name') for p in all_policies if p.get('state_name'))),
        }
