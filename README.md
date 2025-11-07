
# Zero Trust SSH Client

An SSH client with partial zero trust implemented into it. This project is made for... me. For my thesis, specifically.

If you happened to somehow stumble into this repo, I will try to document the project as much as possible.


## Tech Stack

**Client:** Python, PySide6, Paramiko, Cryptography, PySQLite3


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

- Base UI Functionality

- SSH Connection using Paramiko

- Zero Trust auth and checks

- Store connection policies

- DB with sqlite to store logs and history