FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create a non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Set environment variables
ENV PYTHONPATH=/app:/app/src:/app
ENV PORT=8000

# Expose the port
EXPOSE 8000

# Run the application
CMD ["python", "-m", "streamlit", "run", "src/app/main.py", "--server.port=8000", "--server.enableCORS=false", "--server.address=0.0.0.0"] 