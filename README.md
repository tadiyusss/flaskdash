# Flask Dashboard Platform

A modular and extensible admin dashboard built with Flask — designed for developers and startups who want a flexible, scalable backend interface that grows with their project.

This project is **actively being developed** and will serve as a foundation for SaaS products, internal tools, admin panels, and plugin-driven platforms.

---

## Why Use This Dashboard?

Whether you're building a **SaaS**, an **internal management tool**, or a **custom admin system**, this platform gives you the structure and features you need to launch faster and scale with confidence.

---

## Key Features

- **Modular Blueprint Architecture**  
  Cleanly separates logic by feature or module — ideal for large, maintainable codebases.

- **Dynamic Plugin/Extension System**  
  Load third-party or in-house modules without editing the core codebase. Each extension can add its own views and assets.

- **Role-Based Access Control (RBAC)**  
  Built-in roles (Admin, Editor, Viewer) with easy customization. Secure critical routes with decorators.

- **Configurable Settings Management**  
  Admins can manage general site settings (title, description, theme, etc.) from the UI — no code changes required.

---

## Download

```bash
git clone https://github.com/tadiyusss/flaskdash
cd flaskdash
```

## Create Virtual Environment

```bash
python -m venv venv
```

## Activate Virtual Environment

Windows
```powershell
.\venv\Scripts\Activate
```

Linux
```bash
source venv/bin/activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Environment Variables Setup

```bash
cp .env.example .env
```

After copying .env.example file enter your database details and mail server credentials

```env
MYSQL_DATABASE_URL = "mysql+pymysql://USERNAME:PASSWORD@127.0.0.1/DBNAME"
MAIL_SERVER = 127.0.0.1
MAIL_PORT = 587
MAIL_USE_TLS = false
MAIL_USERNAME = 
MAIL_PASSWORD = 
MAIL_DEFAULT_SENDER = "noreply@example.com"
```

Generate SECRET_KEY and paste it to .env file

```python
python -c "import secrets; print(secrets.token_hex(32))"
```

```env
SECRET_KEY="GENERATED_SECRET_KEY"
```

## Run Setup

```bash
python setup.py
```