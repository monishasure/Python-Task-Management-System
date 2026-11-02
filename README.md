# CI/CD Python Flask Application

Converted from the original React + Vite sample into a Python Flask application.

## Run locally

1. Install Python 3.10 or newer.
2. Open a terminal in this project folder.
3. (Optional) Create a virtual environment on Windows:
   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Start the application:
   ```bash
   python app.py
   ```
6. Open http://127.0.0.1:5000 in your browser.

## Run with Docker

```bash
docker build -t python-flask-app .
docker run -d -p 5000:5000 --name python-flask-container python-flask-app
```

Then open http://localhost:5000.

## Jenkins

The included Jenkinsfile installs Flask, builds the Docker image, and deploys the container on port 5000. It uses Windows `bat` steps, so run it on a Windows Jenkins agent with Python and Docker available.
