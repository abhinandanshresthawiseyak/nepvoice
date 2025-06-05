# Use official Python image as a base
FROM python:3.9-slim

# Set working directory
WORKDIR /backend

RUN apt-get update && apt-get install -y \
        ffmpeg 
        
# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port that FastAPI will run on
EXPOSE 5678

# Run FastAPI application with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5678","--reload"]
