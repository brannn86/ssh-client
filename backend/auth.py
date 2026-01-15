"""Very small Zero Trust auth stub for prototype.
It performs local checks: key file exists, policy allows host/user, and returns a tuple (ok, reason).
"""
import os
import json
from typing import Optional
from models.policy import PolicyStore

try:
    import pyotp
except ImportError:
    pyotp = None

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
    def __init__(self, policy_path: str = 'policies.json', totp_secrets_path: str = 'totp_secrets.json'):
        self.policy = PolicyStore(policy_path)
        self.debug_bypass = False  # DEBUG: Set to True to bypass policy checks
        self.totp_secrets_path = totp_secrets_path
        self.totp_secrets = self._load_totp_secrets()


    def _load_totp_secrets(self) -> dict:
        """Load TOTP secrets from file."""
        if os.path.exists(self.totp_secrets_path):
            try:
                with open(self.totp_secrets_path, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_totp_secrets(self):
        """Save TOTP secrets to file."""
        try:
            with open(self.totp_secrets_path, 'w') as f:
                json.dump(self.totp_secrets, f)
        except Exception:
            pass

    def generate_totp_secret(self, user: str) -> str:
        """Generate a new TOTP secret for a user and return provisioning URI."""
        if pyotp is None:
            return None
        
        secret = pyotp.random_base32()
        self.totp_secrets[user] = secret
        self._save_totp_secrets()
        
        # Return the provisioning URI for QR code generation
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(name=user, issuer_name='SSH Client')

    def verify_totp(self, user: str, code: str) -> bool:
        """Verify TOTP code for a user."""
        if pyotp is None or user not in self.totp_secrets:
            return False
        
        try:
            totp = pyotp.TOTP(self.totp_secrets[user])
            # Allow ±1 time window for clock skew
            return totp.verify(code, valid_window=1)
        except Exception:
            return False

    def get_totp_secret(self, user: str) -> Optional[str]:
        """Get the TOTP secret for a user (if it exists)."""
        return self.totp_secrets.get(user)

    def has_totp_enabled(self, user: str) -> bool:
        """Check if TOTP is enabled for a user."""
        return user in self.totp_secrets and pyotp is not None

    def ensure_totp_enabled(self, user: str) -> str:
        """Ensure TOTP is enabled for a user. If not, generate a secret.
        
        Returns the provisioning URI for QR code generation if a new secret was created,
        or None if TOTP was already enabled.
        """
        if pyotp is None:
            return None
        
        if user not in self.totp_secrets:
            # Generate new TOTP secret for this user
            return self.generate_totp_secret(user)
        
        return None  # TOTP already enabled

    def pre_check(self, user: str, host: str, keypath: str = None, totp_code: Optional[str] = None):
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

        # Ensure TOTP is enabled for this user (auto-generate if needed)
        provisioning_uri = self.ensure_totp_enabled(user)
        
        # TOTP is always required (auto-generated if new)
        if not totp_code:
            if provisioning_uri:
                # New TOTP secret created, include provisioning URI in response
                return False, f'TOTP setup required:{provisioning_uri}'
            else:
                return False, 'TOTP required'
        
        if not self.verify_totp(user, totp_code):
            try:
                log_login_attempt(user, host, status='failed', reason='invalid TOTP code')
            except Exception:
                pass
                return False, 'Invalid TOTP code'

        # Placeholder for additional checks (device fingerprint, geolocation, etc.)
        return True, 'ok'

    def toggle_debug_bypass(self):
        """DEBUG: Toggle policy bypass for debugging."""
        self.debug_bypass = not self.debug_bypass
        return self.debug_bypass