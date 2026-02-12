# Record Manipulator Backend API

## Overview

This project is a **Record Manipulator Backend API** that allows users to:

- Upload **CSV** or **Excel (XLS/XLSX)** files
- Create datasets from uploaded files
- Perform full **CRUD operations** on:
  - Datasets
  - Records inside each dataset
- Filter, sort, paginate, and export records
- Export datasets back to **CSV/XLSX**

The system is designed as a **production-grade backend service** using a **layered architecture** to ensure:

- Clear separation of concerns  
- Scalability  
- Maintainability  
- Team collaboration readiness  
- Clean domain boundaries  

The project uses **PostgreSQL** for persistence, **Redis** for caching/ephemeral state, and **uv** as the Python package manager.

---

## Badges

![Python](https://img.shields.io/badge/python-3.12-blue?logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/postgresql-15-blue?logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/redis-7.0-orange?logo=redis&logoColor=white)
![FastAPI](https://img.shields.io/badge/fastapi-0.110-green?logo=fastapi)
![Code Quality](https://img.shields.io/badge/code%20quality-A%2B-brightgreen)

---

## Core Features

### Dataset Management
- Upload CSV/XLS/XLSX files  
- Auto-schema detection  
- Dataset versioning  
- Dataset ownership enforcement  
- Dataset export  

### Record Management
- Paginated record listing  
- JSON-based record storage  
- Partial updates  
- Batch updates  
- Filtering (JSONB)  
- Sorting (JSONB + relational fields)  
- Full CRUD support  

### Data Operations
- CSV import  
- Excel import  
- CSV export  
- Excel export  
- Batch processing  
- Streaming exports  

---

## Table of Contents

- Python Package Manager  
- Python Tools  
- Databases  
- Architecture  
- Folder Structure  
- Running the Application  
- Database Migrations  
- Pre-commit Hooks  
- API Capabilities  
- Notes  

---

## Python Package Manager

### Installing dependencies
- Create a **python virtual environment**

```bash
python-3 -m venv .venv
```
- Activate the Virtual environment
```bash
. .venv/bin/activate
```

- Install Dependencies

```bash
pip install -r requirements.txt
```

## Migragration
Run alembic migration
### Prerequisite
- Set up Databse variables in the .env file
```bash
alembic upgrade head
```

## API Capabilities
### Dataset APIs

- Create dataset from CSV/XLSX
- List datasets
- Update dataset metadata
- Delete dataset
- Export dataset

### Record APIs
- Create record
- Update record
- Batch update records
- Delete record
- Filter records
- Sort records
- Paginate records
- JSONB query support

## Data Model Strategy
### Hybrid Storage

- Relational fields → metadata, ownership, indexing
- JSONB fields → dynamic record structure

This enables:

- Flexible schemas
- Dynamic datasets
- Fast structured queries
- Strong relational guarantees

## Notes

- CSV/XLSX upload is streamed
- Large file handling supported
- Memory-safe exports
- Deterministic pagination
- Schema validation on ingest
- Ownership enforcement
- Role-based access ready
- Multi-tenant ready

### References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Redis-Py Documentation](https://pypi.org/project/redis/)

