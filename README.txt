📋 **Legal Notice**  
This project, including all code and content, is the property of Security Flaw Solutions LLC. Unauthorized use or distribution is prohibited.

# CivicLogHOA — HOA Violation Management Platform

A production-ready, modular SaaS platform for HOA violation management, built with FastAPI (backend), Streamlit (frontend), PostgreSQL, and Stripe. Includes robust RBAC, PDF reporting, file uploads, and subscription billing.

---

## 🚀 Features
- **FastAPI Backend** — Secure, scalable REST API
- **Streamlit Frontend** — Modern, interactive dashboard
- **PostgreSQL Database** — Production-grade relational DB
- **Stripe Billing** — Subscription management & webhooks
- **Role-Based Access** — Admin, HOA Board, Inspector
- **PDF Generation** — Automated violation notices
- **File Uploads** — Secure image/document handling
- **AI-Powered Summaries** — GPT-generated violation reports
- **Comprehensive Validation & Error Handling**
- **Production-Ready Config & Logging**

---

## 🏁 Quick Start (Local Development)

### 1. **Clone the Repository**
```bash
git clone <your-repo-url>
cd CivicLogHOA
```

### 2. **Set Up PostgreSQL Locally**
```bash
# Install PostgreSQL (if not already installed)
# macOS: brew install postgresql
# Ubuntu: sudo apt-get install postgresql
# Windows: Use the official installer

# Start PostgreSQL service
# macOS: brew services start postgresql
# Ubuntu: sudo service postgresql start

# Create database and user
psql postgres
# In psql shell:
CREATE DATABASE civicloghoa_db;
CREATE USER civicloghoa_user WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE civicloghoa_db TO civicloghoa_user;
\q
```

### 3. **Configure Environment Variables**
```bash
cd backend
cp env_example.txt .env
# Edit .env and set:
# DATABASE_URL=postgresql://civicloghoa_user:yourpassword@localhost:5432/civicloghoa_db
# (Fill in all other required secrets: Stripe, OpenAI, etc.)
```

### 4. **Install Dependencies**
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd ../frontend
pip install -r requirements.txt
```

### 5. **Run Database Migrations**
```bash
cd ../backend
alembic upgrade head
```

### 6. **Seed the Database (Optional)**
```bash
python init_db.py
```

### 7. **Run the Application**
```bash
# Backend (FastAPI)
uvicorn main:app --reload

# Frontend (Streamlit)
cd ../frontend
streamlit run dashboard.py
```

---

## 🏭 Production Deployment
- Set `ENVIRONMENT=production` and `DEBUG=false` in `.env`
- Use a secure, production PostgreSQL instance
- Set strong secrets for `SECRET_KEY`, Stripe, and OpenAI
- Configure CORS and email settings as needed
- Use a process manager (e.g., Gunicorn, systemd) for backend
- Use HTTPS in production
- See `PRODUCTION_DEPLOYMENT.md` for advanced deployment

---

## 🧑‍💻 Handoff & Ownership
- All code, data, and configuration are now ready for transfer
- `.env` contains all secrets and environment-specific settings (never commit this file)
- See `PERFORMANCE_NOTES.md` for scaling and optimization
- See `SECURITY_AUDIT_REPORT.md` for security best practices
- All migration/test scripts are included in `backend/`
- For questions, contact the original developer (see Support)
- **Please review the [Terms of Sale](TERMS_OF_SALE.md) before completing your purchase.**

---

## 🧪 Testing
- Run all backend tests:
  ```bash
  cd backend
  pip install -r requirements-test.txt
  python run_tests.py
  ```
- Coverage reports are generated in `backend/htmlcov/`

---

## 🛠️ Troubleshooting
- **401 Unauthorized:** Ensure users exist in PostgreSQL (migrate from SQLite if needed)
- **DB Connection Errors:** Check `DATABASE_URL` and that PostgreSQL is running
- **Migrations Fail:** Ensure Alembic is configured for PostgreSQL and DB is empty/clean
- **Stripe/OpenAI Issues:** Double-check API keys in `.env`
- **Frontend Not Loading:** Ensure Streamlit is running and CORS is configured

---

## Terms of Sale
By purchasing, you agree to the [Terms of Sale](TERMS_OF_SALE.md), which outline final sale, warranty, intellectual property, and buyer responsibilities.

---

## 📄 License
© 2025 Security Flaw Solutions LLC. All rights reserved.

This software is proprietary and confidential. Unauthorized copying, distribution, or modification is prohibited.

Use of this software is also subject to the [Terms of Sale](TERMS_OF_SALE.md).

---

## 🤝 Support
For customization, support, or handoff questions, contact:
- **Email:** sfshkhalsa@gmail.com

---

**Ready for handoff. Build, scale, and monetize with confidence!** 🚀