# Academic Analytics Engine

A data analytics system designed to turn raw academic results into explainable insights for students, teachers, and administrators.

## 🚀 Overview

This project implements a **Data → Metrics → Insights → NLP** pipeline to analyze student performance trends, improvement/decline, and subject correlations. Unlike black-box ML models, this engine prioritizes **explainability** and **rule-based logic** to provide transparent actionable feedback.

### Key Features
- **Trend Analysis**: Tracks performance over time (Semesters/Years).
- **Insight Detection**: Automatically identifies significant improvements or declines.
- **Natural Language Summaries**: Converts data insights into human-readable text.
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
- **Frontend**: Next.js (Planned Phase 3)

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

## 🏃 Usage

### 1. Run the Backend API
You can start the FastAPI server using the helper script:

```bash
./run_backend.sh
```
*Server runs on `http://localhost:8000` with hot-reload enabled.*

### 2. Verify Data Pipeline & API
To verify that the engine and API are working correctly with your dataset:

```bash
python3 verify_api.py   # Tests API Endpoints
# OR
python3 verify_engine.py # Tests Core Logic directly
```

### 3. API Endpoints
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Health check and data status |
| `GET` | `/api/v1/students/{id}/summary` | Individual student performance, history, and NLP insights |
| `GET` | `/api/v1/cohort/trends` | Year-over-year subject performance trends |
| `GET` | `/api/v1/cohort/correlations` | Subject correlation matrix and insights |

### 4. Run the Web Dashboard
Open a new terminal and start the Next.js frontend:

```bash
cd src/web
npm run dev
```
*Dashboard runs on `http://localhost:3000`.*

## 📂 Project Structure

```
.
├── normalize.py            # Data preprocessing script
├── normalized_results.csv  # Cleaned dataset
├── run_backend.sh          # Helper script to start backend
├── verify_api.py           # API Verification script
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
│       ├── components/     # Shared Components (Navbar)
│       └── lib/            # Utilities (API Client)
```

## 🤝 Contributing

This project is currently in active development.
Phase 3 (Web Dashboard) is coming next.
