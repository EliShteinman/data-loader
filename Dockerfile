# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the dependencies file and install them
# This leverages Docker's layer caching for faster builds
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's source code
COPY ./services /app/services

# Expose port 8080 for the application
EXPOSE 8080

# The command to run the application when the container starts
# Note the path to the 'app' object: services.data_loader.main:app
CMD ["uvicorn", "services.data_loader.main:app", "--host", "0.0.0.0", "--port", "8080"]