# 1. Appropriate base image
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# 2. Copy only necessary files first (optimizes Docker cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# 3. Expose the correct port (Flask defaults to 5000)
EXPOSE 5000

# 4. Define CMD to start the application
CMD ["flask", "run", "--host=0.0.0.0"]