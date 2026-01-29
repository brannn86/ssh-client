# Quick Start Guide - Security Testing

## For GUI Users

1. **Open the SSH client application**
2. **Enter target SSH details:**
   - Host: `example.com` (or your target)
   - Port: `22` (default SSH port)
   - User: any username (not used for security tests)

3. **Click "Test Security" button**
   - Button text changes to "Testing..."
   - Results stream to terminal in real-time
   - Takes 2-5 minutes depending on network

4. **Review results:**
   - ✓ = Test passed (good security)
   - ✗ = Test failed or found vulnerability
   - Green summary shows pass rate

5. **Access detailed reports:**
   - Click terminal output to view results
   - CSV files saved to `test_results/` folder
   - Open with Excel/spreadsheet for analysis

## For Command Line Users

### Basic Test
```powershell
python test_runner.py -H example.com
```

### Advanced Options
```powershell
# Non-standard SSH port
python test_runner.py -H example.com -p 2222

# Custom output directory
python test_runner.py -H example.com -o my_security_audit

# Longer timeout for slow networks
python test_runner.py -H example.com --timeout 15
```

### Help
```powershell
python test_runner.py --help
```

## Understanding Results

### Pass Rate
- **90-100%** - Excellent security posture ✓
- **75-90%** - Good security, minor concerns
- **50-75%** - Moderate security, review failures
- **Below 50%** - Poor security, immediate action needed ✗

### Key Metrics
- **Total tests** - Number of security checks performed
- **Pass/Fail ratio** - Security test outcomes
- **Attempts** - Number of operations performed
- **Duration** - How long tests took

### Important Failures
1. **Brute Force Resistance** - No rate limiting detected
2. **Failed Login Attempts** - No temporary account lockout
3. **Concurrent Connections** - Accepts too many simultaneous connections
4. **Error Messages** - Reveals too much information in errors

## CSV Output

### Columns in security_test_*.csv
- **timestamp** - When test ran
- **test_name** - Which security test
- **status** - Result (success/failed/vulnerable/protected)
- **passed** - Boolean pass/fail
- **metrics** - Duration, attempts, successes, failures
- **details** - Test-specific information

### Opening CSV Files
1. **Excel/Spreadsheet**: Double-click CSV file
2. **Power BI**: Import CSV for visualization
3. **Python**: 
   ```python
   import pandas as pd
   df = pd.read_csv('test_results/security_test_20250129_143022.csv')
   print(df.to_string())
   ```

## Interpreting Tests

### Connection Availability
- **PASS**: SSH port responds to connection attempts
- **FAIL**: Cannot connect to SSH port

### Brute Force Resistance  
- **PASS**: Rate limiting blocks rapid attempts
- **FAIL**: Server accepts multiple failed attempts in quick succession

### Failed Login Attempts
- **PASS**: Blocks connections after failed attempts
- **FAIL**: No apparent protection against failed attempts

### Timeout Handling
- **PASS**: Timeouts are handled gracefully
- **FAIL**: Connection attempt hangs indefinitely

### Key Rejection
- **PASS**: Invalid SSH keys are rejected
- **FAIL**: Invalid keys are somehow accepted

### Concurrent Connections
- **PASS**: Limits number of simultaneous connections
- **FAIL**: Accepts unlimited concurrent connections

### Credential Caching
- **PASS**: Credentials not stored in plaintext
- **FAIL**: Credentials found in cleartext locations

### Error Messages
- **PASS**: Generic error messages don't leak info
- **FAIL**: Error messages reveal user existence or other details

## Common Issues

### "Port not reachable"
- Verify host is correct: `ping example.com`
- Verify port: `telnet example.com 22`
- Check firewall rules

### "All tests timeout"
- Network issue or SSH service down
- Try connecting manually first: use Connect button
- Increase timeout: `--timeout 15`

### "Tests run very slowly"
- High network latency - increase timeout
- SSH server slow to respond
- Try from different network

### "Want to stop tests early"
- Close the application
- Or press Ctrl+C in PowerShell

## Next Steps

1. **Review failing tests** for security concerns
2. **Document results** with `test_results/` folder
3. **Take action** on vulnerabilities found
4. **Re-test** after fixes to verify improvements
5. **Establish baseline** for future comparisons

## Tips

- Test during non-critical hours
- Have read-only access (don't run on production)
- Save results with timestamp in filename
- Compare results over time to track improvements
- Share CSV results with security team

---

For detailed documentation, see [SECURITY_TESTING.md](SECURITY_TESTING.md)
