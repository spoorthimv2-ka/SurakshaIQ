# 🚔 SurakshaIQ
### AI-Powered Crime Intelligence & Predictive Policing Platform

<p align="center">
  <img src="https://img.shields.io/badge/Built%20For-KSP%20Datathon%202026-blue?style=for-the-badge">
  <img src="https://img.shields.io/badge/Platform-Zoho%20Catalyst-green?style=for-the-badge">
  <img src="https://img.shields.io/badge/Frontend-React%20%2B%20TypeScript-61DAFB?style=for-the-badge">
  <img src="https://img.shields.io/badge/Backend-FastAPI-orange?style=for-the-badge">
  <img src="https://img.shields.io/badge/AI-LLM%20Powered-purple?style=for-the-badge">
</p>

---

## 📌 Overview

**SurakshaIQ** is an AI-driven Crime Intelligence Platform developed for the **Karnataka State Police Datathon 2026**.

The platform transforms raw FIRs, crime records, criminal networks, and historical police data into actionable intelligence through predictive analytics, hotspot detection, anomaly detection, network analysis, and AI-generated strategic insights.

Instead of simply visualizing crime data, SurakshaIQ helps law enforcement **predict**, **prioritize**, and **prevent** crime.

---

# ✨ Key Features

## 🗺️ Crime Dashboard
- Real-time crime statistics
- FIR analytics
- Crime trend visualization
- District-wise crime distribution
- Interactive charts

---

## 🔥 Crime Hotspot Detection

- AI-generated hotspot identification
- Heatmap visualization
- District ranking
- Station-wise hotspot analysis
- Risk scoring

---

## 📈 Predictive Crime Analytics

- Crime forecasting
- Emerging hotspot prediction
- Temporal intelligence
- Risk index generation
- Patrol recommendations

---

## 🧠 AI Executive Intelligence

Generate strategic insights instantly using LLMs:

- Crime summaries
- District intelligence reports
- Predictive recommendations
- Executive briefing
- Natural language analytics

---

## 🕵️ Repeat Offender Analysis

Automatically identifies:

- Habitual offenders
- Repeat crime patterns
- Criminal history
- Frequency analysis

---

## 🕸 Criminal Network Analysis

Visualizes relationships between:

- Criminals
- Crimes
- FIRs
- Police Stations
- Connected cases

---

## ⚠️ Anomaly Detection

AI detects:

- Unusual crime spikes
- Suspicious activity
- Abnormal reporting trends
- Statistical outliers

---

## 📊 Reports & Intelligence

Generate:

- Crime Reports
- District Reports
- Predictive Reports
- Executive Intelligence Reports

---

## 👮 Role Based Access Control

Supports multiple police roles:

- System Administrator
- State Command
- Range IG
- District SP
- CID Analyst
- Station House Officer
- Investigating Officer

Each role receives access based on operational jurisdiction.

---

# 🏗️ System Architecture

```
                    +---------------------+
                    |     React Client    |
                    +----------+----------+
                               |
                               |
                               ▼
                    +----------------------+
                    | FastAPI Backend API  |
                    +----------+-----------+
                               |
      -------------------------------------------------
      |         |          |          |               |
      ▼         ▼          ▼          ▼               ▼
 Datastore   AI Engine  Analytics  Prediction   Authentication
      |         |          |          |               |
      -----------------------------------------------
                      Zoho Catalyst Platform
```

---

# ⚙️ Tech Stack

## Frontend

- React
- TypeScript
- Tailwind CSS
- React Query
- React Router
- Recharts

---

## Backend

- FastAPI
- Python
- JWT Authentication
- Pydantic
- Async Architecture

---

## Database

- Zoho Catalyst Datastore

Tables include:

- Officer
- Crime
- FIR
- Criminal
- PoliceStation
- District
- CrimeHotspot
- PredictionLedger
- AuditLog
- CrimeCriminalLink
- Alerts
- Reports

---

## AI

- Large Language Models
- Executive Intelligence
- Predictive Analysis
- Crime Summarization
- Strategic Recommendations

---

## Deployment

- Zoho Catalyst AppSail
- Catalyst Functions
- Docker
- Catalyst Web Client

---

# 📂 Project Structure

```
SurakshaIQ/

├── appsail/
│   ├── suraksha-iq-backend/
│   └── Dockerfile
│
├── client/
│   ├── src/
│   ├── public/
│   └── package.json
│
├── functions/
│   ├── system_setup/
│   └── catalyst_bootstrap/
│
├── docs/
│
├── README.md
└── catalyst.json
```

---

# 🚀 Getting Started

## Clone Repository

```bash
git clone https://github.com/<username>/SurakshaIQ.git

cd SurakshaIQ
```

---

## Backend

```bash
cd appsail/suraksha-iq-backend

pip install -r requirements.txt

uvicorn app.main:app --reload
```

---

## Frontend

```bash
cd client

npm install

npm run dev
```

---

# 🔐 Demo Credentials

## System Administrator

```
Badge Number:
KSP-000001

Password:
Demo@1234
```

---

# 📊 Modules

- Dashboard
- Crime Management
- FIR Management
- Hotspot Detection
- Predictive Analytics
- Repeat Offender Analysis
- Criminal Network Analysis
- AI Executive Intelligence
- Reports
- Alerts
- Administration

---

# 🧩 Highlights

- AI-first policing platform
- Predictive crime intelligence
- LLM-powered executive summaries
- Interactive analytics dashboards
- Automated hotspot detection
- Criminal relationship mapping
- Secure RBAC authentication
- Built on Zoho Catalyst Cloud

---

# 🎯 Use Cases

✔ Crime Pattern Analysis

✔ Predictive Policing

✔ Resource Allocation

✔ District Intelligence

✔ Executive Decision Support

✔ Criminal Link Analysis

✔ Investigation Assistance

✔ Public Safety Planning

---

# 👨‍💻 Team

Developed for the **Karnataka State Police Datathon 2026**.

---

# 📜 License

This project is developed solely for educational and hackathon purposes.

---

<p align="center">
<b>🚔 SurakshaIQ — Empowering Smarter, Faster & AI-Driven Policing 🚔</b>
</p>