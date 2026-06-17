# Flask Dashboard Platform

A modular and extensible admin dashboard built with Flask — designed for developers and startups who want a flexible, scalable backend interface that grows with their project.

This project is **actively being developed** and will serve as a foundation for SaaS products, internal tools, admin panels, and plugin-driven platforms.


### Why Use This Dashboard?

Whether you're building a **SaaS**, an **internal management tool**, or a **custom admin system**, this platform gives you the structure and features you need to launch faster and scale with confidence.


### Key Features

- **Modular Blueprint Architecture**  
  Cleanly separates logic by feature or module — ideal for large, maintainable codebases.

- **Dynamic Plugin/Extension System**  
  Load third-party or in-house modules without editing the core codebase. Each extension can add its own views and assets.

- **Role-Based Access Control (RBAC)**  
  Built-in roles (Admin, Editor, Viewer) with easy customization. Secure critical routes with decorators.

- **Configurable Settings Management**  
  Admins can manage general site settings (title, description, theme, etc.) from the UI — no code changes required.


### Project Structure

```text
├───.github
│   └───workflows
├───core
│   ├───forms
│   ├───initializations
│   ├───models
│   ├───static
│   │   ├───css
│   │   ├───images
│   │   │   └───profiles
│   │   └───js
│   ├───templates
│   │   ├───auth
│   │   └───dashboard
│   ├───utils
│   │   └───registry
│   └───views
├───extensions
├───migrations
└───tests
```

---

## Download and Installation

### Download

```bash
git clone https://github.com/tadiyusss/flaskdash
cd flaskdash
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Virtual Environment

Windows
```powershell
.\venv\Scripts\Activate
```

Linux
```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Environment Variables Setup

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

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

```env
SECRET_KEY="GENERATED_SECRET_KEY"
```

### Run Setup

```bash
python setup.py
```

## Extension Setup Guide

Extensions allow developers to add new functionality to the application without modifying the core codebase.

### Extension Directory Structure

All extensions must be stored inside the extensions/ directory.

Example:

```text
extensions/ 
└─ my-extension/ 
   ├── __init__.py 
   ├── metadata.py 
   ├── static/ 
   └── templates/
```

### Required Files

Every extension must contain the following files:

```metadata.py``` Contains metadata used by the extension loader to identify and register the extension.

```__init__.py``` Serves as the extension entry point. This file is responsible for initializing the extension and registering any routes, blueprints, hooks, or services required by the application.

### Metadata Configuration

The `metadata.py` file must define the following variables:

| Variable          | Description                                                                          |
| ----------------- | ------------------------------------------------------------------------------------ |
| `NAME`            | Human-readable name of the extension. (ex: Extension Name)                                                |
| `SLUG`            | Unique identifier used internally. Use lowercase letters, numbers, and hyphens only. (ex: extension-name) |
| `DESCRIPTION`     | Brief summary of the extension's purpose.                                            |
| `VERSION`         | Current extension version.                                                           |
| `DEPENDENCIES`    | List of required extensions that must be loaded first.                               |
| `AUTHOR`          | Extension author or organization.                                                    |
| `URL_PREFIX`      | Base URL path for extension routes. Leave empty if not required.                     |
| `STATIC_FOLDER`   | Directory containing static assets.                                                  |
| `TEMPLATE_FOLDER` | Directory containing template files.                                                 |

Example Metadata Structure

```python
NAME = "Example Extension"
SLUG = "example-extension"
DESCRIPTION = "Provides example functionality."
VERSION = "1.0.0"
DEPENDENCIES = []
AUTHOR = "Developer Name"
URL_PREFIX = "/example"
STATIC_FOLDER = "static"
TEMPLATE_FOLDER = "templates"
```

### Loading Extensions

The application automatically scans the extensions/ directory and loads extensions that contain both:

- metadata.py
- __init__.py

Extensions missing either file will be ignored.

