# python slim image as base
FROM python:3.9-slim-buster

# Set working directory
WORKDIR /app
RUN apt-get update && apt-get install -y sqlite3 && rm -rf /var/lib/apt/lists/*
# Copy requirements file and install dependencies
COPY requirements.txt ./ 
RUN pip install --no-cache-dir -r requirements.txt 

# Copy app files and database
COPY . /app/  
COPY reservations.db /app/  

# Command to run Flask app
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
