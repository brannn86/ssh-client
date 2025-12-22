"""Very small Zero Trust auth stub for prototype.
It performs local checks: key file exists, policy allows host/user, and returns a tuple (ok, reason).
"""
import os
from models.policy import PolicyStore

# local DB helpers for logging failed authentication
try:
    from db.db import log_login_attempt
except Exception:
    # relative import fallback if package layout differs
    try:
        from ..db.db import log_login_attempt
    except Exception:
        # if import fails, define a no-op function
        def log_login_attempt(*args, **kwargs):
            pass


class ZeroTrustAuth:
    def __init__(self, policy_path: str = 'policies.json'):
        self.policy = PolicyStore(policy_path)
        self.debug_bypass = False  # DEBUG: Set to True to bypass policy checks


    def pre_check(self, user: str, host: str, keypath: str = None):
        # DEBUG: Bypass all checks if debug_bypass is enabled
        if self.debug_bypass:
            return True, 'DEBUG: Policy check bypassed'

        # Check key existence if provided
        if keypath:
            if not os.path.exists(keypath):
                reason = 'private key not found'
                try:
                    log_login_attempt(user, host, status='failed', reason=reason)
                except Exception:
                    pass
                return False, reason


        # Basic policy check
        allowed = self.policy.is_allowed(user=user, host=host)
        if not allowed:
            reason = 'policy disallows access to this host for this user'
            try:
                log_login_attempt(user, host, status='failed', reason=reason)
            except Exception:
                pass
            return False, reason


        # Placeholder for additional checks (device fingerprint, geolocation, etc.)
        return True, 'ok'

    def toggle_debug_bypass(self):
        """DEBUG: Toggle policy bypass for debugging."""
        self.debug_bypass = not self.debug_bypass
        return self.debug_bypass