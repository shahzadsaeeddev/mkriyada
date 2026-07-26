# Mkriyada — POS & ZATCA E-Invoicing Backend

A Django REST Framework backend powering a **Point of Sale (POS) and e-invoicing platform** built for a client in **Saudi Arabia**, developed at **Neksio Technology**. The system handles product/inventory management, multi-tenant company accounts, subscriptions and billing, and full **ZATCA (Zakat, Tax and Customs Authority) e-invoicing compliance** — including CSR generation, invoice signing, clearance, and compliance/reporting APIs — with **Keycloak-based authentication and role-based access control (RBAC)**.

---

## Features

- **Point of Sale (POS) core**
  - Products, categories, units of measurement, item tags, media files
  - Multi-company support with per-company data isolation
  - Customer and supplier management
  - Invoicing and transaction processing
  - Activity logs and notification center

- **ZATCA E-Invoicing Compliance**
  - CSR (Certificate Signing Request) generation for EGS (E-invoicing Generation Solution) onboarding
  - Invoice **signing** (Java-based signing service)
  - **Clearance** and **Reporting** invoice flows (Standard & Simplified)
  - **Compliance** checks against ZATCA's simulation APIs
  - Separate **Sandbox** and **Production** onboarding/environments
  - QR code generation for invoices

- **Authentication & Authorization**
  - **Keycloak** SSO via `mozilla-django-oidc`
  - Custom OIDC backend and Keycloak admin integration (user provisioning, role/group assignment)
  - **Role-based access control** via configurable Role Groups
  - API key authentication for machine-to-machine access (`djangorestframework-api-key`)

- **Billing & Subscriptions**
  - Subscription plans and payment history
  - **PayPal** integration for subscription payments

- **Platform**
  - Async task processing with **Celery** + **Redis**
  - **PostgreSQL** database
  - Auto-generated **Swagger / ReDoc** API documentation (`drf-yasg`)
  - Dockerized for consistent deployment

---

## Tech Stack

| Layer            | Technology                                             |
|-------------------|--------------------------------------------------------|
| Framework         | Django, Django REST Framework                          |
| Auth              | Keycloak (OIDC) via `mozilla-django-oidc`, RBAC         |
| Database          | PostgreSQL                                              |
| Async / Queue     | Celery, Redis                                           |
| Payments          | PayPal SDK                                              |
| E-Invoicing       | ZATCA APIs (Compliance, Clearance, Reporting), Java-based signing |
| API Docs          | drf-yasg (Swagger / ReDoc)                              |
| Containerization  | Docker, Docker Compose                                  |
| Web server        | Gunicorn                                                 |

---

---

## Getting Started (Docker)

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) installed

### Setup

1. **Clone the repository**
   ```bash
   git clone git@github.com:shahzadsaeeddev/mkriyada.git
   cd mkriyada
   ```

2. **Configure environment variables**

   Create a `.env` file in the project root (same level as `docker-compose.yaml`) with the following variables:

   ```env
   # Django
   SECRET_KEY=your-django-secret-key
   DEBUG=True

   # Database
   POSTGRES_DB=mkriyada
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=your-db-password
   DJANGO_DB_NAME=mkriyada
   DJANGO_DB_USER=postgres
   DJANGO_DB_PASSWORD=your-db-password
   DJANGO_DB_HOST=db
   DJANGO_DB_PORT=5432

   # Keycloak / OIDC
   OIDC_HOST=https://your-keycloak-host
   OIDC_REALM=your-realm
   OIDC_RP_CLIENT_ID=your-client-id
   OIDC_RP_CLIENT_SECRET=your-client-secret
   OIDC_RP_SIGN_ALGO=RS256
   TOKEN_EXPIRATION_TIME=300
   TOKEN_EXPIRATION_LEEWAY=60

   # PayPal
   PAYPAL_CLIENT_ID=your-paypal-client-id
   PAYPAL_CLIENT_SECRET=your-paypal-client-secret
   PAYPAL_API_BASE=https://api-m.sandbox.paypal.com

   # Email
   EMAIL_HOST_USER=your-email
   EMAIL_HOST_PASSWORD=your-email-password

   # Django superuser (created automatically on first run)
   DJANGO_SUPERUSER_USERNAME=admin
   DJANGO_SUPERUSER_EMAIL=admin@example.com
   DJANGO_SUPERUSER_PASSWORD=change-this-password
   ```

3. **Build and run the containers**
   ```bash
   docker-compose up --build
   ```

   This will:
   - Build and start the Django app (`web`), **PostgreSQL** (`db`), and **Redis** (`redis`)
   - Run migrations automatically
   - Collect static files
   - Create a Django superuser (if it doesn't already exist)
   - Load initial fixture data
   - Start a **Celery worker**
   - Serve the app via **Gunicorn** on port `8000`

4. **Access the application**
   - API base URL: `http://localhost:8000/`
   - Django admin: `http://localhost:8000/admin/`
   - Swagger UI: `http://localhost:8000/swagger/` *(available when `DEBUG=True`)*
   - ReDoc: `http://localhost:8000/redoc/`

---

## API Overview

| Module            | Description                                                  |
|--------------------|----------------------------------------------------------------|
| `/accounts/`       | Authentication, user & role management (Keycloak-backed)       |
| `/` (api)          | Company, Customer, Supplier, Invoices, Dashboard, Reports, Subscriptions, PayPal, ZATCA (Sandbox/Production) |
| `/items/`          | Product catalog: products, categories, units, tags             |

Full request/response schemas are available via the **Swagger UI** once the app is running.

---

## Authentication

This project uses **Keycloak** as the identity provider via OpenID Connect (OIDC):

- User sign-in is delegated to Keycloak; the backend validates tokens through `mozilla-django-oidc`.
- On user creation, accounts are provisioned in Keycloak and assigned to a **Role Group**, which determines access permissions across the API (RBAC).
- Machine-to-machine access is supported via **API keys** as an alternative authentication method.

---

## ZATCA E-Invoicing Flow

1. **CSR Generation** — generate a Certificate Signing Request for the client's EGS (E-invoicing Generation Solution) unit.
2. **Onboarding** — complete Compliance CSID / Production CSID issuance against ZATCA's Sandbox or Production environment.
3. **Invoice Signing** — invoices are digitally signed (Java-based signing service) and a QR code is generated per ZATCA specifications.
4. **Clearance / Reporting** — Standard invoices are sent for **clearance**; Simplified invoices are sent for **reporting**, per ZATCA's e-invoicing regulations.

---

## License

This is a proprietary client project developed by **Neksio Technology**. All rights reserved — not licensed for public reuse or redistribution.

---

## Maintainer

Backend architecture and development by the Neksio Technology backend team, in coordination with the frontend team, for a Saudi Arabia-based POS & e-invoicing client implementation.
