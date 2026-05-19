import subprocess
import sys
import os

print("Installing dependencies from requirements.txt...")
subprocess.run([
    sys.executable, "-m", "pip", "install", 
    "-q", "-r", "requirements.txt"
], check=True)

print(f"Starting Streamlit on port {os.getenv('CDSW_APP_PORT', '8080')}...")
subprocess.run([
    "streamlit", "run", "main.py",
    "--server.port", os.getenv("CDSW_APP_PORT", "8080"),
    "--server.address", "127.0.0.1"
])
