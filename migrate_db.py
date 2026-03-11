#!/usr/bin/env python3

from app.database import engine
from sqlalchemy import text

def migrate_database():
    """Add missing columns to the database schema"""

    with engine.connect() as conn:
        try:
            print("🔍 Checking existing columns...")

            # Check if columns exist first
            result = conn.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'users'
                AND column_name IN ('employee_id', 'department')
            """))
            existing_cols = [row[0] for row in result.fetchall()]

            print(f"Existing columns: {existing_cols}")

            # Add employee_id column if it doesn't exist
            if 'employee_id' not in existing_cols:
                print("📝 Adding employee_id column...")
                conn.execute(text('ALTER TABLE users ADD COLUMN employee_id VARCHAR(50) UNIQUE'))
                print('✅ Added employee_id column')
            else:
                print('✅ employee_id column already exists')

            # Add department column if it doesn't exist
            if 'department' not in existing_cols:
                print("📝 Adding department column...")
                conn.execute(text('ALTER TABLE users ADD COLUMN department VARCHAR(100)'))
                print('✅ Added department column')
            else:
                print('✅ department column already exists')

            # Check and add unique constraint on attendance table
            print("🔍 Checking attendance table constraints...")
            result = conn.execute(text("""
                SELECT constraint_name
                FROM information_schema.table_constraints
                WHERE table_name = 'attendance'
                AND constraint_type = 'UNIQUE'
                AND constraint_name = 'unique_user_date'
            """))

            if not result.fetchone():
                print("📝 Adding unique constraint on attendance table...")
                conn.execute(text('ALTER TABLE attendance ADD CONSTRAINT unique_user_date UNIQUE (user_id, date)'))
                print('✅ Added unique constraint on attendance table')
            else:
                print('✅ Unique constraint already exists on attendance table')

            conn.commit()
            print('🎉 Database schema migration completed successfully!')

        except Exception as e:
            print(f'❌ Migration failed: {e}')
            conn.rollback()
            raise

if __name__ == "__main__":
    migrate_database()