import subprocess
import sys

print("Installing dependencies from requirements.txt...")
subprocess.run([
    sys.executable, "-m", "pip", "install", 
    "-q", "-r", "requirements.txt"
], check=True)

print("Starting Streamlit on port 8100...")
subprocess.run([
    "streamlit", "run", "main.py",
    "--server.port", "8100",
    "--server.address", "0.0.0.0"
])
