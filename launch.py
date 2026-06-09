#!/usr/bin/env python3
"""CML Launch Script — starts YPF BI Monitor on CDSW_APP_PORT."""

import os
import subprocess

port = os.environ.get("CDSW_APP_PORT", "8501")

print(f"🚀 Starting YPF BI Monitor on port {port}...")

subprocess.run([
    "streamlit", "run", "main.py",
    f"--server.port={port}",
    "--server.address=127.0.0.1",
    "--server.headless=true",
    "--server.enableCORS=false",
    "--browser.gatherUsageStats=false",
])
