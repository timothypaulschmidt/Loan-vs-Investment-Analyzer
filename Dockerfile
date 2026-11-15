# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory in container
WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY src/ ./src/

# Listen on all interfaces inside the container, on port 8070
ENV HOST=0.0.0.0
ENV PORT=8070

# Document the port the app uses (you still map it with: docker run -p 8070:8070)
EXPOSE 8070

# Run the application
CMD ["python", "src/main.py"]
