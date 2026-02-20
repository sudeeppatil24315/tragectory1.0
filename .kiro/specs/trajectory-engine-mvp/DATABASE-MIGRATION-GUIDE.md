# Database Migration Guide

Complete guide for migrating data between PostgreSQL and MongoDB databases.

---

## 📋 Table of Contents

1. [PostgreSQL to PostgreSQL Migration](#1-postgresql-to-postgresql-migration)
2. [PostgreSQL to MongoDB Migration](#2-postgresql-to-mongodb-migration)
3. [MongoDB to PostgreSQL Migration](#3-mongodb-to-postgresql-migration)
4. [Best Practices](#4-best-practices)

---

## 1. PostgreSQL to PostgreSQL Migration

### Method 1: pg_dump and pg_restore (Recommended)

**Best for**: Complete database migration, production backups

```bash
# Step 1: Dump source database
pg_dump -h source_host -U source_user -d source_db -F c -f backup.dump

# Step 2: Restore to target database
pg_restore -h target_host -U target_user -d target_db backup.dump

# With password (Windows)
set PGPASSWORD=your_password
pg_dump -h source_host -U source_user -d source_db -F c -f backup.dump
pg_restore -h target_host -U target_user -d target_db backup.dump
```

**Options**:
- `-F c`: Custom format (compressed, best for large DBs)
- `-F p`: Plain SQL format (human-readable)
- `-t table_name`: Dump specific table only
- `--data-only`: Data without schema
- `--schema-only`: Schema without data

**Example - Specific Table**:
```bash
# Dump only students table
pg_dump -h localhost -U postgres -d trajectory_db -t students -F c -f students.dump

# Restore to new database
pg_restore -h new_host -U postgres -d new_db students.dump
```

---

### Method 2: SQL Export/Import

**Best for**: Small databases, cross-version compatibility

```bash
# Step 1: Export to SQL file
pg_dump -h source_host -U source_user -d source_db > backup.sql

# Step 2: Import to target database
psql -h target_host -U target_user -d target_db < backup.sql
```

**Example - Your Project**:
```bash
# Export from Arun's PC
pg_dump -h 192.168.1.100 -U postgres -d trajectory_db > trajectory_backup.sql

# Import to your local PC
psql -h localhost -U postgres -d trajectory_db < trajectory_backup.sql
```

---

### Method 3: Python Script (Programmatic)

**Best for**: Selective migration, data transformation, automation

```python
# migrate_postgres_to_postgres.py

import psycopg2
from psycopg2.extras import RealDictCursor

# Source database connection
source_conn = psycopg2.connect(
    host="source_host",
    database="source_db",
    user="source_user",
    password="source_password"
)

# Target database connection
target_conn = psycopg2.connect(
    host="target_host",
    database="target_db",
    user="target_user",
    password="target_password"
)

def migrate_table(table_name):
    """Migrate a single table from source to target"""
    
    # Fetch data from source
    with source_conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
    
    print(f"Fetched {len(rows)} rows from {table_name}")
    
    # Insert into target
    if rows:
        columns = rows[0].keys()
        placeholders = ', '.join(['%s'] * len(columns))
        insert_query = f"""
            INSERT INTO {table_name} ({', '.join(columns)})
            VALUES ({placeholders})
            ON CONFLICT DO NOTHING
        """
        
        with target_conn.cursor() as cursor:
            for row in rows:
                values = [row[col] for col in columns]
                cursor.execute(insert_query, values)
        
        target_conn.commit()
        print(f"Inserted {len(rows)} rows into {table_name}")

# Migrate specific tables
tables = ['users', 'students', 'alumni', 'skills']
for table in tables:
    try:
        migrate_table(table)
        print(f"✅ {table} migrated successfully")
    except Exception as e:
        print(f"❌ Error migrating {table}: {e}")

source_conn.close()
target_conn.close()
```

**Run it**:
```bash
python migrate_postgres_to_postgres.py
```

---

### Method 4: Using SQLAlchemy (ORM-based)

**Best for**: Projects already using SQLAlchemy

```python
# migrate_with_sqlalchemy.py

from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker

# Source database
source_engine = create_engine('postgresql://user:pass@source_host/source_db')
source_session = sessionmaker(bind=source_engine)()

# Target database
target_engine = create_engine('postgresql://user:pass@target_host/target_db')
target_session = sessionmaker(bind=target_engine)()

# Reflect tables from source
metadata = MetaData()
metadata.reflect(bind=source_engine)

def migrate_table(table_name):
    """Migrate table using SQLAlchemy"""
    
    # Get table object
    table = Table(table_name, metadata, autoload_with=source_engine)
    
    # Fetch all rows from source
    with source_engine.connect() as conn:
        result = conn.execute(table.select())
        rows = result.fetchall()
    
    print(f"Fetched {len(rows)} rows from {table_name}")
    
    # Insert into target
    if rows:
        with target_engine.connect() as conn:
            conn.execute(table.insert(), [dict(row._mapping) for row in rows])
            conn.commit()
    
    print(f"✅ Migrated {table_name}")

# Migrate tables
tables = ['users', 'students', 'alumni']
for table in tables:
    migrate_table(table)
```

---

## 2. PostgreSQL to MongoDB Migration

### Method 1: Python Script (Recommended)

**Best for**: Full control, data transformation

```python
# migrate_postgres_to_mongodb.py

import psycopg2
from psycopg2.extras import RealDictCursor
from pymongo import MongoClient
from datetime import datetime

# PostgreSQL connection
pg_conn = psycopg2.connect(
    host="localhost",
    database="trajectory_db",
    user="postgres",
    password="your_password"
)

# MongoDB connection
mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["trajectory_db"]

def migrate_students():
    """Migrate students table to MongoDB collection"""
    
    # Fetch from PostgreSQL
    with pg_conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("""
            SELECT id, user_id, name, major, semester, gpa, attendance,
                   study_hours_per_week, project_count, created_at, updated_at
            FROM students
        """)
        students = cursor.fetchall()
    
    print(f"Fetched {len(students)} students from PostgreSQL")
    
    # Transform and insert into MongoDB
    mongo_collection = mongo_db["students"]
    
    documents = []
    for student in students:
        doc = {
            "_id": student["id"],  # Use PostgreSQL ID as MongoDB _id
            "user_id": student["user_id"],
            "name": student["name"],
            "major": student["major"],
            "semester": student["semester"],
            "academic": {
                "gpa": float(student["gpa"]) if student["gpa"] else None,
                "attendance": float(student["attendance"]) if student["attendance"] else None
            },
            "behavioral": {
                "study_hours_per_week": student["study_hours_per_week"],
                "project_count": student["project_count"]
            },
            "created_at": student["created_at"],
            "updated_at": student["updated_at"]
        }
        documents.append(doc)
    
    # Insert into MongoDB
    if documents:
        result = mongo_collection.insert_many(documents, ordered=False)
        print(f"✅ Inserted {len(result.inserted_ids)} students into MongoDB")

def migrate_alumni():
    """Migrate alumni table to MongoDB collection"""
    
    with pg_conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("""
            SELECT id, name, major, graduation_year, gpa, attendance,
                   placement_status, company_tier, role_title, salary_range,
                   role_to_major_match_score, created_at
            FROM alumni
        """)
        alumni = cursor.fetchall()
    
    print(f"Fetched {len(alumni)} alumni from PostgreSQL")
    
    mongo_collection = mongo_db["alumni"]
    
    documents = []
    for alum in alumni:
        doc = {
            "_id": alum["id"],
            "name": alum["name"],
            "major": alum["major"],
            "graduation_year": alum["graduation_year"],
            "academic": {
                "gpa": float(alum["gpa"]) if alum["gpa"] else None,
                "attendance": float(alum["attendance"]) if alum["attendance"] else None
            },
            "placement": {
                "status": alum["placement_status"],
                "company_tier": alum["company_tier"],
                "role_title": alum["role_title"],
                "salary_range": alum["salary_range"],
                "role_to_major_match": alum["role_to_major_match_score"]
            },
            "created_at": alum["created_at"]
        }
        documents.append(doc)
    
    if documents:
        result = mongo_collection.insert_many(documents, ordered=False)
        print(f"✅ Inserted {len(result.inserted_ids)} alumni into MongoDB")

# Run migrations
try:
    migrate_students()
    migrate_alumni()
    print("\n✅ Migration completed successfully!")
except Exception as e:
    print(f"❌ Migration failed: {e}")
finally:
    pg_conn.close()
    mongo_client.close()
```

**Install dependencies**:
```bash
pip install psycopg2 pymongo
```

**Run it**:
```bash
python migrate_postgres_to_mongodb.py
```

---

### Method 2: Using Pandas (Data Transformation)

**Best for**: Complex data transformations, analytics

```python
# migrate_with_pandas.py

import pandas as pd
from sqlalchemy import create_engine
from pymongo import MongoClient

# PostgreSQL connection
pg_engine = create_engine('postgresql://user:pass@localhost/trajectory_db')

# MongoDB connection
mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["trajectory_db"]

def migrate_table_to_collection(table_name, collection_name=None):
    """Migrate PostgreSQL table to MongoDB collection using Pandas"""
    
    if collection_name is None:
        collection_name = table_name
    
    # Read from PostgreSQL into DataFrame
    df = pd.read_sql_table(table_name, pg_engine)
    
    print(f"Loaded {len(df)} rows from {table_name}")
    
    # Convert DataFrame to list of dictionaries
    records = df.to_dict('records')
    
    # Handle datetime conversion
    for record in records:
        for key, value in record.items():
            if pd.isna(value):
                record[key] = None
            elif isinstance(value, pd.Timestamp):
                record[key] = value.to_pydatetime()
    
    # Insert into MongoDB
    collection = mongo_db[collection_name]
    if records:
        result = collection.insert_many(records)
        print(f"✅ Inserted {len(result.inserted_ids)} documents into {collection_name}")

# Migrate tables
migrate_table_to_collection('students')
migrate_table_to_collection('alumni')
migrate_table_to_collection('skills')

print("\n✅ All tables migrated to MongoDB!")
```

---

### Method 3: CSV Export/Import

**Best for**: Simple migrations, no code required

```bash
# Step 1: Export PostgreSQL table to CSV
psql -h localhost -U postgres -d trajectory_db -c "\COPY students TO 'students.csv' CSV HEADER"

# Step 2: Import CSV to MongoDB using mongoimport
mongoimport --db trajectory_db --collection students --type csv --headerline --file students.csv
```

**Python alternative**:
```python
# export_to_csv.py
import psycopg2
import csv

conn = psycopg2.connect("postgresql://user:pass@localhost/trajectory_db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM students")
rows = cursor.fetchall()
columns = [desc[0] for desc in cursor.description]

with open('students.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(columns)
    writer.writerows(rows)

print("✅ Exported to students.csv")
```

---

## 3. MongoDB to PostgreSQL Migration

### Method 1: Python Script

```python
# migrate_mongodb_to_postgres.py

from pymongo import MongoClient
import psycopg2
from psycopg2.extras import execute_values

# MongoDB connection
mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["trajectory_db"]

# PostgreSQL connection
pg_conn = psycopg2.connect(
    host="localhost",
    database="trajectory_db",
    user="postgres",
    password="your_password"
)

def migrate_students():
    """Migrate students collection to PostgreSQL table"""
    
    # Fetch from MongoDB
    students = list(mongo_db["students"].find())
    
    print(f"Fetched {len(students)} students from MongoDB")
    
    # Prepare data for PostgreSQL
    values = []
    for student in students:
        values.append((
            student.get("_id"),
            student.get("user_id"),
            student.get("name"),
            student.get("major"),
            student.get("semester"),
            student.get("academic", {}).get("gpa"),
            student.get("academic", {}).get("attendance"),
            student.get("behavioral", {}).get("study_hours_per_week"),
            student.get("behavioral", {}).get("project_count"),
            student.get("created_at"),
            student.get("updated_at")
        ))
    
    # Insert into PostgreSQL
    with pg_conn.cursor() as cursor:
        insert_query = """
            INSERT INTO students (
                id, user_id, name, major, semester, gpa, attendance,
                study_hours_per_week, project_count, created_at, updated_at
            ) VALUES %s
            ON CONFLICT (id) DO UPDATE SET
                name = EXCLUDED.name,
                gpa = EXCLUDED.gpa,
                attendance = EXCLUDED.attendance
        """
        execute_values(cursor, insert_query, values)
        pg_conn.commit()
    
    print(f"✅ Inserted {len(values)} students into PostgreSQL")

# Run migration
try:
    migrate_students()
    print("\n✅ Migration completed!")
except Exception as e:
    print(f"❌ Migration failed: {e}")
    pg_conn.rollback()
finally:
    pg_conn.close()
    mongo_client.close()
```

---

## 4. Best Practices

### 🔒 Security

```python
# Use environment variables for credentials
import os
from dotenv import load_dotenv

load_dotenv()

pg_conn = psycopg2.connect(
    host=os.getenv("PG_HOST"),
    database=os.getenv("PG_DATABASE"),
    user=os.getenv("PG_USER"),
    password=os.getenv("PG_PASSWORD")
)
```

### 📊 Progress Tracking

```python
from tqdm import tqdm

def migrate_with_progress(rows):
    """Migrate with progress bar"""
    for row in tqdm(rows, desc="Migrating"):
        # Insert row
        pass
```

### 🔄 Batch Processing

```python
def migrate_in_batches(rows, batch_size=1000):
    """Process large datasets in batches"""
    
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i + batch_size]
        
        # Insert batch
        with target_conn.cursor() as cursor:
            execute_values(cursor, insert_query, batch)
            target_conn.commit()
        
        print(f"Processed {i + len(batch)}/{len(rows)} rows")
```

### ✅ Data Validation

```python
def validate_migration(source_count, target_count):
    """Validate migration success"""
    
    if source_count == target_count:
        print(f"✅ Validation passed: {source_count} rows")
        return True
    else:
        print(f"❌ Validation failed: {source_count} source, {target_count} target")
        return False

# Example
source_count = source_cursor.execute("SELECT COUNT(*) FROM students").fetchone()[0]
target_count = target_cursor.execute("SELECT COUNT(*) FROM students").fetchone()[0]
validate_migration(source_count, target_count)
```

### 🔙 Backup Before Migration

```bash
# Always backup before migration!
pg_dump -h localhost -U postgres -d trajectory_db -F c -f backup_before_migration.dump
```

### 📝 Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migration.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def migrate_table(table_name):
    logger.info(f"Starting migration of {table_name}")
    try:
        # Migration code
        logger.info(f"✅ {table_name} migrated successfully")
    except Exception as e:
        logger.error(f"❌ Failed to migrate {table_name}: {e}")
```

---

## 🎯 Quick Reference

### PostgreSQL → PostgreSQL
```bash
# Full database
pg_dump -h source -U user -d db | psql -h target -U user -d db

# Single table
pg_dump -h source -U user -d db -t table | psql -h target -U user -d db
```

### PostgreSQL → MongoDB
```python
# Python script (see Method 1 above)
python migrate_postgres_to_mongodb.py
```

### MongoDB → PostgreSQL
```python
# Python script (see Method 1 above)
python migrate_mongodb_to_postgres.py
```

---

## 🚀 Your Project - Practical Example

### Migrate from Arun's PC to Your PC

```python
# migrate_arun_to_local.py

import psycopg2
from psycopg2.extras import execute_values

# Arun's database (source)
source_conn = psycopg2.connect(
    host="192.168.1.100",  # Arun's IP
    database="trajectory_db",
    user="postgres",
    password="arun_password"
)

# Your local database (target)
target_conn = psycopg2.connect(
    host="localhost",
    database="trajectory_db",
    user="postgres",
    password="your_password"
)

tables = ['users', 'students', 'alumni', 'skills', 'trajectory_scores']

for table in tables:
    print(f"\nMigrating {table}...")
    
    # Fetch from Arun's DB
    with source_conn.cursor() as cursor:
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
    
    print(f"  Fetched {len(rows)} rows")
    
    # Insert into your DB
    if rows:
        placeholders = ', '.join(['%s'] * len(columns))
        insert_query = f"""
            INSERT INTO {table} ({', '.join(columns)})
            VALUES ({placeholders})
            ON CONFLICT DO NOTHING
        """
        
        with target_conn.cursor() as cursor:
            execute_values(cursor, insert_query, rows)
            target_conn.commit()
        
        print(f"  ✅ Inserted {len(rows)} rows")

print("\n✅ All tables migrated successfully!")

source_conn.close()
target_conn.close()
```

---

## 📚 Tools & Libraries

### Required Python Packages
```bash
pip install psycopg2-binary pymongo pandas sqlalchemy python-dotenv tqdm
```

### Useful Tools
- **pgAdmin**: PostgreSQL GUI
- **MongoDB Compass**: MongoDB GUI
- **DBeaver**: Universal database tool
- **DataGrip**: JetBrains database IDE

---

## ⚠️ Common Issues

### Issue 1: Connection Timeout
```python
# Increase timeout
conn = psycopg2.connect(
    host="remote_host",
    connect_timeout=30  # 30 seconds
)
```

### Issue 2: Large Dataset Memory Issues
```python
# Use server-side cursor
cursor = conn.cursor(name='fetch_large_dataset')
cursor.itersize = 1000  # Fetch 1000 rows at a time
```

### Issue 3: Data Type Mismatches
```python
# Handle type conversions
def convert_value(value, target_type):
    if value is None:
        return None
    if target_type == 'int':
        return int(value)
    if target_type == 'float':
        return float(value)
    return str(value)
```

---

**Summary**: Use `pg_dump/pg_restore` for PostgreSQL→PostgreSQL, Python scripts for PostgreSQL↔MongoDB. Always backup first!
