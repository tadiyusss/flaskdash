# Flask Dashboard Platform

A modular and extensible admin dashboard built with Flask — designed for developers and startups who want a flexible, scalable backend interface that grows with their project.

This project is **actively being developed** and will serve as a foundation for SaaS products, internal tools, admin panels, and plugin-driven platforms.

## Table of Contents

- [Use Cases](#why-use-this-dashboard)
- [Features](#key-features)
- [Project Structure](#project-structure)
- [Download](#download)
- [Setup Environemnt](#create-virtual-environment)
- [Extension Setup](#extension-setup-guide)
- [Core Integrations](#core-integrations)

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

## Project Structure

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

- ```metadata.py```
- ```__init__.py```

Extensions missing either file will be ignored.

### Extension Initialization Guide (`__init__.py`)

Every extension **must** include an `init_extension(app, db)` function inside its `__init__.py` file.  
This function acts as the **entry point** for registering all extension components into the core system.

### Purpose

The init_extension function is responsible for:

- Initializing database tables (if needed)
- Registering settings
- Registering analytics
- Registering roles
- Registering sidebar/navigation items
- Returning the Flask Blueprint

### Example Implementation

```python
from flask import Blueprint
from .metadata import TEMPLATE_FOLDER, STATIC_FOLDER

bp = Blueprint(
    "example_extension",
    __name__,
    template_folder=TEMPLATE_FOLDER,
    static_folder=STATIC_FOLDER,
    static_url_path="/static/example_extension"
)

from .routes import route_example

def init_extension(app, db):
    with app.app_context():
        # Initialize database tables (if extension uses models)
        db.create_all()
    return bp
```

## Core Integrations

This section explains how extensions integrate with the **core system** using four primary integration points:

- Settings
- Analytics
- Roles
- Sidebar Navigation

All integrations are registered inside the extension’s `init_extension(app, db)` lifecycle through dedicated initialization modules.

The core system provides a **registry-based architecture** that allows extensions to safely extend functionality without modifying core code.

### 1. Settings Integration

Settings allow extensions to expose configurable options inside the **core Settings page**.

Use settings for:

- Feature toggles
- API keys
- UI preferences
- Extension configuration
- Environment-dependent values

#### Adding a Setting Category with Setting Item

```python
from core.utils.registry.settings import register_category
from core.utils.settings import SettingCategory, SettingItem
from wtforms import StringField

settings_category = SettingCategory(
    name="category_name",
    nice_name="Category Name",
    description="A sample setting category",
    settings=[
        SettingItem(
            key="unique_key",
            name="Setting Name",
            value="default_value",
            field=StringField(
                "Field Name", 
                description="Description about the field.",
            ),
            category_name="category_name"
        )
    ]
)
register_category(settings_category)
```

#### Adding a one Setting Item 

```python
from core.utils.registry.settings import register_setting
from core.utils.settings import SettingItem
from wtforms import StringField

item = SettingItem(
    key="another_unique_key",
    name="Another Setting Name",
    value="default_value",
    field=StringField(
        "Another Field Name", 
        description="Another description about the field.",
    ),
    category_name="category_name"
)
register_setting(item)
```

___