# models.py — SQLAlchemy models for the IncidentIQ system

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

# 📝 Incident table
class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(Text)                   # Raw incident report
    summary = Column(Text)                       # GPT summary
    tags = Column(String)                        # Comma-separated tags
    timestamp = Column(DateTime, default=datetime.utcnow)

    store_name = Column(String)                  # Store name (text)
    location = Column(String)                    # Location text
    offender = Column(String)                    # Offender name/alias

    image_url = Column(String, nullable=True)    # Optional image path
    pdf_path = Column(String, nullable=True)     # Generated PDF path
    severity = Column(String, nullable=True)

    # 🔗 FK to reporter
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="incidents")

# 🧑 User table with role-based access
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    email = Column(String, unique=True, nullable=True)
    role = Column(String, default="employee")  # employee | staff | admin
    store_id = Column(Integer, nullable=True)  # store assignment (optional FK)

    incidents = relationship("Incident", back_populates="user", cascade="all, delete-orphan")

# 🏬 Store table (optional)
class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    location = Column(String)

# 🧑‍🚨 Offender table
class Offender(Base):
    __tablename__ = "offenders"

    id = Column(Integer, primary_key=True, index=True)
    alias = Column(String, index=True)
    notes = Column(Text)



