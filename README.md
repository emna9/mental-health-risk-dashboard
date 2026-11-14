# Mental Health Risk Insights Dashboard

**Live demo:** https://dashboard-isg3.onrender.com
**API docs:** https://dashboard-api-zkvb.onrender.com/docs

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

## Deployment

The Docker image runs the FastAPI backend and the Streamlit dashboard in one container. The backend listens on loopback and the dashboard is the only exposed port, so a single public URL is enough. The image installs `requirements-runtime.txt`; XGBoost and the notebook tooling in `requirements.txt` are only needed for training.

### Docker (any host)

```bash
docker build -t mental-health-risk-dashboard .
docker run --rm -p 8501:8501 mental-health-risk-dashboard
```

Or with compose:

```bash
docker compose up --build
```

Then open **http://localhost:8501**. The container health check hits `/_stcore/health`.

### Render (one-click blueprint)

[`render.yaml`](render.yaml) deploys **two free web services** from the same image, because a single 512 MB free instance cannot hold Streamlit and the prediction model at once:

- `dashboard-api` (`APP_MODE=api`): FastAPI only, health check at `/api/v1/health`.
- `dashboard` (`APP_MODE=ui`): Streamlit only, health check at `/_stcore/health`, with `BACKEND_URL` wired to the API service via `fromService`.

1. Push this repository to GitHub.
2. In Render, choose **New > Blueprint** and select the repository. Render reads `render.yaml`.
3. Wait for both builds and open the `dashboard` service URL.

Each free service stays under its 512 MB limit: the API idles near 150 MB and peaks around 310 MB when a prediction loads the model; the dashboard needs roughly 300 MB. Free services sleep after ~15 minutes, so the first request after idle can take a minute while both wake. Increase `BACKEND_TIMEOUT` if that is not enough.

### Other container hosts

The same `Dockerfile` works on Railway, Fly.io, Koyeb, or a VPS. Set `APP_MODE` to `full` (default), `api`, or `ui`. Requirements:

- Expose the container port (`PORT`, default `8501`).
- For `ui`, set `BACKEND_URL` to the API service address.
- Point the platform health check at `/_stcore/health` (UI) or `/api/v1/health` (API).

### Temporary public URL from a local machine

`deploy/start.sh` runs both processes locally and opens a Cloudflare quick tunnel:

```bash
bash deploy/start.sh    # prints PUBLIC URL
bash deploy/stop.sh     # stops everything
```

Quick-tunnel URLs are ephemeral: they change on every restart and stop working when the machine sleeps or the process exits. Use a container host for a stable URL.

### Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `APP_MODE` | `full` | `full` (API + dashboard), `api` (API only), `ui` (dashboard only) |
| `BACKEND_URL` | `http://localhost:8000` | Backend address used by the dashboard (URL or bare hostname) |
| `BACKEND_HOST` / `BACKEND_PORT` | `127.0.0.1` / `8000` | Backend bind address in `full` mode |
| `BACKEND_TIMEOUT` | `90` | Seconds to wait for the API, including cold starts |
| `PORT` | `8501` | Public port (set automatically by most platforms) |
| `ALLOWED_ORIGINS` | `http://localhost:8501,http://127.0.0.1:8501` | Comma-separated CORS origins for the API |

## Modeling

The notebooks cover data preparation, HistGradientBoosting, XGBoost, Balanced Random Forest, and model comparison. The dashboard reads saved benchmark results and uses `models/balanced_rf_artifact.joblib` for predictions. Prior diagnosis and treatment-related columns are excluded from prediction inputs to reduce target leakage.

The target classes are highly imbalanced, so model ranking prioritizes balanced accuracy, followed by minority-class recall and F1. The tuned Balanced Random Forest leads the saved comparison on balanced accuracy (0.6043), although its modest performance reinforces the project's educational scope.

If the artifact is missing or incompatible with your installed libraries, rebuild it in the activated environment, then restart the backend:

```bash
python -c "from app.services.model_service import train_and_persist_best_model; print(train_and_persist_best_model(force=True))"
```

To explore the notebooks, also install `jupyterlab matplotlib seaborn` with pip and run `jupyter lab` from the repository root. Notebook data paths are relative to that directory.
