# 🚗 Vehicle Service Management System

A full-stack web application for managing vehicle services, repairs, components, pricing, and revenue calculation. Built with **Django REST Framework** (backend) and **React.js** (frontend).

---

## 📋 Assignment Features

| # | Requirement | Status | Implementation |
|---|-------------|--------|----------------|
| 1 | Component Registration & Pricing Management | ✅ | Operations users manage components with repair/purchase pricing |
| 2 | Vehicle Repair Tracking | ✅ | Register vehicles, manage repair details, track status |
| 3 | Issue Reporting & Component Selection | ✅ | Choose between new components (replace) or repair services |
| 4 | Final Price Calculation & Payment | ✅ | Auto-calculated `total_price`, simulated payment with audit trail |
| 5 | Revenue Graphs | ✅ | API-ready daily/monthly/yearly revenue aggregation with data scoping |
| ⭐ | Unit Tests (Bonus) | ✅ | **27 tests** covering auth, roles, data scoping, CRUD, payments, models |

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Django 6.0.5 + Django REST Framework 3.17 |
| **Authentication** | JWT (djangorestframework-simplejwt) |
| **Database** | PostgreSQL (SQLite supported) |
| **Frontend** | React.js (separate project) |
| **Charts** | Recharts / Chart.js |

---

## 🧩 Shared Utilities (`apps/common/`)

The project uses a shared utility app across all services for consistent response formatting and error handling:

| Utility | File | Purpose |
|---------|------|---------|
| **ResponseHandler** | `apps/common/utils/response_utils.py` | Standardized JSON envelope: `{ success, message, status_code, data }` |
| **SerializerErrorHandler** | `apps/common/utils/serializer_utils.py` | Recursive DRF error extraction into clean messages |
| **BaseAPIViewSet** | `apps/common/views/base_views.py` | Base ViewSet overriding CRUD methods to use ResponseHandler + SerializerErrorHandler |

### Standard API Response Format

```json
// Success
{
  "success": true,
  "message": "Payment successful",
  "status_code": 200,
  "data": {
    "status": "paid",
    "transaction_id": "PAY-A1B2C3D4E5F6",
    "paid_at": "2026-05-11T23:30:00Z"
  }
}

// Error
{
  "success": false,
  "message": "Amount mismatch",
  "status_code": 400,
  "errors": { "expected": 150.0, "received": 1.0 }
}
```

---

## 🔐 Role-Based Access Control

The system uses **JWT authentication** with two user roles via Django Groups:

| Role | Permissions | Typical User |
|------|------------|--------------|
| **`user`** | Full CRUD on vehicles, service orders, issues; process payments; **read-only** on components | Service staff |
| **`operations`** | Everything a regular user can do **+ full CRUD on components** (register new parts, set pricing) | Inventory manager |

### Data Scoping Rules

| Model | Regular User | Operations User |
|-------|-------------|-----------------|
| **Component** | Read-only (shared catalog) | Full CRUD |
| **Vehicle** | Only sees/edits own (`created_by=self`) | Sees ALL |
| **ServiceOrder** | Only sees/edits own (`created_by=self`) | Sees ALL |
| **Issue** | Only sees/edits own (scoped via `service_order__created_by`) | Sees ALL |
| **Payment** | Can only pay own orders | Can pay ANY order |
| **Revenue** | Only sees revenue from own orders | Sees ALL revenue |

---

## 📡 API Endpoints

### Authentication (`/api/auth/`)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/auth/register/` | ❌ | Register new user with role (`user` or `operations`) |
| POST | `/api/auth/login/` | ❌ | Login, returns JWT access + refresh tokens |
| GET | `/api/auth/me/` | ✅ | Get current user info |
| POST | `/api/auth/token/refresh/` | ❌ | Refresh expired access token |

### Services (`/api/`)

| Method | Endpoint | Auth | Role Required | Description |
|--------|----------|------|---------------|-------------|
| GET | `/api/components/` | ✅ | Any | List all components |
| POST | `/api/components/` | ✅ | **operations only** | Create a new component |
| PATCH | `/api/components/{id}/` | ✅ | **operations only** | Update component pricing |
| GET | `/api/vehicles/` | ✅ | Any | List vehicles (scoped) |
| POST | `/api/vehicles/` | ✅ | Any | Register a vehicle |
| GET | `/api/orders/` | ✅ | Any | List service orders (scoped) |
| POST | `/api/orders/` | ✅ | Any | Create a service order |
| GET | `/api/orders/{id}/` | ✅ | Any | Get order details with issues + total_price |
| GET | `/api/issues/` | ✅ | Any | List issues (scoped) |
| POST | `/api/issues/` | ✅ | Any | Add an issue to an order |
| POST | `/api/orders/{id}/pay/` | ✅ | Any | Process payment (simulated, scoped) |
| GET | `/api/revenue-analytics/` | ✅ | Any | Revenue data (daily/monthly/yearly, scoped) |

---

## 🧪 Running Tests (Bonus Feature)

**27 comprehensive tests** covering all critical paths:

```bash
# Run all tests
python manage.py test apps.services.tests --verbosity=2

# Expected output: 27 tests all pass (OK)
```

### Test Categories

| Category | Tests | What's Covered |
|----------|-------|----------------|
| **AuthTests** | 6 | Registration with roles, login, password mismatch, unauthenticated access blocked |
| **RoleBasedAccessTests** | 4 | Regular users blocked from creating components, ops users can create/update |
| **VehicleTests** | 2 | Create and list vehicles |
| **ServiceOrderTests** | 3 | Create orders, add issues with auto-pricing, total price calculation |
| **PaymentTests** | 3 | Successful payment with audit trail, amount mismatch rejection, double payment prevention |
| **ComponentModelTests** | 1 | Negative price validation |
| **PaymentModelTests** | 2 | Auto-generated transaction ID, string representation |
| **DataScopingTests** | 6 | Users see only own data; ops see all; cross-user payment/issue prevention |

---

## 🚀 Quick Start (Backend)

### Prerequisites

- Python 3.12+
- PostgreSQL (or SQLite for development)

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/Manojkumar-2002/Vehicle-Service-Management-System.git
cd Vehicle-Service-Management-System

# 2. Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate   # Windows
source venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
# Edit .env with your database credentials:
# DB_ENGINE=django.db.backends.postgresql
# DB_NAME=vms_db
# DB_USER=postgres
# DB_PASSWORD=your_password
# DB_HOST=localhost
# DB_PORT=5432
# SECRET_KEY=your-secret-key

# 5. Run migrations
python manage.py migrate

# 6. Set up default groups and admin user
python manage.py setup_groups

# 7. Start the development server
python manage.py runserver
```

---

## 🌐 Quick Start (Frontend)

The React frontend connects to the backend API at `http://localhost:8000/api/`.

### Authentication Flow in React

```javascript
// 1. Register / Login → receive tokens
const response = await fetch('http://localhost:8000/api/auth/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username, password })
});
const result = await response.json();
// result = { success: true, message: "...", status_code: 200, data: { ... } }
const { access, refresh } = result.data;

// 2. Store tokens (localStorage or httpOnly cookies)
localStorage.setItem('access_token', access);
localStorage.setItem('refresh_token', refresh);

// 3. Attach token to all API requests
const headers = {
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${localStorage.getItem('access_token')}`
};

// 4. Auto-refresh when token expires
if (response.status === 401) {
  const refreshResp = await fetch('http://localhost:8000/api/auth/token/refresh/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh: localStorage.getItem('refresh_token') })
  });
}
```

### Role-Based UI Hints

```javascript
// Check user role from the /api/auth/me/ endpoint
const userResp = await fetch('http://localhost:8000/api/auth/me/', { headers });
const { data: user } = await userResp.json();
// user.groups contains ['user'] or ['operations']

// Operations users see "Add Component" button
// Regular users see components as read-only list
```

### Consuming Paginated List Endpoints

All ViewSets use `BaseAPIViewSet` which returns pagination metadata:

```javascript
const resp = await fetch('http://localhost:8000/api/vehicles/', { headers });
const result = await resp.json();
// result = {
//   success: true,
//   message: "Fetched successfully",
//   status_code: 200,
//   data: [ ... vehicles ... ],
//   pagination: { count: 50, page: 1, total_pages: 5 }
// }
```

---

## 🗺️ Project Structure

```
Vehicle-Service-Management-System/
├── apps/
│   ├── common/                    # Shared utilities (reusable across apps)
│   │   ├── utils/
│   │   │   ├── response_utils.py   # ResponseHandler — standard JSON envelope
│   │   │   ├── serializer_utils.py # SerializerErrorHandler — error formatting
│   │   │   └── base_views.py       # BaseAPIViewSet — standardized CRUD responses
│   │   └── apps.py
│   │
│   ├── services/                  # Main app
│   │   ├── constants/
│   │   │   └── enums.py           # OrderStatus, ServiceType, PeriodChoice
│   │   ├── models/
│   │   │   ├── audit_trail.py      # Abstract model: created_by, created_at, updated_by, updated_at
│   │   │   ├── vehicle.py          # Vehicle model (inherits AuditTrail)
│   │   │   ├── component.py        # Component model (parts + pricing)
│   │   │   ├── service_order.py    # ServiceOrder + Issue models (inherits AuditTrail)
│   │   │   └── payment.py          # Payment model (inherits AuditTrail)
│   │   ├── serializers/
│   │   │   ├── service_serializers.py   # Component, Vehicle, Issue, ServiceOrder
│   │   │   └── dashboard_serializer.py  # RevenueQuery serializer
│   │   ├── views/
│   │   │   ├── service.py          # ComponentViewSet, VehicleViewSet (extends BaseAPIViewSet)
│   │   │   ├── payment.py          # PaymentProcessView
│   │   │   └── dashboard.py        # RevenueAnalyticsView (uses ResponseHandler)
│   │   ├── urls.py                # Route definitions
│   │   ├── tests.py               # 27 tests
│   │   └── migrations/            # DB migrations (0001-0006)
│   │
│   └── users/                     # Auth app
│       ├── permissions.py          # IsOperationsUser, IsRegularUser, IsOperationsOrReadOnly
│       ├── serializers.py          # Register, Login, User serializers
│       ├── views.py               # RegisterView, LoginView, UserDetailView (uses ResponseHandler)
│       ├── urls.py                # Auth routes
│       └── management/commands/
│           └── setup_groups.py    # One-time setup: creates groups + admin
│
├── config/
│   ├── settings.py                # DRF + JWT configuration + index optimization
│   └── urls.py                    # Root URL configuration
│
├── manage.py
├── requirements.txt
├── .env                           # Environment variables
└── README.md                      # This file
```

---

## 📊 Revenue Analytics API

```bash
# Daily revenue (last 30 days default)
GET /api/revenue-analytics/?period=daily

# Monthly revenue
GET /api/revenue-analytics/?period=monthly

# Yearly revenue
GET /api/revenue-analytics/?period=yearly

# Custom date range
GET /api/revenue-analytics/?period=daily&from_date=2026-01-01&to_date=2026-12-31
```

Response format:
```json
{
  "success": true,
  "message": "Revenue data fetched successfully",
  "status_code": 200,
  "data": [
    { "date": "2026-05-01", "amount": 450.00 },
    { "date": "2026-05-02", "amount": 230.50 }
  ]
}
```

The React frontend can consume this directly with **Recharts**:
```jsx
const { data } = await response.json();

<BarChart data={data}>
  <XAxis dataKey="date" />
  <YAxis />
  <Tooltip />
  <Bar dataKey="amount" fill="#8884d8" />
</BarChart>
```

---

## 💳 Payment Simulation

The payment endpoint simulates payment verification:

1. Client sends `amount_paid` matching `order.total_price`
2. Server validates the amount
3. Order status changes to `paid`
4. A `Payment` record is created with:
   - Auto-generated `transaction_id` (e.g., `PAY-ABC123...`)
   - `amount`, `status`, `paid_at` timestamp
5. Response includes `transaction_id` for receipt display

```json
// POST /api/orders/5/pay/
// Headers: { Authorization: Bearer <access_token> }
// Request:  { "amount_paid": 150.00 }

// Response:
{
  "success": true,
  "message": "Payment successful",
  "status_code": 200,
  "data": {
    "status": "paid",
    "transaction_id": "PAY-A1B2C3D4E5F6",
    "paid_at": "2026-05-11T23:30:00Z"
  }
}
```

---

## 🗄️ Database Indexes (Performance)

For optimized queries, the following indexes have been added:

| Model | Index | Purpose |
|-------|-------|---------|
| **ServiceOrder** | `status` | Quick filtering by order status |
| **ServiceOrder** | `created_at` | Date range queries for revenue |
| **ServiceOrder** | `created_by` | User data scoping |
| **ServiceOrder** | `(status, created_at, created_by)` | **Composite** — covers revenue query in one index scan |
| **Vehicle** | `created_by` | User data scoping |

---

## 🧹 Management Commands

```bash
# Create admin user + default groups (run once after migrate)
python manage.py setup_groups

# Default superuser created: admin / admin123
```

---

## 📸 Demo Screenshots

*(Add screenshots here after running the application)*

- **Component Management** — Operations user registering new components with pricing
- **Vehicle Registration** — Adding vehicle details (VIN, make, model, owner)
- **Service Order** — Creating an order with issues, selecting repair vs replace
- **Payment** — Processing payment and viewing transaction ID
- **Revenue Graph** — Daily/monthly/yearly revenue visualization

---

## 📝 License

MIT