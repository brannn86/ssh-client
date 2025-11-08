"""Simple JSON-backed policy store."""
import json
import os
from typing import Any


SAMPLE_POLICY = {
    "users": {
        "bran": {
            "allowed_hosts": ["127.0.0.1", "localhost", "192.168.1.100"],
            "blocked_commands": ["rm -rf", "sudo su -"]
        }
    }
}


class PolicyStore:
    def __init__(self, path: str = 'policies.json'):
        self.path = path
        if not os.path.exists(self.path):
            with open(self.path, 'w') as f:
                json.dump(SAMPLE_POLICY, f, indent=2)
        self._load()


    def _load(self):
        with open(self.path, 'r') as f:
            self.data = json.load(f)


    def is_allowed(self, user: str, host: str) -> bool:
        user_obj = self.data.get('users', {}).get(user)
        if not user_obj:
            return False
        allowed = user_obj.get('allowed_hosts', [])
        return host in allowed or host == 'localhost'