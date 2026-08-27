# BTP — Construction Management for ERPNext

> **Construction management for Moroccan BTP companies, built on Frappe and ERPNext.**

BTP is an open-source construction management application being developed for **Moroccan construction and BTP companies**.

The project extends **Frappe / ERPNext** with construction-specific workflows, data models, and business processes while keeping ERPNext as the underlying ERP platform.

> **Status: Work in Progress**
>
> BTP is actively under development. Features, workflows, and the data model are still evolving and the application is not yet considered production-ready.

## Overview

Construction companies have operational requirements that are not fully covered by a general-purpose ERP.

BTP aims to provide a dedicated construction layer on top of ERPNext, covering the workflows involved in managing construction projects, resources, costs, and day-to-day operations.

The project is being developed with the **Moroccan construction market** in mind, with future consideration for local business practices, terminology, and regulatory requirements.

The goal is not to rebuild ERPNext.

Instead, BTP adds the construction-specific functionality needed by BTP companies while continuing to use ERPNext for core ERP capabilities.

## Architecture

```text
┌─────────────────────────────────┐
│              BTP                │
│ Construction-specific features  │
│ Workflows · DocTypes · Reports  │
└────────────────┬────────────────┘
                 │
┌────────────────▼────────────────┐
│            ERPNext              │
│ Accounting · Stock · Projects   │
│ Buying · Selling · HR · CRM     │
└────────────────┬────────────────┘
                 │
┌────────────────▼────────────────┐
│             Frappe              │
│ Framework · ORM · API · Auth    │
│ Permissions · Background Jobs   │
└─────────────────────────────────┘
```

ERPNext already provides core ERP functionality such as accounting, inventory, purchasing, projects, HR, and other business operations. BTP focuses on extending that foundation for construction-specific use cases.

## Target Users

BTP is being designed primarily for Moroccan:

* Construction companies
* BTP contractors
* Civil engineering companies
* Building contractors
* Subcontractors
* Infrastructure companies
* Construction project teams

The application may evolve to support additional construction-related businesses and workflows as development progresses.

## Current Direction

The project is currently focused on establishing the foundation for construction management within ERPNext.

Planned and evolving areas include:

* Construction project management
* Construction-specific DocTypes
* Project and site workflows
* Cost and resource tracking
* Construction operations
* Construction reporting
* Integration with ERPNext's existing modules
* Moroccan-specific business requirements

These areas are part of the project's development direction and should not be interpreted as completed functionality.

## Technology

| Layer                  | Technology                        |
| ---------------------- | --------------------------------- |
| ERP Platform           | ERPNext                           |
| Framework              | Frappe Framework                  |
| Backend                | Python                            |
| Database               | MariaDB                           |
| Frontend               | Frappe UI / JavaScript            |
| Application Management | Frappe Bench                      |
| Code Quality           | Ruff, ESLint, Prettier, PyUpgrade |

## Installation

BTP is installed as a Frappe application inside an existing Frappe/ERPNext Bench environment.

### Requirements

You need a working Frappe Bench installation with ERPNext installed.

### Get the application

```bash
cd $PATH_TO_YOUR_BENCH

bench get-app https://github.com/yassinidyhya/construction_ERP.git --branch develop
```

### Install the application

```bash
bench install-app btp
```

After installation, migrate the site if required:

```bash
bench --site <your-site> migrate
```

## Development

The application is located inside the Bench apps directory:

```text
apps/btp/
```

Start the development environment with:

```bash
bench start
```

Because BTP is still under development, installation and development requirements may change as the project evolves.

## Code Quality

The repository uses `pre-commit` for formatting and linting.

Install the hooks:

```bash
cd apps/btp
pre-commit install
```

Run all checks manually:

```bash
pre-commit run --all-files
```

The current configuration includes:

* Ruff
* ESLint
* Prettier
* PyUpgrade

## Project Structure

The application follows the standard Frappe application structure.

```text
construction_ERP/
├── btp/
│   ├── hooks.py
│   ├── modules.txt
│   └── ...
├── pyproject.toml
├── license.txt
└── README.md
```

As development progresses, construction-specific modules, DocTypes, reports, workflows, and utilities will be added to the application.

## Project Status

**Work in Progress**

BTP is not a finished product.

The project is currently being developed as a foundation for a construction management solution for Moroccan BTP companies.

The architecture, data model, workflows, and functionality may change significantly during development.

Do not use the current version as a production construction management system unless you have independently reviewed and validated the application for your requirements.

## Roadmap

The roadmap will evolve alongside the project.

Potential areas of development include:

* [ ] Construction project workflows
* [ ] Site management
* [ ] Construction cost management
* [ ] Resource management
* [ ] Construction reporting
* [ ] Moroccan business localization
* [ ] Additional ERPNext integrations
* [ ] Production deployment readiness
* [ ] Documentation and user guides

## Contributing

BTP is a public project and contributions, issues, and suggestions are welcome.

If you want to propose a significant change, open an issue first so the approach can be discussed before implementation.

Before submitting changes, run:

```bash
pre-commit run --all-files
```

## License

BTP is released under the MIT License.

See [`license.txt`](license.txt) for the complete license text.

## Built With

* [Frappe Framework](https://frappe.io/)
* [ERPNext](https://erpnext.com/)

---

**BTP** — Building construction management capabilities for ERPNext, with Moroccan BTP companies in mind.
