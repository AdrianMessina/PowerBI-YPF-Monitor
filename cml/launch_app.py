"""Cloudera CDSW/CML Application entry point for YPF BI Monitor."""

import os
import subprocess
import sys

subprocess.run([
    sys.executable, "-m", "streamlit", "run", "main.py",
    "--server.port", os.environ.get("CDSW_APP_PORT", "8501"),
    "--server.address", "127.0.0.1",
    "--server.headless", "true",
    "--server.useStarlette", "false",
    "--browser.gatherUsageStats", "false",
])
