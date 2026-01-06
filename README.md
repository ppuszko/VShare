# Vectorized Multi-Tenant Document Management Service
### A specialized document management system designed for secure, group-isolated data ingestion and hybrid search. This project provides a structured pipeline for processing documents, generating embeddings via an asynchronous worker, and querying data within strict multi-tenant boundaries.

# System Architecture
The system is split into three main components:

### FastAPI Backend: Handles user authentication, group-based permission logic (Multi-tenancy), and provides endpoints for document metadata management and search.

### Hybrid Search Engine: Combines traditional metadata filtering (categories, timeframes) with dense and sparse search to capture both semantic meaning and specific keywords. Seaerching is pefromed on quantized dense vectors for high efficiency. Resulting pool of fetched data is then reranked with multi-vectors to provde highest data accuracy.

### Asynchronous Worker: A dedicated worker process that handles document parsing and embedding generation with work report sent via e-mail.

# Multi-Tenancy & Security
The system is built from the ground up to support Group Isolation:

Ownership: Every document and vector chunk is tied to a group_uid and a user_uid.

Isolation: Users can only search, view, or upload documents belonging to their specific group.

RBAC: Integrated Role-Based Access Control (Admin/User) to manage group-level permissions.

# Features
Data Ingestion Pipeline
Async Processing: Documents are uploaded and immediately handed off to the worker.
Metadata Association: Support for user-defined per-group categories and titles during upload.
