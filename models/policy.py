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

    def is_command_allowed(self, user: str, command: str) -> tuple[bool, str]:
        """Check if a command is allowed for a user.
        
        Returns: (is_allowed: bool, reason: str)
        """
        user_obj = self.data.get('users', {}).get(user)
        if not user_obj:
            return True, 'ok'  # If user not in policy, allow command
        
        blocked_commands = user_obj.get('blocked_commands', [])
        cmd_stripped = command.strip()
        
        # Extract the base command (first word)
        cmd_base = cmd_stripped.split()[0] if cmd_stripped else ''
        
        # Check if command matches any blocked pattern
        for blocked in blocked_commands:
            blocked_base = blocked.split()[0] if blocked else ''
            
            # Exact match (e.g., "rm -rf" matches "rm -rf" exactly)
            if cmd_stripped == blocked:
                return False, f'Command "{command}" is blocked'
            
            # Base command match (e.g., "rm" blocks any "rm" command like "rm file.txt")
            if cmd_base == blocked_base:
                return False, f'Command "{command}" matches blocked command "{blocked}"'
            
            # Prefix match for multi-word blocks (e.g., "sudo su -" blocks "sudo su - user")
            if cmd_stripped.startswith(blocked + ' ') or cmd_stripped.startswith(blocked + '\t'):
                return False, f'Command "{command}" matches blocked pattern "{blocked}"'
        
        return True, 'ok'