#!/usr/bin/env python3
"""
Example usage of the security testing framework.
Shows how to use SecurityTester and CSVReporter programmatically.
"""

from testing.security_tester import SecurityTester
from utilities.csv_reporter import CSVReporter
from datetime import datetime
import json


def example_basic_test():
    """Basic example: Run tests on localhost."""
    print("=" * 70)
    print("EXAMPLE 1: Basic Security Test")
    print("=" * 70)
    
    # Create tester for localhost
    tester = SecurityTester(host='localhost', port=22, timeout=5)
    
    # Run all tests
    print("\nRunning tests...")
    results = tester.run_all_tests()
    
    # Print summary
    summary = tester.get_summary()
    print(f"\nTests Completed: {summary['passed_tests']}/{summary['total_tests']} passed")
    print(f"Pass Rate: {summary['pass_rate_percent']:.1f}%")
    print(f"Total Duration: {summary['total_duration_ms']:.0f}ms")


def example_individual_test():
    """Example: Run individual tests."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Individual Test")
    print("=" * 70)
    
    tester = SecurityTester(host='192.168.1.1', port=22, timeout=5)
    
    # Run only connection test
    print("\nTesting connection availability...")
    metrics = tester.test_connection_availability()
    
    print(f"Status: {metrics.status}")
    print(f"Passed: {metrics.passed}")
    print(f"Duration: {metrics.duration_ms:.0f}ms")
    print(f"Details: {metrics.details}")
    
    if metrics.errors:
        print(f"Errors: {metrics.errors}")


def example_with_csv_output():
    """Example: Run tests and save to CSV."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Run Tests with CSV Output")
    print("=" * 70)
    
    # Create tester and reporter
    tester = SecurityTester(host='example.com', port=22, timeout=5)
    reporter = CSVReporter(output_dir='test_results')
    
    # Run tests
    print("\nRunning security tests...")
    test_results = tester.run_all_tests()
    summary = tester.get_summary()
    
    # Convert to report format
    results_dict = {
        name: {
            'status': metrics.status,
            'passed': metrics.passed,
            'metrics': {
                'duration_ms': metrics.duration_ms,
                'attempts': metrics.attempts,
                'successes': metrics.successes,
                'failures': metrics.failures,
                'error_count': len(metrics.errors),
            },
            'details': str(metrics.details),
        }
        for name, metrics in test_results.items()
    }
    
    # Write CSV files
    csv_file = reporter.write_test_results(results_dict)
    summary_file = reporter.write_summary(summary)
    
    print(f"\n✓ Results saved to: {csv_file}")
    print(f"✓ Summary saved to: {summary_file}")
    print(f"\nPass Rate: {summary['pass_rate_percent']:.1f}%")


def example_analyze_results():
    """Example: Analyze test results programmatically."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Analyze Results")
    print("=" * 70)
    
    tester = SecurityTester(host='target.example.com', port=2222, timeout=5)
    
    print("\nRunning tests...")
    results = tester.run_all_tests()
    
    # Analyze results
    print("\nAnalysis:")
    
    # Find failed tests
    failed_tests = [name for name, metrics in results.items() if not metrics.passed]
    print(f"\nFailed Tests ({len(failed_tests)}):")
    for test in failed_tests:
        metrics = results[test]
        print(f"  - {test}: {metrics.status}")
    
    # Find vulnerable tests (failed with specific issue)
    vulnerable = [name for name, metrics in results.items() 
                  if metrics.status == 'vulnerable']
    print(f"\nVulnerable Areas ({len(vulnerable)}):")
    for test in vulnerable:
        metrics = results[test]
        print(f"  - {test}")
        for error in metrics.errors[:1]:
            print(f"    Issue: {error}")
    
    # Performance metrics
    print("\nPerformance:")
    total_time = sum(m.duration_ms for m in results.values())
    avg_time = total_time / len(results)
    print(f"  Total: {total_time:.0f}ms")
    print(f"  Average per test: {avg_time:.0f}ms")
    
    # Attempt metrics
    print("\nAttempt Metrics:")
    total_attempts = sum(m.attempts for m in results.values())
    total_successes = sum(m.successes for m in results.values())
    total_failures = sum(m.failures for m in results.values())
    print(f"  Total attempts: {total_attempts}")
    print(f"  Successful: {total_successes}")
    print(f"  Failed: {total_failures}")


def example_batch_testing():
    """Example: Test multiple hosts."""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Batch Testing Multiple Hosts")
    print("=" * 70)
    
    hosts = [
        ('localhost', 22),
        ('192.168.1.1', 22),
        ('example.com', 22),
    ]
    
    all_results = {}
    reporter = CSVReporter(output_dir='batch_test_results')
    
    for host, port in hosts:
        print(f"\nTesting {host}:{port}...")
        
        try:
            tester = SecurityTester(host=host, port=port, timeout=5)
            results = tester.run_all_tests()
            summary = tester.get_summary()
            
            all_results[f'{host}:{port}'] = {
                'summary': summary,
                'results': results,
            }
            
            print(f"  ✓ Pass rate: {summary['pass_rate_percent']:.1f}%")
        
        except Exception as e:
            print(f"  ✗ Error: {e}")
            all_results[f'{host}:{port}'] = {'error': str(e)}
    
    # Summarize batch results
    print("\n" + "-" * 70)
    print("Batch Summary:")
    for host_port, data in all_results.items():
        if 'error' in data:
            print(f"  {host_port}: ERROR - {data['error']}")
        else:
            rate = data['summary']['pass_rate_percent']
            print(f"  {host_port}: {rate:.1f}% pass rate")


def example_export_json():
    """Example: Export results as JSON for processing."""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Export Results as JSON")
    print("=" * 70)
    
    tester = SecurityTester(host='example.com', port=22, timeout=5)
    results = tester.run_all_tests()
    summary = tester.get_summary()
    
    # Convert to JSON-serializable format
    json_data = {
        'timestamp': datetime.now().isoformat(),
        'summary': summary,
        'tests': {
            name: {
                'status': metrics.status,
                'passed': metrics.passed,
                'duration_ms': metrics.duration_ms,
                'attempts': metrics.attempts,
                'successes': metrics.successes,
                'failures': metrics.failures,
                'error_count': len(metrics.errors),
                'details': metrics.details,
            }
            for name, metrics in results.items()
        }
    }
    
    # Save to JSON file
    with open('test_results.json', 'w') as f:
        json.dump(json_data, f, indent=2)
    
    print("\n✓ Results exported to test_results.json")
    print(f"  Timestamp: {json_data['timestamp']}")
    print(f"  Tests: {len(json_data['tests'])}")
    print(f"  Pass rate: {json_data['summary']['pass_rate_percent']:.1f}%")


def example_custom_test_sequence():
    """Example: Run custom test sequence."""
    print("\n" + "=" * 70)
    print("EXAMPLE 7: Custom Test Sequence")
    print("=" * 70)
    
    tester = SecurityTester(host='example.com', port=22, timeout=5)
    
    # Run specific tests in order
    test_sequence = [
        ('Connection', tester.test_connection_availability),
        ('Brute Force', tester.test_brute_force_resistance),
        ('Timeouts', tester.test_timeout_handling),
    ]
    
    print("\nRunning custom test sequence...")
    for test_name, test_func in test_sequence:
        print(f"\n{test_name}...", end=' ')
        try:
            metrics = test_func()
            symbol = '✓' if metrics.passed else '✗'
            print(f"{symbol} {metrics.status}")
        except Exception as e:
            print(f"✗ Error: {e}")


if __name__ == '__main__':
    print("\nSSH Security Testing Framework - Examples\n")
    
    # Choose which examples to run
    examples = [
        ('1', 'Basic Test', example_basic_test),
        ('2', 'Individual Test', example_individual_test),
        ('3', 'CSV Output', example_with_csv_output),
        ('4', 'Analyze Results', example_analyze_results),
        ('5', 'Batch Testing', example_batch_testing),
        ('6', 'Export JSON', example_export_json),
        ('7', 'Custom Sequence', example_custom_test_sequence),
    ]
    
    print("Available examples:")
    for num, name, _ in examples:
        print(f"  {num}. {name}")
    
    choice = input("\nRun example (or 'all' for all): ").strip()
    
    if choice.lower() == 'all':
        for num, name, func in examples:
            try:
                func()
            except Exception as e:
                print(f"\nError in example {num}: {e}")
    else:
        for num, name, func in examples:
            if num == choice:
                func()
                break
        else:
            print("Invalid choice")
