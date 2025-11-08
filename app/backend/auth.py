"""Very small Zero Trust auth stub for prototype.
It performs local checks: key file exists, policy allows host/user, and returns a tuple (ok, reason).
"""
import os
from app.models.policy import PolicyStore


class ZeroTrustAuth:
    def __init__(self, policy_path: str = 'policies.json'):
        self.policy = PolicyStore(policy_path)


    def pre_check(self, user: str, host: str, keypath: str = None):
        # Check key existence if provided
        if keypath:
            if not os.path.exists(keypath):
                return False, 'private key not found'


        # Basic policy check
        allowed = self.policy.is_allowed(user=user, host=host)
        if not allowed:
            return False, 'policy disallows access to this host for this user'


        # Placeholder for additional checks (device fingerprint, geolocation, etc.)
        return True, 'ok'