# Command Code GO API Wrapper (V1)

## Overview

Proyek ini bertujuan membangun REST API yang membungkus Command Code CLI menggunakan akun Command Code GO.

Sistem ini memungkinkan aplikasi lain mengakses kemampuan Command Code melalui HTTP API tanpa perlu upgrade ke paket Pro.

Backend akan menjalankan Command Code CLI secara otomatis menggunakan worker yang dikontrol oleh queue.

---

# Goals

Tujuan utama:

- Mengekspos Command Code GO sebagai REST API.
- Mendukung mode Chat dan Agent.
- Menyediakan antrean job yang stabil.
- Menjalankan maksimal 2 worker secara paralel.
- Mengisolasi workspace setiap job.
- Menyediakan API Key Authentication.
- Tetap ringan dan mudah dideploy.

---

# Non Goals

Versi pertama tidak mencakup:

- PostgreSQL
- Dashboard Admin
- Multi Tenant
- Billing System
- Kubernetes
- Horizontal Scaling
- Streaming Response
- WebSocket

---

# Technology Stack

## Backend

- Python 3.12+
- FastAPI
- Uvicorn

## Queue System

- Redis
- RQ (Redis Queue)

## Runtime

- Command Code CLI

## Reverse Proxy

- Nginx (opsional)

## Deployment

- Ubuntu Server VM
- Docker Compose

---

# Architecture

```text
Client
   │
   ▼
FastAPI
   │
   ▼
Redis Queue
   │
   ├─────────────┐
   ▼             ▼
Worker 1     Worker 2
   │             │
   ▼             ▼
 cmd -p       cmd -p
 --yolo       --yolo
```

---

# Why Redis?

Hasil benchmark:

```bash
cmd -p "hello"
```

≈ 10-20 detik

```bash
cmd -p "buatkan CRUD Express.js"
```

≈ 40 detik

Karena setiap request membutuhkan waktu cukup lama, diperlukan sistem antrean agar:

- request tidak bentrok
- worker dapat dikontrol
- proses lebih stabil
- mudah di-scale di masa depan

Redis dipilih karena:

- ringan
- mudah diinstall
- konsumsi RAM kecil
- cocok untuk queue sederhana

---

# Worker Strategy

Jumlah worker:

```text
2 Worker
```

Alasan:

- penggunaan pribadi
- hasil testing menunjukkan beberapa proses Command Code dapat berjalan bersamaan
- mengurangi risiko rate limit
- tetap memungkinkan concurrency ringan

Flow:

```text
Request 1 → Worker 1
Request 2 → Worker 2
Request 3 → Queue
Request 4 → Queue
```

---

# Job Lifecycle

## Step 1

Client mengirim request:

```http
POST /v1/chat
```

atau

```http
POST /v1/agent
```

---

## Step 2

FastAPI membuat:

```text
job_id
```

Contoh:

```text
job_123
```

---

## Step 3

Job dimasukkan ke Redis Queue.

Status:

```text
queued
```

---

## Step 4

Worker mengambil job.

Status:

```text
running
```

---

## Step 5

Worker menjalankan:

Chat Mode:

```bash
cmd -p "<prompt>"
```

Agent Mode:

```bash
cmd -p "<prompt>" --yolo
```

---

## Step 6

Hasil disimpan.

Status:

```text
completed
```

atau

```text
failed
```

---

# Workspace Isolation

Setiap job memiliki workspace sendiri.

Struktur:

```text
/workspaces
│
├── job_001
├── job_002
├── job_003
└── job_004
```

Contoh:

```bash
/workspaces/job_001
```

Worker akan:

```bash
cd /workspaces/job_001

cmd -p "buatkan CRUD Express.js" --yolo
```

Keuntungan:

- file tidak saling bertabrakan
- lebih aman
- lebih mudah dibersihkan

---

# Storage Strategy

Versi pertama tidak menggunakan database.

Data job disimpan dalam file JSON.

Contoh:

```text
/storage
│
├── jobs.json
└── api_keys.json
```

---

## jobs.json

Contoh:

```json
{
  "job_123": {
    "status": "completed",
    "created_at": "...",
    "completed_at": "...",
    "result": "..."
  }
}
```

---

## api_keys.json

Contoh:

```json
[
  {
    "name": "default",
    "api_key": "sk_xxxxx"
  }
]
```

---

# API Design

## POST /v1/chat

Chat biasa.

Request:

```json
{
  "prompt": "jelaskan JWT"
}
```

Response:

```json
{
  "job_id": "job_123",
  "status": "queued"
}
```

---

## POST /v1/agent

Agent mode.

Request:

```json
{
  "prompt": "buatkan CRUD Express.js"
}
```

Response:

```json
{
  "job_id": "job_456",
  "status": "queued"
}
```

Worker akan menjalankan:

```bash
cmd -p "<prompt>" --yolo
```

---

## GET /v1/jobs/{job_id}

Response:

```json
{
  "job_id": "job_123",
  "status": "running"
}
```

atau

```json
{
  "job_id": "job_123",
  "status": "completed",
  "result": "..."
}
```

---

# Authentication

Menggunakan API Key.

Header:

```http
Authorization: Bearer sk_xxxxx
```

Semua endpoint wajib menggunakan API Key.

---

# Rate Limiting

Versi pertama:

```text
20 request / menit
```

per API Key.

Implementasi menggunakan Redis.

---

# Logging

Setiap job menyimpan:

- prompt
- execution time
- status
- error
- worker

Tujuan:

- debugging
- monitoring
- audit sederhana

---

# Error Handling

Handle kondisi:

- timeout
- Command Code crash
- Redis disconnect
- invalid API key
- worker exception

Status:

```text
failed
```

beserta pesan error.

---

# Docker Compose

Service yang dijalankan:

```text
api
redis
worker-1
worker-2
```

Tidak ada PostgreSQL.

Tidak ada RabbitMQ.

Tidak ada Celery.

---

# Deployment Requirement

VM Ubuntu:

```text
CPU  : 4 vCPU
RAM  : 4-8 GB
Disk : 30+ GB
```

Sudah lebih dari cukup.

---

# Future Upgrade Path

Jika penggunaan meningkat:

V2:

- PostgreSQL
- Dashboard
- OpenAI Compatible Endpoint

V3:

- Streaming Response
- WebSocket
- Multi User

V4:

- Horizontal Worker Scaling
- Kubernetes

---

# Final Objective

Membangun API pribadi berbasis Command Code GO yang:

- ringan
- mudah di-maintain
- mendukung 2 worker paralel
- aman melalui workspace isolation
- siap digunakan oleh aplikasi lain melalui HTTP API
- mudah ditingkatkan ke arsitektur yang lebih besar di masa depan
