# Graide

Graide is a data analytics system designed to turn raw academic results into explainable insights for students, teachers, and administrators.

## 🚀 Overview

This project implements a **Data → Metrics → Insights → NLP** pipeline to analyze student performance trends, improvement/decline, and subject correlations. Unlike black-box ML models, this engine prioritizes **explainability** and **rule-based logic** to provide transparent actionable feedback.

### Key Features
- **Trend Analysis**: Tracks performance over time (Semesters/Years).
- **Insight Detection**: Automatically identifies significant improvements or declines.
- **Natural Language Summaries**: Converts data insights into human-readable text.
- **Machine Learning**: Predicts future scores and assesses dropout risks (Clustering & Linear Regression).
- **Role-Based Access**: Secure JWT authentication. Teachers only see metrics for their assigned subjects, while Admins have full access.
- **Subject Correlations**: Heatmaps showing relationships between subject performances.
- **API First**: Fully decoupled FastAPI backend serving ready-to-consume insights.

## 🏗 Architecture

The system is built on a 4-layer architecture:

1.  **Data Layer**: Ingests normalized CSV data.
2.  **Metrics Layer**: Computes objective statistics (averages, deltas, correlations).
3.  **Insight Layer**: Applies rules to metrics to detect patterns.
4.  **NLP Layer**: Generates English descriptions from structured insights.

## 🛠 Tech Stack

- **Core Engine**: Python (Pandas, NumPy)
- **API**: FastAPI (Uvicorn)
- **Frontend**: Next.js (React, Tailwind CSS, Recharts)

## 📦 Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/michaelnkema1/results-analytics-engine.git
    cd results-analytics-engine
    ```

2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Initialize the database with demo users:
    ```bash
    python3 src/api/seed.py
    ```

    *(Note: For the frontend, run `npm install` inside `src/web` if starting manually).*

## 🏃 Usage

### 1. Unified Start (Recommended)
The easiest way to start both the backend and frontend is using the helper script:

**Linux/Mac:**
```bash
./start.sh
```

**Windows:**
Double-click `start.bat` or run:
```cmd
start.bat
```

- **Backend API**: `http://localhost:8000`
- **Web Dashboard**: `http://localhost:3000`

### Demo Accounts
- **Admin**: `admin@graide.com` / `adminpassword` (Full Access, Can Upload Data)
- **Teacher (Subject_1)**: `math@graide.com` / `password123`
- **Teacher (Subject_2, Subject_3)**: `science@graide.com` / `password123`

### 2. Manual Startup
If you prefer running them separately:

**Backend:**
```bash
./run_backend.sh
```

**Frontend:**
```bash
cd src/web
npm run dev
```

### 3. API Endpoints
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/datasets/upload` | Upload raw CSV dataset (Admin Only) |
| `POST` | `/api/v1/datasets/{id}/process` | Normalize and ingest dataset (Admin Only) |
| `POST` | `/api/v1/auth/login` | JWT Login endpoint |
| `GET` | `/api/v1/students` | List all students |
| `GET` | `/api/v1/students/{id}/summary` | Individual student performance & automation insights |
| `GET` | `/api/v1/students/{id}/ml/forecast` | Predict future scores via Linear Regression |
| `GET` | `/api/v1/cohort/trends` | Year-over-year subject performance trends (Filtered by Role) |
| `GET` | `/api/v1/cohort/correlations` | Subject correlation matrix (Filtered by Role) |

## 📂 Project Structure

```
.
├── start.sh                # Main entry point (Backend + Frontend)
├── run_backend.sh          # Helper script for backend only
├── results.csv             # Sample dataset
├── requirements.txt        # Python dependencies
├── src/
│   ├── api/                # FastAPI Application
│   │   └── main.py         # API Routes & Lifespan Logic
│   ├── engine/             # Core Analytics Logic
│   │   ├── ingest.py       # Data Ingestion & Normalization
│   │   ├── metrics.py      # Statistical computations
│   │   ├── insights.py     # Rule-based pattern detection
│   │   └── nlp.py          # Text generation
│   └── web/                # Next.js Frontend
│       ├── app/            # App Router Pages
│       ├── components/     # Shared Components
│       └── lib/            # Utilities
```

## 🤝 Contributing

This project is in active development.
- **Phase 1 & 2**: Core Engine & API (Completed)
- **Phase 3**: Web Dashboard (Completed)
- **Phase 4**: Machine Learning / Predictive Models (Completed)
- **Phase 5**: Role-Based Account System (Completed)
- **Phase 6**: Advanced NLP Context Generation (Planned)
