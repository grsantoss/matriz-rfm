# RFM Insights - Database Migrations

import os
import sys
import argparse
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Add the project root to the path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Import models
from backend.models import Base
from config import config

# Create database engine
engine = create_engine(config.DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize the database by creating all tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

def drop_db():
    """Drop all database tables"""
    print("WARNING: This will drop all tables in the database!")
    confirm = input("Are you sure you want to continue? (y/n): ")
    if confirm.lower() != 'y':
        print("Operation cancelled.")
        return
    
    print("Dropping database tables...")
    Base.metadata.drop_all(bind=engine)
    print("Database tables dropped successfully!")

def seed_db():
    """Seed the database with initial data"""
    from .auth import get_password_hash
    from .models import User
    
    print("Seeding database with initial data...")
    
    # Create session
    db = SessionLocal()
    
    try:
        # Check if admin user exists
        admin = db.query(User).filter(User.email == "admin@rfminsights.com").first()
        
        if not admin:
            # Create admin user
            admin = User(
                email="admin@rfminsights.com",
                password=get_password_hash("admin123"),  # Change this in production
                full_name="Admin User",
                company_name="RFM Insights",
                is_active=True,
                is_admin=True
            )
            db.add(admin)
            db.commit()
            print("Admin user created successfully!")
        else:
            print("Admin user already exists.")
        
        # Add more seed data here as needed
        
        print("Database seeded successfully!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()

def main():
    """Main function to handle database migrations"""
    parser = argparse.ArgumentParser(description="RFM Insights Database Migrations")
    parser.add_argument('--init', action='store_true', help='Initialize the database')
    parser.add_argument('--drop', action='store_true', help='Drop all database tables')
    parser.add_argument('--seed', action='store_true', help='Seed the database with initial data')
    
    args = parser.parse_args()
    
    if args.init:
        init_db()
    elif args.drop:
        drop_db()
    elif args.seed:
        seed_db()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()