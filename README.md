<<<<<<< HEAD
# ⚡ RapidVenta – Online Auction House

> Production-ready Django 5.2 MVP · Python 3.12 · PostgreSQL/SQLite · Sky Blue & White UI

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Project Structure](#project-structure)
3. [Quick Start](#quick-start)
4. [Environment Variables](#environment-variables)
5. [Apps & Responsibilities](#apps--responsibilities)
6. [Key Design Decisions](#key-design-decisions)
7. [Auction Lifecycle](#auction-lifecycle)
8. [Closing Auctions](#closing-auctions)
9. [Bulk Upload CSV](#bulk-upload-csv)
10. [Admin Panel](#admin-panel)
11. [Production Deployment](#production-deployment)

---

## Architecture Overview

```
Browser → Django Views (CBV) → Services → Models → PostgreSQL
                                ↑
                           Selectors (read-only queries)
                           Signals   (side-effects)
```

- **Views** are thin: they validate input, call a service, redirect or render.
- **Services** (`services.py` in each app) own all business logic.
- **Selectors** (`selectors.py`) own all read queries — no raw ORM in views.
- **Signals** handle decoupled side-effects (email notifications, audit logs).

---

## Project Structure

```
rapidventa/
├── manage.py
├── requirements.txt
├── .env.example
├── sample_listings.csv
│
├── rapidventa/                  # Django project package
│   ├── settings/
│   │   ├── base.py              # Shared settings
│   │   ├── development.py       # SQLite + console email
│   │   └── production.py        # PostgreSQL + SMTP + security headers
│   ├── urls.py
│   ├── celery.py
│   ├── wsgi.py
│   └── asgi.py
│
├── accounts/                    # Custom User, auth, profiles
│   ├── managers.py
│   ├── models.py                # User (email-based, roles, is_validated_by_admin)
│   ├── services.py              # register_user, update_profile, validate_user
│   ├── selectors.py
│   ├── forms.py
│   ├── views.py                 # CBV: Register, Login, Dashboard, Profile, History
│   ├── urls.py
│   ├── signals.py
│   └── admin.py                 # Bulk validate users
│
├── listings/                    # Auction listings & categories
│   ├── managers.py              # active(), ended_unclosed(), by_seller()
│   ├── models.py                # Category, Listing (with Status enum)
│   ├── services.py              # create, approve, reject, close, republish, bulk_upload
│   ├── selectors.py
│   ├── forms.py                 # ListingForm, ListingFilterForm, CSVUploadForm
│   ├── views.py                 # CBV: List, Detail, Create, MyListings, CSVUpload
│   ├── urls.py
│   ├── signals.py
│   └── admin.py                 # Approve/reject listings
│
├── bids/                        # Bidding engine
│   ├── models.py                # Bid (user, listing, amount, timestamp)
│   ├── services.py              # place_bid (all rules enforced here)
│   ├── selectors.py
│   ├── forms.py
│   ├── views.py                 # PlaceBidView (POST only)
│   ├── urls.py
│   └── signals.py               # Outbid notifications
│
├── orders/                      # Post-auction order tracking
│   ├── models.py                # Order (UUID ref, status, tracking_number)
│   ├── services.py              # create_order, advance_status, cancel, update_tracking
│   ├── selectors.py
│   ├── forms.py
│   ├── views.py                 # CBV: OrderList, OrderDetail, StaffOrderList
│   ├── urls.py
│   └── admin.py
│
├── core/                        # Shared utilities
│   ├── mixins.py                # SellerRequiredMixin, StaffRequiredMixin, ValidatedUserRequiredMixin
│   ├── utils.py                 # humanize_timedelta, slugify_unique
│   └── management/
│       └── commands/
│           └── close_auctions.py  # ★ THE AUCTION ENGINE
│
├── templates/
│   ├── base.html
│   ├── components/
│   │   ├── navbar.html
│   │   ├── footer.html
│   │   ├── messages.html
│   │   └── pagination.html
│   ├── accounts/                # login, register, dashboard, profile, auction_history
│   ├── listings/                # list, detail, create, my_listings, upload_csv
│   └── orders/                  # list, detail, staff_list
│
└── static/
    ├── css/main.css             # Full design system (700+ lines, CSS variables)
    └── js/main.js               # Countdown timers, bid UI, auto-dismiss alerts
```

---

## Quick Start

### 1. Clone & create virtual environment

```bash
git clone <repo>
cd rapidventa
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env – at minimum set SECRET_KEY
# Leave USE_SQLITE=True for local development
```

### 3. Apply migrations & create superuser

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 4. Create initial categories (via Django shell or admin)

```bash
python manage.py shell
>>> from listings.models import Category
>>> Category.objects.create(name="Watches", slug="watches")
>>> Category.objects.create(name="Art", slug="art")
>>> Category.objects.create(name="Furniture", slug="furniture")
>>> exit()
```

### 5. Run development server

```bash
python manage.py runserver
```

### 6. Start Celery worker and beat scheduler (auction auto-close)

Redis must be running locally (`redis-server`). Open two extra terminals:

```bash
celery -A rapidventa worker -l info
celery -A rapidventa beat -l info
```

The beat scheduler fires `core.tasks.close_auctions_task` every 60 seconds,
closing any ACTIVE listings whose `end_time` has passed.

Visit:
- **Frontend**: http://localhost:8000
- **Admin**: http://localhost:8000/admin

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | *required* | Django secret key |
| `DEBUG` | `True` | Debug mode |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Comma-separated allowed hosts |
| `USE_SQLITE` | `True` | Use SQLite instead of PostgreSQL |
| `DB_NAME` | `rapidventa_db` | PostgreSQL database name |
| `DB_USER` | `rapidventa_user` | PostgreSQL user |
| `DB_PASSWORD` | *required* | PostgreSQL password |
| `DB_HOST` | `localhost` | PostgreSQL host |
| `DB_PORT` | `5432` | PostgreSQL port |
| `CELERY_BROKER_URL` | `redis://localhost:6379/0` | Redis URL for Celery |
| `BID_INCREMENT` | `10.00` | Minimum bid step above current highest |

---

## Apps & Responsibilities

### `accounts`
- **Model**: `User` (email-based, `full_name`, `phone`, `address`, `national_id`, `role`, `is_validated_by_admin`)
- **Roles**: `BUYER`, `SELLER`, `ADMIN`
- **Key rule**: `user.can_bid` = `is_active AND is_validated_by_admin`
- **Admin action**: Bulk validate/invalidate users

### `listings`
- **Models**: `Category`, `Listing`
- **Status flow**: `DRAFT → PENDING → ACTIVE → CLOSED | VOID → REPUBLISHED`
- **Key fields**: `secret_reserve_price` (hidden from buyers), `min/max_public_price`
- **Seller only**: Create listings, bulk CSV upload

### `bids`
- **Model**: `Bid` (user, listing, amount, timestamp)
- **Rules enforced in `place_bid()`**:
  1. User must be authenticated and `is_validated_by_admin = True`
  2. Listing must be `ACTIVE` and within `start_time..end_time`
  3. Seller cannot bid on own listing
  4. Amount must be ≥ current highest bid + `BID_INCREMENT`

### `orders`
- **Model**: `Order` (UUID reference, buyer, listing, winning_bid_amount, tracking_number)
- **Status flow**: `PENDING_PAYMENT → PAID → SHIPPED → COMPLETED`
- **No payment integration** — pure status tracking
- **Staff only**: Advance status, add tracking number, cancel

### `core`
- **Mixins**: `SellerRequiredMixin`, `StaffRequiredMixin`, `ValidatedUserRequiredMixin`
- **Management command**: `close_auctions`

---

## Auction Lifecycle

```
Seller creates listing
        ↓
    [PENDING] ← Admin reviews in /admin
        ↓ (approved)
    [ACTIVE]  ← Buyers bid
        ↓ (end_time passes)
  close_auctions command runs
        ↓
  Highest bid >= secret_reserve_price?
     YES → [CLOSED]         NO → [VOID]
            ↓                      ↓
        Order created        Listing duplicated
                              as [REPUBLISHED]
```

---

## Closing Auctions

The `close_auctions` management command processes all `ACTIVE` listings
whose `end_time` has passed.

```bash
# Dry run (no changes committed):
python manage.py close_auctions --dry-run

# Live run:
python manage.py close_auctions
```

### Cron (every 5 minutes)
```cron
*/5 * * * * /path/to/venv/bin/python /path/to/manage.py close_auctions >> /var/log/rapidventa/cron.log 2>&1
```

### Celery Beat (production recommended)

The beat schedule is already configured in `rapidventa/settings/base.py`:

```python
CELERY_BEAT_SCHEDULE = {
    "close-auctions-every-60-seconds": {
        "task": "core.tasks.close_auctions_task",
        "schedule": timedelta(seconds=60),
    },
}
```

Start the worker and scheduler in two separate terminals:

```bash
celery -A rapidventa worker -l info
celery -A rapidventa beat -l info
```

---

## Bulk Upload CSV

CSV format (see `sample_listings.csv`):

```
title,description,category_slug,min_price,max_price,reserve_price,start_time,end_time
```

- `category_slug` must match an existing `Category.slug`
- Datetime format: `YYYY-MM-DD HH:MM:SS`
- Errors are reported per-row; successful rows are committed

---

## Admin Panel

Navigate to `/admin/`:

| Section | Key Actions |
|---|---|
| **Users** | Validate / invalidate users in bulk |
| **Listings** | Approve / reject pending listings, edit `secret_reserve_price` |
| **Bids** | Read-only bid audit log |
| **Orders** | Advance order status, add tracking numbers |
| **Categories** | Create and manage categories with slugs |

---

## Production Deployment

### 1. Switch settings module

```bash
export DJANGO_SETTINGS_MODULE=rapidventa.settings.production
```

### 2. Collect static files

```bash
python manage.py collectstatic --noinput
```

### 3. Run with Gunicorn

```bash
gunicorn rapidventa.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --worker-class sync \
  --access-logfile /var/log/rapidventa/access.log \
  --error-logfile /var/log/rapidventa/error.log
```

### 4. Nginx reverse proxy (snippet)

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location /static/ {
        alias /var/www/rapidventa/static/;
    }

    location /media/ {
        alias /var/www/rapidventa/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 5. Start Celery workers

```bash
celery -A rapidventa worker -l info
celery -A rapidventa beat   -l info
```

---

## Extending to SaaS

This MVP is structured to scale to a multi-tenant SaaS product:

1. **Multi-tenancy**: Add a `Tenant` model and middleware to `core/`
2. **Payments**: Plug Stripe/PayPal into `orders/services.py` — the status machine is already in place
3. **WebSockets**: Replace polling countdown with Django Channels for real-time bid updates
4. **API**: Add `api/` app with DRF serializers — services layer is already framework-agnostic
5. **Search**: Swap `title__icontains` in `ListingListView` for Elasticsearch via `django-elasticsearch-dsl`
=======
# rapidventa
Auction Website Powered By Django 5.2
>>>>>>> f1958ac492ccad82a190944299a26ef80dda8468
