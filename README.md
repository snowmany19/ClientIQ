📌 **Legal Notice**  
This project, including all code and content, is the property of Security Flaw Solutions LLC. Unauthorized use or distribution is prohibited.

# 🛡️ IncidentIQ

**IncidentIQ** is a modern, AI-powered incident logging and reporting system built for retailers, security teams, and store managers. It supports secure image uploads, auto-generated PDF reports, and integrates with Stripe for SaaS billing. Designed for rapid deployment and future upgrades including multi-store support, role-based access, and analytics dashboards.

---

## 🚀 Features

- 🔐 **Secure Login** (JWT-based authentication)
- 📝 **Incident Reporting** with GPT-generated summaries
- 🖼️ **Image Upload Support**
- 📄 **PDF Report Generation**
- 📊 **Live Dashboard & Graphs**
- 💳 **Stripe-Ready Billing Logic**
- 🧱 PostgreSQL-First Database (with SQLAlchemy ORM)
- 🧪 Easily Extensible for Enterprise-Grade Features

---

## 🗂️ Project Structure

incidentiq/
├── backend/
│ ├── main.py # FastAPI app
│ ├── database.py # SQLAlchemy DB setup
│ ├── init_db.py # Run once to initialize tables
│ ├── models.py # ORM models
│ ├── schemas.py # Pydantic schemas
│ ├── stripe.py # Billing logic (incomplete, placeholder)
│ ├── routes/
│ │ ├── auth.py # Auth routes (JWT login/register)
│ │ └── incidents.py # Incident submission, retrieval
│ ├── utils/
│ │ ├── image_uploader.py # Local image handling
│ │ ├── pdf.py # PDF generation logic
│ │ └── auth_utils.py # Hashing, JWT token generation
│ └── core/
│ └── config.py # Environment config loader
│
├── frontend/ (Optional - Streamlit/Dashboard UI)
│ └── dashboard.py
│
├── .env # Your secrets (never commit this)
├── .env.example # Template environment file
└── README.md