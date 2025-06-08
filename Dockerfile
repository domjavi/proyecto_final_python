# Use the official Python image as a base
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Instalar netcat para usar 'nc' en start.sh
RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

# Copy only the requirements file to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Copy the start script
COPY start.sh .

# Make the start script executable
RUN chmod +x start.sh

# Expose the application port
EXPOSE 8000

# Run the application
CMD ["./start.sh"]