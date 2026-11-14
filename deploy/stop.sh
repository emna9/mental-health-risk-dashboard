#!/usr/bin/env bash
# Stop the dashboard, its API, and the public tunnel.
pkill -f 'streamlit run streamlit_app.py' 2>/dev/null
pkill -f 'uvicorn app.backend.main:app' 2>/dev/null
pkill -f 'cloudflared tunnel --url' 2>/dev/null
echo "Stopped dashboard processes."
