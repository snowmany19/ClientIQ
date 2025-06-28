# models_template.py
# Template for adapting the SaaS engine to different domains

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

# ============================================================================
# CORE USER MODEL (Keep this for all SaaS)
# ============================================================================

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="employee")  # admin, staff, employee
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=True)
    
    # Billing fields
    subscription_status = Column(String, default="inactive")
    plan_id = Column(String, nullable=True)
    stripe_customer_id = Column(String, nullable=True)
    stripe_subscription_id = Column(String, nullable=True)
    
    # Relationships
    store = relationship("Store", back_populates="users")
    # Add your domain-specific relationships here

# ============================================================================
# STORE MODEL (Keep for multi-tenant SaaS)
# ============================================================================

class Store(Base):
    __tablename__ = "stores"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    location = Column(String)
    
    # Relationships
    users = relationship("User", back_populates="store")
    # Add your domain-specific relationships here

# ============================================================================
# DOMAIN-SPECIFIC MODELS (Replace with your domain)
# ============================================================================

# EXAMPLE 1: INCIDENT MANAGEMENT
class Incident(Base):
    __tablename__ = "incidents"
    
    id = Column(Integer, primary_key=True, index=True)
    description = Column(Text)
    store_name = Column(String)
    location = Column(String)
    offender = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    reported_by = Column(String)
    severity = Column(String, default="medium")
    tags = Column(String, nullable=True)
    image_path = Column(String, nullable=True)
    pdf_path = Column(String, nullable=True)
    summary = Column(Text, nullable=True)

# EXAMPLE 2: CUSTOMER RELATIONSHIP MANAGEMENT (CRM)
class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String, nullable=True)
    company = Column(String, nullable=True)
    status = Column(String, default="active")  # active, inactive, prospect
    created_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)
    assigned_to = Column(Integer, ForeignKey("users.id"))

class Interaction(Base):
    __tablename__ = "interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(String)  # call, email, meeting, note
    subject = Column(String)
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    follow_up_date = Column(DateTime, nullable=True)

# EXAMPLE 3: PROJECT MANAGEMENT
class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    status = Column(String, default="active")  # active, completed, on-hold
    priority = Column(String, default="medium")  # low, medium, high
    start_date = Column(DateTime)
    due_date = Column(DateTime, nullable=True)
    assigned_to = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    title = Column(String)
    description = Column(Text, nullable=True)
    status = Column(String, default="todo")  # todo, in-progress, done
    priority = Column(String, default="medium")
    assigned_to = Column(Integer, ForeignKey("users.id"))
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# EXAMPLE 4: INVENTORY MANAGEMENT
class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    sku = Column(String, unique=True, index=True)
    description = Column(Text, nullable=True)
    category = Column(String)
    price = Column(Float)
    cost = Column(Float)
    stock_quantity = Column(Integer, default=0)
    reorder_level = Column(Integer, default=10)
    supplier = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    type = Column(String)  # in, out, adjustment
    quantity = Column(Integer)
    user_id = Column(Integer, ForeignKey("users.id"))
    notes = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

# ============================================================================
# HOW TO USE THIS TEMPLATE
# ============================================================================

"""
1. Choose your domain (CRM, Project Management, Inventory, etc.)
2. Copy the relevant models to models.py
3. Update the relationships and foreign keys
4. Create corresponding schemas in schemas.py
5. Update routes to match your domain
6. Customize frontend components
7. Update database migrations

EXAMPLE: For CRM, you would:
- Keep User and Store models
- Use Customer and Interaction models
- Remove Incident model
- Update all references from 'incident' to 'customer'
- Update frontend to show customer management instead of incidents
""" 