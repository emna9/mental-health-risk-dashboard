# Mental Health Risk Insights Dashboard

An interactive Streamlit dashboard with a FastAPI backend for exploring mental health patterns, comparing machine learning models, and trying predictions with a tuned Balanced Random Forest. Includes demographic analysis, lifestyle and support indicators, model comparisons, and a filterable data explorer.

## What You Can Explore

- **Population overview:** filter records by demographic characteristics and compare patterns across groups.
- **Symptoms and contributing factors:** explore relationships between reported symptoms, work stress, lifestyle habits, and social support.
- **Model Lab:** compare HistGradientBoosting, XGBoost, and Balanced Random Forest using saved evaluation metrics and feature importance.
- **Prediction Sandbox:** enter a sample profile to explore the selected model's output.
- **Data Explorer:** inspect filtered records and download them as CSV for further analysis.

Streamlit provides the interface and Plotly charts, while FastAPI exposes analytics and prediction endpoints. Shared Python services handle data preparation for the dashboard, filtering, and model inference; the notebooks document the training and evaluation workflow.

## Dataset

Uses the [Global Mental Health & Lifestyle Survey Dataset](https://www.kaggle.com/datasets/dhrubangtalukdar/global-mental-health-and-lifestyle-survey-dataset) by **Dhrubang Talukdar** on Kaggle: 10,000 synthetic records with 50 input features and the binary target `Has_Mental_Health_Issue`.

The source CSV is in `data/raw/`; cleaned data, modeling data, and benchmark results are in `data/processed/`. These files and the trained model are included, so no separate download or training is needed to start the dashboard.

**For educational purposes only.** The data is synthetic and does not represent real individuals. Predictions illustrate model behavior and must not be used for diagnosis or medical decisions. Feature importance shows associations, not causation.

## Repository Structure

```text
app/
  backend/           # FastAPI routes, schemas, and dependencies
  config/            # Data and model paths
  dashboard/         # Streamlit interface and reusable components
  services/          # Data loading, analytics, filtering, and prediction
  utils/             # Constants, formatting, and plots
.streamlit/          # Dashboard theme and configuration
data/
  raw/               # Source dataset
  processed/         # Prepared datasets and model comparison results
models/              # Trained Balanced Random Forest artifact
*.ipynb              # Data preparation, model training, and comparison
streamlit_app.py     # Dashboard entry point
requirements.txt    # Python dependencies
```

## Installation and Run

Use Python 3.12 or newer. From the repository root, create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell, activate it with `.venv\Scripts\Activate.ps1` instead. On systems where Python is named `python3`, use that command to create the environment.

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Start the backend:

```bash
python -m uvicorn app.backend.main:app --reload
```

In a second terminal, activate the same environment and start the dashboard from the repository root:

```bash
python -m streamlit run streamlit_app.py
```

Open the dashboard at **http://localhost:8501**. API documentation is available at **http://localhost:8000/docs**. Both processes must remain running. The frontend connects to `http://localhost:8000` by default; set `BACKEND_URL` in its terminal to use a different backend address.

## Modeling

The notebooks cover data preparation, HistGradientBoosting, XGBoost, Balanced Random Forest, and model comparison. The dashboard reads saved benchmark results and uses `models/balanced_rf_artifact.joblib` for predictions. Prior diagnosis and treatment-related columns are excluded from prediction inputs to reduce target leakage.

The target classes are highly imbalanced, so model ranking prioritizes balanced accuracy, followed by minority-class recall and F1. The tuned Balanced Random Forest leads the saved comparison on balanced accuracy (0.6043), although its modest performance reinforces the project's educational scope.

If the artifact is missing or incompatible with your installed libraries, rebuild it in the activated environment, then restart the backend:

```bash
python -c "from app.services.model_service import train_and_persist_best_model; print(train_and_persist_best_model(force=True))"
```

To explore the notebooks, also install `jupyterlab matplotlib seaborn` with pip and run `jupyter lab` from the repository root. Notebook data paths are relative to that directory.
