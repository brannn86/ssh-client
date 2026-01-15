
# Zero Trust SSH Client

An SSH client with partial zero trust implemented into it. This project is made for... me. For my thesis, specifically.

If you happened to somehow stumble into this repo, I will try to document the project as much as possible.


## Requirements

```bash
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


## Roadmap

- Base UI Functionality ✅

- SSH Connection using Paramiko ✅

- Zero Trust auth and checks ✅

- Store connection policies ✅

- DB with sqlite to store logs and history ✅