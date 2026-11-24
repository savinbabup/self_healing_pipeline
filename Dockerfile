# Self-Healing CI/CD Pipeline — calculator app in a container
FROM python:3.11-slim

WORKDIR /app

COPY self-healing/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY self-healing/ .

CMD ["python", "-m", "pytest", "test_calc.py", "-q"]
