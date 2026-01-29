#!/usr/bin/env python3
"""
Security test runner script for SSH client.
Orchestrates all security tests and outputs results to CSV.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from testing.security_tester import SecurityTester
from utilities.csv_reporter import CSVReporter


def run_security_tests(
    host: str,
    port: int = 22,
    output_dir: str = 'test_results',
    timeout: int = 5,
) -> tuple[dict, str]:
    """
    Run security tests on target SSH host.
    
    Args:
        host: Target SSH host
        port: Target SSH port
        output_dir: Directory to store CSV reports
        timeout: Connection timeout in seconds
        
    Returns:
        Tuple of (test_results, csv_file_path)
    """
    print(f'[*] Starting security tests on {host}:{port}')
    print(f'[*] Output directory: {output_dir}')
    print()
    
    # Initialize tester and reporter
    tester = SecurityTester(host=host, port=port, timeout=timeout)
    reporter = CSVReporter(output_dir=output_dir)
    
    # Run all tests
    print('[*] Running tests...')
    test_results = tester.run_all_tests()
    
    # Get summary
    summary = tester.get_summary()
    
    # Print results to console
    print()
    print('=' * 70)
    print('SECURITY TEST RESULTS')
    print('=' * 70)
    print()
    
    for test_name, metrics in test_results.items():
        status_symbol = '✓' if metrics.passed else '✗'
        print(f'{status_symbol} {test_name:30s} [{metrics.status:15s}] ({metrics.duration_ms:.0f}ms)')
        
        if metrics.errors:
            for error in metrics.errors:
                print(f'  ⚠ {error}')
        
        if metrics.details:
            for key, value in metrics.details.items():
                if isinstance(value, (int, float, bool)):
                    print(f'  {key}: {value}')
                elif isinstance(value, str) and len(value) < 60:
                    print(f'  {key}: {value}')
    
    print()
    print('-' * 70)
    print('SUMMARY')
    print('-' * 70)
    print(f'Total tests:        {summary["total_tests"]}')
    print(f'Passed:             {summary["passed_tests"]}')
    print(f'Failed:             {summary["failed_tests"]}')
    print(f'Pass rate:          {summary["pass_rate_percent"]:.1f}%')
    print(f'Total duration:     {summary["total_duration_ms"]:.0f}ms')
    print(f'Total attempts:     {summary["total_attempts"]}')
    print(f'Successful ops:     {summary["total_successes"]}')
    print(f'Failed ops:         {summary["total_failures"]}')
    print()
    
    # Write results to CSV
    print('[*] Writing results to CSV...')
    
    # Convert metrics to dictionary format
    results_dict = {
        name: {
            'status': metrics.status,
            'passed': metrics.passed,
            'metrics': {
                'duration_ms': metrics.duration_ms,
                'attempts': metrics.attempts,
                'successes': metrics.successes,
                'failures': metrics.failures,
            },
            'details': str(metrics.details) if metrics.details else '',
        }
        for name, metrics in test_results.items()
    }
    
    # Write detailed test results
    csv_file = reporter.write_test_results(results_dict)
    print(f'[+] Results saved to: {csv_file}')
    
    # Write summary
    summary_file = reporter.write_summary(summary)
    print(f'[+] Summary saved to: {summary_file}')
    
    print()
    return test_results, csv_file


def main():
    """Main entry point for test runner script."""
    parser = argparse.ArgumentParser(
        description='Security test suite for SSH client',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python test_runner.py -H 192.168.1.100
  python test_runner.py -H example.com -p 2222 -o my_tests
  python test_runner.py -H localhost --timeout 10
        ''',
    )
    
    parser.add_argument(
        '-H', '--host',
        required=True,
        help='Target SSH host',
    )
    parser.add_argument(
        '-p', '--port',
        type=int,
        default=22,
        help='Target SSH port (default: 22)',
    )
    parser.add_argument(
        '-o', '--output',
        default='test_results',
        help='Output directory for CSV reports (default: test_results)',
    )
    parser.add_argument(
        '-t', '--timeout',
        type=int,
        default=5,
        help='Connection timeout in seconds (default: 5)',
    )
    
    args = parser.parse_args()
    
    try:
        run_security_tests(
            host=args.host,
            port=args.port,
            output_dir=args.output,
            timeout=args.timeout,
        )
    except KeyboardInterrupt:
        print('\n[!] Tests interrupted by user')
        sys.exit(1)
    except Exception as e:
        print(f'[!] Error: {e}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
