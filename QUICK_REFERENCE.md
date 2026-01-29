# Security Testing Framework - Quick Reference Card

## 📍 Location Quick Links

| Item | Path |
|------|------|
| Main Test Class | `testing/security_tester.py` |
| CSV Reporter | `utilities/csv_reporter.py` |
| CLI Tool | `test_runner.py` |
| Documentation | `SECURITY_TESTING.md` |
| Examples | `example_usage.py` |
| Test Results | `test_results/` (auto-created) |

---

## 🎯 Three Ways to Test

### Option 1: GUI (Easiest)
```
1. Open SSH Client
2. Enter target host: example.com
3. Click [Test Security] button
4. Wait for results
5. Find CSV files in test_results/
```

### Option 2: Command Line
```powershell
python test_runner.py -H example.com
```

### Option 3: Python Code
```python
from testing.security_tester import SecurityTester

tester = SecurityTester(host='example.com', port=22)
results = tester.run_all_tests()
```

---

## 🧪 Security Tests

| # | Test Name | What It Tests |
|---|-----------|---------------|
| 1 | Connection Availability | SSH port open? |
| 2 | Brute Force Resistance | Rate limiting? |
| 3 | Failed Login Attempts | Account lockout? |
| 4 | Timeout Handling | Graceful timeouts? |
| 5 | Key Rejection | Invalid keys blocked? |
| 6 | Concurrent Connections | DoS protection? |
| 7 | Credential Caching | Secure storage? |
| 8 | Error Messages | Information leak? |

---

## 📊 Results Format

### Console Output
```
✓ test_name [status] (123ms)
✗ test_name [status] (456ms)
  ⚠ Error message details
```

### CSV Files
```
security_test_YYYYMMDD_HHMMSS.csv
test_summary.csv
```

### Pass Rate
- ✅ 90-100%: Excellent
- ⚠️ 75-90%: Good
- ⚠️ 50-75%: Fair
- ❌ <50%: Poor

---

## 🔧 CLI Arguments

```bash
python test_runner.py
  -H, --host       TARGET_HOST (required)
  -p, --port       SSH_PORT (default: 22)
  -o, --output     OUTPUT_DIR (default: test_results)
  -t, --timeout    TIMEOUT_SECS (default: 5)
  --help           Show help
```

### Examples
```bash
python test_runner.py -H localhost
python test_runner.py -H example.com -p 2222
python test_runner.py -H example.com -o my_audit
python test_runner.py -H example.com --timeout 15
```

---

## 📈 Key Metrics

### Per-Test
- **duration_ms**: How long test took
- **attempts**: Number of operations
- **successes**: Successful operations
- **failures**: Failed operations
- **errors**: Error messages

### Summary
- **total_tests**: Tests run
- **passed_tests**: Tests passed
- **failed_tests**: Tests failed
- **pass_rate_percent**: Percentage
- **total_duration_ms**: Total time

---

## 🚨 Important Warnings

### Critical Failures
- ❌ Brute Force Resistance = VULNERABLE
- ❌ Concurrent Connections = No Limits
- ❌ Error Messages = Information Leak
- ❌ Key Rejection = Invalid Keys Accepted

### What Triggers Each
1. **Brute Force**: Server accepts rapid auth attempts
2. **Concurrent**: Accepts 3+ simultaneous connections
3. **Error Messages**: Error reveals user existence
4. **Key Rejection**: Invalid key path accepted

---

## 📁 File Structure

```
testing/
├── __init__.py              (empty)
└── security_tester.py       (900+ lines)
    ├── TestMetrics class
    └── SecurityTester class

utilities/
├── __init__.py              (empty)
└── csv_reporter.py          (150+ lines)
    └── CSVReporter class

test_runner.py              (CLI interface)
example_usage.py            (7 examples)

test_results/               (auto-created)
├── security_test_*.csv
└── test_summary.csv
```

---

## ✅ Checklist

- [x] Core testing engine created
- [x] CSV reporting module created
- [x] CLI tool created
- [x] GUI button integrated
- [x] Background threading added
- [x] Documentation written
- [x] Examples provided
- [x] Error handling implemented
- [x] No new dependencies needed
- [x] Ready for production

---

## 🎓 Usage Examples

### Example 1: GUI
```
1. Open app → Enter host → Click "Test Security"
2. View results in terminal
3. Check test_results/ folder
```

### Example 2: CLI Basic
```bash
python test_runner.py -H example.com
```

### Example 3: CLI Advanced
```bash
python test_runner.py -H example.com -p 2222 -o audit --timeout 15
```

### Example 4: Programmatic
```python
from testing.security_tester import SecurityTester
from utilities.csv_reporter import CSVReporter

tester = SecurityTester('example.com', 22)
results = tester.run_all_tests()
reporter = CSVReporter()
reporter.write_test_results(results)
```

### Example 5: Batch Testing
```python
hosts = ['host1.com', 'host2.com', 'host3.com']
for host in hosts:
    tester = SecurityTester(host)
    results = tester.run_all_tests()
    # Process results
```

---

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Connection fails | Verify host/port, check firewall |
| Tests timeout | Increase timeout: `--timeout 15` |
| Import error | `pip install -r requirements.txt` |
| Button not working | Check test_results folder exists |
| Slow tests | Network latency, increase timeout |

---

## 📊 Reading CSV Results

### Open in Excel
```
1. Double-click .csv file
2. View in spreadsheet
3. Sort/filter as needed
4. Create charts
```

### Open in Python
```python
import pandas as pd
df = pd.read_csv('test_results/security_test_*.csv')
print(df)
```

### Column Guide
- **timestamp**: When test ran
- **test_name**: Which test
- **status**: Result (success/failed/vulnerable)
- **passed**: Boolean T/F
- **metrics**: Performance data
- **details**: Additional info

---

## 🎯 Common Scenarios

### Scenario 1: Test Local SSH
```bash
python test_runner.py -H localhost
```

### Scenario 2: Test Remote Server
```bash
python test_runner.py -H ssh.company.com
```

### Scenario 3: Test Non-Standard Port
```bash
python test_runner.py -H example.com -p 2222
```

### Scenario 4: Create Audit Report
```bash
python test_runner.py -H example.com -o "audit_$(date +%Y%m%d)"
```

### Scenario 5: Slow Network
```bash
python test_runner.py -H example.com --timeout 20
```

---

## 📚 Documentation Map

| Document | Contains |
|----------|----------|
| FRAMEWORK_SUMMARY.md | Big picture overview |
| SECURITY_TESTING.md | Complete reference |
| TESTING_QUICK_START.md | Getting started |
| TESTING_IMPLEMENTATION.md | Technical details |
| SAMPLE_TEST_OUTPUT.md | Real examples |
| example_usage.py | Code examples |
| This file | Quick reference |

---

## 🚀 Getting Started

1. **First Time Users**: Read `TESTING_QUICK_START.md`
2. **Want Details**: Read `SECURITY_TESTING.md`
3. **Need Examples**: Run `example_usage.py`
4. **Want Integration**: Study `example_usage.py` code
5. **Need Help**: Check this quick reference

---

## ⌛ Typical Timing

| Phase | Duration |
|-------|----------|
| Connection test | ~100-200ms |
| Brute force test | ~1-2 seconds |
| Failed login test | ~1-2 seconds |
| Timeout test | ~500-1000ms |
| All other tests | ~200-500ms each |
| **Total** | **~10-30 seconds** |

*(Times vary with network and server response)*

---

## 🎁 What You Have

✅ 8 comprehensive security tests
✅ Detailed metrics collection
✅ CSV report generation
✅ GUI integration
✅ CLI tool
✅ Python API
✅ Full documentation
✅ Working examples
✅ Error handling
✅ Background processing

---

**Version**: 1.0 | **Date**: January 2025 | **Status**: ✅ Production Ready

For more info: See FRAMEWORK_SUMMARY.md
