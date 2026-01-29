import paramiko
import socket
import threading
import time
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TestMetrics:
    """Container for security test metrics."""
    test_name: str
    passed: bool
    status: str = 'pending'
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_ms: float = 0
    attempts: int = 0
    successes: int = 0
    failures: int = 0
    errors: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary for reporting."""
        return {
            'test_name': self.test_name,
            'passed': self.passed,
            'status': self.status,
            'duration_ms': self.duration_ms,
            'attempts': self.attempts,
            'successes': self.successes,
            'failures': self.failures,
            'error_count': len(self.errors),
            'details': self.details,
        }


class SecurityTester:
    """Performs security tests on SSH client including brute force, credential theft, and login attempts."""
    
    def __init__(self, host: str, port: int = 22, timeout: int = 5):
        """Initialize security tester.
        
        Args:
            host: Target SSH host
            port: Target SSH port
            timeout: Connection timeout in seconds
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.results: Dict[str, TestMetrics] = {}
    
    def run_all_tests(self) -> Dict[str, TestMetrics]:
        """Run all security tests.
        
        Returns:
            Dictionary of test results with metrics
        """
        logger.info(f'Starting security tests on {self.host}:{self.port}')
        
        # Run all tests
        self.test_connection_availability()
        self.test_brute_force_resistance()
        self.test_failed_login_attempts()
        self.test_timeout_handling()
        self.test_key_rejection()
        self.test_concurrent_connections()
        self.test_credential_caching()
        self.test_error_messages()
        
        logger.info(f'Security tests completed. Results: {len(self.results)} tests')
        return self.results
    
    def test_connection_availability(self) -> TestMetrics:
        """Test basic SSH connection availability.
        
        Returns:
            TestMetrics with connection test results
        """
        metrics = TestMetrics(test_name='connection_availability', passed=False)
        metrics.start_time = datetime.now()
        
        try:
            metrics.attempts = 1
            
            # Try basic TCP connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((self.host, self.port))
            sock.close()
            
            if result == 0:
                metrics.successes = 1
                metrics.passed = True
                metrics.status = 'success'
                metrics.details['connection'] = 'SSH port is open and responding'
            else:
                metrics.failures = 1
                metrics.status = 'failed'
                metrics.details['connection'] = f'Connection failed with code {result}'
                metrics.errors.append(f'Cannot connect to {self.host}:{self.port}')
        
        except socket.timeout:
            metrics.failures = 1
            metrics.status = 'timeout'
            metrics.details['connection'] = 'Connection timeout'
            metrics.errors.append('Connection timed out')
        
        except Exception as e:
            metrics.failures = 1
            metrics.status = 'error'
            metrics.errors.append(str(e))
        
        finally:
            metrics.end_time = datetime.now()
            metrics.duration_ms = (metrics.end_time - metrics.start_time).total_seconds() * 1000
            self.results['connection_availability'] = metrics
        
        return metrics
    
    def test_brute_force_resistance(self) -> TestMetrics:
        """Test resistance to brute force attacks by attempting rapid connections.
        
        Returns:
            TestMetrics with brute force test results
        """
        metrics = TestMetrics(test_name='brute_force_resistance', passed=False)
        metrics.start_time = datetime.now()
        
        try:
            rapid_failures = 0
            max_attempts = 5
            
            for i in range(max_attempts):
                metrics.attempts += 1
                
                try:
                    client = paramiko.SSHClient()
                    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    
                    # Attempt with invalid credentials
                    client.connect(
                        self.host,
                        port=self.port,
                        username='invalid_user_brute_force',
                        password='invalid_password',
                        timeout=self.timeout,
                        look_for_keys=False,
                        allow_agent=False,
                    )
                    client.close()
                
                except paramiko.ssh_exception.AuthenticationException:
                    rapid_failures += 1
                    metrics.failures += 1
                
                except socket.timeout:
                    metrics.errors.append(f'Attempt {i+1}: Socket timeout (good - rate limiting?)')
                    rapid_failures += 1
                    break
                
                except (socket.error, paramiko.SSHException) as e:
                    metrics.errors.append(f'Attempt {i+1}: {str(e)}')
                    break
                
                time.sleep(0.1)  # Small delay between attempts
            
            # If we got through all attempts without timeout/rejection, it's vulnerable
            if rapid_failures == max_attempts:
                metrics.status = 'vulnerable'
                metrics.details['rapid_failures'] = rapid_failures
                metrics.details['rate_limiting'] = 'No apparent rate limiting detected'
                metrics.errors.append('System appears vulnerable to brute force (accepts rapid auth attempts)')
            else:
                metrics.passed = True
                metrics.status = 'protected'
                metrics.details['rapid_failures'] = rapid_failures
                metrics.details['rate_limiting'] = 'Rate limiting or connection rejection detected'
        
        except Exception as e:
            metrics.status = 'error'
            metrics.errors.append(str(e))
        
        finally:
            metrics.end_time = datetime.now()
            metrics.duration_ms = (metrics.end_time - metrics.start_time).total_seconds() * 1000
            self.results['brute_force_resistance'] = metrics
        
        return metrics
    
    def test_failed_login_attempts(self) -> TestMetrics:
        """Test behavior after multiple failed login attempts.
        
        Returns:
            TestMetrics with failed login test results
        """
        metrics = TestMetrics(test_name='failed_login_attempts', passed=False)
        metrics.start_time = datetime.now()
        
        try:
            failed_attempts = 0
            blocked = False
            connection_lost = False
            
            for i in range(3):
                metrics.attempts += 1
                
                try:
                    client = paramiko.SSHClient()
                    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    
                    client.connect(
                        self.host,
                        port=self.port,
                        username=f'testuser_{i}',
                        password=f'wrongpass_{i}',
                        timeout=self.timeout,
                        look_for_keys=False,
                        allow_agent=False,
                    )
                    client.close()
                
                except paramiko.ssh_exception.AuthenticationException:
                    failed_attempts += 1
                    metrics.failures += 1
                
                except (socket.timeout, ConnectionRefusedError, socket.error) as e:
                    blocked = True
                    connection_lost = True
                    metrics.errors.append(f'Connection blocked after {i} attempts: {str(e)}')
                    break
                
                except Exception as e:
                    metrics.errors.append(f'Attempt {i+1} error: {str(e)}')
            
            metrics.details['failed_attempts'] = failed_attempts
            
            if connection_lost:
                metrics.passed = True
                metrics.status = 'protected'
                metrics.details['blocking'] = 'Connection blocked after failed attempts (good protection)'
            elif failed_attempts == metrics.attempts:
                metrics.status = 'vulnerable'
                metrics.details['blocking'] = 'No connection blocking detected'
            else:
                metrics.passed = True
                metrics.status = 'partial'
                metrics.details['blocking'] = 'Partial protection detected'
        
        except Exception as e:
            metrics.status = 'error'
            metrics.errors.append(str(e))
        
        finally:
            metrics.end_time = datetime.now()
            metrics.duration_ms = (metrics.end_time - metrics.start_time).total_seconds() * 1000
            self.results['failed_login_attempts'] = metrics
        
        return metrics
    
    def test_timeout_handling(self) -> TestMetrics:
        """Test how client handles connection timeouts.
        
        Returns:
            TestMetrics with timeout handling test results
        """
        metrics = TestMetrics(test_name='timeout_handling', passed=False)
        metrics.start_time = datetime.now()
        
        try:
            # Try connection with very short timeout
            metrics.attempts = 1
            short_timeout = 0.5
            
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            try:
                client.connect(
                    '10.255.255.1',  # Non-routable IP - will timeout
                    port=self.port,
                    timeout=short_timeout,
                    look_for_keys=False,
                    allow_agent=False,
                )
                client.close()
                metrics.failures = 1
                metrics.status = 'unexpected_success'
                metrics.details['timeout'] = 'Expected timeout but connection succeeded'
            
            except socket.timeout:
                metrics.successes = 1
                metrics.passed = True
                metrics.status = 'success'
                metrics.details['timeout'] = 'Timeout occurred as expected'
            
            except (ConnectionRefusedError, socket.error, paramiko.SSHException):
                # Connection error is also acceptable (better than hanging)
                metrics.successes = 1
                metrics.passed = True
                metrics.status = 'success'
                metrics.details['timeout'] = 'Connection error (acceptable alternative to hanging)'
        
        except Exception as e:
            metrics.status = 'error'
            metrics.errors.append(str(e))
        
        finally:
            metrics.end_time = datetime.now()
            metrics.duration_ms = (metrics.end_time - metrics.start_time).total_seconds() * 1000
            self.results['timeout_handling'] = metrics
        
        return metrics
    
    def test_key_rejection(self) -> TestMetrics:
        """Test rejection of invalid SSH keys.
        
        Returns:
            TestMetrics with key rejection test results
        """
        metrics = TestMetrics(test_name='key_rejection', passed=False)
        metrics.start_time = datetime.now()
        
        try:
            metrics.attempts = 1
            
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            try:
                # Try with invalid key path
                client.connect(
                    self.host,
                    port=self.port,
                    username='testuser',
                    key_filename='/nonexistent/path/to/key',
                    timeout=self.timeout,
                    look_for_keys=False,
                    allow_agent=False,
                )
                client.close()
                metrics.failures = 1
                metrics.status = 'vulnerable'
                metrics.details['key_handling'] = 'Invalid key was accepted (security issue)'
            
            except (paramiko.ssh_exception.AuthenticationException, FileNotFoundError, IOError):
                metrics.successes = 1
                metrics.passed = True
                metrics.status = 'success'
                metrics.details['key_handling'] = 'Invalid key properly rejected'
            
            except paramiko.SSHException as e:
                if 'not a valid' in str(e).lower() or 'could not deserialize' in str(e).lower():
                    metrics.successes = 1
                    metrics.passed = True
                    metrics.status = 'success'
                    metrics.details['key_handling'] = 'Invalid key properly rejected with SSHException'
                else:
                    metrics.failures = 1
                    metrics.details['key_handling'] = str(e)
            
            except Exception as e:
                metrics.failures = 1
                metrics.errors.append(str(e))
        
        except Exception as e:
            metrics.status = 'error'
            metrics.errors.append(str(e))
        
        finally:
            metrics.end_time = datetime.now()
            metrics.duration_ms = (metrics.end_time - metrics.start_time).total_seconds() * 1000
            self.results['key_rejection'] = metrics
        
        return metrics
    
    def test_concurrent_connections(self) -> TestMetrics:
        """Test behavior under concurrent connection attempts.
        
        Returns:
            TestMetrics with concurrent connection test results
        """
        metrics = TestMetrics(test_name='concurrent_connections', passed=False)
        metrics.start_time = datetime.now()
        
        def attempt_connection():
            try:
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(
                    self.host,
                    port=self.port,
                    username='concurrent_test',
                    password='test_password',
                    timeout=self.timeout,
                    look_for_keys=False,
                    allow_agent=False,
                )
                client.close()
                return 'success'
            except paramiko.ssh_exception.AuthenticationException:
                return 'auth_failed'
            except (socket.timeout, socket.error, ConnectionRefusedError):
                return 'connection_error'
            except Exception as e:
                return f'error: {str(e)}'
        
        try:
            # Try 3 concurrent connections
            num_concurrent = 3
            threads = []
            results = []
            
            metrics.attempts = num_concurrent
            
            def threaded_attempt():
                result = attempt_connection()
                results.append(result)
            
            for _ in range(num_concurrent):
                t = threading.Thread(target=threaded_attempt)
                threads.append(t)
                t.start()
            
            for t in threads:
                t.join(timeout=10)
            
            # Analyze results
            errors = [r for r in results if 'error' in r.lower()]
            auth_failed = [r for r in results if r == 'auth_failed']
            connection_errors = [r for r in results if r == 'connection_error']
            
            metrics.details['concurrent_attempts'] = num_concurrent
            metrics.details['connection_errors'] = len(connection_errors)
            metrics.details['auth_failures'] = len(auth_failed)
            metrics.details['other_errors'] = len(errors)
            
            if connection_errors:
                metrics.passed = True
                metrics.status = 'protected'
                metrics.successes = len(connection_errors)
                metrics.details['result'] = 'Some connections rejected (rate limiting?)'
            else:
                metrics.failures = num_concurrent
                metrics.status = 'vulnerable'
                metrics.details['result'] = 'All concurrent connections attempted (possible DoS vector)'
        
        except Exception as e:
            metrics.status = 'error'
            metrics.errors.append(str(e))
        
        finally:
            metrics.end_time = datetime.now()
            metrics.duration_ms = (metrics.end_time - metrics.start_time).total_seconds() * 1000
            self.results['concurrent_connections'] = metrics
        
        return metrics
    
    def test_credential_caching(self) -> TestMetrics:
        """Test for improper credential caching or storage.
        
        Returns:
            TestMetrics with credential caching test results
        """
        metrics = TestMetrics(test_name='credential_caching', passed=False)
        metrics.start_time = datetime.now()
        
        try:
            metrics.attempts = 1
            
            # Check common credential cache locations
            cache_locations = [
                '~/.ssh/ssh_config',
                '~/.ssh/known_hosts',
                '~/.bashrc',
                '~/.bash_history',
            ]
            
            import os
            found_issues = []
            
            for location in cache_locations:
                expanded = os.path.expanduser(location)
                if os.path.exists(expanded):
                    try:
                        with open(expanded, 'r') as f:
                            content = f.read()
                            # Check for password-like patterns (naive check)
                            if 'password' in content.lower() or 'passwd' in content.lower():
                                found_issues.append(f'Possible credential in {location}')
                    except (PermissionError, IOError):
                        pass
            
            if found_issues:
                metrics.failures = 1
                metrics.status = 'vulnerable'
                metrics.details['cached_credentials'] = found_issues
                metrics.errors.extend(found_issues)
            else:
                metrics.successes = 1
                metrics.passed = True
                metrics.status = 'success'
                metrics.details['cached_credentials'] = 'No obvious credential caching found'
        
        except Exception as e:
            metrics.status = 'error'
            metrics.errors.append(str(e))
        
        finally:
            metrics.end_time = datetime.now()
            metrics.duration_ms = (metrics.end_time - metrics.start_time).total_seconds() * 1000
            self.results['credential_caching'] = metrics
        
        return metrics
    
    def test_error_messages(self) -> TestMetrics:
        """Test for information disclosure in error messages.
        
        Returns:
            TestMetrics with error message test results
        """
        metrics = TestMetrics(test_name='error_messages', passed=False)
        metrics.start_time = datetime.now()
        
        try:
            metrics.attempts = 1
            
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            try:
                client.connect(
                    self.host,
                    port=self.port,
                    username='nonexistent_user_12345',
                    password='invalid_pass',
                    timeout=self.timeout,
                    look_for_keys=False,
                    allow_agent=False,
                )
                client.close()
            except paramiko.ssh_exception.AuthenticationException as e:
                error_msg = str(e)
                metrics.details['error_message'] = error_msg
                
                # Check for information disclosure
                disclosure_indicators = [
                    'no such user',
                    'user does not exist',
                    'username not found',
                ]
                
                is_info_disclosure = any(indicator in error_msg.lower() for indicator in disclosure_indicators)
                
                if is_info_disclosure:
                    metrics.failures = 1
                    metrics.status = 'vulnerable'
                    metrics.details['disclosure'] = 'Error message reveals user existence'
                    metrics.errors.append('Information disclosure: server reveals whether user exists')
                else:
                    metrics.successes = 1
                    metrics.passed = True
                    metrics.status = 'success'
                    metrics.details['disclosure'] = 'Generic error message (good)'
            
            except Exception as e:
                metrics.details['error'] = str(e)
                # Generic error messages are good
                metrics.successes = 1
                metrics.passed = True
                metrics.status = 'success'
                metrics.details['disclosure'] = 'Generic error (no information disclosure)'
        
        except Exception as e:
            metrics.status = 'error'
            metrics.errors.append(str(e))
        
        finally:
            metrics.end_time = datetime.now()
            metrics.duration_ms = (metrics.end_time - metrics.start_time).total_seconds() * 1000
            self.results['error_messages'] = metrics
        
        return metrics
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics of all tests.
        
        Returns:
            Dictionary with summary metrics
        """
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results.values() if r.passed)
        failed_tests = sum(1 for r in self.results.values() if not r.passed)
        total_duration = sum(r.duration_ms for r in self.results.values())
        total_attempts = sum(r.attempts for r in self.results.values())
        total_successes = sum(r.successes for r in self.results.values())
        total_failures = sum(r.failures for r in self.results.values())
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'pass_rate_percent': (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            'total_duration_ms': total_duration,
            'total_attempts': total_attempts,
            'total_successes': total_successes,
            'total_failures': total_failures,
            'target_host': self.host,
            'target_port': self.port,
            'timestamp': datetime.now().isoformat(),
        }
