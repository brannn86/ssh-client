# SSH Client - Building & Distribution Guide

## Building the Portable Executable

### Prerequisites
- Python 3.10+ installed
- All dependencies installed: `pip install -r requirements.txt`
- PyInstaller is already in requirements.txt

### Build Instructions

#### On Linux/Mac:
```bash
chmod +x build.sh
./build.sh
```

#### On Windows:
```cmd
build.bat
```

### Output
The executable will be created in `dist/ssh-client/` with:
- `ssh-client` (Linux/Mac) or `ssh-client.exe` (Windows)
- `policies.json` - Policy configuration
- `totp_secrets.json` - TOTP secrets (created on first run if needed)
- `zt_ssh.db` - Database (created on first run)

## Running the Application

### From Build Directory:
```bash
# Linux/Mac
cd dist/ssh-client
./ssh-client

# Windows
cd dist\ssh-client
ssh-client.exe
```

### Portable Distribution:
```bash
# Create a zip archive
cd dist
zip -r ssh-client.zip ssh-client/

# On Windows, use:
# powershell -Command "Compress-Archive -Path ssh-client -DestinationPath ssh-client.zip"
```

## Important Notes

1. **Config Files Location**: All JSON and database files are stored in the same directory as the executable, making it truly portable.

2. **First Run**: On first connection, the app will:
   - Create `totp_secrets.json` for TOTP storage
   - Initialize `zt_ssh.db` for session/login history

3. **Distribution**: Users only need to:
   - Extract the zip file
   - Run the executable
   - All dependencies are bundled (no Python installation needed)

4. **Cross-Platform**: 
   - Build on Linux/Mac produces Linux/Mac executable
   - Build on Windows produces Windows executable
   - For multi-platform distribution, build on each target OS

## Customization

### Add Application Icon:
Edit `build.spec` and change:
```python
icon=None,
```
to:
```python
icon='path/to/icon.ico',
```

### Console Window:
For debugging, change `console=False` to `console=True` in `build.spec` to show console output.

### File Size:
- Without compression: ~200-300 MB
- With UPX compression: ~100-150 MB (UPX may not work on all systems)

## Troubleshooting

### "PyInstaller not found":
```bash
pip install pyinstaller
```

### Module not found errors:
Ensure all hidden imports in `build.spec` match your dependencies.

### Database/Config files not found:
Make sure you run the executable from the directory where the config files are located, or ensure they're in the same directory as the executable.

### Build on Linux doesn't include PySide6:
Add to your `build.spec` datas section if needed:
```python
datas=[
    ('path/to/PySide6', 'PySide6'),
],
```
