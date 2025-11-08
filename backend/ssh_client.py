import paramiko
import socket
from typing import Optional


class SSHClientManager:
    def __init__(self):
        self.client = None


    def open_session(self, host: str, port: int = 22, username: str = None, key_filename: Optional[str] = None):
        """Open SSH connection and return a channel if successful."""
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            connect_kwargs = dict(hostname=host, port=port, username=username, timeout=5)
            if key_filename:
                connect_kwargs['key_filename'] = key_filename
            else:
                # fallback to agent/ssh config
                pass


            self.client.connect(**connect_kwargs)
            transport = self.client.get_transport()
            if transport and transport.is_active():
                chan = transport.open_session()
                chan.get_pty()
                chan.invoke_shell()
                return chan
            return None
        except (paramiko.ssh_exception.AuthenticationException) as e:
            raise e
        except (socket.error, paramiko.SSHException) as e:
            raise e


    def close(self):
        if self.client:
            self.client.close()
            self.client = None