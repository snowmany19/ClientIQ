📋 **Legal Notice**  
This project, including all code and content, is the property of Security Flaw Solutions LLC. Unauthorized use or distribution is prohibited.

# ContractGuard.ai — AI Contract Review Platform

A production-ready, modular SaaS platform for AI-powered contract review and analysis, built with FastAPI (backend), Next.js (frontend), PostgreSQL, and Stripe. Includes robust RBAC, PDF reporting, file uploads, and subscription billing.

---

## 🚀 Features
- **FastAPI Backend** — Secure, scalable REST API
- **Next.js Frontend** — Modern, interactive dashboard
- **PostgreSQL Database** — Production-grade relational DB
- **Stripe Billing** — Subscription management & webhooks
- **Role-Based Access** — Admin, Analyst, Viewer
- **PDF Generation** — Automated contract analysis reports
- **File Uploads** — Secure document handling (PDF, DOCX, TXT)
- **AI-Powered Analysis** — GPT-generated contract summaries and risk assessments
- **Comprehensive Validation & Error Handling**
- **Production-Ready Config & Logging**

---

## 🏁 Quick Start (Local Development)

### 1. **Clone the Repository**
```bash
git clone <your-repo-url>
cd contractguard
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
CREATE DATABASE contractguard_db;
CREATE USER contractguard_user WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE contractguard_db TO contractguard_user;
\q
```

### 3. **Configure Environment Variables**
```bash
cd backend
cp env_example.txt .env
# Edit .env and set:
# DATABASE_URL=postgresql://contractguard_user:yourpassword@localhost:5432/contractguard_db
# (Fill in all other required secrets: Stripe, OpenAI, etc.)
```

### 4. **Install Dependencies**
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd ../frontend-nextjs
npm install
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

# Frontend (Next.js)
cd ../frontend-nextjs
npm run dev
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

## 💰 Pricing Plans
- **Solo**: $39/month - 10 contracts/month, 1 user
- **Team**: $99/month - 50 contracts/month, 5 users
- **Business**: $299/month - 250 contracts/month, 20 users
- **Enterprise**: $999/month - 1000 contracts/month, unlimited users
- **White Label**: Contact us for custom solutions

---

## 🧑‍💻 Handoff & Ownership
- All code, data, and configuration are now ready for transfer
- `.env` contains all secrets and environment-specific settings (never commit this file)
- See `scripts/README.md` for utility scripts and setup
- See `SMTP_SETUP_GUIDE.md` for email configuration
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

## 🐳 Docker Deployment
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## 🛠️ Troubleshooting
- **401 Unauthorized:** Ensure users exist in PostgreSQL (migrate from SQLite if needed)
- **DB Connection Errors:** Check `DATABASE_URL` and that PostgreSQL is running
- **Migrations Fail:** Ensure Alembic is configured for PostgreSQL and DB is empty/clean
- **Stripe/OpenAI Issues:** Double-check API keys in `.env`
- **Frontend Not Loading:** Ensure Next.js is running and CORS is configured
- **Contract Analysis Issues:** Verify OpenAI API key and model access

---

## License
This software is proprietary and confidential. Unauthorized copying, distribution, or modification is prohibited.

---

## 📄 License
© 2025 Security Flaw Solutions LLC. All rights reserved.

This software is proprietary and confidential. Unauthorized copying, distribution, or modification is prohibited.

See [LICENSE.txt](LICENSE.txt) for full license terms.

---

## 🤝 Support
For customization, support, or handoff questions, contact:
- **Email:** sfshkhalsa@gmail.com

---

**Ready for handoff. Build, scale, and monetize with confidence!** 🚀