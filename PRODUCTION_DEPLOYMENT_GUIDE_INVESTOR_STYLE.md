# 🚀 A.I.ncident – Production Deployment Guide

This guide provides a streamlined path to deploying A.I.ncident in a secure, production-ready environment. With a modern FastAPI backend, Streamlit frontend, PostgreSQL database, and Stripe billing integration, most technical teams can deploy and launch in under **60 minutes**.

---

## ✅ Pre-Deployment Checklist

Ensure the following before deployment:

- ✅ Business bank account + Stripe account (for live payments)
- ✅ PostgreSQL database provisioned (e.g., Railway, Supabase, RDS)
- ✅ Environment variables configured (see `.env.example`)
- ✅ Python 3.10+ installed (locally or in CI/CD pipeline)
- ✅ Optional: SMTP server or Mailgun for email alerts

---

## ⚙️ 1. Backend Setup

### 🔹 Install dependencies

```bash
pip install -r requirements.txt
```

### 🔹 Environment Configuration

Copy the example file and fill in your values:

```bash
cp .env.example .env
```

Key variables:

- `DATABASE_URL` – PostgreSQL URI
- `JWT_SECRET_KEY` – use `openssl rand -hex 32` to generate
- `STRIPE_SECRET_KEY` – your live Stripe key
- `OPENAI_API_KEY` – required for GPT tagging/summarization
- `ENVIRONMENT` – set to `production` in production

### 🔹 Run Alembic Migrations

```bash
alembic upgrade head
```

This sets up all required tables and constraints.

### 🔹 Start the Backend API

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 🖥️ 2. Frontend Setup (Streamlit)

### 🔹 Install frontend dependencies

Ensure `streamlit`, `requests`, and `ag-grid` are installed:

```bash
pip install -r frontend/requirements.txt
```

### 🔹 Configure API base URL

Edit `frontend/utils/api.py`:

```python
API_BASE_URL = "https://your-backend-url.com"
```

### 🔹 Run Streamlit Frontend

```bash
cd frontend
streamlit run dashboard.py
```

---

## 💳 3. Stripe Integration Notes

- Stripe is fully integrated with:
  - Checkout
  - Billing portal
  - Webhooks for activation

- Webhook setup URL:
  ```
  https://your-backend-url.com/webhooks/stripe
  ```

- Plans are defined in Stripe Dashboard. Match product IDs in `.env`.

---

## 🔐 4. Security Notes

- 🔒 All critical/high-risk issues resolved (see Security Audit)
- 🛡️ File upload security hardened (hash checks, type validation)
- 🔐 JWT secrets enforced with production validation
- 🚫 Debug mode disabled by default in production

---

## 🧪 5. Optional Add-Ons

You may optionally configure:

- ✅ SMTP server for email alerts
- ✅ Redis for caching model results
- ✅ CI/CD via GitHub Actions or Railway
- ✅ Admin analytics dashboard

---

## 📈 Deployment Time Estimate

| Step | Time |
|------|------|
| Backend setup & DB | ~15 mins |
| Frontend setup | ~10 mins |
| Stripe config | ~15–20 mins |
| Security/validation | ~10 mins |
| **Total time** | **~45–60 mins** |

---

## 📦 Ready for Launch

Once deployed, you'll have:

- ✅ Role-based access (Admin, Staff, Employee)
- ✅ AI incident tagging, severity prediction, GPT summaries
- ✅ Secure incident logging with PDF export
- ✅ Stripe-powered billing & access control
- ✅ Dashboard with filters, charts, and CSV exports

For any optional deployment support, contact **Security Flaw Solutions LLC** 

---

