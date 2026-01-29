# Academic Analytics Engine

A data analytics system designed to turn raw academic results into explainable insights for students, teachers, and administrators.

## 🚀 Overview

This project implements a **Data → Metrics → Insights → NLP** pipeline to analyze student performance trends, improvement/decline, and subject correlations. Unlike black-box ML models, this engine prioritizes **explainability** and **rule-based logic** to provide transparent actionable feedback.

### Key Features
- **Trend Analysis**: Tracks performance over time (Semesters/Years).
- **Insight Detection**: Automatically identifies significant improvements or declines.
- **Natural Language Summaries**: Converts data insights into human-readable text.
- **Cohort Analysis**: (In Progress) Metrics for entire batches/classes.

## 🏗 Architecture

The system is built on a 4-layer architecture:

1.  **Data Layer**: Ingests normalized CSV data.
2.  **Metrics Layer**: Computes objective statistics (averages, deltas, correlations).
3.  **Insight Layer**: Applies rules to metrics to detect patterns.
4.  **NLP Layer**: Generates English descriptions from structured insights.

## 🛠 Tech Stack

- **Core Engine**: Python (Pandas, NumPy)
- **API**: FastAPI (Planned)
- **Frontend**: Next.js (Planned)

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

## 🏃 Usage (Core Engine)

To verify the core logic and see sample insights in the console:

```bash
python3 verify_engine.py
```

## 📂 Project Structure

```
.
├── normalize.py            # Data preprocessing script
├── normalized_results.csv  # Cleaned dataset
├── verify_engine.py        # Pipeline verification script
├── src/
│   ├── api/                # FastAPI application (Coming Soon)
│   └── engine/             # Core Analytics Logic
│       ├── metrics.py      # Statistical computations
│       ├── insights.py     # Rule-based pattern detection
│       └── nlp.py          # Text generation
```

## 🤝 Contributing

This project is currently in active development.

