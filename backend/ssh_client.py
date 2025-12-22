import os
import paramiko
import socket
from typing import Optional

# local DB helpers
try:
    from db.db import log_session_start, log_session_end, log_event, log_login_attempt
except Exception:
    # relative import fallback if package layout differs
    try:
        from ..db.db import log_session_start, log_session_end, log_event, log_login_attempt
    except Exception:
        # define no-ops if import fails
        def log_session_start(*args, **kwargs):
            return None
        def log_session_end(*args, **kwargs):
            pass
        def log_event(*args, **kwargs):
            pass
        def log_login_attempt(*args, **kwargs):
            pass


class SSHClientManager:
    def __init__(self):
        self.client = None
        # collected debug info about key loading attempts (list of dicts)
        self.debug_key_attempts = []
        # current active session id in DB (None when not connected)
        self.active_session_id = None


    def open_session(self, host: str, port: int = 22, username: str = None,
                     key_filename: Optional[str] = None, key_passphrase: Optional[str] = None):
        """Open SSH connection and return a channel if successful.

        If the provided private key file is encrypted, you can pass the
        optional `key_passphrase` so the key can be loaded and supplied as a
        PKey to Paramiko. This supports ed25519 keys via Paramiko's
        Ed25519Key.from_private_key_file (Paramiko >= 2.11).
        """
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # reset debug attempts for this connection try
        self.debug_key_attempts = []
        try:
            connect_kwargs = dict(hostname=host, port=port, username=username, timeout=5)
            if key_filename:
                # First attempt: let Paramiko handle the key_filename (agent/ssh config fallback)
                connect_kwargs['key_filename'] = key_filename

            def _load_private_key(path: str, password: Optional[str]):
                """Attempt to load a private key file as different key types.

                Returns a Paramiko PKey instance on success, or raises the last
                exception if all attempts fail.
                """
                # record attempts for debugging (do not store passphrase)
                last_exc = None
                attempted = []
                loaders = [
                    ('ed25519', getattr(paramiko, 'Ed25519Key', None)),
                    ('rsa', getattr(paramiko, 'RSAKey', None)),
                    ('ecdsa', getattr(paramiko, 'ECDSAKey', None)),
                    ('dss', getattr(paramiko, 'DSSKey', None)),
                ]
                for name, cls in loaders:
                    if cls is None:
                        continue
                    # Try with provided password first (if any), then without
                    try_variants = []
                    if password is not None:
                        try_variants.append(password)
                        try_variants.append(None)
                    else:
                        try_variants.append(None)

                    for pw in try_variants:
                        try:
                            # record attempt (only whether pw was used)
                            attempted.append({'path': path, 'loader': name, 'used_password': pw is not None})
                            pkey = cls.from_private_key_file(path, password=pw)
                            # successful load: store debug info and return
                            self.debug_key_attempts.append({'path': path, 'loader': name, 'used_password': pw is not None, 'result': 'ok'})
                            return pkey
                        except Exception as e:
                            last_exc = e
                            # record failure
                            attempted.append({'path': path, 'loader': name, 'used_password': pw is not None, 'error': str(e)})
                            # try next variant/loader
                            continue
                # store aggregate attempts for the path
                if attempted:
                    self.debug_key_attempts.append({'path': path, 'attempts': attempted})
                # If we reach here, no loader succeeded
                raise last_exc if last_exc is not None else ValueError('Unable to load private key')

            # Try normal connect first
            try:
                self.client.connect(**connect_kwargs)
            except paramiko.ssh_exception.PasswordRequiredException:
                # Key is encrypted and Paramiko needs a passphrase
                if not key_passphrase:
                    raise

                # If a specific key file was provided, try loading it with the passphrase
                if key_filename:
                    pkey = _load_private_key(key_filename, key_passphrase)
                    self.client.connect(hostname=host, port=port, username=username, pkey=pkey, timeout=5)
                else:
                    # No key path provided: scan common default key files in ~/.ssh
                    default_files = [
                        os.path.expanduser('~/.ssh/id_ed25519'),
                        os.path.expanduser('~/.ssh/id_rsa'),
                        os.path.expanduser('~/.ssh/id_ecdsa'),
                        os.path.expanduser('~/.ssh/id_dsa'),
                    ]
                    found = False
                    for fpath in default_files:
                        if os.path.exists(fpath):
                            try:
                                pkey = _load_private_key(fpath, key_passphrase)
                                # use a fresh SSHClient for each attempt to avoid state issues
                                try:
                                    self.client.close()
                                except Exception:
                                    pass
                                self.client = paramiko.SSHClient()
                                self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                                try:
                                    self.client.connect(hostname=host, port=port, username=username, pkey=pkey, timeout=5)
                                    found = True
                                    break
                                except paramiko.ssh_exception.AuthenticationException:
                                    # key not accepted by server; try next key file
                                    continue
                                except Exception:
                                    # other SSH/connect error, try next file
                                    continue
                            except Exception:
                                # key load failed: try next file
                                continue
                    if not found:
                        # nothing worked; re-raise a helpful exception
                        raise paramiko.SSHException('Encrypted private key; passphrase provided but no usable key found')
            except paramiko.SSHException as e:
                # Older Paramiko versions may raise SSHException with message
                # mentioning 'encrypted' for encrypted keys — try to handle that.
                if 'encrypted' in str(e).lower() and key_passphrase:
                    # prefer explicit key_filename if given
                    try:
                        if key_filename and os.path.exists(key_filename):
                            pkey = _load_private_key(key_filename, key_passphrase)
                            self.client.connect(hostname=host, port=port, username=username, pkey=pkey, timeout=5)
                        else:
                            # scan default keys
                            default_files = [
                                os.path.expanduser('~/.ssh/id_ed25519'),
                                os.path.expanduser('~/.ssh/id_rsa'),
                                os.path.expanduser('~/.ssh/id_ecdsa'),
                                os.path.expanduser('~/.ssh/id_dsa'),
                            ]
                            for fpath in default_files:
                                if os.path.exists(fpath):
                                    try:
                                        pkey = _load_private_key(fpath, key_passphrase)
                                        try:
                                            self.client.close()
                                        except Exception:
                                            pass
                                        self.client = paramiko.SSHClient()
                                        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                                        try:
                                            self.client.connect(hostname=host, port=port, username=username, pkey=pkey, timeout=5)
                                            break
                                        except paramiko.ssh_exception.AuthenticationException:
                                            # not accepted, try next
                                            continue
                                        except Exception:
                                            continue
                                    except Exception:
                                        continue
                    except Exception:
                        raise
                else:
                    raise

            transport = self.client.get_transport()
            if transport and transport.is_active():
                chan = transport.open_session()
                chan.get_pty()
                chan.invoke_shell()
                # record session start in DB (username/host available in args)
                try:
                    # store session id for later event logging and end marking
                    self.active_session_id = log_session_start(username, host)
                except Exception:
                    # non-fatal: don't break the connection if logging fails
                    self.active_session_id = None
                return chan
            return None
        except (paramiko.ssh_exception.AuthenticationException) as e:
            # log failed SSH authentication
            try:
                log_login_attempt(username, host, port=port, status='failed', reason=f'SSH auth failed: {str(e)}')
            except Exception:
                pass
            raise e
        except (socket.error, paramiko.SSHException) as e:
            # log other connection errors
            try:
                log_login_attempt(username, host, port=port, status='failed', reason=f'SSH connection error: {str(e)}')
            except Exception:
                pass
            raise e


    def close(self):
        if self.client:
            self.client.close()
            self.client = None
        # mark session end in DB if we have an active session id
        try:
            if getattr(self, 'active_session_id', None) is not None:
                log_session_end(self.active_session_id, status='closed')
                self.active_session_id = None
        except Exception:
            pass

    def log_command(self, command_text: str):
        """Log an executed command (or other event) associated with the active session."""
        try:
            sid = getattr(self, 'active_session_id', None)
            if sid is not None:
                # include a short prefix so events are clear
                log_event(sid, f'cmd: {command_text}')
        except Exception:
            # swallow DB errors to avoid breaking terminal I/O
            pass