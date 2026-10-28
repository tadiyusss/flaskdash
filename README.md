# Flask Dashboard Platform

A modular and extensible admin dashboard built with Flask — designed for developers and startups who want a flexible, scalable backend interface that grows with their project.

This project is **actively being developed** and will serve as a foundation for SaaS products, internal tools, admin panels, and plugin-driven platforms.

## Table of Contents

- [Use Cases](#why-use-this-dashboard)
- [Features](#key-features)
- [Project Structure](#project-structure)
- [Download](#download)
- [Setup Environemnt](#create-virtual-environment)
- [CLI Commands](#custom-cli-commands)
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
Directory structure:
└── flaskdash/
    ├── README.md
    ├── build-themes.js
    ├── config.py
    ├── docker-compose.yml
    ├── Dockerfile
    ├── package.json
    ├── requirements.txt
    ├── ruff.toml
    ├── run.py
    ├── tailwind.config.js
    ├── .dockerignore
    ├── .env.example
    ├── core/
    │   ├── __init__.py
    │   ├── context.py
    │   ├── defaults.py
    │   ├── extensions.py
    │   ├── route.py
    │   ├── commands/
    │   ├── forms/
    │   ├── initializations/
    │   ├── models/
    │   ├── static/
    │   │   ├── css/
    │   │   └── js/
    │   ├── stubs/
    │   │   └── extensions/
    │   │       ├── forms/
    │   │       ├── initialization/
    │   │       ├── models/
    │   │       ├── routes/
    │   │       └── templates/
    │   ├── templates/
    │   │   ├── auth/
    │   │   └── dashboard/
    │   ├── utils/
    │   │   └── registry/
    │   └── views/
    ├── migrations/
    ├── tests/
    └── themes/
        └── default/

```

---

## Download and Installation

### Download

```bash
git clone https://github.com/tadiyusss/flaskdash
cd flaskdash
```

### Install and Build Node Dependencies

```
npm install
npm run build
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
DATABASE_URL = "mysql+pymysql://USERNAME:PASSWORD@127.0.0.1/DBNAME"
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

### Run Migrations

```bash
flask --app run.py extensions upgrade-all
```

### Create Administrator Account

```bash
flask --app run.py users create-admin
```

## Custom CLI Commands

The platform ships with a set of custom Flask CLI commands for managing extensions, themes, and users. All commands are run through the Flask CLI:

```bash
flask --app run.py <group> <command> [options]
```

To list the available groups or the commands inside a group, use `--help`:

```bash
flask --app run.py --help
flask --app run.py extensions --help
```

Options marked as **prompted** will ask for input interactively if you don't pass them as flags.

- [Extensions Commands](#extensions-commands)
- [Themes Commands](#themes-commands)
- [Users Commands](#users-commands)

---

### Extensions Commands

Commands for creating, migrating, and managing extensions.

```bash
flask --app run.py extensions <command>
```

| Command         | Description                                          |
| --------------- | ---------------------------------------------------- |
| `create`        | Generate a new extension from the stub template.     |
| `delete`        | Delete an existing extension.                        |
| `makemigration` | Create a migration file for an extension.            |
| `upgrade`       | Run migrations for a specific extension.             |
| `upgrade-all`   | Run migrations for all extensions.                   |
| `current-db`    | Show the current database version of an extension.   |
| `install-deps`  | Install requirements for all extensions.             |

#### Create an Extension

Opens an interactive prompt and generates a blank extension inside the `extensions/` directory using the stub files in `core/stubs/extensions/`.

```bash
flask --app run.py extensions create
```

| Option     | Description                    |
| ---------- | ------------------------------ |
| `--name`   | Name of the new extension. **(prompted)** |
| `--author` | Name of the author. **(prompted)**        |

Example:

```bash
flask --app run.py extensions create --name "My Extension" --author "Developer Name"
```

The extension name is converted automatically:

| Format      | Example        | Used For                          |
| ----------- | -------------- | --------------------------------- |
| Snake case  | `my_extension` | Directory name                    |
| Slug case   | `my-extension` | Extension slug and URL            |

After creation, visit `http://localhost:8000/my-extension` once the server is running to check the extension.

#### Delete an Extension

Permanently deletes an extension and all of its files. You will be asked to confirm before anything is removed.

```bash
flask --app run.py extensions delete
```

| Option   | Description                          |
| -------- | ------------------------------------ |
| `--name` | Name of the extension to delete. **(prompted)** |

Example:

```bash
flask --app run.py extensions delete --name "My Extension"
```

> **Warning:** This action cannot be undone.

#### Create a Migration

Generates a new migration file for an extension. If the extension does not have a `migrations/` directory yet, it is initialized automatically and the extension's migration `env.py` is patched.

```bash
flask --app run.py extensions makemigration
```

| Option                | Description                                    |
| --------------------- | ---------------------------------------------- |
| `--extension`, `-e`   | Name of the extension. **(prompted)**          |
| `--message`, `-m`     | Short description of the change. *(optional)*  |

Example:

```bash
flask --app run.py extensions makemigration -e "My Extension" -m "add posts table"
```

If no model changes are detected, no migration file is created.

#### Run Migrations for an Extension

Applies the pending migrations of a single extension.

```bash
flask --app run.py extensions upgrade
```

| Option              | Description                           |
| ------------------- | ------------------------------------- |
| `--extension`, `-e` | Name of the extension. **(prompted)** |

Example:

```bash
flask --app run.py extensions upgrade -e my_extension
```

#### Run Migrations for All Extensions

Loops through every extension directory and applies their pending migrations.

```bash
flask --app run.py extensions upgrade-all
```

#### Show Current Database Version

Shows the current migration version of an extension's database.

```bash
flask --app run.py extensions current-db
```

| Option              | Description                           |
| ------------------- | ------------------------------------- |
| `--extension`, `-e` | Name of the extension. **(prompted)** |

Example:

```bash
flask --app run.py extensions current-db -e my_extension
```

#### Install Extension Dependencies

Installs the requirements of every registered extension and prints `ok` or `FAILED` for each one.

```bash
flask --app run.py extensions install-deps
```

Example output:

```text
my_extension: ok
another_extension: FAILED
```

___

### Themes Commands

Commands for listing, building, and inspecting themes.

```bash
flask --app run.py themes <command>
```

| Command | Description                                  |
| ------- | -------------------------------------------- |
| `list`  | List all available themes.                   |
| `build` | Compile and prepare a theme for use.         |
| `view`  | View information about a theme.              |

#### List Themes

Prints the name of every available theme.

```bash
flask --app run.py themes list
```

Example output:

```text
Available themes:
- default
```

#### Build a Theme

Compiles and prepares the selected theme for use.

```bash
flask --app run.py themes build
```

| Option            | Description                                                |
| ----------------- | ---------------------------------------------------------- |
| `--theme`, `-t`   | Name of the theme to build, without `.css`. **(prompted)** |

Example:

```bash
flask --app run.py themes build -t default
```

If the theme does not exist, `Theme '<name>' not found.` is shown. Any build error is printed to the console.

#### View Theme Information

Shows the details of the selected theme as `key: value` pairs.

```bash
flask --app run.py themes view
```

| Option            | Description                                               |
| ----------------- | --------------------------------------------------------- |
| `--theme`, `-t`   | Name of the theme to view, without `.css`. **(prompted)** |

Example:

```bash
flask --app run.py themes view -t default
```

___

### Users Commands

Commands for managing user accounts.

```bash
flask --app run.py users <command>
```

| Command        | Description                          |
| -------------- | ------------------------------------ |
| `create-admin` | Create a new administrator user.     |
| `delete-user`  | Delete a user by username.           |

#### Create an Administrator

Creates a new user and assigns them the `Administrator` role. The password is entered through a hidden prompt and must be typed twice.

```bash
flask --app run.py users create-admin
```

| Option        | Description                                  |
| ------------- | -------------------------------------------- |
| `--username`  | Username of the administrator. **(prompted)**   |
| `--firstname` | First name of the administrator. **(prompted)** |
| `--lastname`  | Last name of the administrator. **(prompted)**  |
| `--email`     | Email address of the administrator. **(prompted)** |

Example:

```bash
flask --app run.py users create-admin --username admin --firstname John --lastname Doe --email admin@example.com
```

You will then be asked for:

```text
Password (inputs are hidden):
Retype Password (inputs are hidden):
```

If the passwords do not match, the command exits without creating the user.

> **Note:** The `Administrator` role must already exist in the database. Run the migrations first (`extensions upgrade-all`).

#### Delete a User

Deletes an existing user by username.

```bash
flask --app run.py users delete-user
```

| Option       | Description                                   |
| ------------ | --------------------------------------------- |
| `--username` | Username of the user to delete. **(prompted)** |

Example:

```bash
flask --app run.py users delete-user --username johndoe
```

If the user does not exist, `User '<username>' not found.` is shown.

> **Warning:** This action cannot be undone and does not ask for confirmation.

___

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

### Creating a Extension

Running the command below will automatically generate a blank extension for development. 

```
flask --app run.py extensions create 
```

## Core Integrations

This section explains how extensions integrate with the **core system** using four primary integration points:

- [Settings](#1-settings-integration)
- [Analytics](#2-analytics-widget-integration)
- [Roles](#3-analytics-widget-integration)
- [Sidebar Navigation](#4-dashboard-side-navigation-integration)

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

### 2. Analytics Widget Integration

Analytics allow extensions to display dashboard metrics on the core home page.

Use analytics for:

- Usage statistics
- Business metrics
- System health indicators
- Feature activity tracking

#### Adding a Analytics Grid and Analytics Item

```python
from core.utils.analytics import Grid, SmallAnalyticsCardData
from core.utils.registry.analytics import register_analytics


ANALYTICS = [
    Grid(
        title="Grid Title",
        contents=[
            SmallAnalyticsCardData(
                title="Data Name",
                value_function=lambda: data_func(),
                roles=["Administrator"],
                icon="<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 20 20' fill='currentColor' class='fd-analytics-section-title'><path d='M10 12.5a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5Z' /><path fill-rule='evenodd' d='M.664 10.59a1.651 1.651 0 0 1 0-1.186A10.004 10.004 0 0 1 10 3c4.257 0 7.893 2.66 9.336 6.41.147.381.146.804 0 1.186A10.004 10.004 0 0 1 10 17c-4.257 0-7.893-2.66-9.336-6.41ZM14 10a4 4 0 1 1-8 0 4 4 0 0 1 8 0Z' clip-rule='evenodd' /></svg>"
            )
        ],
        roles=["Administrator"],
    )
]
register_analytics(item)
```

___

### 3. Custom Role Integration

Roles define access control and permissions for both core and extension features.

Use roles for:
- Route protection
- Feature access control
- Admin/user separation
- Fine-grained permission handling

#### Creating a Role

```python
from core.utils.registry.roles import register_role
from core.utils.roles import Role

role = Role(
    name="Role Name",
    description="Description about the role.",
)

register_role(role)
```

___

### 4. Dashboard Side Navigation Integration

Sidebar navigation allows extensions to register menu items in the authenticated user dashboard.

Use sidebar items for:
- Extension pages
- Dashboard tools
- Feature entry points
- Navigation shortcuts

#### Creating a sidebar category with items

```python
from core.utils.registry.side_navigation import register_category
from core.utils.dashboard import DashboardCategory, DashboardItem

category = DashboardCategory(
    name="Category Name",
    roles=["Administrator"],
    items=[
        DashboardItem(
            name="Item Name",
            icon_type="svg",
            icon="<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 20 20' fill='currentColor' class='fd-sidebar-item'><path fill-rule='evenodd' d='M18 10a8 8 0 1 1-16 0 8 8 0 0 1 16 0ZM8.94 6.94a.75.75 0 1 1-1.061-1.061 3 3 0 1 1 2.871 5.026v.345a.75.75 0 0 1-1.5 0v-.5c0-.72.57-1.172 1.081-1.287A1.5 1.5 0 1 0 8.94 6.94ZM10 15a1 1 0 1 0 0-2 1 1 0 0 0 0 2Z' clip-rule='evenodd' /></svg>",
            route="extension_name.function_name",
            roles=["Administrator"]
        )
    ]
)

register_category(category)
```

Registering a sidebar item with an existing category

```python
from core.utils.registry.side_navigation import register_sidebar_item
from core.utils.dashboard import DashboardItem

item = DashboardItem(
    name="Another item name",
    icon_type="svg",
    icon="<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 20 20' fill='currentColor' class='fd-sidebar-item'><path fill-rule='evenodd' d='M18 10a8 8 0 1 1-16 0 8 8 0 0 1 16 0ZM8.94 6.94a.75.75 0 1 1-1.061-1.061 3 3 0 1 1 2.871 5.026v.345a.75.75 0 0 1-1.5 0v-.5c0-.72.57-1.172 1.081-1.287A1.5 1.5 0 1 0 8.94 6.94ZM10 15a1 1 0 1 0 0-2 1 1 0 0 0 0 2Z' clip-rule='evenodd' /></svg>",
    route="extension_name.function_name",
    roles=["Administrator"]
)

register_sidebar_item(item, "Category Name")
```

___