import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Store, Incident, Offender
from sqlalchemy.exc import IntegrityError

# SQLite setup
sqlite_url = "sqlite:///./incidentiq.db"
sqlite_engine = create_engine(sqlite_url)
SqliteSession = sessionmaker(bind=sqlite_engine)
sqlite_session = SqliteSession()

# PostgreSQL setup
postgres_url = os.getenv("DATABASE_URL", "postgresql://jaclynbaker@localhost:5432/incidentiq_db")
postgres_engine = create_engine(postgres_url)
PostgresSession = sessionmaker(bind=postgres_engine)
postgres_session = PostgresSession()

# Ensure tables exist in Postgres
Base.metadata.create_all(bind=postgres_engine)

def migrate_table(model, unique_field="id"):
    print(f"Migrating {model.__tablename__}...")
    records = sqlite_session.query(model).all()
    migrated = 0
    skipped = 0
    for record in records:
        # Check if record with same ID already exists in Postgres
        existing = postgres_session.query(model).filter(getattr(model, unique_field) == getattr(record, unique_field)).first()
        if existing:
            skipped += 1
            continue
        # Prepare a new instance for Postgres
        data = {col.name: getattr(record, col.name) for col in model.__table__.columns}
        new_record = model(**data)
        postgres_session.add(new_record)
        try:
            postgres_session.commit()
            migrated += 1
        except IntegrityError:
            postgres_session.rollback()
            skipped += 1
    print(f"  Done: {model.__tablename__} (migrated: {migrated}, skipped: {skipped})")

def migrate_all():
    # Migrate in order: Store, User, Offender, Incident
    migrate_table(Store)
    migrate_table(User)
    migrate_table(Offender)
    migrate_table(Incident)
    print("✅ Migration complete!")

if __name__ == "__main__":
    migrate_all() 