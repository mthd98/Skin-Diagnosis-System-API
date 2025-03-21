# Use Python 3.12 Slim
FROM python:3.12.6-slim

# Set working directory inside the container
WORKDIR /Skin-Diagnosis-System-API

# Copy application files into the container
COPY . /Skin-Diagnosis-System-API

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose FastAPI API port
EXPOSE 8080

# Ensure the container runs FastAPI correctly
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
