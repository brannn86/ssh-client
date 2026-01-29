# SSH Security Testing Framework

A comprehensive security testing suite for your SSH client application. Tests for brute force resistance, credential theft, login attempts, and other security vulnerabilities.

## Features

### Security Tests Included

1. **Connection Availability** - Tests if SSH port is open and responding
2. **Brute Force Resistance** - Tests for rapid authentication attempt handling and rate limiting
3. **Failed Login Attempts** - Tests behavior after multiple failed login attempts
4. **Timeout Handling** - Tests how the client handles connection timeouts
5. **Key Rejection** - Tests rejection of invalid SSH keys
6. **Concurrent Connections** - Tests behavior under concurrent connection attempts
7. **Credential Caching** - Tests for improper credential caching or storage
8. **Error Messages** - Tests for information disclosure in error messages

### Output Formats

- **Console Output** - Real-time test progress and results
- **CSV Reports** - Detailed metrics and statistics saved to CSV files
- **Summary Statistics** - Overall pass/fail rates and performance metrics

## Usage

### Command Line Testing

```bash
# Basic test
python test_runner.py -H example.com

# Custom port
python test_runner.py -H example.com -p 2222

# Custom output directory
python test_runner.py -H example.com -o my_test_results

# Custom timeout
python test_runner.py -H example.com --timeout 10
```

### GUI Testing

1. Launch the SSH client application
2. Enter the target SSH host and port
3. Click the **"Test Security"** button
4. Results will display in the terminal and be saved to `test_results/` directory

## Output

### CSV Files

Two CSV files are generated for each test run:

1. **security_test_YYYYMMDD_HHMMSS.csv** - Detailed test results
   - Timestamp
   - Test name
   - Pass/Fail status
   - Duration (ms)
   - Attempts, successes, failures
   - Detailed metrics and error information

2. **test_summary.csv** - Summary statistics
   - Total tests run
   - Pass rate percentage
   - Total duration
   - Attempts and success rates
   - Target host and port

### Example Output

```
✓ connection_availability     [success        ] (123ms)
✗ brute_force_resistance      [vulnerable     ] (456ms)
  ⚠ System appears vulnerable to brute force

============================================================================
SUMMARY
============================================================================
Total tests:        8
Passed:             6
Failed:             2
Pass rate:          75.0%
Total duration:     2345ms
Total attempts:     23
Successful ops:     18
Failed ops:         5
```

## Architecture

### Components

#### `testing/security_tester.py`
Core security testing class with all test implementations.

**Key Classes:**
- `TestMetrics` - Data class for storing test results and metrics
- `SecurityTester` - Main testing class with individual test methods

**Key Methods:**
- `run_all_tests()` - Execute all security tests
- `get_summary()` - Get summary statistics

#### `utilities/csv_reporter.py`
Handles CSV output and reporting of test results.

**Key Methods:**
- `write_test_results()` - Write detailed test results to CSV
- `write_summary()` - Write summary statistics to CSV
- `get_latest_report()` - Get path to most recent report

#### `test_runner.py`
Command-line interface for running security tests standalone.

#### GUI Integration (`gui/main_window.py`)
- Added "Test Security" button to main window
- Integrated testing framework into GUI
- Results display in terminal widget
- Background thread processing to avoid UI blocking

## Test Metrics

Each test tracks the following metrics:

- **passed** - Boolean indicating if test passed
- **status** - Test status (success, failed, vulnerable, protected, etc.)
- **duration_ms** - Test execution time in milliseconds
- **attempts** - Number of connection/auth attempts made
- **successes** - Number of successful operations
- **failures** - Number of failed operations
- **errors** - List of error messages encountered
- **details** - Test-specific detailed information

## Security Considerations

⚠️ **Important:** Only run these tests on systems you own or have explicit permission to test. Unauthorized security testing is illegal.

### What This Tests For

- **Brute Force** - Does the system rate limit rapid auth attempts?
- **DoS Resistance** - How does it handle concurrent connections?
- **Error Disclosure** - Do error messages reveal sensitive information?
- **Timeouts** - Does the client handle timeouts gracefully?
- **Key Validation** - Are invalid keys properly rejected?
- **Credential Storage** - Are credentials securely handled?

### What This Doesn't Test

- Encryption algorithms
- Cryptographic strength
- Network-level attacks
- Advanced persistence techniques
- Compliance with specific standards

## Example Workflow

```python
from testing.security_tester import SecurityTester
from utilities.csv_reporter import CSVReporter

# Create tester
tester = SecurityTester(host='example.com', port=22, timeout=5)

# Run all tests
results = tester.run_all_tests()

# Get summary
summary = tester.get_summary()

# Report results
reporter = CSVReporter(output_dir='test_results')
csv_file = reporter.write_test_results({
    name: {
        'status': metrics.status,
        'passed': metrics.passed,
        'metrics': {
            'duration_ms': metrics.duration_ms,
            'attempts': metrics.attempts,
        }
    }
    for name, metrics in results.items()
})
```

## Results Directory

Test results are stored in a `test_results/` directory with the following structure:

```
test_results/
├── security_test_20250129_143022.csv
├── security_test_20250129_150530.csv
└── test_summary.csv
```

Each test run creates a new timestamped CSV file, so historical data is preserved.

## Troubleshooting

### Connection Timeouts
If tests timeout frequently, increase the timeout value:
```bash
python test_runner.py -H example.com --timeout 15
```

### Port Not Accessible
Ensure the target port is accessible from your network:
```bash
nc -zv example.com 22
```

### Import Errors
Ensure all dependencies are installed:
```bash
pip install paramiko PyQt6
```

## Future Enhancements

Potential improvements for the security testing framework:

- [ ] Customizable test profiles (basic, comprehensive, custom)
- [ ] Password spray detection
- [ ] SSH version detection and vulnerability scanning
- [ ] Key exchange algorithm analysis
- [ ] Cipher strength analysis
- [ ] Comparative reporting across multiple hosts
- [ ] HTML report generation
- [ ] Real-time graphical dashboard
- [ ] Integration with vulnerability databases

## License

Part of the SSH Zero Trust Client project.
