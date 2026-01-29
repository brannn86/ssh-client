
# Zero Trust SSH Client

An SSH client with partial zero trust implemented into it. This project is made for... me. For my thesis, specifically.

If you happened to somehow stumble into this repo, I will try to document the project as much as possible.


## Requirements

```bash
  Python=3.14.0
  PySide6>=6.10
  paramiko>=4.0
  cryptography>=46.0
  bcrypt>=5.0
  PyNaCl>=1.5
  pyotp>=2.9.0
  qrcode>=7.4
  Pillow>=10.0.0
```


## Run Locally (venv recommended)

Clone the project

```bash
  git clone https://github.com/brannn86/ssh-client
```

Go to the project directory

```bash
  cd ssh-client
```

Install dependencies

```bash
  pip install -r requirements.txt
```

Run the program

```bash
  python main.py
```


## Security Testing Framework

This project now includes a **comprehensive security testing framework** for testing SSH connections and servers.

### Quick Start

**From GUI:**
1. Open the SSH client
2. Enter target host and port
3. Click "Test Security" button
4. Results appear in terminal and are saved to CSV

**From Command Line:**
```bash
python test_runner.py -H example.com
python test_runner.py -H example.com -p 2222 --timeout 15
```

**From Python Code:**
```python
from testing.security_tester import SecurityTester
tester = SecurityTester(host='example.com', port=22)
results = tester.run_all_tests()
```

### What's Tested

- Connection availability
- Brute force resistance
- Failed login attempts
- Timeout handling
- SSH key rejection
- Concurrent connections
- Credential caching
- Error message disclosure

### Output

- Real-time console output
- CSV reports with detailed metrics
- Summary statistics
- Historical tracking

### Documentation

- [FRAMEWORK_SUMMARY.md](FRAMEWORK_SUMMARY.md) - Overview
- [TESTING_QUICK_START.md](TESTING_QUICK_START.md) - Getting started
- [SECURITY_TESTING.md](SECURITY_TESTING.md) - Complete reference
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Quick lookup
- [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) - All docs

For more details, see [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md).


## Roadmap

- Base UI Functionality ✅

- SSH Connection using Paramiko ✅

- Zero Trust auth and checks ✅

- Store connection policies ✅

- DB with sqlite to store logs and history ✅

- Security Testing Framework ✅